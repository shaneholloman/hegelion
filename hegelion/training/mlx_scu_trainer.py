"""
Hegelion MLX SCU Trainer
Combines Apple Silicon optimization (MLX) with Shannon Control Unit (SCU) adaptive regularization.

Logic:
1. Train Loop in MLX
2. Calculate DataBPT (Loss)
3. Calculate ParamBPT (LoRA weights complexity)
4. Update Lambda (Regularization strength) via PID Control
5. Optimize: Loss = CE + lambda * L2
"""

import time
import math
import json
import argparse
from pathlib import Path
import numpy as np

# MLX imports
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
from mlx.utils import tree_flatten, tree_map

# MLX-LM imports
try:
    import ai2_olmo
except ImportError:
    pass
from mlx_lm import load
from mlx_lm.tuner.utils import linear_to_lora_layers


# SCU Control Logic (Re-implemented for independence)
def calculate_data_bpt(loss_nats):
    return loss_nats / math.log(2)

def calculate_param_bpt(model, sigma=0.01, tokens_per_epoch=1000000):
    """Calculate ParamBPT for trainable parameters (LoRA) in MLX."""
    param_sum = 0.0
    
    # Iterate over trainable parameters
    # In MLX, we filter for trainable ones. 
    # Since we apply LoRA, usually only LoRA layers are trainable.
    # We can iterate the tree.
    
    total_params = 0
    for name, weight in tree_flatten(model.trainable_parameters()):
        # Sum of squares
        param_sum += mx.sum(weight ** 2).item()
        total_params += weight.size
        
    if total_params == 0:
        return 1e-9 # Avoid zero division
        
    # Convert to bits
    param_bpt = param_sum / (2 * sigma**2 * tokens_per_epoch * math.log(2))
    return param_bpt, param_sum

def update_lambda(lmbda, S_meas, S_target, I, Kp=0.8, Ki=0.15, deadband=0.002, 
                  lmin=1e-4, lmax=10.0, i_min=-0.2, i_max=0.2):
    """PID Controller for Lambda."""
    error = S_meas - S_target
    
    if abs(error) <= deadband:
        return lmbda, I * 0.995 # Leak
        
    I = I * 0.995
    I = max(i_min, min(i_max, I + Ki * error))
    
    control_effort = Kp * error + I
    lmbda_new = lmbda * math.exp(control_effort)
    lmbda_new = max(lmin, min(lmax, lmbda_new))
    
    return lmbda_new, I

def loss_fn(model, inputs, targets, lmbda, sigma, tokens_per_epoch, lengths):
    # Forward pass
    logits = model(inputs)
    logits = logits.astype(mx.float32)
    
    # Cross Entropy Loss
    # Masking padding tokens: we assume inputs are padded with 0 or similar and ignore them?
    # Actually mlx_lm trainer usually handles masking if provided.
    # Here we'll do a standard CE.
    
    ce_loss = nn.losses.cross_entropy(logits, targets, reduction='none')
    
    # Mask out padding (assuming lengths provided or implicit)
    # For simplicity, average over all non-masked
    mask = (targets != -100) # Standard ignore index
    ce_loss = mx.sum(ce_loss * mask) / mx.sum(mask)
    
    # SCU Regularization Term
    # L2 = sum(w^2) / (2*sigma^2)
    # We calculate this purely for gradients.
    # ParamBPT calculation is separate but related.
    
    l2_sum = 0
    for _, weight in tree_flatten(model.trainable_parameters()):
        l2_sum = l2_sum + mx.sum(weight ** 2)
        
    reg_term = l2_sum / (2 * sigma**2)
    
    # Total Loss = CE + lambda * (Reg_term normalized per token??)
    # In SCU derivation: Loss = CE + lambda * Reg_loss_per_token
    # Reg_loss_per_token = ParamBPT * ln(2) = sum(w^2) / (2*sigma^2 * N)
    # So we divide by tokens_per_epoch (N)
    
    total_reg = (lmbda * reg_term) / tokens_per_epoch
    
    return ce_loss + total_reg, ce_loss

def train_scu(args):
    np.random.seed(args.seed)
    mx.random.seed(args.seed)

    print(f"Loading model: {args.model}")
    model, tokenizer = load(args.model)
    
    # Freeze base model before applying LoRA so quantized weights stay constant
    model.freeze()
    
    # Apply LoRA
    print("Applying LoRA adapters...")
    # We use the standard config usually passed to mlx_lm
    lora_config = {
        "rank": args.lora_rank,
        "scale": float(args.lora_alpha),
        "dropout": args.lora_dropout,
        # "keys": ["q_proj", "v_proj", "k_proj", "o_proj"] # Let auto-detect work
    }
    
    # Apply to all layers
    linear_to_lora_layers(model, num_layers=1000, config=lora_config)

    # Ensure only LoRA adapters are trainable to avoid gradients through quantized weights
    model.freeze()  # freeze newly created modules (base weights stay frozen)

    def _unfreeze_lora_params(_, module):
        if hasattr(module, "lora_a") and hasattr(module, "lora_b"):
            module.unfreeze(keys=["lora_a", "lora_b"], recurse=False)

    model.apply_to_modules(_unfreeze_lora_params)

    n_trainable = sum(p.size for _, p in tree_flatten(model.trainable_parameters()))
    print(f"Trainable parameters: {n_trainable}")
    if n_trainable == 0:
        raise ValueError("No trainable parameters! LoRA failed to apply.")

    # Optimizer
    optimizer = optim.AdamW(learning_rate=args.lr)
    
    # SCU State
    lmbda = args.lambda_init
    I = 0.0
    tokens_per_epoch = args.tokens_per_epoch # Fixed normalization constant
    sigma = args.prior_sigma
    
    # Data Loading
    print(f"Loading data from {args.data}")
    
    # Simple dataset loader
    def load_dataset(path):
        data = []
        with open(path, 'r') as f:
            for line in f:
                if not line.strip(): continue
                obj = json.loads(line)
                text = obj.get('text', '')
                if text:
                    # Tokenize
                    # Append EOS
                    ids = tokenizer.encode(text) + [tokenizer.eos_token_id]
                    data.append(np.array(ids))
        return data

    dataset = load_dataset(args.data)
    print(f"Loaded {len(dataset)} examples")
    
    # Training Loop
    steps = 0
    max_steps = args.iters
    batch_size = args.batch_size
    
    # Prepare function for grad
    # We use nn.value_and_grad which handles trainable parameters automatically
    
    loss_value_and_grad = nn.value_and_grad(model, loss_fn)

    def step(model, inputs, targets, lmbda):
        (loss, ce_loss), grads = loss_value_and_grad(
            model, inputs, targets, lmbda, sigma, tokens_per_epoch, None
        )
        return loss, ce_loss, grads

    print("Starting SCU Training...")
    
    # Create batches manually for control
    # We simply shuffle and slice
    
    while steps < max_steps:
        # Shuffle
        indices = np.random.permutation(len(dataset))
        
        for i in range(0, len(dataset), batch_size):
            if steps >= max_steps: break
            
            batch_idx = indices[i:i+batch_size]
            batch_data = [dataset[k] for k in batch_idx]
            
            # Pad batch
            max_len = max(len(x) for x in batch_data)
            # Truncate if too long?
            if max_len > 2048: max_len = 2048
            
            inputs_np = np.zeros((len(batch_data), max_len), dtype=np.int32)
            targets_np = np.full((len(batch_data), max_len), -100, dtype=np.int32) # -100 for ignore
            
            for j, seq in enumerate(batch_data):
                L = min(len(seq), max_len)
                # Causal LM: input is seq[:-1], target is seq[1:]
                # But usually we just feed seq and shift inside or feed (seq[:-1], seq[1:])
                # Let's do (seq[:-1], seq[1:])
                if L < 2: continue
                
                # Inputs
                inputs_np[j, :L-1] = seq[:L-1]
                # Targets
                targets_np[j, :L-1] = seq[1:L]
            
            inputs = mx.array(inputs_np)
            targets = mx.array(targets_np)
            
            # Step
            (total_loss, ce_loss_val, grads) = step(model, inputs, targets, lmbda)
            
            optimizer.update(model, grads)
            mx.eval(model.parameters(), optimizer.state)
            
            # SCU Updates (Post-step measurement)
            # Calculate BPTs
            data_bpt = calculate_data_bpt(ce_loss_val.item())
            param_bpt, _ = calculate_param_bpt(model, sigma, tokens_per_epoch)
            
            S_meas = param_bpt / (data_bpt + param_bpt + 1e-9)
            
            # Update Lambda
            lmbda_old = lmbda
            lmbda, I = update_lambda(lmbda, S_meas, args.target_s, I, Kp=args.kp, Ki=args.ki)
            
            # Logging
            if steps % 10 == 0:
                print(f"Step {steps}: Loss={ce_loss_val.item():.3f}, DataBPT={data_bpt:.3f}, "
                      f"ParamBPT={param_bpt:.5f}, S={S_meas:.2%}, λ={lmbda_old:.3f} -> {lmbda:.3f}")
            
            steps += 1
            
            # Save adapter occasionally
            if steps % 100 == 0:
                print(f"Saving adapter to {args.adapter_path}")
                model.save_weights(str(Path(args.adapter_path) / "weights.safetensors"))
                with open(Path(args.adapter_path) / "adapter_config.json", "w") as f:
                    json.dump(lora_config, f, indent=2)

    # Final Save
    Path(args.adapter_path).mkdir(parents=True, exist_ok=True)
    model.save_weights(str(Path(args.adapter_path) / "weights.safetensors"))
    with open(Path(args.adapter_path) / "adapter_config.json", "w") as f:
        json.dump(lora_config, f, indent=2)
    print("Training complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="mlx-community/OLMo-7B-0724-hf-4bit")
    parser.add_argument("--data", required=True)
    parser.add_argument("--adapter_path", default="adapters/hegelion_mlx_scu")
    parser.add_argument("--iters", type=int, default=1000)
    parser.add_argument("--batch_size", type=int, default=1)
    parser.add_argument("--lr", type=float, default=1e-5)
    
    # LoRA Args
    parser.add_argument("--lora_rank", type=int, default=16)
    parser.add_argument("--lora_alpha", type=int, default=32)
    parser.add_argument("--lora_dropout", type=float, default=0.05)
    
    # SCU Args
    parser.add_argument("--target_s", type=float, default=0.01)
    parser.add_argument("--kp", type=float, default=0.8)
    parser.add_argument("--ki", type=float, default=0.15)
    parser.add_argument("--lambda_init", type=float, default=1.0)
    parser.add_argument("--prior_sigma", type=float, default=0.01)
    parser.add_argument("--tokens_per_epoch", type=float, default=1000000)
    parser.add_argument("--seed", type=int, default=42)
    
    args = parser.parse_args()
    train_scu(args)

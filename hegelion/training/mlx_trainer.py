"""
Hegelion MLX Trainer for Apple Silicon

Fine-tunes an OLMo/Llama/Qwen model on Hegelion reasoning traces using LoRA.
Optimized for M-series chips (M1/M2/M3/M4).

Requirements:
    pip install mlx-lm
"""

import argparse
import importlib.util
import sys
from pathlib import Path

if importlib.util.find_spec("mlx_lm") is None:
    print("Error: mlx-lm not installed. Run: pip install mlx-lm", file=sys.stderr)
    sys.exit(1)


def train_hegelion_adapter(
    model_path: str,
    data_path: str,
    adapter_path: str = "artifacts/adapters",
    iters: int = 600,
    batch_size: int = 1,
    lora_layers: int = 8,
    learning_rate: float = 1e-5,
    **kwargs,
):
    print("--- Hegelion MLX Trainer ---")
    print(f"Model: {model_path}")
    print(f"Data: {data_path}")

    # We shell out to the mlx_lm CLI for robustness,
    # as it handles the complex training loop, validation, and saving perfectly.
    # This is the standard recommended way to use MLX for LoRA.

    cmd = [
        sys.executable,
        "-m",
        "mlx_lm.lora",
        "--model",
        model_path,
        "--train",
        "--data",
        data_path,  # Expects directory with train.jsonl / valid.jsonl
        "--iters",
        str(iters),
        "--batch-size",
        str(batch_size),
        "--num-layers",
        str(lora_layers),
        "--learning-rate",
        str(learning_rate),
        "--adapter-path",
        adapter_path,
        "--save-every",
        "100",
        "--steps-per-eval",
        "50",
    ]

    if kwargs.get("max_seq_length"):
        cmd.extend(["--max-seq-length", str(kwargs["max_seq_length"])])

    if kwargs.get("grad_checkpoint"):
        cmd.append("--grad-checkpoint")

    print(f"Running: {' '.join(cmd)}")

    import subprocess

    try:
        subprocess.run(cmd, check=True)
        print(f"\nSuccess! Adapters saved to {adapter_path}")
        print("To fuse and upload:")
        print(
            f"  python -m mlx_lm.fuse --model {model_path} --adapter-path {adapter_path} --upload-name my-hegelion-model"
        )
    except subprocess.CalledProcessError as e:
        print(f"Training failed with error: {e}")
        sys.exit(1)


def prepare_data_for_mlx(jsonl_path: str, output_dir: str = "artifacts/data/mlx"):
    """
    MLX expects a directory with 'train.jsonl' and 'valid.jsonl'.
    This helper converts our single generator output to that format.
    """
    import json
    import random

    path = Path(jsonl_path)
    if not path.exists():
        print(f"Data file not found: {jsonl_path}")
        return

    out_path = Path(output_dir)
    out_path.mkdir(exist_ok=True)

    print(f"Preparing data from {jsonl_path}...")

    data = []
    with open(path, "r") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                obj = json.loads(line)

                # Standardize reasoning tags for DeepSeek R1 models
                # R1 expects <think>...</think> but our data might have <thought>
                output_text = obj.get("output", "")
                output_text = output_text.replace("<thought>", "<think>").replace(
                    "</thought>", "</think>"
                )

                # MLX format: {"text": "..."}
                # We need to construct the full prompt text including system/user/assistant tokens
                # Simple ChatML-like format for now

                text = (
                    "<|im_start|>system\n"
                    f"{obj.get('system', '')}<|im_end|>\n"
                    "<|im_start|>user\n"
                    f"{obj.get('instruction', '')}<|im_end|>\n"
                    "<|im_start|>assistant\n"
                    f"{output_text}<|im_end|>\n"
                )
                data.append({"text": text})
            except Exception:
                pass

    random.shuffle(data)
    split_idx = int(len(data) * 0.9)
    train_data = data[:split_idx]
    valid_data = data[split_idx:]

    with open(out_path / "train.jsonl", "w") as f:
        for entry in train_data:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")

    with open(out_path / "valid.jsonl", "w") as f:
        for entry in valid_data:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")

    print(
        f"Saved {len(train_data)} training and {len(valid_data)} validation examples to {output_dir}/"
    )
    return str(out_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B")
    parser.add_argument("--data", required=True, help="Path to generated hegelion_kimi_data.jsonl")
    parser.add_argument("--iters", type=int, default=600)
    parser.add_argument("--batch-size", type=int, default=1, help="Batch size per step")
    parser.add_argument("--lora-layers", type=int, default=8, help="Number of LoRA layers")
    parser.add_argument("--max-seq-length", type=int, default=2048, help="Maximum sequence length")
    parser.add_argument(
        "--grad-checkpoint",
        action="store_true",
        help="Enable gradient checkpointing to save memory",
    )
    args = parser.parse_args()

    data_dir = prepare_data_for_mlx(args.data)
    if data_dir:
        train_hegelion_adapter(
            args.model,
            data_dir,
            iters=args.iters,
            batch_size=args.batch_size,
            lora_layers=args.lora_layers,
            max_seq_length=args.max_seq_length,
            grad_checkpoint=args.grad_checkpoint,
        )

"""
Hegelion Unsloth Trainer

This script fine-tunes a Llama-3 model to internalize the dialectical process.
It uses Unsloth for memory-efficient 4-bit training.

Requirements:
    pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
    pip install --no-deps "xformers<0.0.27" "trl<0.9.0" peft accelerate bitsandbytes

Usage:
    python -m hegelion.training.unsloth_trainer --dataset hegelion_data.jsonl
"""

import torch
import sys


def train(
    dataset_path: str,
    model_name: str = "unsloth/llama-3-8b-Instruct-bnb-4bit",
    output_dir: str = "hegelion_lora_model",
    max_seq_length: int = 2048,
):
    # Check for CUDA
    if not torch.cuda.is_available():
        print("WARNING: CUDA not detected. Unsloth requires an NVIDIA GPU.", file=sys.stderr)
        print(
            "This script is intended to run on Linux with GPUs (e.g. Lambda Labs, RunPod).",
            file=sys.stderr,
        )
        return

    from unsloth import FastLanguageModel
    from trl import SFTTrainer
    from transformers import TrainingArguments
    from datasets import load_dataset

    print(f"Loading model: {model_name}")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=max_seq_length,
        dtype=None,
        load_in_4bit=True,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=3407,
        use_rslora=False,
        loftq_config=None,
    )

    # Load Dataset
    # Format: {"instruction": "...", "output": "..."}
    dataset = load_dataset("json", data_files=dataset_path, split="train")

    # Formatting function
    prompt_style = """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{}

### Response:
{}"""

    def formatting_prompts_func(examples):
        instructions = examples["instruction"]
        outputs = examples["output"]
        texts = []
        for instruction, output in zip(instructions, outputs):
            text = prompt_style.format(instruction, output) + tokenizer.eos_token
            texts.append(text)
        return {"text": texts}

    dataset = dataset.map(formatting_prompts_func, batched=True)

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=max_seq_length,
        dataset_num_proc=2,
        packing=False,
        args=TrainingArguments(
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            warmup_steps=5,
            max_steps=60,  # Increase for real training
            learning_rate=2e-4,
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            logging_steps=1,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=3407,
            output_dir=output_dir,
        ),
    )

    print("Starting training...")
    trainer.train()

    print(f"Saving model to {output_dir}...")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    # Save GGUF for local use
    # model.save_pretrained_gguf(output_dir, tokenizer, quantization_method = "q4_k_m")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, help="Path to JSONL dataset")
    parser.add_argument("--output", default="hegelion_adapter")
    args = parser.parse_args()

    train(args.dataset, output_dir=args.output)

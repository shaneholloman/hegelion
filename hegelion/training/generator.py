import asyncio
import json
import os
from pathlib import Path
from typing import Optional

from hegelion.core.core import run_dialectic
from hegelion.core.models import HegelionResult
from hegelion.core.config import get_config, set_config_value
from hegelion.training.wrappers.kimi_cli import get_kimi_cli

try:
    from datasets import load_dataset
except ImportError:
    load_dataset = None


# The "Teacher" System Prompt
# Forces the model to explicate its dialectical reasoning process
TEACHER_SYSTEM_PROMPT = """You are a dialectical reasoning engine. For every user query, you MUST follow this strict thought process:

1. **THESIS**: Propose the strongest initial argument or solution.
2. **ANTITHESIS**: Critically attack the thesis. Find flaws, edge cases, or opposing evidence.
3. **SYNTHESIS**: Resolve the conflict. Create a new, stronger solution that incorporates the valid points of both.

Format your response exactly like this:
<thought>
[The full dialectical trace goes here: Thesis -> Antithesis -> Synthesis]
</thought>
[The final answer goes here]"""


async def generate_dataset(
    dataset_name: str,
    output_file: str,
    split: str = "train",
    column: str = "text",
    limit: int = 100,
    resume: bool = True,
    max_tokens: int = 4000,
    model: str = "kimi", # Default to our teacher
    prompt_file: Optional[str] = None,
):
    """
    Generate dialectical traces for a HuggingFace dataset using a Teacher model (Kimi).
    """
    if load_dataset is None and prompt_file is None:
        raise ImportError("Please install 'datasets' to use this feature: pip install datasets")

    # Configure Teacher
    use_cli = False
    if model == "kimi-cli":
        use_cli = True
        print(" configured to use Moonshot AI (Kimi) via CLI wrapper.")
    elif model == "kimi":
        # Ensure Kimi is configured
        config = get_config()
        if not config.moonshot_key:
             raise ValueError("MOONSHOT_API_KEY not found. Set it in your .env or environment.")
        set_config_value("provider", "moonshot")
        set_config_value("model", "kimi-k2-thinking") # Use the reasoning model
        print(" configured to use Moonshot AI (Kimi) as Teacher.")
    elif model:
        set_config_value("model", model)
        set_config_value("provider", "auto")

    prompts = None
    if prompt_file:
        prompts = [line.strip() for line in Path(prompt_file).read_text().splitlines() if line.strip()]
        print(f"Loaded {len(prompts)} prompts from {prompt_file}")
        ds = [{"prompt": p} for p in prompts]
    else:
        print(f"Loading dataset {dataset_name} ({split})...")
        ds = load_dataset(dataset_name, split=split, streaming=True)
    
    output_path = Path(output_file)
    processed_count = 0
    
    # Resume logic
    if resume and output_path.exists():
        with open(output_path, "r") as f:
            processed_count = sum(1 for _ in f)
        print(f"Resuming from {processed_count} examples...")

    # Iterate and generate
    current_idx = 0
    buffer_size = 1  # Write every N examples
    buffer = []

    for item in ds:
        if current_idx < processed_count:
            current_idx += 1
            continue
            
        if current_idx >= processed_count + limit:
            break

        # Extract prompt (handle different dataset formats)
        if prompt_file:
            query = item.get("prompt", "")
        elif column in item:
            query = item[column]
        elif "prompt" in item:
            query = item["prompt"]
        elif "instruction" in item:
            query = item["instruction"]
        else:
            print(f"Skipping item {current_idx}: No suitable text column found.")
            current_idx += 1
            continue

        # Truncate extremely long inputs to keep teacher focus
        query = query[:2000]

        try:
            print(f"[{current_idx}] Generating dialectic for: {query[:50]}...")
            
            # We run the dialectic. Ideally, we want the backend to use our SYSTEM_PROMPT.
            # However, `run_dialectic` orchestrates T->A->S itself.
            # To perform "Distillation" where Kimi does the *whole* thinking in one shot
            # (as per the Agent plan), we should actually bypass the multi-turn engine
            # and just ask Kimi to produce the trace in one go.
            # BUT, since we have the Hegelion Engine, we can use it to produce structured data too.
            # Let's stick to the Agent Plan: Use Kimi to generate the trace via a single powerful prompt
            # OR let Hegelion Engine orchestrate it.
            # 
            # Decision: Let Hegelion Engine orchestrate it. It produces structured JSON
            # which is cleaner for training than parsing raw text.
            # We just need Kimi to be the backend *intelligence*.
            
            if use_cli:
                # Bypass engine for CLI
                cli = get_kimi_cli()
                # Kimi CLI might not follow "system prompt" strictly in standard mode,
                # but we prepend it to the query.
                
                # IMPORTANT: Ensure no external tools are called unless explicitly desired.
                # Kimi CLI has built-in tools (like search). We want purely internal reasoning
                # based on the prompt to teach "thinking", not "searching".
                # We can't easily disable tools in CLI without flags (if any), but we can instruct:
                no_search_instruction = "Do not use any external tools or web search. Rely only on your internal knowledge."
                
                cli_prompt = f"{no_search_instruction}\n\n{query}"
                raw_response = await cli.generate(cli_prompt, system_prompt=TEACHER_SYSTEM_PROMPT)
                
                # We need to parse the raw response into a HegelionResult-like structure if possible
                # or just use it directly for the dataset if it followed the format.
                # Assuming Kimi CLI follows the prompt:
                
                # Simple parsing logic (robustness needed in prod)
                thesis = ""
                antithesis = ""
                synthesis = ""
                
                # Create a dummy result for consistency
                result = HegelionResult(
                    query=query,
                    mode="synthesis",
                    thesis="[Generated via CLI]", 
                    antithesis="[Generated via CLI]",
                    synthesis=raw_response, # The whole response is the synthesis/trace
                    contradictions=[],
                    research_proposals=[],
                    metadata={"source": "kimi_cli"}
                )
            else:
                result = await run_dialectic(
                    query=query,
                    max_tokens_per_phase=max_tokens,
                    use_search=False 
                )
            
            # Format for Training (Unsloth / MLX)
            # We format the output to look like a "Thinking" model's stream
            
            if use_cli:
                final_output = result.synthesis # CLI returns the full trace directly
            else:
                trace_text = (
                    f"THESIS:\n{result.thesis}\n\n"
                    f"ANTITHESIS:\n{result.antithesis}\n\n"
                    f"SYNTHESIS:\n{result.synthesis}"
                )
                final_output = f"<thought>\n{trace_text}\n</thought>\n{result.synthesis}"

            entry = {
                "instruction": query,
                "input": "",
                "output": final_output,
                "system": "You are a dialectical reasoning engine.",
                "hegelion_trace": result.to_dict() 
            }
            
            buffer.append(json.dumps(entry, ensure_ascii=False))
            
            if len(buffer) >= buffer_size:
                with open(output_path, "a", encoding="utf-8") as f:
                    f.write("\n".join(buffer) + "\n")
                buffer = []
                
        except Exception as e:
            print(f"Error processing item {current_idx}: {e}")
        
        current_idx += 1

    # Flush remaining
    if buffer:
        with open(output_path, "a", encoding="utf-8") as f:
            f.write("\n".join(buffer) + "\n")

    print(f"Done. Saved to {output_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="HuggingFaceH4/ultrafeedback_binarized")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for shuffling")
    parser.add_argument("--output", default="hegelion_kimi_data.jsonl")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--split", default="train", help="Dataset split to use")
    parser.add_argument("--model", help="Teacher model", default="kimi")
    parser.add_argument("--prompt-file", help="Optional newline-delimited prompts to bypass HF datasets")
    args = parser.parse_args()
    
    asyncio.run(generate_dataset(
        dataset_name=args.dataset,
        output_file=args.output,
        split=args.split,
        limit=args.limit,
        model=args.model,
        prompt_file=args.prompt_file
    ))

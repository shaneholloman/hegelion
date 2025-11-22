# Project Status Handover

## 1. Data Generation (Active)
- **Process:** A background job (PID 83875) is generating 1000 dialectical training examples using Kimi CLI.
- **File:** `hegelion_kimi_training_data.jsonl`
- **Status:** Running. The previous process was restarted to fix a bug where raw Python objects were being written to the file. The current output is clean JSON with `<thought>` tags.
- **Goal:** Convert `HuggingFaceH4/ultrafeedback_binarized` into `Thesis->Antithesis->Synthesis` reasoning traces.
- **Action:** Check progress with `wc -l hegelion_kimi_training_data.jsonl`. The script automatically handles resuming if interrupted (run the same command).

## 2. Training Pipeline (Mac/MLX)
- **Goal:** Train `mlx-community/OLMo-7B-0724-hf-4bit` on this data using Shannon Control Unit (SCU) optimization.
- **Script:** `hegelion/training/mlx_scu_trainer.py`
- **Status:** Prototype exists. Tested with dummy data.
- **Next Step:** Once data generation reaches ~1000 samples:
    1. Stop the generator.
    2. Convert data (ensure `text` field exists, though the generator should now produce `output` which is sufficient).
    3. Run training:
       ```bash
       uv run python -m hegelion.training.mlx_scu_trainer \
         --model mlx-community/OLMo-7B-0724-hf-4bit \
         --data hegelion_kimi_training_data.jsonl \
         --adapter_path adapters/hegelion_mlx_scu \
         --iters 100 --batch_size 1
       ```

## 3. Environment
- **Dependencies:** `mlx`, `mlx-lm`, `ai2-olmo` are installed.
- **Hardware:** Apple Silicon (verified working for generation).
- **Tools:** `kimi-cli` is used for data generation (no API key required if configured).

const QuickStart = () => {
  return (
    <section id="quick-start">
      <h2>Quick Start</h2>
      
      <pre><code>{`# Install Hegelion MCP server
pip install hegelion

# Generate dialectical data with Kimi CLI
python -m hegelion.training.generator \\
  --dataset HuggingFaceH4/ultrafeedback_binarized \\
  --output artifacts/data/hegelion_kimi_training_data.jsonl \\
  --limit 500 --model kimi-cli

# Train on Apple Silicon (M1/M2/M3/M4)
uv run python -m hegelion.training.mlx_scu_trainer \\
  --model deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B \\
  --data artifacts/data/hegelion_scu_ready.jsonl \\
  --adapter_path artifacts/adapters/hegelion\\_1.5b\\_v1 \\
  --batch_size 4 --iters 500`}</code></pre>
    </section>
  )
}

export default QuickStart


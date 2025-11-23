const TechnicalSpecs = () => {
  return (
    <section id="technical-specs">
      <h2>Technical Specifications</h2>
      
      <h3>Dialectical Trace Format</h3>
      
      <pre><code>{`{
  "instruction": "How do I improve code review?",
  "output": "<thought>\\n**THESIS**: Mandatory reviews for all PRs...\\n**ANTITHESIS**: Bottlenecks, resentment...\\n**SYNTHESIS**: Tiered system by risk...\\n</thought>\\n\\nImplement tiered review: critical paths...",
  "metadata": {
    "personas": ["logician", "empiricist", "ethicist"],
    "contradictions_found": 7,
    "iterations": 3,
    "synthesis_tokens": 423
  }
}`}</code></pre>
      
      <h3>SCU Control Parameters</h3>
      
      <ul>
        <li><strong>target_s:</strong> 0.01 (desired S-ratio)</li>
        <li><strong>Kp:</strong> 0.8 (proportional gain)</li>
        <li><strong>Ki:</strong> 0.15 (integral gain)</li>
        <li><strong>λ_range:</strong> [1e-4, 10.0] (adaptive regularization strength)</li>
        <li><strong>tokens_per_epoch:</strong> Auto-computed from dataset</li>
      </ul>
      
      <h3>Training Hyperparameters</h3>
      
      <pre><code>{`model: deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B
lora_rank: 16
lora_alpha: 32
lora_dropout: 0.05
learning_rate: 1e-5
batch_size: 4
max_seq_length: 4096
iters: 500
warmup_steps: 50  # conservative
max_grad_norm: 1.0  # for stability`}</code></pre>
    </section>
  )
}

export default TechnicalSpecs


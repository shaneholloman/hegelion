const ForResearchers = () => {
  return (
    <section id="for-researchers">
      <h2>For Researchers</h2>
      
      <h3>Citation</h3>
      
      <pre><code>{`@inproceedings{hegelion2025,
  title={Hegelion: Adversarial Reasoning via Dialectical Synthesis in Language Models},
  author={Your Name},
  booktitle={arXiv preprint arXiv:2411.xxxxx},
  year={2025},
  url={https://github.com/yourusername/hegelion}
}`}</code></pre>
      
      <h3>Reproducibility</h3>
      
      <p>All experiments run with:</p>
      <ul>
        <li><strong>Random seed:</strong> 42 (training), 123/456 (data gen instances)</li>
        <li><strong>Hardware:</strong> Apple M3 Max, 36GB unified memory</li>
        <li><strong>Software:</strong> Python 3.12, mlx-lm 0.21, ai2-olmo 0.3</li>
        <li><strong>Data:</strong> HuggingFaceH4/ultrafeedback_binarized (train_prefs split)</li>
      </ul>
      
      <p>To reproduce:</p>
      <ol>
        <li>Clone repository</li>
        <li>Install dependencies: <code>pip install -r requirements-training.txt</code></li>
        <li>Generate data: <code>python -m hegelion.training.generator --limit 500 --model kimi-cli</code></li>
        <li>Train: <code>uv run python -m hegelion.training.mlx_scu_trainer --iters 500</code></li>
      </ol>
      
      <h3>Open Problems</h3>
      
      <ol>
        <li><strong>Hierarchical Synthesis:</strong> Multi-level dialectics for complex reasoning</li>
        <li><strong>Meta-Learning:</strong> Models that learn to structure their own dialectics</li>
        <li><strong>Verification:</strong> Formal proof that synthesis improves answer quality</li>
        <li><strong>Efficiency:</strong> Reduce compute cost while maintaining quality</li>
        <li><strong>Scale:</strong> Apply to larger models (70B+) with distributed training</li>
      </ol>
    </section>
  )
}

export default ForResearchers


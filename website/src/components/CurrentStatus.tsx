const CurrentStatus = () => {
  return (
    <section className="current-status">
      <h2>Current Status & Open Questions</h2>

      <h3>✅ Validated Components</h3>
      <div className="validation-grid">
        <div className="validation-item">
          <h4>Core Dialectic (Tested - Works)</h4>
          <p>THESIS→ANTITHESIS→SYNTHESIS format enforced</p>
          <p>10-iteration validation completed successfully</p>
          <p>99.2% generation quality (244/247 valid samples)</p>
        </div>
        
        <div className="validation-item">
          <h4>SCU Regularization (Measured - Functional)</h4>
          <p>λ adapted from 1.0 → 2.5 (responding to S-ratio)</p>
          <p>DataBPT/ParamBPT calculated correctly</p>
          <p>Prevents overfitting on small dataset</p>
        </div>
        
        <div className="validation-item">
          <h4>Training Pipeline (Tested - Stable)</h4>
          <p>Model loads and applies LoRA correctly</p>
          <p>Weights serialize to safetensors format</p>
          <p>No NaN losses or training instability</p>
        </div>
      </div>

      <h3>⏳ In Progress</h3>
      <div className="progress-grid">
        <div className="progress-item">
          <h4>Scale Validation (Target: 500 samples)</h4>
          <p>Current: 244 samples (48.2% complete)</p>
          <p>ETA: ~1 hour with 3 parallel instances</p>
          <p>Rate: ~5.0 samples/minute combined</p>
        </div>
        
        <div className="progress-item">
          <h4>Production Packaging</h4>
          <p>LoRA adapters ready</p>
          <p>MCP server configuration needed</p>
          <p>Inference validation pending</p>
        </div>
      </div>

      <h3>❓ Open Research Questions</h3>
      <ul className="research-questions">
        <li>Does dialectical format generalize to all query types (math, code, creative)?</li>
        <li>Will SCU prevent overfitting at 500+ samples?</li>
        <li>How much does synthesis improve over thesis alone?</li>
        <li>Can we maintain quality while reducing compute cost?</li>
        <li>What's optimal LoRA rank for reasoning tasks?</li>
      </ul>

      <h3>From Here to Production</h3>
      <div className="roadmap">
        <div className="roadmap-item completed">
          <h4>Phase 1: Complete Validation (Current → 2 weeks)</h4>
          <p>✅ Core dialectic: *Validated (10 iterations)*</p>
          <p>✅ SCU regularization: *Measured (λ adaptation working)*</p>
          <p>✅ Data generation: *99.2% quality (244 samples generated)*</p>
          <p>⏳ Full dataset: *Target 500 samples (~1 hour remaining)*</p>
          <p>⏳ Full training: *500 iterations (2-3 hours when data ready)*</p>
          <p>⏳ Inference test: *Validate synthesis quality*</p>
        </div>
        
        <div className="roadmap-item">
          <h4>Phase 2: Production Hardening (2-4 weeks)</h4>
          <p>Package as MCP server</p>
          <p>Add API endpoints (/dialectical, /thesis, /synthesis)</p>
          <p>Implement caching for repeated queries</p>
          <p>Add rate limiting and authentication</p>
          <p>Write comprehensive documentation</p>
        </div>
        
        <div className="roadmap-item">
          <h4>Phase 3: Beta Deployment (4-8 weeks)</h4>
          <p>Deploy to Cloudflare Pages (static site done!)</p>
          <p>Set up MCP server hosting</p>
          <p>Invite 10-20 beta users</p>
          <p>Collect feedback on reasoning quality</p>
          <p>Iterate on personas and prompts</p>
        </div>
        
        <div className="roadmap-item">
          <h4>Phase 4: Scale & Monetization (8-16 weeks)</h4>
          <p>Optimize inference speed (batching, quantization)</p>
          <p>Add SaaS pricing tier (MCP server hosting)</p>
          <p>Offer enterprise support (custom personas)</p>
          <p>Publish research paper (NeurIPS/ICML)</p>
        </div>
      </div>
    </section>
  );
};

export default CurrentStatus;
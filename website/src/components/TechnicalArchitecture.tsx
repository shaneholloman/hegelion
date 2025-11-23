const TechnicalArchitecture = () => {
  return (
    <section id="technical-architecture">
      <h2>Technical Architecture</h2>
      
      <h3>Core Dialectic Engine</h3>
      
      <pre><code>{`# Hegelion runs a structured debate

class DialecticalReasoner:
    def __init__(self, model, personas=["logician", "empiricist", "ethicist"]):
        self.model = model
        self.personas = personas
    
    def run_dialectic(self, query):
        # Phase 1: Thesis generation
        thesis = self.model.generate_thesis(query)
        
        # Phase 2: Council critique (multi-persona antithesis)
        contradictions = []
        for persona in self.personas:
            critique = self.model.critique_thesis(thesis, persona)
            contradictions.extend(critique.contradictions)
        
        antithesis = self.synthesize_critiques(contradictions)
        
        # Phase 3: Synthesize via PID control
        synthesis = self.model.synthesize(thesis, antithesis)
        
        return HegelionResult(
            thesis=thesis,
            antithesis=antithesis,
            synthesis=synthesis,
            contradictions=contradictions
        )`}</code></pre>
      
      <h3>Shannon Control Unit (SCU)</h3>
      
      <p>Adaptive regularization that balances model complexity vs. data fit:</p>
      
      <pre><code>{`Loss = CrossEntropy + λ × L2(LoRA parameters)

Where λ adapts via PID control:
    λ ← λ × exp(Kp × error + Ki × ∫error dt)
    
error = (ParamBPT / (DataBPT + ParamBPT)) - target_S`}</code></pre>
      
      <p>SCU automatically increases regularization when model complexity grows too large relative to data complexity.</p>
      
      <h3>Training Pipeline</h3>
      
      <pre><code>{`UltraFeedback → Kimi (Dialectical Teacher) → JSONL
                                   ↓
SCU Format Conversion → mlx_scu_trainer → Adapters
                                   ↓
Production Model (DeepSeek 1.5B + LoRA)`}</code></pre>
    </section>
  )
}

export default TechnicalArchitecture


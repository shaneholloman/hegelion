const WhatHegelionDoes = () => {
  return (
    <section id="what-hegelion-does">
      <h2>What Hegelion Does</h2>
      
      <p>
        Instead of generating a single answer, Hegelion forces the model to think dialectically:
      </p>
      
      <ul style={{ marginTop: 'var(--spacing-md)' }}>
        <li><strong>Step 1: Thesis</strong> - Propose the strongest initial argument</li>
        <li><strong>Step 2: Antithesis</strong> - Attack the thesis, find flaws and contradictions</li>
        <li><strong>Step 3: Synthesis</strong> - Resolve the conflict, create stronger answer</li>
      </ul>
      
      <p style={{ marginTop: 'var(--spacing-md)' }}>
        This adversarial process produces more robust, nuanced reasoning than single-pass generation.
      </p>
      
      <h3>Interactive Demo</h3>
      
      <p>Try Hegelion reasoning on any question:</p>
      
      <pre><code>{`# Run Hegelion CLI
hegelion-cli "Should we implement universal basic income?"

# Output follows strict dialectical format
<thought>
**THESIS**: Implement UBI to eliminate poverty...

**ANTITHESIS**: UBI disincentivizes work, causes inflation...

**SYNTHESIS**: Conditional cash transfers + job guarantees...
</thought>

[Final answer incorporating synthesis]`}</code></pre>
    </section>
  )
}

export default WhatHegelionDoes


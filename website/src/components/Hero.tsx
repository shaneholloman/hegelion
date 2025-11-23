const Hero = () => {
  return (
    <section className="hero" style={{ paddingTop: '6rem', paddingBottom: '4rem', textAlign: 'center' }}>
      <blockquote style={{ 
        fontSize: 'var(--text-xl)', 
        marginBottom: 'var(--spacing-md)',
        fontStyle: 'italic',
        color: 'var(--text-secondary)'
      }}>
        "The truth is the whole. The whole, however, is merely the essential nature reaching its completeness through the process of its own development."
        <br />
        <span style={{ fontSize: 'var(--text-base)', marginTop: 'var(--spacing-xs)', display: 'block' }}>
          — <strong>G.W.F. Hegel</strong>
        </span>
      </blockquote>
      
      <h1>Hegelion</h1>
      <h2 style={{ fontSize: 'var(--text-2xl)', fontWeight: 400, color: 'var(--text-secondary)', marginTop: 'var(--spacing-sm)' }}>
        Dialectical Reasoning Engine
      </h2>
      
      <p style={{ 
        fontSize: 'var(--text-lg)', 
        marginTop: 'var(--spacing-md)',
        maxWidth: '800px',
        marginLeft: 'auto',
        marginRight: 'auto'
      }}>
        Adversarial Reasoning Engine for Language Models
        <br />
        Adversarial thinking that forces thesis → antithesis → synthesis before acting
      </p>
    </section>
  )
}

export default Hero


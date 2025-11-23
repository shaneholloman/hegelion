const Footer = () => {
  return (
    <footer style={{ 
      backgroundColor: 'var(--bg-secondary)', 
      padding: 'var(--spacing-lg) var(--spacing-md)',
      marginTop: 'var(--spacing-xl)',
      borderTop: '1px solid var(--border)'
    }}>
      <div className="container" style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: 'var(--spacing-lg)',
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <div>
          <h4 style={{ marginBottom: 'var(--spacing-sm)' }}>Hegelion</h4>
          <p style={{ fontSize: 'var(--text-sm)', color: 'var(--text-tertiary)' }}>
            Dialectical Reasoning Engine
          </p>
        </div>
        
        <div>
          <h4 style={{ marginBottom: 'var(--spacing-sm)' }}>Technology</h4>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            <li style={{ marginBottom: 'var(--spacing-xs)' }}>
              <a href="https://github.com/yourusername/hegelion" target="_blank" rel="noopener noreferrer">
                GitHub Repository
              </a>
            </li>
            <li style={{ marginBottom: 'var(--spacing-xs)' }}>
              <a href="#technical-specs">Technical Details</a>
            </li>
            <li style={{ marginBottom: 'var(--spacing-xs)' }}>
              <a href="#quick-start">Documentation</a>
            </li>
          </ul>
        </div>
        
        <div>
          <h4 style={{ marginBottom: 'var(--spacing-sm)' }}>Connect</h4>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            <li style={{ marginBottom: 'var(--spacing-xs)' }}>
              <a href="https://twitter.com/shannonlabs" target="_blank" rel="noopener noreferrer">
                X (Twitter)
              </a>
            </li>
            <li style={{ marginBottom: 'var(--spacing-xs)' }}>
              <a href="mailto:contact@shannonlabs.dev">Email</a>
            </li>
            <li style={{ marginBottom: 'var(--spacing-xs)' }}>
              <a href="https://shannonlabs.dev" target="_blank" rel="noopener noreferrer">
                Shannon Labs
              </a>
            </li>
          </ul>
        </div>
      </div>
      
      <div style={{ 
        marginTop: 'var(--spacing-lg)', 
        paddingTop: 'var(--spacing-md)',
        borderTop: '1px solid var(--border)',
        textAlign: 'center',
        fontSize: 'var(--text-sm)',
        color: 'var(--text-tertiary)'
      }}>
        © 2025 Shannon Labs, Inc. • MIT License
      </div>
    </footer>
  )
}

export default Footer


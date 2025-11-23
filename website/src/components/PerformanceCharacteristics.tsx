const PerformanceCharacteristics = () => {
  return (
    <section id="performance-characteristics">
      <h2>Performance Characteristics</h2>
      
      <h3>Data Efficiency</h3>
      
      <table>
        <thead>
          <tr>
            <th>Samples</th>
            <th>Training Time (M2)</th>
            <th>Loss Reduction</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>50</td>
            <td>15 min</td>
            <td>3.2 → 2.8</td>
          </tr>
          <tr>
            <td>500</td>
            <td>2.5 hours</td>
            <td>3.2 → 2.1</td>
          </tr>
          <tr>
            <td>5000</td>
            <td>25 hours</td>
            <td>3.2 → 1.8</td>
          </tr>
        </tbody>
      </table>
      
      <p style={{ fontStyle: 'italic', marginTop: 'var(--spacing-sm)' }}>
        SCU regularization enables training on smaller datasets without overfitting
      </p>
      
      <h3>Model Sizes Tested</h3>
      
      <table>
        <thead>
          <tr>
            <th>Model</th>
            <th>Trainable Parameters</th>
            <th>Memory (batch=4)</th>
            <th>Speed</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>1.5B</td>
            <td>18M (LoRA r=16)</td>
            <td>6-8 GB</td>
            <td>Fast</td>
          </tr>
          <tr>
            <td>3B</td>
            <td>36M (LoRA r=32)</td>
            <td>12-16 GB</td>
            <td>Medium</td>
          </tr>
          <tr>
            <td>7B</td>
            <td>72M (LoRA r=64)</td>
            <td>24-32 GB</td>
            <td>Slow</td>
          </tr>
        </tbody>
      </table>
      
      <p style={{ fontStyle: 'italic', marginTop: 'var(--spacing-sm)' }}>
        1.5B offers best speed/quality tradeoff for prototyping
      </p>
    </section>
  )
}

export default PerformanceCharacteristics


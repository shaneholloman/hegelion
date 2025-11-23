# Hegelion

> *“The truth is the whole. The whole, however, is merely the essential nature reaching its completeness through the process of its own development.”*  
> — **G.W.F. Hegel**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/hegelion.svg)](https://badge.fury.io/py/hegelion)
[![Status](https://img.shields.io/badge/status-actively--maintained-brightgreen.svg)](https://github.com/Hmbown/Hegelion)

## Model-Agnostic Hegelion: Works with Any LLM

This version of Hegelion works with **whatever LLM is currently calling the MCP server** instead of making its own API calls. Perfect for:

- **Cursor**
- **Claude Desktop**
- **VS Code**
- **Antigravity** or other MCP-compatible environments

## Pick Your MCP Server (start here)

- **Prompt-only (default):** `hegelion-server` returns structured prompts and never makes API calls. Works out of the box in IDEs; zero API keys. Add it to MCP config and your editor/agent can run every step locally.
- **Backend (optional):** `hegelion-server` runs the dialectic itself with your provider keys (set in `.env`). Use when you want to offload reasoning to a specific model or automate without the editor in the loop.

Minimal MCP config for the prompt server:
```json
{
  "mcpServers": {
    "hegelion": {
      "command": "hegelion-server",
      "args": []
    }
  }
}
```

## 🎯 **The Problem This Solves**

Instead of configuring API keys and making external calls, users can:

1. Use Hegelion with their existing LLM setup
2. Experience dialectical reasoning with any model
3. No additional configuration or costs
4. Works instantly in any MCP environment

## 🛠️ **How It Works**

The `hegelion-server` returns **structured prompts** instead of making API calls:

### Single-Shot Dialectic (Powerful Models)
```python
# For models that can handle complex reasoning
prompt = await dialectical_single_shot(
    query="Can AI be genuinely creative?",
    use_search=True,
    use_council=True
)
# Returns one comprehensive prompt that guides the LLM through:
# THESIS → ANTITHESIS → SYNTHESIS
```

### Step-by-Step Workflow (Any Model)
```python
# For systematic execution
workflow = await dialectical_workflow(
    query="Should we implement universal basic income?", 
    use_council=True,
    use_judge=True,
    format="workflow"
)
# Returns structured steps that can be executed sequentially
```

### Manual Step Control
```python
# For maximum control
step1 = await thesis_prompt(query="Your question")
step2 = await antithesis_prompt(query="Your question", thesis="<result from step1>")  
step3 = await synthesis_prompt(query="Your question", thesis="<step1>", antithesis="<step2>")
```

## 📋 **Available Tools**

### `dialectical_workflow`
Returns a structured workflow for step-by-step execution:
- **Input**: query, options (search, council, judge)
- **Output**: JSON workflow with step-by-step prompts
- **Best for**: Systematic execution, complex queries

### `dialectical_single_shot`  
Returns one comprehensive prompt for powerful models:
- **Input**: query, options (search, council)
- **Output**: Single prompt with complete instructions
- **Best for**: Large context models capable of multi-step reasoning

### `thesis_prompt` / `antithesis_prompt` / `synthesis_prompt`
Individual step prompts for manual control:
- **Best for**: Custom workflows, experimentation

## 🎭 **Feature Support**

All Phase 2 features work in prompt-driven mode:

- **🔍 Search Grounding**: Prompts include instructions to use available search tools
- **👥 Council Critiques**: Generates Logician + Empiricist + Ethicist perspectives
- **⚖️ Quality Evaluation**: Includes structured evaluation prompts
- **📊 Structured Output**: Guides LLM to return properly formatted results

## 🔧 **Setup**

### Automated Setup (Recommended)

Run:
```bash
hegelion-setup-mcp
```
Copy the output to your `claude_desktop_config.json` or Cursor MCP settings.

### Manual Setup

If you prefer to configure it manually:

#### Claude Desktop
```json
{
  "mcpServers": {
    "hegelion": {
      "command": "hegelion-server",
      "args": []
    }
  }
}
```

#### Cursor/VS Code
1. Install Hegelion MCP extension (or configure via command)
2. Configure to use `hegelion-server`
3. Works with any model you have configured

## 💡 **Usage Examples**

### Example Output: "Untapped Resource for Technological Advancement"

> **Query:** "What is a potential untapped resource for technological advancement?"

<details open>
<summary><b>🔍 Phase 1: The Thesis</b></summary>

**Proposal:** *Industrial Waste Heat for Compute*  
Use waste heat from factories to power "thermo-computational" networks, turning entropy into zero-cost energy.
</details>

<details open>
<summary><b>⚔️ Phase 2: The Antithesis (Council of Critics)</b></summary>

- **The Logician**: *Thermodynamic Limit Conflict.* Carnot efficiency limits make converting low-grade heat to electricity fundamentally unviable.
- **The Empiricist**: *Spatial Mismatch.* Factories are hot/dirty environments; data centers require cool/clean ones. The engineering overhead outweighs the gain.
- **The Ethicist**: *Perverse Incentives.* Monetizing waste encourages industries to *remain* inefficient to sell their "fuel."
</details>

<details open>
<summary><b>✨ Phase 3: The Synthesis</b></summary>

**Resolution:** *Latent Heat Storage as a Service*  
The breakthrough isn't **converting** heat (inefficient), but leveraging the **demand** for heat. 

Instead of making electricity from heat, we place compute nodes inside water heaters and district heating systems. The "waste" heat from the computer becomes the useful product (hot water), achieving 100% system efficiency and resolving the "Perverse Incentive" by replacing fossil fuel heating with compute-generated heat.

*   **Research Proposal**: Micro-Fluidic Compute Heaters
*   **Prediction**: Decentralized compute heaters can reduce household energy consumption by 15%.
</details>

---

### 📊 Comparison: Standard LLM vs. Hegelion

When asking the same question ("What is a potential untapped resource for technological advancement?"), the difference in approach is striking:

| Feature | Standard LLM Call | Hegelion Dialectic |
| :--- | :--- | :--- |
| **The Output** | **Biological Compute (Organoid Intelligence)** | **Latent Heat Storage as a Service** |
| **The Process** | **Linear Retrieval**: Identifies a trending technology (Organoids) and summarizes known research (energy efficiency, learning speed). | **Adversarial Evolution**: Starts with a thesis (Waste Heat), destroys it with logic/ethics (Thermodynamics/Perverse Incentives), and builds a *new* solution from the wreckage. |
| **The Value** | Provides an **informative summary** of what others are doing. | Generates a **novel structural insight** by resolving a contradiction. |
| **The Vibe** | *"Here is a textbook definition."* | *"Here is a breakthrough argument."* |

---

### 🧠 Why This Happens: The Structural Bias

Why does Hegelion produce radically different answers?

Standard LLMs optimize for **probability and helpfulness**, usually retrieving the most popular or exciting "correct" answer found in their training data (like Organoid Intelligence).

Hegelion optimizes for **conflict and negation**.
1.  **The Structure Forces Conflict**: The prompt explicitly demands an *Antithesis* phase where the model MUST attack its own initial idea.
2.  **Safety in Physics**: To survive the "Council of Critics" (Logician, Empiricist), the model subconsciously gravitates towards topics with "hard walls" (like Thermodynamics or Economics) rather than speculative ones.
3.  **Creativity via Destruction**: By forcing the model to destroy its first idea ("convert heat to electricity"), it is forced to invent a third way ("use heat as a service") that satisfies the constraints.

**The format forces the content.** You don't get a summary; you get an evolution.

---

### Quick Dialectical Analysis
1. Call `dialectical_single_shot` tool
2. Paste the returned prompt into your LLM
3. Get complete thesis → antithesis → synthesis

### Structured Workflow
1. Call `dialectical_workflow` tool
2. Execute each step from the JSON workflow
3. Use outputs from previous steps as inputs to next steps

### Council-Enhanced Analysis
1. Use `use_council=true` in any tool
2. Get multi-perspective critiques (Logic, Empirical, Ethical)
3. Comprehensive analysis from multiple expert viewpoints

## 🚀 **Benefits**

- **Zero Configuration**: No API keys or backend setup needed
- **Model Flexibility**: Works with any modern LLM capable of instruction following
- **Cost Efficiency**: Uses your existing LLM setup, no additional charges  
- **Instant Access**: Experience dialectical reasoning immediately
- **Full Feature Set**: All Phase 2 capabilities (search, council, judge) available

This approach makes Hegelion truly accessible to any user with any LLM setup!

---

## 🔬 Next Steps & Research

### Model Training Pipeline

We are actively training the **DeepSeek-R1-Distill-Qwen-1.5B** model using Hegelion's dialectical reasoning framework. The training pipeline incorporates:

- **Shannon Control Unit (SCU)**: An adaptive regularization technique that automatically balances model complexity vs. data fit using PID control. SCU dynamically adjusts regularization strength (`λ`) based on the ratio of parameter complexity (ParamBPT) to data complexity (DataBPT), preventing overfitting while maintaining model expressiveness.

- **MLX Optimization**: Training is optimized for Apple Silicon (M1/M2/M3/M4) using MLX, enabling efficient fine-tuning on consumer hardware.

For technical details, see [`README_TRAINING.md`](README_TRAINING.md) and [`docs/TRAINING_PROTOCOL.md`](docs/TRAINING_PROTOCOL.md).

### Hegelian Dialectic Training Dataset

A core research direction is creating training datasets that embed the dialectical reasoning process directly into the model's thinking patterns. Each training example forces the model through the **Thesis → Antithesis → Synthesis** cycle:

**Training Format:**
```
<thought>
THESIS: [Initial proposal or answer]
ANTITHESIS: [Adversarial critique, contradictions, edge cases]
SYNTHESIS: [Resolved answer that incorporates valid points from both]
</thought>
[Final answer]
```

**Hypothesis**: This structured thinking process reduces hallucinations by:

1. **Forcing Adversarial Self-Critique**: The Antithesis phase explicitly attacks the initial thesis, identifying hallucinations, unverifiable claims, and risky assumptions before they propagate to the final answer.

2. **Requiring Evidence-Based Synthesis**: The Synthesis phase must resolve contradictions, forcing the model to ground its reasoning in verifiable information rather than confident speculation.

3. **Internalizing Critical Thinking**: By training on this pattern, models may internalize the habit of challenging their own assumptions before answering, leading to more reliable outputs.

**Research Goals:**

- Measure hallucination reduction in models trained with dialectical data vs. standard instruction tuning
- Evaluate whether the T→A→S structure becomes an internalized reasoning pattern
- Compare reasoning quality and fact-checking capabilities across different training approaches

The data generation pipeline uses [`hegelion.training.generator`](hegelion/training/generator.py) to create dialectical training examples, and the SCU training implementation is available in [`hegelion.training.mlx_scu_trainer`](hegelion/training/mlx_scu_trainer.py).

---

## Documentation

-   [Quick Start (docs/QUICKSTART.md)](docs/QUICKSTART.md)
-   [User Guide (docs/USER_GUIDE.md)](docs/USER_GUIDE.md)
-   [Model-Agnostic Prompt Server (docs/MODEL_AGNOSTIC.md)](docs/MODEL_AGNOSTIC.md)
-   [MCP Reference (docs/MCP.md)](docs/MCP.md)
-   [Contributing (CONTRIBUTING.md)](CONTRIBUTING.md)

## License

Hegelion is licensed under the [MIT License](LICENSE).

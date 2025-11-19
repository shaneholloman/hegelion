# Model-Agnostic Hegelion: Works with Any LLM

This version of Hegelion works with **whatever LLM is currently calling the MCP server** instead of making its own API calls. Perfect for:

- **Cursor** with Gemini 3, Claude 3.5, or any model
- **Claude Desktop** using its native model
- **VS Code** with any configured LLM
- **Antigravity** or other MCP-compatible environments

## 🎯 **The Problem This Solves**

Instead of configuring API keys and making external calls, users can:
1. Use Hegelion with their existing LLM setup
2. Experience dialectical reasoning with Gemini 3, Claude 3.5, etc.
3. No additional configuration or costs
4. Works instantly in any MCP environment

## 🛠️ **How It Works**

The `hegelion-prompt-server` returns **structured prompts** instead of making API calls:

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
- **Best for**: Gemini 3, Claude 3.5, GPT-4+ models

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

### Claude Desktop
```json
{
  "mcpServers": {
    "hegelion-prompt": {
      "command": "hegelion-prompt-server",
      "args": []
    }
  }
}
```

### Cursor/VS Code
1. Install Hegelion MCP extension (or configure via command)
2. Configure to use `hegelion-prompt-server`
3. Works with any model you have configured

## 💡 **Usage Examples**

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
- **Model Flexibility**: Works with Gemini 3, Claude 3.5, GPT-4+, local models
- **Cost Efficiency**: Uses your existing LLM setup, no additional charges  
- **Instant Access**: Experience dialectical reasoning immediately
- **Full Feature Set**: All Phase 2 capabilities (search, council, judge) available

This approach makes Hegelion truly accessible to any user with any LLM setup!

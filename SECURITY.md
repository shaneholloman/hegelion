# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.3.x   | :white_check_mark: |
| < 0.3.0 | :x:                |

## Reporting a Vulnerability

To report a security vulnerability, please **do not open a public issue**.

Instead, please email `hunter@shannonlabs.dev` with the subject line "Hegelion Security Vulnerability". We will respond within 48 hours.

### Key Considerations

- **API Keys**: Hegelion handles API keys for various LLM providers. Ensure you are using the recommended environment variable configuration or secure MCP configuration. Never commit `.env` files.
- **Prompt Injection**: As a framework for LLMs, Hegelion is subject to the inherent risks of prompt injection. While the framework encourages structured reasoning, it does not inherently sanitize all inputs against adversarial attacks on the underlying model.


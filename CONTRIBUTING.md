# Contributing to Hegelion

Thank you for your interest in contributing to Hegelion! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.10+ (regularly tested on 3.10 and 3.11)
- `uv` recommended for dependency management (fallback: standard `pip`)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Hmbown/Hegelion.git
   cd Hegelion
   ```

2. **Install dependencies (prefer `uv`)**
   ```bash
   uv sync --dev              # creates .venv and installs runtime + dev deps
   ```

   Alternative with pip:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

### Running Tests

```bash
# Run all tests
uv run pytest -v

# Run with coverage
uv run pytest --cov=hegelion --cov-report=html

# Run specific test file
uv run pytest tests/test_core.py -v
```

### Code Quality

```bash
# Format code
uv run black hegelion tests

# Lint code
uv run ruff check hegelion tests

# Run both
uv run black hegelion tests && uv run ruff check hegelion tests
```

### Pre-commit Hooks

Install pre-commit hooks to automatically format and lint code before commits:

```bash
uv run pre-commit install
```

### CLI Smoke Tests

Verify CLI tools work correctly:

```bash
uv run hegelion --help
uv run hegelion-bench --help
uv run hegelion-server --help
```

## Making Changes

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes**
   - Write clear, focused commits
   - Add tests for new functionality
   - Update documentation as needed

3. **Ensure tests pass**
   ```bash
   uv run pytest -v
   ```

4. **Ensure code quality**
   ```bash
   uv run black hegelion tests
   uv run ruff check hegelion tests
   ```

## Submitting Changes

1. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request**
   - Open a PR on GitHub
   - Provide a clear description of changes
   - Reference any related issues
   - Ensure CI checks pass

3. **Review Process**
   - Maintainers will review your PR
   - Address any feedback or requested changes
   - Once approved, your PR will be merged

## Code Style

- Follow PEP 8 style guidelines
- Use `black` for code formatting (line length: 88)
- Use `ruff` for linting
- Write docstrings for public functions and classes
- Type hints are encouraged but not required

## Testing Guidelines

- Write tests for new features
- Ensure existing tests continue to pass
- Aim for clear, readable test code
- Use descriptive test names

## Reporting Issues

- Use GitHub Issues to report bugs or request features
- Provide clear descriptions and reproduction steps
- Include relevant environment information (Python version, OS, etc.)
- For bugs, include error messages and stack traces

## Questions?

Feel free to open an issue with questions or reach out to the maintainers.

Thank you for contributing to Hegelion!


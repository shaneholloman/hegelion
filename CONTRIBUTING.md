# Contributing to Hegelion

Thank you for your interest in contributing to Hegelion! We welcome contributions from everyone. This document provides guidelines to ensure that contributing to Hegelion is a smooth and collaborative process.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Project Philosophy](#project-philosophy)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running Tests](#running-tests)
- [Development Workflow](#development-workflow)
  - [Branching](#branching)
  - [Making Changes](#making-changes)
  - [Code Quality](#code-quality)
  - [Submitting a Pull Request](#submitting-a-pull-request)
- [Architectural Overview](#architectural-overview)
- [Coding Guidelines](#coding-guidelines)
- [Reporting Issues](#reporting-issues)

---

## Code of Conduct

All contributors are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please take a moment to read it to understand our commitment to fostering an open and welcoming environment.

---

## Project Philosophy

Hegelion is a research tool designed for robustness, clarity, and extensibility. Our goal is to provide a stable platform for evaluating and improving AI reasoning.

-   **Clarity over cleverness:** Write code that is easy to understand and maintain.
-   **Robustness is key:** The tool should handle real-world model outputs and fail gracefully.
-   **Extensibility by design:** The architecture should make it easy to add new backends, features, and evaluation metrics.
-   **Documentation is paramount:** Changes should be reflected in the `README.md` and `HEGELION_SPEC.md`.

---

## Getting Started

### Prerequisites

-   Python 3.10+
-   `uv` is recommended for dependency management, but `pip` is also supported.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Hmbown/Hegelion.git
    cd Hegelion
    ```

2.  **Install dependencies:**
    ```bash
    # Using uv (recommended)
    uv sync --dev

    # Using pip
    pip install -e ".[dev]"
    ```

3.  **Set up environment variables:**
    ```bash
    cp .env.example .env
    # Edit .env with your API keys for testing
    ```

### Running Tests

Ensure your environment is set up correctly by running the test suite.

```bash
# Run all tests
uv run pytest -v

# Run tests with coverage report
uv run pytest --cov=hegelion --cov-report=html
```

---

## Development Workflow

### Branching

Create a descriptive branch name based on the type of change:

-   **Features:** `feature/your-feature-name`
-   **Bug Fixes:** `fix/your-bug-fix`
-   **Documentation:** `docs/your-doc-update`
-   **Refactoring:** `refactor/your-refactor-description`

### Making Changes

-   Write clear, atomic commits.
-   Ensure new features are covered by tests.
-   Update the `README.md`, `HEGELION_SPEC.md`, and any other relevant documentation if you are changing user-facing behavior.

### Code Quality

Before committing, ensure your code is formatted and linted correctly. We use `black` for formatting and `ruff` for linting.

```bash
# Format and lint your code
uv run black hegelion tests
uv run ruff check hegelion tests
```

We highly recommend installing the pre-commit hooks to automate this process:

```bash
uv run pre-commit install
```

### Submitting a Pull Request

1.  Push your branch to your fork on GitHub.
2.  Open a pull request against the `main` branch of the Hegelion repository.
3.  Provide a clear title and a detailed description of your changes.
4.  Link to any relevant issues.
5.  Ensure all CI checks pass.

---

## Architectural Overview

Hegelion's codebase is organized into several key modules:

-   `hegelion/core.py`: The main public API (`run_dialectic`, `run_benchmark`).
-   `hegelion/engine.py`: The core logic for the Thesis → Antithesis → Synthesis loop.
-   `hegelion/backends.py`: Abstractions for interacting with different LLM providers.
-   `hegelion/prompts.py`: The prompt templates for each phase of the dialectic.
-   `hegelion/models.py`: Pydantic models for data structures like `HegelionResult`.
-   `hegelion/parsing.py`: Functions for extracting structured data (contradictions, research proposals) from model outputs.
-   `hegelion/scripts/hegelion_cli.py`: The implementation of the `hegelion` and `hegelion-bench` command-line tools.

---

## Coding Guidelines

-   **Style:** Follow PEP 8. Our line length is 88 characters, enforced by `black`.
-   **Typing:** Use type hints for all function signatures.
-   **Docstrings:** Write Google-style docstrings for all public modules, classes, and functions.
-   **Tests:** Use `pytest` for testing. Test files should be placed in the `tests/` directory and mirror the structure of the `hegelion/` directory.

---

## Reporting Issues

If you encounter a bug or have a feature request, please open an issue on GitHub. Provide as much detail as possible, including:

-   A clear and descriptive title.
-   Steps to reproduce the issue.
-   Your operating system and Python version.
-   Any relevant error messages or stack traces.

Thank you for helping us improve Hegelion!
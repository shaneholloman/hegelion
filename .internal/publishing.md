# Publishing Guide

This guide documents the release process for Hegelion.

## Prerequisites

- `uv` installed
- PyPI account with API token

## Automated Release (Recommended)

1. **Bump version** in `hegelion/__init__.py` and `pyproject.toml`.
2. **Update CHANGELOG.md**.
3. **Run the publish script:**

   ```bash
   # Export your PyPI token
   export PYPI_TOKEN=pypi-...
   
   # Run the script
   ./scripts/publish_pypi.sh
   ```

## Manual Release

If you prefer to run the steps manually or need to debug:

1. **Clean previous builds:**
   ```bash
   rm -rf dist/ build/ *.egg-info/
   ```

2. **Build the package:**
   ```bash
   uv run python -m build
   ```

3. **Verify the package (optional but recommended):**
   ```bash
   uv run twine check dist/*
   ```

4. **Upload to PyPI:**
   ```bash
   uv run twine upload dist/* --username __token__ --password <your-pypi-token>
   ```

## Release Checklist

- [ ] Run full test suite: `uv run pytest`
- [ ] Verify version numbers match in `pyproject.toml` and `__init__.py`
- [ ] Update `CHANGELOG.md`
- [ ] Commit all changes
- [ ] Tag the release in git: `git tag v0.3.0 && git push origin v0.3.0`

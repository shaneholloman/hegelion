# Publishing Guide

## Quick PyPI Publish

1. **Get PyPI API Token**
   - Go to [PyPI API Tokens](https://pypi.org/manage/account/token/)
   - Create new token for this project
   - Copy the token (starts with `pypi-`)

2. **Publish with script**
   ```bash
   PYPI_TOKEN=<your-token> ./scripts/publish_pypi.sh
   ```

## Manual Publishing (if script fails)

1. **Clean and build**
   ```bash
   rm -rf dist/ build/ *.egg-info/
   uv run python -m build
   ```

2. **Check packages**
   ```bash
   uv run twine check dist/*
   ```

3. **Upload to PyPI**
   ```bash
   uv run twine upload dist/* --username __token__ --password <PYPI_TOKEN>
   ```

## Pre-release Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md`
- [ ] Run tests: `uv run pytest`
- [ ] Build packages: `uv run python -m build`
- [ ] Check packages: `uv run twine check dist/*`
- [ ] Commit and tag release
- [ ] Publish to PyPI
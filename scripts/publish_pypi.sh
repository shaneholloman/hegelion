#!/bin/bash
# Publish hegelion to PyPI
# Usage: PYPI_TOKEN=<token> ./scripts/publish_pypi.sh
#
# To create a PyPI API token:
# 1. Go to https://pypi.org/manage/account/token/
# 2. Create a new token with scope for this project
# 3. Copy the token (including the "pypi-" prefix)
# 4. Use: PYPI_TOKEN=<token> ./scripts/publish_pypi.sh

set -e

if [ -z "$PYPI_TOKEN" ]; then
    echo "Error: PYPI_TOKEN environment variable is required"
    echo "Create a token at: https://pypi.org/manage/account/token/"
    echo "Usage: PYPI_TOKEN=<token> ./scripts/publish_pypi.sh"
    exit 1
fi

echo "Building distribution..."
# Clean old builds first
rm -rf dist/ build/ *.egg-info/
uv run python -m build

echo "Publishing to PyPI..."
uv run twine upload dist/* --username __token__ --password "${PYPI_TOKEN}"

echo ""
echo "✅ Published to PyPI!"
echo ""
echo "To install:"
echo "  pip install hegelion"
echo ""
echo "To install latest version:"
echo "  pip install --upgrade hegelion"
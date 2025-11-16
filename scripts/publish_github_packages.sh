#!/bin/bash
# Publish hegelion to GitHub Packages
# Usage: GITHUB_TOKEN=<token> ./scripts/publish_github_packages.sh
#
# To create a GitHub token:
# 1. Go to https://github.com/settings/tokens
# 2. Generate new token (classic)
# 3. Select scope: write:packages
# 4. Copy the token and use: GITHUB_TOKEN=<token> ./scripts/publish_github_packages.sh

set -e

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable is required"
    echo "Create a token at: https://github.com/settings/tokens"
    echo "Required scope: write:packages"
    exit 1
fi

echo "Building distribution..."
uv run python -m build

echo "Publishing to GitHub Packages..."
# GitHub Packages uses PyPI-compatible API
# Repository URL format: https://upload.pypi.org/legacy/ (same as PyPI)
# But we authenticate with GitHub username and token
uv run twine upload \
  --repository-url https://upload.pypi.org/legacy/ \
  --username Hmbown \
  --password "${GITHUB_TOKEN}" \
  dist/*

echo ""
echo "✅ Published to GitHub Packages!"
echo ""
echo "To install from GitHub Packages:"
echo "  export GITHUB_TOKEN=<your-token>"
echo "  pip install hegelion \\"
echo "    --index-url https://\${GITHUB_TOKEN}@pypi.pkg.github.com/Hmbown/simple"
echo ""
echo "Or configure ~/.pip/pip.conf:"
echo "  [global]"
echo "  extra-index-url = https://<token>@pypi.pkg.github.com/Hmbown/simple"

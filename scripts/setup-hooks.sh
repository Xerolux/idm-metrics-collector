#!/bin/bash
# Setup script for git hooks
# Run this from the repository root to install pre-push hooks

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
HOOKS_DIR="$REPO_ROOT/.git/hooks"
SOURCE_HOOKS="$SCRIPT_DIR/hooks"

echo "Installing git hooks..."

# Install pre-push hook
if [ -f "$SOURCE_HOOKS/pre-push" ]; then
    cp "$SOURCE_HOOKS/pre-push" "$HOOKS_DIR/pre-push"
    chmod +x "$HOOKS_DIR/pre-push"
    echo "  - Installed pre-push hook"
fi

echo ""
echo "Git hooks installed successfully!"
echo ""
echo "The following checks will run before each push:"
echo "  - ruff check (linting)"
echo "  - ruff format --check (formatting)"
echo "  - pytest (tests)"
echo ""
echo "To skip hooks temporarily, use: git push --no-verify"

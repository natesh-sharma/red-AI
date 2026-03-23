#!/usr/bin/env bash
# Run the RED-AI test suite.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== RED-AI Test Suite ==="
echo ""

# Run unittest discovery
python3 -m unittest discover -s tests -v 2>&1 | grep -v '^\[1;'

echo ""
echo "=== Done ==="

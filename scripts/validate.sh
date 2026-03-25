#!/usr/bin/env bash
# Validate RED-AI project: syntax check all Python files, run tests, check schema.
set -euo pipefail

cd "$(dirname "$0")/.."
ERRORS=0

echo "=== RED-AI Validation ==="
echo ""

# 1. Python syntax check
echo "[1/4] Checking Python syntax..."
for f in red_ai/*.py tests/*.py; do
    if ! python3 -m py_compile "$f" 2>/dev/null; then
        echo "  FAIL: $f"
        ERRORS=$((ERRORS + 1))
    fi
done
[ $ERRORS -eq 0 ] && echo "  All files OK"

# 2. Import check
echo "[2/4] Checking imports..."
if python3 -c "from red_ai.cli import main; from red_ai.ai_engine import get_ai_response; from red_ai.local_commands import LOCAL_COMMANDS" 2>/dev/null; then
    echo "  All imports OK"
else
    echo "  FAIL: Import errors detected"
    ERRORS=$((ERRORS + 1))
fi

# 3. Run tests
echo "[3/4] Running tests..."
TEST_OUTPUT=$(python3 -m unittest discover -s tests 2>&1)
if echo "$TEST_OUTPUT" | grep -q "^OK"; then
    TOTAL=$(echo "$TEST_OUTPUT" | grep -m1 "^Ran [0-9]" | sed 's/^Ran \([0-9]*\).*/\1/')
    echo "  $TOTAL tests passed"
else
    echo "  FAIL: Tests failed"
    ERRORS=$((ERRORS + 1))
fi

# 4. Check for secrets
echo "[4/4] Scanning for hardcoded secrets..."
SECRETS=$(grep -rnE '(password|secret|api_key|token)\s*=' red_ai/*.py 2>/dev/null | grep -vE '(environ|getenv|args\.|#|None|""|'\'\'')' | head -5 || true)
if [ -n "$SECRETS" ]; then
    echo "  WARNING: Possible hardcoded secrets:"
    echo "$SECRETS" | sed 's/^/    /'
else
    echo "  No secrets detected"
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "=== Validation PASSED ==="
else
    echo "=== Validation FAILED ($ERRORS errors) ==="
    exit 1
fi

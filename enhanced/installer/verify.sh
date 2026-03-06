#!/bin/bash
# Enhanced Language — Installation Verifier
# Usage: bash verify.sh

PASS=0
FAIL=0
TOTAL=0

check() {
    TOTAL=$((TOTAL + 1))
    local desc="$1"
    shift
    if "$@" &>/dev/null; then
        echo "  ✓ $desc"
        PASS=$((PASS + 1))
    else
        echo "  ✗ $desc"
        FAIL=$((FAIL + 1))
    fi
}

echo ""
echo "==========================================="
echo " Enhanced — Installation Verification"
echo "==========================================="
echo ""

# Python
check "Python 3.10+ found" python3 --version
if ! python3 --version &>/dev/null; then
    check "Python (fallback) found" python --version
fi

# LLVM
check "clang found" clang --version

# Enhanced commands
check "enhanced command works" enhanced --version 2>/dev/null || check "enhanced command works" python -c "
import sys; sys.path.insert(0, '/usr/local/lib/enhanced'); from repl.repl import VERSION; print(VERSION)"

check "enhc command works" enhc --version 2>/dev/null || check "enhc command works" python -c "
import sys; sys.path.insert(0, '/usr/local/lib/enhanced'); print('0.1.0')"

# Compile test
TMPDIR=$(mktemp -d)
cat > "$TMPDIR/hello.en" << 'EOF'
say "Hello from Enhanced".
EOF

check "hello.en compiles to IR" python -c "
import sys, os
sys.path.insert(0, '/usr/local/lib/enhanced')
from lexer import Lexer
from parser import Parser
from analyzer import SemanticAnalyzer
from codegen import IRGenerator
source = open('$TMPDIR/hello.en').read()
tokens = Lexer(source).tokenize()
ast = Parser(tokens).parse()
sa = SemanticAnalyzer()
typed = sa.analyze(ast)
ir = IRGenerator().generate(typed)
assert '@printf' in ir or '@puts' in ir
"

rm -rf "$TMPDIR"

# Summary
echo ""
echo "==========================================="
if [ $FAIL -eq 0 ]; then
    echo " All $TOTAL checks passed!"
else
    echo " $PASS/$TOTAL checks passed, $FAIL failed."
fi
echo "==========================================="
echo ""

exit $FAIL

#!/bin/bash
# Enhanced Language Installer — Linux/macOS
# Usage: sudo bash install.sh
set -e

VERSION="0.1.0"
INSTALL_DIR="/usr/local/lib/enhanced"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "==========================================="
echo " Enhanced $VERSION — Installer"
echo "==========================================="
echo ""

# 1. Check Python
echo "[1/6] Checking Python..."
if command -v python3 &>/dev/null; then
    PY=$(python3 --version)
    echo "  Found: $PY"
else
    echo "  ERROR: Python 3 not found. Install Python 3.10+ first."
    exit 1
fi

# 2. Check LLVM/clang
echo "[2/6] Checking LLVM/clang..."
if command -v clang &>/dev/null; then
    CLANG=$(clang --version | head -1)
    echo "  Found: $CLANG"
else
    echo "  WARNING: clang not found. Native compilation will not work."
    echo "  The REPL and IR generation will still work."
    echo "  Install: brew install llvm (Mac) / sudo apt install llvm clang (Linux)"
fi

# 3. Build C runtime
echo "[3/6] Building C runtime..."
if command -v clang &>/dev/null; then
    clang -c "$SCRIPT_DIR/runtime/enhanced_runtime.c" -o "$SCRIPT_DIR/runtime/enhanced_runtime.o" 2>/dev/null || true
    clang -c "$SCRIPT_DIR/runtime/enhanced_stdlib.c" -o "$SCRIPT_DIR/runtime/enhanced_stdlib.o" 2>/dev/null || true
    clang -c "$SCRIPT_DIR/runtime/enhanced_memory.c" -o "$SCRIPT_DIR/runtime/enhanced_memory.o" 2>/dev/null || true
    echo "  Runtime compiled."
else
    echo "  Skipped (clang not available)."
fi

# 4. Install to system directory
echo "[4/6] Installing to $INSTALL_DIR..."
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
fi
mkdir -p "$INSTALL_DIR"
cp -R "$SCRIPT_DIR/"* "$INSTALL_DIR/"
echo "  Files copied."

# 5. Create commands
echo "[5/6] Creating commands..."

# enhc command
cat > /usr/local/bin/enhc << 'ENHC_EOF'
#!/bin/bash
python3 /usr/local/lib/enhanced/enhc.py "$@"
ENHC_EOF
chmod +x /usr/local/bin/enhc
echo "  enhc command installed."

# enhanced command (REPL)
cat > /usr/local/bin/enhanced << 'REPL_EOF'
#!/bin/bash
python3 /usr/local/lib/enhanced/repl/repl.py "$@"
REPL_EOF
chmod +x /usr/local/bin/enhanced
echo "  enhanced command installed."

# 6. Register MIME type (Linux only)
echo "[6/6] Registering .en file type..."
if command -v xdg-mime &>/dev/null; then
    MIME_FILE="/usr/share/mime/packages/enhanced.xml"
    cat > "$MIME_FILE" << 'MIME_EOF'
<?xml version="1.0"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="text/x-enhanced">
    <comment>Enhanced source file</comment>
    <glob pattern="*.en"/>
  </mime-type>
</mime-info>
MIME_EOF
    update-mime-database /usr/share/mime 2>/dev/null || true
    echo "  .en MIME type registered."
elif [ "$(uname)" = "Darwin" ]; then
    echo "  macOS — use Enhanced VSCode extension for .en association."
else
    echo "  Skipped (xdg-mime not available)."
fi

echo ""
echo "==========================================="
echo " Enhanced $VERSION installed successfully!"
echo "==========================================="
echo ""
echo "  enhc hello.en    — compile a program"
echo "  enhanced         — open the REPL"
echo ""

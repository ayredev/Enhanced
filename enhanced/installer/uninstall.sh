#!/bin/bash
# Enhanced Language — Uninstaller
# Usage: sudo bash uninstall.sh

set -e

INSTALL_DIR="/usr/local/lib/enhanced"
BIN_ENHC="/usr/local/bin/enhc"
BIN_REPL="/usr/local/bin/enhanced"

echo ""
echo "==========================================="
echo " Enhanced — Uninstaller"
echo "==========================================="
echo ""

# Remove installed files
if [ -d "$INSTALL_DIR" ]; then
    echo "[1/3] Removing $INSTALL_DIR..."
    rm -rf "$INSTALL_DIR"
    echo "  Done."
else
    echo "[1/3] $INSTALL_DIR not found — skipping."
fi

# Remove commands
if [ -f "$BIN_ENHC" ] || [ -L "$BIN_ENHC" ]; then
    echo "[2/3] Removing enhc command..."
    rm -f "$BIN_ENHC"
    echo "  Done."
else
    echo "[2/3] enhc command not found — skipping."
fi

if [ -f "$BIN_REPL" ] || [ -L "$BIN_REPL" ]; then
    echo "[3/3] Removing enhanced command..."
    rm -f "$BIN_REPL"
    echo "  Done."
else
    echo "[3/3] enhanced command not found — skipping."
fi

# Remove MIME type (Linux)
if command -v xdg-mime &>/dev/null; then
    xdg-mime uninstall /usr/share/mime/packages/enhanced.xml 2>/dev/null || true
fi

echo ""
echo "==========================================="
echo " Enhanced has been uninstalled."
echo "==========================================="
echo ""

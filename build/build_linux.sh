#!/bin/bash
# Script de build para Linux/WSL/Git Bash
set -e

PYTHON_BIN="python3"
if ! command -v python3 &> /dev/null; then
    if command -v python &> /dev/null; then
        PYTHON_BIN="python"
    else
        echo "Python não encontrado! Instale python3."
        exit 1
    fi
fi

REQ_FILE="$(dirname "$0")/../requirements.txt"

$PYTHON_BIN -m pip install --upgrade --user pip setuptools wheel
$PYTHON_BIN -m pip install --user -r "$REQ_FILE"

# Build com PyInstaller
$PYTHON_BIN -m pip install --user pyinstaller
$PYTHON_BIN -m PyInstaller build/build.spec

echo "Build finalizado! O executável está na pasta dist/."

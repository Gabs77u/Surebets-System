#!/bin/bash
# Script de build automatizado para Surebets System
set -e

# 1. Instala dependências
pip install -r requirements.txt

# 2. Gera o executável com PyInstaller
pyinstaller build.spec

# 3. Mensagem final
if [ -f dist/SurebetsSystem.exe ]; then
    echo "Build concluído com sucesso! O executável está em dist/SurebetsSystem.exe"
else
    echo "Erro no build. Verifique o log."
fi

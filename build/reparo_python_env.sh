#!/bin/bash
# Script de reparo automático do ambiente Python para Surebets System (Linux)
# Corrige problemas de setuptools, pip, wheel e dependências quebradas
set -e

# Detecta python3 ou python
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

# Atualiza pip, setuptools e wheel para o usuário
$PYTHON_BIN -m pip install --upgrade --user pip setuptools wheel

# Limpa o cache do pip
$PYTHON_BIN -m pip cache purge || true

# Instala numpy separadamente (resolve muitos problemas de build)
$PYTHON_BIN -m pip install --user numpy==1.26.4

# Instala as demais dependências normalmente
if ! $PYTHON_BIN -m pip install --user -r "$REQ_FILE"; then
    echo "\n[ERRO] Houve um problema ao instalar as dependências.\nSe aparecer mensagem de conflito de dependências, tente rodar:\n  $PYTHON_BIN -m pip install --user --force-reinstall -r \"$REQ_FILE\"\nOu remova manualmente os pacotes conflitantes com:\n  $PYTHON_BIN -m pip uninstall <pacote>\nDepois rode este script novamente.\n"
    exit 1
fi

echo "Ambiente Python reparado! Agora tente rodar o build normalmente."

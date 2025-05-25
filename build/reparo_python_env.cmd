@echo off
REM Script de reparo automático do ambiente Python para Surebets System (Windows)
REM Corrige problemas de setuptools, pip, wheel e dependências quebradas

REM Atualiza pip, setuptools e wheel para o usuário
python -m pip install --upgrade --user pip setuptools wheel

REM Limpa o cache do pip
python -m pip cache purge

REM Instala numpy separadamente (resolve muitos problemas de build)
pip install --user numpy==1.26.4

REM Instala as demais dependências normalmente
pip install --user -r ..\requirements.txt

echo Ambiente Python reparado! Agora tente rodar o build normalmente.
pause

@echo off
REM Script de build para Windows
setlocal

REM Detecta python3 ou python
where python3 >nul 2>nul
if %errorlevel%==0 (
    set PYTHON_BIN=python3
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set PYTHON_BIN=python
    ) else (
        echo Python não encontrado! Instale python3.
        exit /b 1
    )
)

set REQ_FILE=%~dp0..\requirements.txt

%PYTHON_BIN% -m pip install --upgrade --user pip setuptools wheel
%PYTHON_BIN% -m pip install --user -r "%REQ_FILE%"

REM Build com PyInstaller
%PYTHON_BIN% -m pip install --user pyinstaller
%PYTHON_BIN% -m PyInstaller build\build.spec

echo Build finalizado! O executável está na pasta dist\.
endlocal

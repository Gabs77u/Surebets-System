@echo off
REM Script de build automatizado para Windows
pip install -r requirements.txt
pyinstaller --distpath "%USERPROFILE%\Desktop" build.spec
IF EXIST "%USERPROFILE%\Desktop\SurebetsSystem.exe" (
    echo Build concluido com sucesso! O executavel esta na sua Area de Trabalho: %USERPROFILE%\Desktop\SurebetsSystem.exe
) ELSE (
    echo Erro no build. Verifique o log.
)

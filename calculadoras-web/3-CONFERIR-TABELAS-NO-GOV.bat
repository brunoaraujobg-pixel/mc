@echo off
REM Confere as tabelas da calculadora direto nos sites oficiais do governo.
REM Precisa ter Python instalado e internet funcionando.
chcp 65001 >nul
title Conferencia das tabelas oficiais
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 goto sem_python

python conferir-tabelas.py
echo.
echo ----------------------------------------------------------------
echo  Terminou. Leia o resumo acima antes de fechar esta janela.
echo ----------------------------------------------------------------
pause
goto fim

:sem_python
echo.
echo  ==============================================================
echo   O Python nao esta instalado neste computador.
echo  ==============================================================
echo.
echo   Para instalar:
echo     1. Acesse  https://www.python.org/downloads/
echo     2. Baixe a versao para Windows e execute o instalador.
echo     3. IMPORTANTE: na primeira tela, marque a caixinha
echo        "Add Python to PATH" antes de clicar em Install.
echo     4. Termine a instalacao, feche esta janela e rode
echo        este arquivo de novo.
echo.
echo   Sem o Python, a conferencia tem de ser feita na mao,
echo   seguindo a lista do README.md.
echo.
pause

:fim

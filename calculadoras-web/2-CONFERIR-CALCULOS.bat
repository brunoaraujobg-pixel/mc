@echo off
REM Abre a pagina interna que confere os calculos contra valores feitos na mao.
title Conferencia dos calculos
echo.
echo  Abrindo a pagina de conferencia dos calculos...
echo.
echo  Procure a linha no topo da pagina. Ela precisa dizer:
echo      "47 testes ^| 47 passaram ^| 0 falharam"
echo.
echo  Se aparecer alguma falha em vermelho, NAO publique a pagina.
echo.
start "" "%~dp0testes.html"
timeout /t 6 >nul

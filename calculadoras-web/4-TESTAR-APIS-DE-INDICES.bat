@echo off
REM Testa se as APIs oficiais de indices (Banco Central, IBGE) respondem
REM a partir do seu navegador. Precisa de internet.
title Teste das APIs de indices
echo.
echo  Abrindo o teste das APIs oficiais de indices...
echo.
echo  A pagina testa sozinha. Leia a faixa colorida do topo e me mande
echo  o resultado (verde, vermelho ou misturado).
echo.
echo  Se ficar verde, me mande tambem os numeros de cada linha: e assim
echo  que a gente confirma se o codigo de cada serie esta certo.
echo.
start "" "%~dp0teste-api-indices.html"
timeout /t 8 >nul

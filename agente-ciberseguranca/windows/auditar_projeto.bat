@echo off
REM ============================================================
REM Audita um projeto procurando falhas de seguranca.
REM
REM COMO USAR (duas formas):
REM  1) Arraste a pasta do projeto e solte sobre este arquivo.
REM  2) Ou de dois cliques e digite o caminho quando for pedido.
REM ============================================================
chcp 65001 >nul
cd /d "%~dp0.."

set PROJETO=%~1
if "%PROJETO%"=="" (
  echo.
  set /p PROJETO=Digite o caminho do projeto a auditar: 
)
if "%PROJETO%"=="" (
  echo Nenhum caminho informado. Encerrando.
  pause
  exit /b 3
)

where python >nul 2>nul
if errorlevel 1 (
  echo ERRO: Python nao encontrado. Instale em https://www.python.org/downloads/
  pause
  exit /b 3
)

echo.
echo Auditando: %PROJETO%
echo (somente leitura - nada sera alterado no projeto)
echo.
python auditor.py --projeto "%PROJETO%" --online
set RESULTADO=%errorlevel%

echo.
if %RESULTADO%==0 (
  echo ==========================================================
  echo  SEM ACHADO CRITICO OU ALTO.
  echo  Ainda assim, percorra checklists\CHECKLIST-PRE-DEPLOY.md
  echo  antes de publicar na internet.
  echo ==========================================================
) else if %RESULTADO%==1 (
  echo ==========================================================
  echo  ATENCAO: FORAM ENCONTRADOS ACHADOS CRITICO/ALTO.
  echo  NAO publique este projeto antes de corrigir.
  echo  Abra o relatorio na pasta relatorios\
  echo ==========================================================
) else (
  echo Erro na execucao. Confira a mensagem acima.
)
echo.
pause
exit /b %RESULTADO%

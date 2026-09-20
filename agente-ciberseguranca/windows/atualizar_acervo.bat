@echo off
REM ============================================================
REM Atualiza o acervo de ciberseguranca (fontes oficiais).
REM Basta dar dois cliques neste arquivo.
REM ============================================================
chcp 65001 >nul
cd /d "%~dp0.."

echo.
echo ==========================================================
echo  ATUALIZACAO DO ACERVO DE CIBERSEGURANCA
echo ==========================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo ERRO: Python nao encontrado.
  echo Instale em https://www.python.org/downloads/ marcando a opcao
  echo "Add python.exe to PATH" durante a instalacao.
  echo.
  pause
  exit /b 3
)

echo Situacao atual do acervo:
python baixar_acervo.py --verificar-validade
echo.
echo Baixando/atualizando as fontes essenciais...
echo.
python baixar_acervo.py --somente-essenciais
set RESULTADO=%errorlevel%

echo.
if %RESULTADO%==0 (
  echo CONCLUIDO SEM ERROS.
) else (
  echo CONCLUIDO COM AVISOS: alguma fonte falhou. Veja o log em acervo\_logs
  echo e confira se a URL mudou no arquivo fontes.json.
)
echo.
echo Indice do acervo: acervo\INDICE.md
echo.
echo Para baixar TAMBEM a base completa de CVEs (arquivo grande), rode:
echo     python baixar_acervo.py --id cve-lista-completa
echo.
pause
exit /b %RESULTADO%

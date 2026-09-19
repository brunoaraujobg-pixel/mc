<#
    instalar_hook_git.ps1
    Instala um "hook" de Git em um projeto: antes de cada 'git push', a auditoria
    de seguranca roda automaticamente e BLOQUEIA o envio se houver achado
    CRITICO ou ALTO.

    COMO EXECUTAR:
      powershell -ExecutionPolicy Bypass -File "C:\projetos\agente-ciberseguranca\windows\instalar_hook_git.ps1" -Projeto "C:\projetos\importar-notas"

    Para desativar depois: apague o arquivo .git\hooks\pre-push do projeto.
#>

param(
    [Parameter(Mandatory = $true)][string]$Projeto
)

$ErrorActionPreference = "Stop"
$agente = Split-Path -Parent $PSScriptRoot
$hooks = Join-Path $Projeto ".git\hooks"

if (-not (Test-Path (Join-Path $Projeto ".git"))) {
    Write-Host "ERRO: $Projeto nao e um repositorio Git (pasta .git nao encontrada)." -ForegroundColor Red
    exit 3
}
New-Item -ItemType Directory -Force -Path $hooks | Out-Null

$auditor = (Join-Path $agente "auditor.py") -replace '\\', '/'
$destino = Join-Path $hooks "pre-push"

$conteudo = @"
#!/bin/sh
# Instalado por instalar_hook_git.ps1 (Agente de Ciberseguranca).
# Bloqueia o push quando ha achado CRITICO ou ALTO.
echo ""
echo "== Auditoria de seguranca antes do push =="
python "$auditor" --projeto "." --online
CODIGO=\$?
if [ \$CODIGO -eq 1 ]; then
  echo ""
  echo "PUSH BLOQUEADO: ha achado CRITICO ou ALTO. Veja o relatorio em:"
  echo "  $($agente -replace '\\','/')/relatorios"
  echo ""
  echo "Para enviar mesmo assim (use apenas com justificativa): git push --no-verify"
  exit 1
fi
if [ \$CODIGO -eq 3 ]; then
  echo "Auditoria nao pode ser executada (erro). Push liberado, mas verifique."
fi
exit 0
"@

Set-Content -Path $destino -Value $conteudo -Encoding ASCII -NoNewline
Write-Host ""
Write-Host "Hook instalado em: $destino" -ForegroundColor Green
Write-Host "A partir de agora, 'git push' neste projeto roda a auditoria primeiro."
Write-Host ""

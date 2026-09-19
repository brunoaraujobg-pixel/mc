<#
    agendar_trimestral.ps1
    Cria no Agendador de Tarefas do Windows uma tarefa que atualiza o acervo
    de ciberseguranca a cada 3 meses (1o dia de janeiro, abril, julho e outubro).

    COMO EXECUTAR (uma unica vez):
      1. Clique com o botao direito no menu Iniciar > Terminal (Administrador)
         ou Windows PowerShell (Administrador).
      2. Rode:
         powershell -ExecutionPolicy Bypass -File "C:\projetos\agente-ciberseguranca\windows\agendar_trimestral.ps1"

    Para remover depois:
         schtasks /Delete /TN "Agente Ciberseguranca - Atualizar Acervo" /F
#>

param(
    [string]$Hora = "09:00",
    [string]$NomeTarefa = "Agente Ciberseguranca - Atualizar Acervo"
)

$ErrorActionPreference = "Stop"

$pastaProjeto = Split-Path -Parent $PSScriptRoot
$bat = Join-Path $PSScriptRoot "atualizar_acervo.bat"

Write-Host ""
Write-Host "=========================================================="
Write-Host " AGENDAMENTO TRIMESTRAL - AGENTE DE CIBERSEGURANCA"
Write-Host "=========================================================="
Write-Host "Projeto : $pastaProjeto"
Write-Host "Tarefa  : $NomeTarefa"
Write-Host "Quando  : dia 1 de JAN, ABR, JUL e OUT as $Hora"
Write-Host ""

if (-not (Test-Path $bat)) {
    Write-Host "ERRO: nao encontrei $bat" -ForegroundColor Red
    exit 3
}

# Remove agendamento anterior com o mesmo nome (evita duplicidade)
schtasks /Query /TN "$NomeTarefa" *> $null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Tarefa ja existia. Recriando..."
    schtasks /Delete /TN "$NomeTarefa" /F | Out-Null
}

schtasks /Create `
    /TN "$NomeTarefa" `
    /TR "cmd /c `"$bat`"" `
    /SC MONTHLY `
    /M JAN,APR,JUL,OCT `
    /D 1 `
    /ST $Hora `
    /RL LIMITED `
    /F

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Falhou ao criar a tarefa. Rode o PowerShell como Administrador." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Tarefa criada com sucesso." -ForegroundColor Green
Write-Host ""
Write-Host "Conferir     : schtasks /Query /TN `"$NomeTarefa`" /V /FO LIST"
Write-Host "Testar agora : schtasks /Run /TN `"$NomeTarefa`""
Write-Host "Remover      : schtasks /Delete /TN `"$NomeTarefa`" /F"
Write-Host ""
Write-Host "Observacao: se o computador estiver desligado na data, o Windows executa"
Write-Host "a tarefa na proxima vez que ligar (ajuste em Propriedades > Condicoes)."
Write-Host ""

# Checklist de protecao de rede do escritorio contabil

Foco: o cenario real de um escritorio de contabilidade (maquinas Windows, sistema
Dominio, certificados digitais de clientes, acesso a portais fiscais, eventual
acesso remoto). Revisar a cada 3 meses, junto com a atualizacao do acervo.

Referencias no acervo: `rede/NIST_SP_800-41r1_firewall.pdf`,
`rede/NIST_SP_800-46r2_acesso_remoto.pdf`, `frameworks/NIST_SP_800-63B_autenticacao.pdf`,
`brasil/CERTbr_cartilha_seguranca.pdf`.

| Data da revisao | Responsavel | Pendencias abertas |
|---|---|---|
|  |  |  |

---

## 1. Perimetro e roteador

- [ ] Senha do roteador/modem trocada da padrao de fabrica.
- [ ] Administracao do roteador acessivel somente pela rede interna (nao pela internet).
- [ ] Firmware do roteador atualizado nos ultimos 6 meses.
- [ ] Wi-Fi com WPA2 ou WPA3 e senha longa; rede de visitantes separada da rede do escritorio.
- [ ] Nenhuma porta redirecionada (port forwarding) sem necessidade justificada e documentada.
- [ ] **RDP (porta 3389) nao exposto direto na internet.** Se ha acesso remoto, e por VPN.

## 2. Estacoes e servidor

- [ ] Windows com atualizacoes automaticas ativas em todas as maquinas.
- [ ] Antivirus/Defender ativo, com verificacao periodica e alertas chegando a alguem.
- [ ] Firewall do Windows ativo em todas as maquinas.
- [ ] Usuario do dia a dia **nao** e administrador (conta de administrador separada).
- [ ] Disco criptografado (BitLocker) em notebooks que saem do escritorio.
- [ ] Bloqueio de tela automatico apos inatividade.
- [ ] Nenhuma maquina com Windows fora de suporte.

## 3. Contas, senhas e acessos

- [ ] Cada pessoa tem seu proprio usuario (nao existe login compartilhado).
- [ ] Gerenciador de senhas em uso (Bitwarden/KeePass) no lugar de planilha ou papel.
- [ ] MFA ativo em: e-mail, gov.br, contas de nuvem, GitHub e sistemas com acesso externo.
- [ ] Senhas longas (frase de 12+ caracteres) em vez de troca periodica obrigatoria (NIST 800-63B).
- [ ] Ao desligar um funcionario, existe rotina que revoga todos os acessos no mesmo dia.
- [ ] Procuracoes eletronicas (e-CAC) revisadas: so ha procuracao ativa de cliente ativo.

## 4. Certificados digitais dos clientes

- [ ] Arquivos A1 (.pfx) guardados em pasta unica com acesso restrito, fora de projeto e fora do Git.
- [ ] Senhas dos certificados no gerenciador de senhas, nunca em planilha aberta ou no codigo.
- [ ] Controle de validade dos certificados (data de vencimento por cliente).
- [ ] Token/cartao A3 nao fica conectado em maquina sem necessidade.
- [ ] Sei quais automacoes usam qual certificado (inventario simples, mesmo em planilha).

## 5. Backup (o item que salva de ransomware)

- [ ] Regra 3-2-1: 3 copias, 2 midias diferentes, 1 fora do escritorio/na nuvem.
- [ ] Ao menos uma copia **offline ou imutavel** (ransomware criptografa tambem o backup em rede).
- [ ] Backup inclui: base do Dominio, pastas de XML, documentos e planilhas de controle.
- [ ] Restauracao **testada** nos ultimos 3 meses (backup nao testado nao e backup).
- [ ] Tempo estimado para voltar a operar conhecido e aceitavel.

## 6. E-mail e phishing (porta de entrada mais comum)

- [ ] Equipe orientada: nao abrir anexo de boleto/NF-e inesperado, confirmar remetente por telefone.
- [ ] Dominio proprio com SPF, DKIM e DMARC configurados.
- [ ] Ninguem transmite senha por e-mail ou WhatsApp.
- [ ] Alteracao de dados bancarios de cliente/fornecedor exige confirmacao por canal diferente.
- [ ] Treinamento rapido com a equipe nos ultimos 6 meses (Cartilha CERT.br serve de base).

## 7. Segmentacao e sistemas internos

- [ ] Servidor do Dominio/banco de dados nao usado como maquina de navegacao na internet.
- [ ] Compartilhamentos de rede com permissao por usuario/setor (nao "Todos: controle total").
- [ ] Pastas que alimentam sistemas (`C:\NOTA ENTRADA`, `C:\NOTA SAIDA`, `C:\Fronteira`, EFD,
      relatorios de API) com acesso restrito a quem precisa e protegidas no backup.
- [ ] Maquinas de automacao (robos/Selenium) rodando em usuario dedicado e com privilegio minimo.

## 8. Deteccao e resposta

- [ ] Alguem olha os alertas (antivirus, falhas de login, aviso de conta invadida).
- [ ] Contatos de emergencia definidos: suporte de TI, contador responsavel, provedor.
- [ ] Plano escrito de 1 pagina: o que fazer nas primeiras 2 horas de um ransomware
      (desconectar da rede, nao pagar, acionar backup, registrar ocorrencia).
- [ ] Sei o prazo e o canal de comunicacao de incidente a ANPD, se houver dado pessoal envolvido.
- [ ] CVEs do catalogo CISA KEV conferidas contra os softwares em uso (`acervo/vulnerabilidades/cisa_kev.csv`).

---

## Resultado da revisao

| Severidade | Pendencias | Prazo |
|---|---|---|
| Critica |  |  |
| Alta |  |  |
| Media |  |  |

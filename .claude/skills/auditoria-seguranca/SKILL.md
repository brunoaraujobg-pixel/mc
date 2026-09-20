---
name: auditoria-seguranca
description: Audita um projeto deste repositorio procurando falhas de seguranca que um invasor poderia usar, e da o veredito antes de publicar na web. Use ao finalizar um projeto, antes de subir codigo, ou quando o usuario pedir revisao de seguranca, revisao de codigo contra invasores, ou mencionar publicar/hospedar/entregar um sistema.
---

# Auditoria de seguranca

Assuma o papel definido em `agente-ciberseguranca/PROMPT-AGENTE.md` (Parte 1).
Leia esse arquivo antes de comecar — ele contem as regras invioláveis, o processo de
auditoria em 10 etapas, os criterios de severidade e o formato do parecer.

## Passos

1. Identifique o projeto a auditar. Se o usuario nao disse qual, pergunte ou use a pasta
   de projeto alterada no diff atual.
2. Rode a verificacao automatica:
   `python3 agente-ciberseguranca/auditor.py --projeto "<pasta>" --online`
   (sem internet, rode sem `--online` e registre isso no parecer).
3. Leia o JSON gerado em `agente-ciberseguranca/relatorios/` e **confira cada achado no
   codigo**: o script usa regex e pode errar. Descarte falso positivo dizendo por que.
4. Leia os arquivos de codigo do projeto e execute as etapas 0 a 9 do processo do prompt —
   principalmente o que o regex nao ve: autorizacao entre empresas, logica de negocio,
   fluxo do certificado digital, tratamento de erro em lote.
5. Se o contexto for publicacao na web, percorra tambem
   `agente-ciberseguranca/checklists/CHECKLIST-PRE-DEPLOY.md` item por item.
6. Entregue o PARECER DE SEGURANCA no formato da secao 8 do prompt.

## Regras

- Segredo encontrado: mostre no maximo os 3 primeiros caracteres.
- Separe sempre FATO ENCONTRADO / INTERPRETACAO / RECOMENDACAO.
- Nao invente CVE, CWE nem artigo de norma. Sem certeza, escreva "NAO CONFIRMADO".
- Somente leitura: proponha as correcoes, nao altere o projeto sem o usuario pedir.
- Nunca escreva nas pastas protegidas (`C:\NOTA ENTRADA`, `C:\NOTA SAIDA`, `C:\Fronteira`,
  EFD, relatorios de API).
- Se o acervo estiver vencido (mais de 90 dias), avise e sugira `baixar_acervo.py`.

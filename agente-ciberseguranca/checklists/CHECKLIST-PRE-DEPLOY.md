# Checklist obrigatorio antes de publicar na web ou entregar um projeto

Regra: a verificacao automatica (`auditor.py`) encontra padrao de texto.
Este checklist cobre o que **so uma pessoa consegue julgar**. Nenhum projeto
vai para a internet com item marcado como NAO.

Preencha uma copia deste arquivo por projeto e guarde junto do relatorio da auditoria.

| Projeto | Data | Responsavel | Versao |
|---|---|---|---|
|  |  |  |  |

---

## 1. Segredos e certificados

- [ ] Rodei `python auditor.py --projeto "CAMINHO" --online` e nao ha achado CRITICO nem ALTO.
- [ ] Nenhuma senha, token ou chave aparece no codigo (estao em `.env` ou variavel de ambiente).
- [ ] O `.env` **nao** esta no Git (`git ls-files | findstr .env` nao retorna nada).
- [ ] Certificado digital A1 (.pfx) esta fora da pasta do projeto, em local com acesso restrito.
- [ ] Toda credencial que em algum momento ficou no codigo **foi trocada**, nao apenas removida.
- [ ] Se o projeto ja foi enviado ao GitHub: confirmei que o historico nao contem segredo
      (`git log -p | findstr /I "senha password token"`).

## 2. Entrada de dados (tudo que vem de fora e suspeito)

- [ ] XML de NF-e/CT-e e lido com `defusedxml` e com limite de tamanho.
- [ ] Todo SQL usa consulta parametrizada (`?` ou `%s`), nunca f-string ou concatenacao.
- [ ] Nome de arquivo recebido de fora e validado (`os.path.basename` + lista de extensoes permitidas).
- [ ] Nenhum dado externo chega a `eval`, `exec` ou comando de sistema.
- [ ] Planilha/CSV do cliente: campos numericos e datas sao validados antes de gravar.

## 3. Autenticacao e acesso (se o sistema tem login ou fica exposto)

- [ ] Existe autenticacao em **todas** as rotas, exceto as explicitamente publicas.
- [ ] Senhas gravadas com bcrypt ou argon2 (nunca MD5/SHA1/texto puro).
- [ ] Segundo fator (MFA) ativo, no minimo para usuario administrador.
- [ ] Um usuario nao consegue ver dados de outra empresa trocando o ID na URL/requisicao
      (testei manualmente com dois cadastros).
- [ ] Sessao expira e o logout invalida o token.
- [ ] Nao existe usuario/senha padrao ("admin/admin") nem conta de teste ativa.

## 4. Exposicao na rede

- [ ] Servico escuta em `127.0.0.1` quando o uso e local; se precisa de rede, ha firewall restringindo.
- [ ] Acesso e por HTTPS com certificado valido (sem `verify=False` em nenhum ponto).
- [ ] Porta de banco de dados **nao** esta publicada na internet.
- [ ] CORS lista dominios especificos, nao `*`.
- [ ] Modo debug desligado; a tela de erro nao mostra caminho de arquivo, SQL nem versao de biblioteca.
- [ ] Ha limite de requisicoes (rate limit) nas rotas de login e de consulta pesada.

## 5. Dados pessoais e LGPD

- [ ] O sistema guarda somente os dados necessarios (CPF, CNPJ, salario: ha finalidade clara).
- [ ] Logs nao contem senha, token, CPF completo nem numero de certificado.
- [ ] Backup dos dados existe, esta criptografado e foi **testado restaurando** ao menos uma vez.
- [ ] Ha registro de quem acessou/alterou dado sensivel (log de auditoria com usuario e data).
- [ ] Sei dizer o que fazer em caso de vazamento (comunicacao a ANPD e aos titulares).

## 6. Dependencias e ambiente

- [ ] `requirements.txt` com todas as versoes fixadas (`==`).
- [ ] Consulta de vulnerabilidade feita (`--online` ou `pip-audit -r requirements.txt`) sem achado ALTO.
- [ ] Python e bibliotecas em versao com suporte.
- [ ] O projeto roda em usuario sem privilegio de administrador.

## 7. Operacao e recuperacao

- [ ] Existe log de execucao com data, empresa e resultado (sem dado sensivel).
- [ ] Erro em uma empresa nao interrompe o processamento das demais.
- [ ] Ha como reprocessar um periodo sem duplicar registro.
- [ ] As pastas que alimentam outros sistemas (`C:\NOTA ENTRADA`, `C:\NOTA SAIDA`, `C:\Fronteira`,
      pastas de EFD e relatorios de API) **nao** sao alteradas por este projeto.
- [ ] Sei restaurar o sistema se a maquina for perdida hoje (documentado, nao na memoria).

---

## Resultado

| Campo | Preenchimento |
|---|---|
| Itens NAO marcados |  |
| Achados CRITICO/ALTO em aberto |  |
| Decisao | [ ] PUBLICAR   [ ] CORRIGIR ANTES   [ ] NAO PUBLICAR |
| Data da proxima revisao |  |

**Referencias**: OWASP ASVS 5.0 (`acervo/owasp/OWASP_ASVS_5.0.pdf`),
OWASP Top 10, OWASP WSTG, NIST CSF 2.0, LGPD (Lei 13.709/2018).

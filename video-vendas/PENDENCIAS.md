# Pendências e próximos passos (arquivado para continuar no PC)

## Estado atual
- **V1 pronta** (PR #11): vídeo 9:16 + texto + ntfy + log. Falta testar no Windows
  com produto real, chave do Claude e ntfy.

## Próximo projeto: V1.5 "Escolher produtos" (afiliado Shopee)
Decisões já tomadas:
- Modelo: **afiliado** (Bruno já tem conta aprovada).
- Nicho: **casa e festa** (material de festa e coisas de casa).
- Quer **pouca intervenção humana**: a única parada obrigatória será o "ok" da
  lista de produtos do dia pelo celular (ntfy).

Fluxo planejado:
```
Affiliate Open API (productOfferV2, casa + festa, ordenado por vendas)
  -> pontuar (vendas x comissão x preço)
  -> top 10 enviado ao celular para "ok"
  -> produto.txt automático (nome, preço, link de afiliado via generateShortLink)
  -> mídia: só se própria/autorizada; senão fila "aguardando mídia"
  -> V1 gera vídeo + texto
```

## O que levar ao PC para continuar (o chat da nuvem não alcança o site da Shopee)
1. Entrar em https://open-api.affiliate.shopee.com.br/explorer/v2 com a conta de afiliado
   e rodar `productOfferV2`. Anotar os **campos** e os **parâmetros de ordenação**
   (dá para ordenar por vendas? filtrar por categoria?).
2. Copiar o texto dos **termos do programa de afiliados** sobre uso de imagens/vídeos
   dos anúncios (decide se a mídia pode vir do anúncio).
3. App ID e App Secret (painel de afiliados > Open API). **Nunca colar o Secret no
   chat**; vai para `chave_shopee.txt` (fora do GitHub).

## Ainda NÃO confirmado (só resumos de terceiros, não documentação oficial)
- Endpoint BR: open-api.affiliate.shopee.com.br/graphql; assinatura HMAC-SHA256.
- Consultas: productOfferV2, shopOfferV2, conversionReport, generateShortLink.

## V2 / V3 (depois)
- V2: agendamento (TikTok Content Posting API / Metricool / Shopee) após pesquisa
  na documentação oficial e escolha do caminho.
- V3: métricas (conversionReport) e sugestão de quais produtos repetir.

## Ideias de negócio (depois)
- Vídeos curtos de contabilidade (MEI, DAS, DEFIS, Simples) para atrair clientes.
- Alertas de prazo fiscal por assinatura (a partir do projeto eSocial/folha).
- Importação de XML de notas como serviço para outros escritórios.
- Monitor de licitações por CNAE.

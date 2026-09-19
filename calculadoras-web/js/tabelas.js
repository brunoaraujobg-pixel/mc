/* =============================================================================
   TABELAS.JS  —  ARQUIVO ÚNICO DE CONFIGURAÇÃO DAS TABELAS OFICIAIS
   -----------------------------------------------------------------------------
   TODA tabela, alíquota, faixa, dedução e percentual usado pelas calculadoras
   está AQUI. Para atualizar a página quando a legislação mudar (reajuste anual
   da tabela do IR, nova portaria do INSS, etc.), altere SOMENTE este arquivo.
   Nenhum número de tabela deve ser escrito nos outros arquivos .js.

   Cada bloco traz:
     FONTE ........ norma / origem oficial
     VIGENCIA ..... a partir de quando vale
     CONFERIDO EM . data da última conferência

   >>> AVISO PARA O BRUNO <<<
   Os valores abaixo foram levantados em 19/09/2026 cruzando várias publicações
   que reproduzem as normas citadas. O ambiente onde esta página foi gerada NÃO
   conseguiu abrir diretamente os sites gov.br (bloqueio de rede), então a
   conferência final na fonte oficial ainda precisa ser feita por você antes de
   publicar. Veja o passo "CONFERÊNCIA OBRIGATÓRIA" no README.md.
============================================================================= */

var TABELAS = {

  versao: '2026.1',
  atualizadoEm: '19/09/2026',
  conferidoNaFonteOficial: false, // <<< marcar true depois da conferência no gov.br

  /* ---------------------------------------------------------------------------
     1) INSS — CONTRIBUIÇÃO DO SEGURADO EMPREGADO / DOMÉSTICO / AVULSO
     FONTE ........ Portaria Interministerial MPS/MF nº 13, de 09/01/2026
                    (DOU de 12/01/2026, Edição 7, Seção 1, pág. 58)
     VIGENCIA ..... competências a partir de janeiro/2026
     CONFERIDO EM . 19/09/2026
     OBS .......... cálculo PROGRESSIVO por faixas sucessivas: cada parcela do
                    salário sofre a alíquota da sua faixa (não é alíquota única).
                    Salário mínimo 2026: R$ 1.621,00 | Teto: R$ 8.475,55
                    Desconto máximo resultante: R$ 988,09
  --------------------------------------------------------------------------- */
  inss: {
    fonte: 'Portaria Interministerial MPS/MF nº 13, de 09/01/2026',
    vigencia: 'a partir de 01/2026',
    salarioMinimo: 1621.00,
    teto: 8475.55,
    faixas: [
      { ate: 1621.00, aliquota: 0.075 },
      { ate: 2902.84, aliquota: 0.090 },
      { ate: 4354.27, aliquota: 0.120 },
      { ate: 8475.55, aliquota: 0.140 }
    ]
  },

  /* ---------------------------------------------------------------------------
     2) IRRF — TABELA PROGRESSIVA MENSAL
     FONTE ........ Lei nº 15.191, de 11/08/2025 (converteu a MP nº 1.294/2025)
     VIGENCIA ..... rendimentos a partir de maio/2025 — mantida em 2026
     CONFERIDO EM . 19/09/2026
  --------------------------------------------------------------------------- */
  irrf: {
    fonte: 'Lei nº 15.191/2025 (tabela progressiva mensal)',
    vigencia: 'a partir de 05/2025, vigente em 2026',
    faixas: [
      { ate: 2428.80,  aliquota: 0.000, deduzir:   0.00 },
      { ate: 2826.65,  aliquota: 0.075, deduzir: 182.16 },
      { ate: 3751.05,  aliquota: 0.150, deduzir: 394.16 },
      { ate: 4664.68,  aliquota: 0.225, deduzir: 675.49 },
      { ate: Infinity, aliquota: 0.275, deduzir: 908.73 }
    ],

    // Dedução mensal por dependente — Lei nº 9.250/1995, art. 4º, III,
    // com redação da Lei nº 13.149/2015 (valor inalterado desde 04/2015).
    deducaoDependente: 189.59,

    // Desconto simplificado mensal = 25% do limite da 1ª faixa (25% de 2.428,80).
    // Substitui TODAS as deduções legais quando for mais vantajoso.
    // FONTE: Lei nº 13.149/2015 c/c Lei nº 15.191/2025.
    descontoSimplificado: 607.20,

    /* -------------------------------------------------------------------------
       REDUTOR DO IMPOSTO — "isenção até R$ 5.000"
       FONTE ....... Lei nº 15.270, de 26/11/2025
                     + orientação da Receita Federal de dezembro/2025
       VIGENCIA .... rendimentos recebidos a partir de 01/01/2026
       COMO FUNCIONA:
         1) apura-se o IRRF normalmente pela tabela progressiva acima;
         2) aplica-se um REDUTOR sobre o imposto apurado:
            - rendimento tributável mensal até R$ 5.000,00 ......... zera o IRRF
              (redução de até R$ 312,89)
            - de R$ 5.000,01 até R$ 7.350,00 ...... 978,62 - (0,133145 x rendimento)
            - acima de R$ 7.350,00 ................ sem redutor
         3) o redutor nunca é maior que o imposto apurado (não gera restituição).
       OBS: a base do redutor é o RENDIMENTO TRIBUTÁVEL BRUTO do mês
            (e não a base de cálculo após deduções).
    ------------------------------------------------------------------------- */
    redutor2026: {
      fonte: 'Lei nº 15.270/2025',
      vigencia: 'a partir de 01/01/2026',
      limiteIsencaoTotal: 5000.00,
      limiteReducaoParcial: 7350.00,
      reducaoMaxima: 312.89,
      constante: 978.62,
      coeficiente: 0.133145
    }
  },

  /* ---------------------------------------------------------------------------
     3) SIMPLES NACIONAL — ANEXOS I a V
     FONTE ........ Lei Complementar nº 123/2006, Anexos I a V
                    (redação dada pela LC nº 155/2016, vigente desde 01/2018)
     VIGENCIA ..... 2026 — sem alteração de faixas ou alíquotas para este ano
     CONFERIDO EM . 19/09/2026
     CÁLCULO ...... alíquota efetiva = ((RBT12 x alíquota) - parcela a deduzir) / RBT12
                    RBT12 = receita bruta acumulada nos 12 meses anteriores
     LIMITES ...... teto do Simples: R$ 4.800.000,00 por ano-calendário
                    sublimite de ICMS/ISS dentro do DAS: R$ 3.600.000,00
  --------------------------------------------------------------------------- */
  simples: {
    fonte: 'LC nº 123/2006, Anexos I a V (redação da LC nº 155/2016)',
    vigencia: 'desde 01/2018, vigente em 2026',
    limiteAnual: 4800000.00,
    sublimiteIcmsIss: 3600000.00,
    fatorR: 0.28, // folha 12m / RBT12 >= 28% => Anexo III; abaixo => Anexo V

    anexos: {
      I: {
        nome: 'Anexo I — Comércio',
        faixas: [
          { ate:  180000.00, aliquota: 0.0400, deduzir:      0.00 },
          { ate:  360000.00, aliquota: 0.0730, deduzir:   5940.00 },
          { ate:  720000.00, aliquota: 0.0950, deduzir:  13860.00 },
          { ate: 1800000.00, aliquota: 0.1070, deduzir:  22500.00 },
          { ate: 3600000.00, aliquota: 0.1430, deduzir:  87300.00 },
          { ate: 4800000.00, aliquota: 0.1900, deduzir: 378000.00 }
        ]
      },
      II: {
        nome: 'Anexo II — Indústria',
        faixas: [
          { ate:  180000.00, aliquota: 0.0450, deduzir:      0.00 },
          { ate:  360000.00, aliquota: 0.0780, deduzir:   5940.00 },
          { ate:  720000.00, aliquota: 0.1000, deduzir:  13860.00 },
          { ate: 1800000.00, aliquota: 0.1120, deduzir:  22500.00 },
          { ate: 3600000.00, aliquota: 0.1470, deduzir:  85500.00 },
          { ate: 4800000.00, aliquota: 0.3000, deduzir: 720000.00 }
        ]
      },
      III: {
        nome: 'Anexo III — Serviços (inclui CPP no DAS)',
        faixas: [
          { ate:  180000.00, aliquota: 0.0600, deduzir:      0.00 },
          { ate:  360000.00, aliquota: 0.1120, deduzir:   9360.00 },
          { ate:  720000.00, aliquota: 0.1350, deduzir:  17640.00 },
          { ate: 1800000.00, aliquota: 0.1600, deduzir:  35640.00 },
          { ate: 3600000.00, aliquota: 0.2100, deduzir: 125640.00 },
          { ate: 4800000.00, aliquota: 0.3300, deduzir: 648000.00 }
        ]
      },
      IV: {
        nome: 'Anexo IV — Serviços (CPP recolhida FORA do DAS)',
        faixas: [
          { ate:  180000.00, aliquota: 0.0450, deduzir:      0.00 },
          { ate:  360000.00, aliquota: 0.0900, deduzir:   8100.00 },
          { ate:  720000.00, aliquota: 0.1020, deduzir:  12420.00 },
          { ate: 1800000.00, aliquota: 0.1400, deduzir:  39780.00 },
          { ate: 3600000.00, aliquota: 0.2200, deduzir: 183780.00 },
          { ate: 4800000.00, aliquota: 0.3300, deduzir: 828000.00 }
        ]
      },
      V: {
        nome: 'Anexo V — Serviços intelectuais (Fator R abaixo de 28%)',
        faixas: [
          { ate:  180000.00, aliquota: 0.1550, deduzir:      0.00 },
          { ate:  360000.00, aliquota: 0.1800, deduzir:   4500.00 },
          { ate:  720000.00, aliquota: 0.1950, deduzir:   9900.00 },
          { ate: 1800000.00, aliquota: 0.2050, deduzir:  17100.00 },
          { ate: 3600000.00, aliquota: 0.2300, deduzir:  62100.00 },
          { ate: 4800000.00, aliquota: 0.3050, deduzir: 540000.00 }
        ]
      }
    }
  },

  /* ---------------------------------------------------------------------------
     4) LUCRO PRESUMIDO
     FONTE ........ Lei nº 9.249/1995, art. 15 e art. 20 (percentuais de presunção)
                    Lei nº 9.430/1996, art. 1º e 2º (apuração trimestral, adicional)
                    Lei nº 9.715/1998 e Lei nº 9.718/1998 (PIS/COFINS cumulativos)
     VIGENCIA ..... regra geral vigente em 2026
     CONFERIDO EM . 19/09/2026

     MAJORAÇÃO DE 2026 (LC nº 224/2025):
       redução linear de 10% dos benefícios fiscais federais. No Lucro Presumido
       isso se traduz em ACRÉSCIMO DE 10% nos percentuais de presunção de IRPJ e
       CSLL sobre a PARCELA da receita bruta que exceder R$ 1.250.000,00 por
       TRIMESTRE (R$ 5.000.000,00 por ano). Ex.: presunção de 32% vira 35,2%
       sobre o excedente; 8% vira 8,8%.
       Vigência: IRPJ a partir do 1º trimestre/2026; CSLL a partir do 2º
       trimestre/2026 (noventena). Existem decisões judiciais questionando a
       medida — por isso ela fica em um campo LIGA/DESLIGA abaixo.
  --------------------------------------------------------------------------- */
  lucroPresumido: {
    fonte: 'Lei nº 9.249/1995 art. 15 e 20; Lei nº 9.430/1996; LC nº 224/2025',
    vigencia: '2026',

    // percentuais de presunção por tipo de atividade
    presuncao: {
      comercio:  { irpj: 0.08, csll: 0.12 },
      industria: { irpj: 0.08, csll: 0.12 },
      servico:   { irpj: 0.32, csll: 0.32 }
    },

    irpjAliquota: 0.15,
    irpjAdicionalAliquota: 0.10,
    irpjAdicionalLimiteTrimestral: 60000.00, // R$ 20.000,00 por mês

    csllAliquota: 0.09,

    // PIS/COFINS regime CUMULATIVO
    pisCumulativo: 0.0065,
    cofinsCumulativo: 0.0300,

    // Majoração da LC nº 224/2025
    majoracaoLC224: {
      ativa: true,
      fator: 1.10,
      limiteTrimestral: 1250000.00,
      limiteAnual: 5000000.00,
      observacao: 'IRPJ desde o 1º tri/2026; CSLL desde o 2º tri/2026. Medida questionada judicialmente.'
    }
  },

  /* ---------------------------------------------------------------------------
     5) LUCRO REAL
     FONTE ........ Lei nº 9.430/1996 (IRPJ/CSLL); Lei nº 9.249/1995 art. 3º
                    Lei nº 10.637/2002 (PIS não cumulativo — 1,65%)
                    Lei nº 10.833/2003 (COFINS não cumulativa — 7,6%)
     VIGENCIA ..... regra geral vigente em 2026
     CONFERIDO EM . 19/09/2026
  --------------------------------------------------------------------------- */
  lucroReal: {
    fonte: 'Lei nº 9.430/1996; Lei nº 10.637/2002; Lei nº 10.833/2003',
    vigencia: '2026',
    irpjAliquota: 0.15,
    irpjAdicionalAliquota: 0.10,
    irpjAdicionalLimiteMensal: 20000.00, // R$ 240.000,00 por ano
    csllAliquota: 0.09,
    pisNaoCumulativo: 0.0165,
    cofinsNaoCumulativa: 0.0760
  },

  /* ---------------------------------------------------------------------------
     6) CONTRIBUIÇÃO PREVIDENCIÁRIA PATRONAL (CPP) — regime normal
     FONTE ........ Lei nº 8.212/1991, art. 22, I (20% sobre a folha)
                    RAT/FAP: Decreto nº 3.048/1999, Anexo V (1%, 2% ou 3%,
                    ajustado pelo FAP de 0,5 a 2,0)
                    Terceiros (Sistema S, Salário-Educação, INCRA): Lei nº 11.457/2007
     OBS .......... o percentual de terceiros varia conforme o FPAS da empresa.
                    Aqui usamos uma MÉDIA para estimativa. No cálculo real do
                    cliente isso deve vir do FPAS/RAT efetivos da empresa.
  --------------------------------------------------------------------------- */
  cpp: {
    fonte: 'Lei nº 8.212/1991 art. 22; Decreto nº 3.048/1999 Anexo V; Lei nº 11.457/2007',
    patronal: 0.20,
    ratMedio: 0.02,        // RAT presumido de 2% (varia de 1% a 3%, ajustado pelo FAP de 0,5 a 2,0)
    terceirosMedio: 0.058, // 5,8% é o percentual mais comum (comércio/serviços)
    // Total estimado = 27,8%. Com RAT de 1% dá 26,8%; com RAT de 3% dá 28,8%.
    // No cálculo real do cliente, usar o RAT/FAP e o código FPAS efetivos da empresa.
    get total() { return this.patronal + this.ratMedio + this.terceirosMedio; }
  },

  /* ---------------------------------------------------------------------------
     7) REFORMA TRIBUTÁRIA — IBS / CBS (apenas aviso na tela, não entra no cálculo)
     FONTE ........ Lei Complementar nº 214/2025, arts. 343, 346 e 348
     SITUAÇÃO 2026: fase de TESTE. CBS a 0,9% e IBS a 0,1%, compensáveis com
                    PIS/COFINS do mesmo período; a empresa que cumprir as
                    obrigações acessórias fica dispensada do recolhimento.
                    Por isso NÃO representam custo adicional em 2026 e não são
                    somados na simulação.
     A PARTIR DE 2027: extinção de PIS/COFINS e entrada efetiva da CBS.
                    ESTA PÁGINA PRECISARÁ SER REVISTA ANTES DE JANEIRO/2027.
  --------------------------------------------------------------------------- */
  reformaTributaria: {
    fonte: 'LC nº 214/2025, arts. 343, 346 e 348',
    cbsTeste2026: 0.009,
    ibsTeste2026: 0.001,
    entraNoCalculo: false,
    avisoRevisao: 'A partir de 2027 PIS/COFINS são extintos e a CBS passa a ser cobrada. Revisar esta calculadora antes de janeiro/2027.'
  },

  /* ---------------------------------------------------------------------------
     8) ÍNDICES DE ATUALIZAÇÃO MONETÁRIA
     FONTE ........ API pública do Banco Central — Sistema Gerenciador de Séries
                    Temporais (SGS). Endereço:
                    https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados
                    Aberta, sem cadastro e sem chave de acesso.
     VIGENCIA ..... os valores vêm do próprio BCB a cada consulta, então NÃO
                    existe tabela para atualizar aqui. É a grande diferença em
                    relação às tabelas de IR e INSS acima.
     CONFERIDO EM . 19/09/2026 (códigos das séries a confirmar — veja abaixo)

     >>> A CONFIRMAR <<<
     Os códigos das séries precisam da sua conferência. Abra o arquivo
     teste-api-indices.html (ou o atalho 4-TESTAR-APIS-DE-INDICES.bat): ele
     mostra os últimos valores que cada série devolve, para você comparar com
     o índice que conhece. Se algum código estiver trocado, corrija aqui.

     COMO CADA ÍNDICE ACUMULA
       "composto" — o índice de cada mês incide sobre o valor já corrigido:
                    fator = (1+i1) x (1+i2) x ... x (1+in)
       "soma"     — as taxas mensais são somadas, sem capitalização. É a regra
                    da SELIC para tributos federais (Lei nº 9.430/1996, art. 61,
                    parágrafo 3º), somando-se ainda 1% no mês do pagamento.
  --------------------------------------------------------------------------- */
  indices: {
    fonte: 'Banco Central — API pública do SGS (api.bcb.gov.br)',
    urlBase: 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.',
    codigosConferidos: false, // <<< marcar true depois de rodar o teste das APIs

    lista: [
      { chave: 'ipca', nome: 'IPCA', serie: 433, metodo: 'composto',
        orgao: 'IBGE (divulgado no SGS do Banco Central)',
        uso: 'Índice oficial da inflação. O mais usado em contratos e em correção de valores em geral.' },

      { chave: 'inpc', nome: 'INPC', serie: 188, metodo: 'composto',
        orgao: 'IBGE (divulgado no SGS do Banco Central)',
        uso: 'Muito usado em reclamações trabalhistas e em reajustes salariais.' },

      { chave: 'igpm', nome: 'IGP-M', serie: 189, metodo: 'composto',
        orgao: 'FGV (divulgado no SGS do Banco Central)',
        uso: 'O índice tradicional dos contratos de aluguel.' },

      { chave: 'tr', nome: 'TR — Taxa Referencial', serie: 226, metodo: 'composto',
        orgao: 'Banco Central',
        uso: 'Correção do FGTS e de alguns contratos.' },

      { chave: 'selic', nome: 'SELIC', serie: 4390, metodo: 'soma',
        orgao: 'Banco Central',
        uso: 'Juros de mora de tributos federais.',
        observacao: 'Para tributos federais, somam-se as SELIC mensais e acrescenta-se 1% ' +
                    'referente ao mês do pagamento (Lei nº 9.430/1996, art. 61, parágrafo 3º).',
        acrescentaUmPorCento: true }
    ]
  },

  /* ---------------------------------------------------------------------------
     9) DADOS DO ESCRITÓRIO (usados no cabeçalho, rodapé e botões de contato)
  --------------------------------------------------------------------------- */
  escritorio: {
    nome: 'M Contabilidade',
    endereco: 'Rua da Palma, 295 — Sala 113, Santo Antônio, Recife-PE',
    telefoneFixo: '(81) 3224-3472',
    telefoneCelular: '(81) 9 8774-7434',
    whatsapp: '5581987747434',
    site: 'mccontabilidadebrasil.com.br'
  }
};

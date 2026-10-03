class ErroAgente(Exception):
    """Erro com etapa e instrução de como corrigir."""

    def __init__(self, etapa, mensagem, como_corrigir=""):
        super().__init__(mensagem)
        self.etapa = etapa
        self.mensagem = mensagem
        self.como_corrigir = como_corrigir

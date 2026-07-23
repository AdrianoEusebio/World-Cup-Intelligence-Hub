from dataclasses import dataclass

@dataclass
class RankingEntry:
    """Entidade que representa uma seleção no Ranking Mundial da FIFA."""
    ranqueamento: int
    nome_selecao: str
    pontos: float

    def __post_init__(self):
        from core.utils.normalization import normalizar_nome_selecao
        self.nome_selecao = normalizar_nome_selecao(self.nome_selecao)

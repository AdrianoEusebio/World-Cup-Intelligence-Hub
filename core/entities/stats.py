from dataclasses import dataclass
from typing import Optional

@dataclass
class SelectionStats:
    """Entidade unificada contendo vitórias acumuladas e pontuação no ranking FIFA."""
    nome_selecao: str
    vitorias: int
    pontos: Optional[float] = None

    def __post_init__(self):
        from core.utils.normalization import normalizar_nome_selecao
        self.nome_selecao = normalizar_nome_selecao(self.nome_selecao)

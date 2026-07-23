from dataclasses import dataclass
from typing import Optional

@dataclass
class Match:
    """Entidade que representa uma partida de futebol da Copa do Mundo."""
    id: Optional[int]
    time_da_casa: str
    time_visitante: str
    placar_time_da_casa: Optional[int]
    placar_time_visitante: Optional[int]
    status: str

    def __post_init__(self):
        from core.utils.normalization import normalizar_nome_selecao
        self.time_da_casa = normalizar_nome_selecao(self.time_da_casa)
        self.time_visitante = normalizar_nome_selecao(self.time_visitante)

    @property
    def is_finished(self) -> bool:
        return self.status.upper() == "FINALIZADA"

    @property
    def winner(self) -> Optional[str]:
        """Retorna o nome do time vencedor. Se for empate ou inacabada, retorna None."""
        if not self.is_finished or self.placar_time_da_casa is None or self.placar_time_visitante is None:
            return None
        if self.placar_time_da_casa > self.placar_time_visitante:
            return self.time_da_casa
        elif self.placar_time_visitante > self.placar_time_da_casa:
            return self.time_visitante
        return None

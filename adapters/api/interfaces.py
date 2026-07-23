from abc import ABC, abstractmethod
from core.entities.match import Match

class MatchRepository(ABC):
    """Interface abstrata (contrato) para o repositório de partidas de futebol."""

    @abstractmethod
    def get_all_matches(self) -> list[Match]:
        """Obtém todas as partidas de futebol disponíveis na fonte de dados."""
        pass

from abc import ABC, abstractmethod
from core.entities.ranking import RankingEntry

class RankingScraper(ABC):
    """Interface abstrata para o scraper de ranking mundial da FIFA."""

    @abstractmethod
    def fetch_top_10(self, url: str) -> list[RankingEntry]:
        """Acessa a URL configurada, extrai o Top 10 atual das seleções e retorna os dados."""
        pass

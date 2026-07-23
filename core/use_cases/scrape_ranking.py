from adapters.scraper.interfaces import RankingScraper
from core.entities.ranking import RankingEntry
from config.settings import settings
from config.logging_config import logger

class ScrapeRankingUseCase:
    """Caso de uso responsável por orquestrar a raspagem do ranking da FIFA."""

    def __init__(self, scraper: RankingScraper):
        self.scraper = scraper

    def execute(self) -> list[RankingEntry]:
        logger.info("Executando o caso de uso de raspagem do ranking FIFA...")
        return self.scraper.fetch_top_10(settings.URL_RANKING_FIFA)

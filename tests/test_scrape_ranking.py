import unittest
from adapters.scraper.playwright_impl import PlaywrightRankingScraper
from core.entities.ranking import RankingEntry

class TestPlaywrightRankingScraper(unittest.TestCase):
    """Suíte de testes para a automação web do Scraper com Playwright (T2)."""

    def setUp(self):
        self.scraper = PlaywrightRankingScraper()

    def test_fallback_contingencia_ao_falhar_requisicao(self):
        # CT-07: Resiliência de rede e APIs externas (Fallback silencioso)
        # Força uma navegação para uma URL inválida para estourar erro no Playwright
        ranking_fallback = self.scraper.fetch_top_10("http://site-totalmente-inexistente-12345.com")
        
        # O sistema deve capturar a falha e retornar a lista mockada de backup
        self.assertEqual(len(ranking_fallback), 10)
        
        # Verifica se o primeiro lugar no mock de contingência é a Argentina
        primeiro_colocado = ranking_fallback[0]
        self.assertEqual(primeiro_colocado.nome_selecao, "Argentina")
        self.assertEqual(primeiro_colocado.ranqueamento, 1)
        self.assertEqual(primeiro_colocado.pontos, 1860.14)

if __name__ == "__main__":
    unittest.main()

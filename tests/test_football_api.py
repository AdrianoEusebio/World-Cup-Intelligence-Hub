import unittest
from unittest.mock import patch, MagicMock
import requests
from adapters.api.football_api import HttpMatchRepository
from config.settings import settings

class TestHttpMatchRepository(unittest.TestCase):
    """Suíte de testes para a ingestão de partidas com resiliência de rede e API (T1)."""

    def setUp(self):
        self.repo = HttpMatchRepository()

    def test_fallback_quando_api_key_vazia(self):
        # CT-06: Se a chave for vazia, deve carregar as partidas do arquivo de mock local
        with patch.object(settings, "FOOTBALL_API_KEY", ""):
            # Re-inicializa o repositório para capturar a chave vazia
            repo_sem_chave = HttpMatchRepository()
            partidas = repo_sem_chave.get_all_matches()
            
            # Deve carregar com sucesso as 14 partidas do mock local
            self.assertEqual(len(partidas), 14)
            self.assertEqual(partidas[0].time_da_casa, "Brazil")

    @patch("requests.get")
    def test_fallback_quando_api_excede_limite_requisicoes_429(self, mock_get):
        # CT-06: Se a API retornar erro de cota (429), deve acionar o fallback local
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        partidas = self.repo.get_all_matches()
        
        # Garante que as 14 partidas locais foram carregadas como contingência
        self.assertEqual(len(partidas), 14)
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_fallback_quando_rede_indisponivel_timeout(self, mock_get):
        # CT-06: Se a rede cair ou der timeout, deve acionar o fallback silenciosamente
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")
        
        partidas = self.repo.get_all_matches()
        
        # Garante que as 14 partidas locais foram carregadas como contingência
        self.assertEqual(len(partidas), 14)
        mock_get.assert_called_once()

if __name__ == "__main__":
    unittest.main()

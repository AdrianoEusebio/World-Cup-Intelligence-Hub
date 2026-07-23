import unittest
from unittest.mock import MagicMock
from adapters.api.interfaces import MatchRepository
from core.use_cases.process_matches import ProcessMatchesUseCase
from core.entities.match import Match
from core.enum import StatusPartida

class TestProcessMatchesUseCase(unittest.TestCase):
    """Suíte de testes para o caso de uso de processamento de partidas com Pandas (T1)."""

    def setUp(self):
        # Cria um mock do repositório de partidas para isolar o teste unitário
        self.mock_repo = MagicMock(spec=MatchRepository)
        self.use_case = ProcessMatchesUseCase(self.mock_repo)

    def test_processamento_sucesso_calculo_estatisticas(self):
        # CT-01 & CT-02: Garantir processamento analítico correto e limpeza de nulos
        partidas_teste = [
            # Partidas finalizadas válidas
            Match(id=1, time_da_casa="Spain", time_visitante="France", placar_time_da_casa=3, placar_time_visitante=1, status="FINALIZADA"), # 4 gols, Vencedor: Spain
            Match(id=2, time_da_casa="France", time_visitante="Brazil", placar_time_da_casa=2, placar_time_visitante=1, status="FINALIZADA"), # 3 gols, Vencedor: France
            Match(id=3, time_da_casa="Brazil", time_visitante="Spain", placar_time_da_casa=2, placar_time_visitante=1, status="FINALIZADA"), # 3 gols, Vencedor: Brazil
            Match(id=4, time_da_casa="England", time_visitante="Germany", placar_time_da_casa=0, placar_time_visitante=0, status="FINALIZADA"), # 0 gols, Empate (sem vencedor)
            Match(id=5, time_da_casa="Italy", time_visitante="Spain", placar_time_da_casa=1, placar_time_visitante=2, status="FINALIZADA"), # 3 gols, Vencedor: Spain
            
            # Partida não finalizada (deve ser limpa/ignorada)
            Match(id=6, time_da_casa="Brazil", time_visitante="Germany", placar_time_da_casa=1, placar_time_visitante=0, status="AGENDADA"),
            
            # Partida com placar nulo (deve ser limpa/ignorada)
            Match(id=7, time_da_casa="France", time_visitante="Spain", placar_time_da_casa=None, placar_time_visitante=None, status="FINALIZADA")
        ]
        
        # Configura o mock para retornar a lista de testes
        self.mock_repo.get_all_matches.return_value = partidas_teste
        
        # Executa o caso de uso
        top_selecoes, media_gols = self.use_case.execute()
        
        # Validação da limpeza de dados e cálculo da média
        # Total de gols das 5 partidas válidas: 4 + 3 + 3 + 0 + 3 = 13
        # Média de gols: 13 / 5 = 2.6
        self.assertEqual(media_gols, 2.6)
        
        # Validação do ranking de vitórias
        # Spain: 2 vitórias (Match 1, Match 5)
        # France: 1 vitória (Match 2)
        # Brazil: 1 vitória (Match 3)
        self.assertEqual(len(top_selecoes), 3)
        
        # O primeiro lugar deve ser Spain com 2 vitórias
        primeiro_lugar = top_selecoes[0]
        self.assertEqual(primeiro_lugar.nome_selecao, "Spain")
        self.assertEqual(primeiro_lugar.vitorias, 2)

    def test_processamento_sem_partidas_finalizadas(self):
        # CT-05: Resiliência caso não haja dados válidos no arquivo
        partidas_invalidas = [
            Match(id=1, time_da_casa="Brazil", time_visitante="France", placar_time_da_casa=1, placar_time_visitante=1, status="AGENDADA")
        ]
        self.mock_repo.get_all_matches.return_value = partidas_invalidas
        
        top_selecoes, media_gols = self.use_case.execute()
        
        # Se nenhuma partida é válida, a média de gols deve ser NaN (interpretada como 0 no assert ou tratada)
        import math
        self.assertTrue(math.isnan(media_gols) or media_gols == 0.0)
        self.assertEqual(len(top_selecoes), 0)

if __name__ == "__main__":
    unittest.main()

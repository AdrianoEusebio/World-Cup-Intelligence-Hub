import unittest
from unittest.mock import MagicMock
from adapters.database.interfaces import SelectionStatsRepository
from core.use_cases.merge_persist import MergeAndPersistUseCase
from core.entities.stats import SelectionStats
from core.entities.ranking import RankingEntry

class TestMergeAndPersistUseCase(unittest.TestCase):
    """Suíte de testes para o caso de uso de cruzamento de dados e idempotência (T3)."""

    def setUp(self):
        self.mock_db_repo = MagicMock(spec=SelectionStatsRepository)
        self.use_case = MergeAndPersistUseCase(self.mock_db_repo)

    def test_merge_cruzamento_sucesso(self):
        # CT-03: Cruzamento de dados de fontes distintas
        vitorias_analise = [
            SelectionStats(nome_selecao="Brazil", vitorias=4),
            SelectionStats(nome_selecao="France", vitorias=3),
            SelectionStats(nome_selecao="Argentina", vitorias=2),
            SelectionStats(nome_selecao="Germany", vitorias=1)
        ]
        
        ranking_fifa = [
            RankingEntry(ranqueamento=1, nome_selecao="Argentina", pontos=1970.37),
            RankingEntry(ranqueamento=2, nome_selecao="France", pontos=1948.97),
            RankingEntry(ranqueamento=3, nome_selecao="Brazil", pontos=1804.92),
            RankingEntry(ranqueamento=4, nome_selecao="England", pontos=1922.83) # Inglaterra está no ranking mas não tem vitórias
        ]
        
        # Executa o merge
        resultado = self.use_case.execute(vitorias_analise, ranking_fifa)
        
        # Valida que todos os registros (incluindo a Inglaterra sem vitórias e Alemanha sem ranking) foram processados
        self.assertEqual(len(resultado), 5)
        
        # Converte em dicionário para facilitar asserções
        mapa_resultado = {r.nome_selecao: r for r in resultado}
        
        # 1. Brasil deve ter 4 vitórias e 1804.92 pontos
        self.assertEqual(mapa_resultado["Brazil"].vitorias, 4)
        self.assertEqual(mapa_resultado["Brazil"].pontos, 1804.92)
        
        # 2. Inglaterra deve ter 0 vitórias (preenchido pelo fillna) e 1922.83 pontos
        self.assertEqual(mapa_resultado["England"].vitorias, 0)
        self.assertEqual(mapa_resultado["England"].pontos, 1922.83)
        
        # 3. Alemanha deve ter 1 vitória e pontos None (NULL no banco)
        self.assertEqual(mapa_resultado["Germany"].vitorias, 1)
        self.assertIsNone(mapa_resultado["Germany"].pontos)
        
        # Valida que o método save() do repositório foi chamado exatamente 5 vezes
        self.assertEqual(self.mock_db_repo.save.call_count, 5)

if __name__ == "__main__":
    unittest.main()

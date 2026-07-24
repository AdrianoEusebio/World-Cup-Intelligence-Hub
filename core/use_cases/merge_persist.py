import pandas as pd
from adapters.database.interfaces import SelectionStatsRepository
from core.entities.stats import SelectionStats
from core.entities.ranking import RankingEntry
from config.logging_config import logger

class MergeAndPersistUseCase:
    """Caso de uso responsável por cruzar os dados analíticos com os dados de scraping e persistir no banco."""

    def __init__(self, stats_repo: SelectionStatsRepository):
        self.stats_repo = stats_repo

    def execute(self, lista_vitorias: list[SelectionStats], lista_ranking: list[RankingEntry]) -> list[SelectionStats]:
        logger.info("Iniciando cruzamento de dados (Vitórias x Ranking)...")

        df_vits = pd.DataFrame([v.__dict__ for v in lista_vitorias]) if lista_vitorias else pd.DataFrame(columns=['nome_selecao', 'vitorias'])
        if not df_vits.empty:
            df_vits = df_vits.drop(columns=['pontos'], errors='ignore')

        df_rank = pd.DataFrame([r.__dict__ for r in lista_ranking]) if lista_ranking else pd.DataFrame(columns=['nome_selecao', 'pontos'])
        if not df_rank.empty:
            df_rank = df_rank.drop(columns=['ranqueamento'], errors='ignore')

        df_consolidado = pd.merge(df_vits, df_rank, on='nome_selecao', how='outer')
        lista_retorno = []
        if not df_consolidado.empty:
            df_consolidado['vitorias'] = df_consolidado['vitorias'].fillna(0).astype(int)
            df_consolidado = df_consolidado.where(pd.notnull(df_consolidado), None)

        for index, linha in df_consolidado.iterrows():
            try:
                pontos_raw = linha['pontos']
                pontos_val = float(pontos_raw) if pd.notna(pontos_raw) else None
                
                stats = SelectionStats(
                    nome_selecao=linha['nome_selecao'],
                    vitorias=int(linha['vitorias']),
                    pontos=pontos_val
                )
                self.stats_repo.save(stats)
                lista_retorno.append(stats)
                
            except Exception as e:
                logger.error(f"Erro ao salvar dados da seleção {linha['nome_selecao']}: {e}")

        logger.info("Persistência dos dados consolidados finalizada com sucesso.")
        
        return lista_retorno

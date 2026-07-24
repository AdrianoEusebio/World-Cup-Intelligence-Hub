import pandas as pd
from adapters.api.interfaces import MatchRepository
from core.entities.stats import SelectionStats
from config.logging_config import logger
from core.enum import StatusPartida

class ProcessMatchesUseCase:
    """Caso de uso responsável por limpar e processar estatísticas das partidas usando Pandas."""
    def __init__(self, match_repo: MatchRepository):
        self.match_repo = match_repo

    def execute(self) -> tuple[list[SelectionStats], float]:
        partidas = self.match_repo.get_all_matches()
        
        dados_partidas = []
        for p in partidas:
            dicionario = p.__dict__.copy()
            dicionario['time_vencedor'] = p.winner
            dados_partidas.append(dicionario)

        df = pd.DataFrame(dados_partidas)
        status_finalizada = StatusPartida.FINALIZADA.value
        df = df[(df['status'] == status_finalizada) & 
                (df['placar_time_da_casa'].notna()) & 
                (df['placar_time_visitante'].notna())].copy()
        
        df_limpo = df

        df_limpo['gols_total'] = df_limpo['placar_time_da_casa'] + df_limpo['placar_time_visitante']
        media_gols = df_limpo['gols_total'].mean()

        top_5_series = df_limpo['time_vencedor'].value_counts().head(5)
        
        selecoes_consolidadas = []
        for selecao, vits in top_5_series.items():
            if selecao:
                selecoes_consolidadas.append(
                    SelectionStats(nome_selecao=str(selecao), vitorias=int(vits))
                )
        logger.info(f"Processamento Pandas concluído. Média de gols: {media_gols:.2f}")
        return selecoes_consolidadas, media_gols
import uuid
from adapters.api.football_api import HttpMatchRepository
from adapters.scraper.playwright_impl import PlaywrightRankingScraper
from adapters.database.postgres_impl import PostgreSqlSelectionRepository, PostgreSqlPipelineLogRepository
from adapters.llm.openai_client import OpenAICompatibleLLMClient
from core.use_cases.process_matches import ProcessMatchesUseCase
from core.use_cases.scrape_ranking import ScrapeRankingUseCase
from core.use_cases.merge_persist import MergeAndPersistUseCase
from core.use_cases.generate_llm_insight import GenerateLLMInsightUseCase
from core.entities.log import PipelineLog
from config.logging_config import logger

def main():
    id_execucao = str(uuid.uuid4())
    logger.info("=" * 75)
    logger.info(f"INICIANDO PIPELINE DE INTEGRACAO")
    logger.info(f"EXECUTION ID: {id_execucao}")
    logger.info("=" * 75)
    
    try:
        # 1. Setup dos Repositórios (Adaptadores)
        match_repo = HttpMatchRepository()
        db_stats_repo = PostgreSqlSelectionRepository()
        db_log_repo = PostgreSqlPipelineLogRepository(db_stats_repo)
        scraper = PlaywrightRankingScraper()
        llm_client = OpenAICompatibleLLMClient()
        
        # 2. Setup dos Casos de Uso (Core)
        process_matches_uc = ProcessMatchesUseCase(match_repo)
        scrape_ranking_uc = ScrapeRankingUseCase(scraper)
        merge_uc = MergeAndPersistUseCase(db_stats_repo)
        generate_insight_uc = GenerateLLMInsightUseCase(db_stats_repo, llm_client)
        
        # --- PASSO A: Ingestão de Partidas ---
        logger.info("\n" + "-" * 75)
        logger.info("[PASSO 1] Ingestão de Partidas Real-Time & Limpeza (Pandas)")
        logger.info("-" * 75)
        top_vitorias, media_gols = process_matches_uc.execute()
        db_log_repo.write_log(PipelineLog(
            id_execucao=id_execucao, 
            passo="PROCESSAMENTO_PARTIDAS", 
            nivel="INFO", 
            mensagem=f"Média de gols calculada: {media_gols:.2f}"
        ))
        
        # --- PASSO B: Automação Web (Scraping) ---
        logger.info("\n" + "-" * 75)
        logger.info("[PASSO 2] Automação de Raspagem de Rankings FIFA (Playwright)")
        logger.info("-" * 75)
        ranking_real = scrape_ranking_uc.execute()
        db_log_repo.write_log(PipelineLog(
            id_execucao=id_execucao, 
            passo="SCRAPING_RANKING", 
            nivel="INFO", 
            mensagem=f"Raspagem concluída. {len(ranking_real)} seleções coletadas."
        ))
        
        # --- PASSO C: Merge & Persistência ---
        logger.info("\n" + "-" * 75)
        logger.info("[PASSO 3] Cruzamento de Fontes (Outer Join) & Persistência Idempotente")
        logger.info("-" * 75)
        dados_consolidados = merge_uc.execute(top_vitorias, ranking_real)
        db_log_repo.write_log(PipelineLog(
            id_execucao=id_execucao, 
            passo="PERSISTENCIA_DADOS", 
            nivel="INFO", 
            mensagem=f"Dados persistidos com sucesso. {len(dados_consolidados)} registros processados."
        ))

        # --- PASSO D: Geração de Insights com LLM ---
        logger.info("\n" + "-" * 75)
        logger.info("[PASSO 4] Análise Esportiva de Alta Confiabilidade (IA / LLM)")
        logger.info("-" * 75)
        insight = generate_insight_uc.execute()
        db_log_repo.write_log(PipelineLog(
            id_execucao=id_execucao, 
            passo="GERACAO_INSIGHTS", 
            nivel="INFO", 
            mensagem="Insights gerados e exportados para arquivo."
        ))
        
        # --- EXIBIÇÃO DE RESULTADOS ---
        logger.info("\n" + "=" * 75)
        logger.info("=== PIPELINE FINALIZADO COM SUCESSO ===")
        logger.info(f"Média de gols de todas as partidas: {media_gols:.2f}")
        logger.info("TABELA CONSOLIDADA SALVA NO BANCO (PostgreSQL)")
        logger.info("-" * 75)
        for s in dados_consolidados:
            logger.info(f"Seleção: {s.nome_selecao:<15} | Vitórias: {s.vitorias:<3} | Pontos Ranking: {str(s.pontos):<8}")
        logger.info("-" * 75)
        
        logger.info("\n=== INSIGHT ANALÍTICO DA IA ===")
        logger.info(f"\n{insight}")
        logger.info("=" * 75 + "\n")
            
    except Exception as e:
        logger.error(f"FALHA CRÍTICA NO PIPELINE: {e}", exc_info=True)
        db_log_repo.write_log(PipelineLog(
            id_execucao=id_execucao, 
            passo="PIPELINE_ERROR", 
            nivel="ERROR", 
            mensagem=f"Falha na execução: {str(e)}"
        ))

if __name__ == "__main__":
    main()

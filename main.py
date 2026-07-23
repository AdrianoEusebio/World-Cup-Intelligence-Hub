import uuid
from adapters.api.local_json import LocalJsonMatchRepository
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
    logger.info(f"Iniciando Pipeline de Inteligência da Copa do Mundo (ID: {id_execucao})...")
    
    try:
        # 1. Setup dos Repositórios (Adaptadores)
        match_repo = LocalJsonMatchRepository()
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
        logger.info("[PASSO A] Iniciando processamento analítico das partidas...")
        top_vitorias, media_gols = process_matches_uc.execute()
        db_log_repo.write_log(PipelineLog(
            id_execucao=id_execucao, 
            passo="PROCESSAMENTO_PARTIDAS", 
            nivel="INFO", 
            mensagem=f"Média de gols calculada: {media_gols:.2f}"
        ))
        
        # --- PASSO B: Automação Web (Scraping) ---
        logger.info("[PASSO B] Iniciando raspagem do ranking FIFA ao vivo...")
        ranking_real = scrape_ranking_uc.execute()
        db_log_repo.write_log(PipelineLog(
            id_execucao=id_execucao, 
            passo="SCRAPING_RANKING", 
            nivel="INFO", 
            mensagem=f"Raspagem concluída. {len(ranking_real)} seleções coletadas."
        ))
        
        # --- PASSO C: Merge & Persistência ---
        logger.info("[PASSO C] Executando merge analítico e persistência no PostgreSQL...")
        dados_consolidados = merge_uc.execute(top_vitorias, ranking_real)
        db_log_repo.write_log(PipelineLog(
            id_execucao=id_execucao, 
            passo="PERSISTENCIA_DADOS", 
            nivel="INFO", 
            mensagem=f"Dados persistidos com sucesso. {len(dados_consolidados)} registros processados."
        ))

        # --- PASSO D: Geração de Insights com LLM ---
        logger.info("[PASSO D] Iniciando geração de insights com IA...")
        insight = generate_insight_uc.execute()
        db_log_repo.write_log(PipelineLog(
            id_execucao=id_execucao, 
            passo="GERACAO_INSIGHTS", 
            nivel="INFO", 
            mensagem="Insights gerados e exportados para arquivo."
        ))
        
        # --- EXIBIÇÃO DE RESULTADOS ---
        logger.info("=== PIPELINE EXECUTADO COM SUCESSO ===")
        logger.info(f"Média de gols do campeonato: {media_gols:.2f}")
        logger.info("=== LEITURA DE DADOS UNIFICADOS SALVOS NO BANCO ===")
        for s in dados_consolidados:
            logger.info(f"Seleção: {s.nome_selecao} | Vitórias: {s.vitorias} | Pontos Ranking: {s.pontos}")
        
        logger.info("\n=== INSIGHT GERADO PELA IA ===")
        logger.info(f"\n{insight}")
            
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

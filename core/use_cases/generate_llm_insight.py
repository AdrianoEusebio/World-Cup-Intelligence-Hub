from pathlib import Path
from adapters.llm.interfaces import LLMClient
from adapters.database.interfaces import SelectionStatsRepository
from config.settings import settings
from config.logging_config import logger

class GenerateLLMInsightUseCase:
    """Caso de uso responsável por buscar os dados consolidados do banco, gerar insights e salvar no arquivo txt."""

    def __init__(self, stats_repo: SelectionStatsRepository, llm_client: LLMClient):
        self.stats_repo = stats_repo
        self.llm_client = llm_client
        self.base_dir = Path(__file__).resolve().parent.parent.parent

    def execute(self) -> str:
        logger.info("Executando caso de uso de geração de insights com LLM...")

        top_3 = self.stats_repo.get_top_3()
        if not top_3:
            logger.warning("Nenhum dado de seleção encontrado no banco. Não há dados para enviar à LLM.")
            return ""

        linhas_dados = []
        for i, s in enumerate(top_3, 1):
            pontos_str = f"{s.pontos:.2f}" if s.pontos is not None else "Sem ranking"
            linhas_dados.append(f"{i}º Lugar: {s.nome_selecao} - {s.vitorias} vitórias, {pontos_str} pontos no ranking.")

        dados_texto = "\n".join(linhas_dados)
        
        prompt = settings.LLM_PROMPT_TEMPLATE.format(dados_texto=dados_texto)

        insight = self.llm_client.generate_insight(prompt)

        caminho_arquivo = self.base_dir / settings.CAMINHO_EXPORT_INSIGHTS
        caminho_arquivo.parent.mkdir(exist_ok=True)
        
        try:
            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                f.write(insight)
                
            logger.info(f"Insight de IA exportado com sucesso em: {caminho_arquivo}")
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo de insights: {e}")

        return insight

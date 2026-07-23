from openai import OpenAI
from adapters.llm.interfaces import LLMClient
from config.settings import settings
from config.logging_config import logger

class OpenAICompatibleLLMClient(LLMClient):
    """Adaptador de LLM que suporta qualquer provedor compatível com o padrão OpenAI (OpenAI, DeepSeek, Ollama, etc.)."""

    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_API_BASE_URL
        self.model = settings.LLM_MODEL

    def generate_insight(self, prompt: str) -> str:
        # TDD CT-08: Se a chave estiver vazia, ativa o fallback com mock silencioso
        if not self.api_key or not self.api_key.strip():
            logger.warning("LLM_API_KEY não configurada no .env. Ativando MockLLMClient silenciosamente.")
            return self._obter_insight_mock()

        logger.info(f"Enviando dados para a LLM ({self.model}) via API...")
        try:
            # Inicializa o cliente oficial da OpenAI parametrizado
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um analista especialista em dados esportivos da Copa do Mundo."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            insight = response.choices[0].message.content
            logger.info("Insight gerado pela LLM com sucesso.")
            return insight
            
        except Exception as e:
            logger.error(f"Falha na comunicação com a API da LLM: {e}. Acionando fallback mockado.")
            return self._obter_insight_mock()

    def _obter_insight_mock(self) -> str:
        """Retorna uma análise simulada realista de fallback."""
        return (
            "=== World Cup Intelligence Hub - Análise de IA (Simulada) ===\n\n"
            "Com base nas estatísticas consolidadas das partidas recentes e nos dados do ranking mundial, "
            "as três seleções com maior probabilidade de sucesso no próximo torneio são:\n\n"
            "1. Argentina: Mantém uma pontuação altíssima no ranking e demonstra consistência ofensiva.\n"
            "2. France: Equipe taticamente disciplinada, com alta média de gols por partida.\n"
            "3. Brazil: Maior volume de vitórias nos confrontos simulados, despontando como forte candidata.\n\n"
            "Previsão: A disputa final tende a concentrar-se entre Argentina e França, com o Brasil correndo por fora "
            "com alto poder de fogo."
        )

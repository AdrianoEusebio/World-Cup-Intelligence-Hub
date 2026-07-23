from abc import ABC, abstractmethod

class LLMClient(ABC):
    """Interface abstrata (contrato) para integração com IA (LLMs)."""

    @abstractmethod
    def generate_insight(self, prompt: str) -> str:
        """Envia o prompt contendo as seleções e retorna a análise da LLM."""
        pass

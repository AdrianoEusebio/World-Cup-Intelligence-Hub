from abc import ABC, abstractmethod
from core.entities.stats import SelectionStats
from core.entities.log import PipelineLog

class SelectionStatsRepository(ABC):
    """Interface abstrata para salvar estatísticas consolidadas."""

    @abstractmethod
    def save(self, stats: SelectionStats) -> None:
        """Salva ou atualiza as estatísticas de uma seleção."""
        pass

    @abstractmethod
    def get_top_3(self) -> list[SelectionStats]:
        """Obtém as 3 melhores seleções baseando-se no critério de vitórias e pontos."""
        pass


class PipelineLogRepository(ABC):
    """Interface abstrata para persistência de logs de execução do pipeline."""

    @abstractmethod
    def write_log(self, log_entry: PipelineLog) -> None:
        """Grava uma entrada de log de execução no banco de dados PostgreSQL."""
        pass

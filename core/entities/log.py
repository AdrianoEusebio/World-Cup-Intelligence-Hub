from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class PipelineLog:
    """Entidade que representa um registro de log de execução no banco de dados."""
    id_execucao: str
    passo: str
    nivel: str
    mensagem: str
    id: Optional[int] = None
    timestamp: Optional[datetime] = None

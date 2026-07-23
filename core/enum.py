from enum import Enum

class StatusPartida(Enum):
    AGENDADA = "AGENDADA"
    FINALIZADA = "FINALIZADA"
    CANCELADA = "CANCELADA"
    INDEFINIDO = "INDEFINIDO"

class ResultadoPartida(Enum):
    HOME_WINS = "HOME_WINS"
    AWAY_WINS = "AWAY_WINS"
    DRAW = "DRAW"
    UNDEFINED = "UNDEFINED"
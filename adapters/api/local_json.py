import json
from pathlib import Path
from adapters.api.interfaces import MatchRepository
from core.entities.match import Match
from config.settings import settings
from config.logging_config import logger

class LocalJsonMatchRepository(MatchRepository):

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.arquivo_path = self.base_dir / settings.ARQUIVO_PARTIDAS_MOCK
    
    def get_all_matches(self) -> list[Match]:
        logger.info(f"Lendo partidas do arquivo local: {self.arquivo_path}")

        if not self.arquivo_path.exists():
            logger.error(f"Arquivo de mock não encontrado: {self.arquivo_path}")
            raise FileNotFoundError(f"Arquivo não encontrado: {self.arquivo_path}")

        with open(self.arquivo_path, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        partidas_mapeadas = []
        matches_list = dados.get("matches", [])
        
        for m in matches_list:
            score_data = m.get("score") or {}
            full_time = score_data.get("fullTime") or {}
            
            placar_casa = full_time.get("home")
            placar_visitante = full_time.get("away")
            
            partida = Match(
                id=m.get("id"),
                time_da_casa=m["homeTeam"]["name"],
                time_visitante=m["awayTeam"]["name"],
                placar_time_da_casa=int(placar_casa) if placar_casa is not None else None,
                placar_time_visitante=int(placar_visitante) if placar_visitante is not None else None,
                status="FINALIZADA" if m["status"] == "FINISHED" else m["status"]
            )
            partidas_mapeadas.append(partida)
        logger.info(f"Sucesso! {len(partidas_mapeadas)} partidas carregadas e traduzidas.")
        return partidas_mapeadas
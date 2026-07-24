import requests
from adapters.api.interfaces import MatchRepository
from adapters.api.local_json import LocalJsonMatchRepository
from core.entities.match import Match
from config.settings import settings
from config.logging_config import logger

class HttpMatchRepository(MatchRepository):

    def __init__(self):
        self.local_repo = LocalJsonMatchRepository()
        self.api_key = settings.FOOTBALL_API_KEY
        self.url = settings.URL_API_PARTIDAS

    def get_all_matches(self) -> list[Match]:
        if not self.api_key or not self.api_key.strip():
            logger.warning("FOOTBALL_API_KEY não configurada no .env. Ativando fallback do JSON local.")
            return self.local_repo.get_all_matches()

        logger.info(f"Consumindo partidas da API oficial Football-Data.org na URL: {self.url}")
        
        try:
            headers = {"X-Auth-Token": self.api_key}
            response = requests.get(self.url, headers=headers, timeout=10)
            req_available = response.headers.get("X-Requests-Available-Minute")
            req_reset = response.headers.get("X-RequestCounter-Reset")

            if req_available is not None:
                logger.info(f"API Football: {req_available} requisições restantes neste minuto. Reseta em {req_reset}s.")

            if response.status_code == 429:
                logger.warning("Limite de requisições excedido na API de Futebol (Status 429). Acionando fallback do JSON local.")
                return self.local_repo.get_all_matches()

            if response.status_code != 200:
                logger.warning(f"Erro ao acessar API de Futebol (Status {response.status_code}). Acionando fallback do JSON local.")
                return self.local_repo.get_all_matches()

            dados = response.json()
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

            logger.info(f"Sucesso! {len(partidas_mapeadas)} partidas carregadas e traduzidas da API oficial.")
            return partidas_mapeadas

        except Exception as e:
            logger.warning(f"Falha de conexão com a API de Futebol (Erro: {e}). Acionando fallback do JSON local.")
            return self.local_repo.get_all_matches()

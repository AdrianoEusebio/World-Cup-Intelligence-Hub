import os
import json
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

class Settings:

    def __init__(self):
        config_path = BASE_DIR / "config.json"
        db_port_raw = os.getenv("DB_PORT")
        if not config_path.exists():
            raise FileNotFoundError("Arquivo de configuração não encontrado!")

        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        
        # carregar campos da config.json
        self.URL_RANKING_FIFA: str = config_data["URL_RANKING_FIFA"]
        self.ARQUIVO_PARTIDAS_MOCK: str = config_data["ARQUIVO_PARTIDAS_MOCK"]
        self.URL_API_PARTIDAS: str = config_data.get("URL_API_PARTIDAS", "https://api.football-data.org/v4/competitions/WC/matches")
        self.CAMINHO_EXPORT_CSV: str = config_data["CAMINHO_EXPORT_CSV"]
        self.CAMINHO_EXPORT_INSIGHTS: str = config_data["CAMINHO_EXPORT_INSIGHTS"]
        self.TEMPO_DE_ESPERA: int = config_data["TEMPO_DE_ESPERA"]

        # Índices de calibração do scraper (Requisito 4)
        self.SCRAPER_INDICE_RANQUEAMENTO: int = config_data.get("SCRAPER_INDICE_RANQUEAMENTO", 0)
        self.SCRAPER_INDICE_SELECAO: int = config_data.get("SCRAPER_INDICE_SELECAO", 1)
        self.SCRAPER_INDICE_PONTOS: int = config_data.get("SCRAPER_INDICE_PONTOS", 2)

        # Prompts da LLM carregados do config.json
        self.LLM_SYSTEM_PROMPT: str = config_data.get("LLM_SYSTEM_PROMPT", " ")
        self.LLM_PROMPT_TEMPLATE: str = config_data.get("LLM_PROMPT_TEMPLATE", "Dados:\n{dados_texto}")

        # carregar .env
        self.DB_HOST: str = os.getenv("DB_HOST", "localhost")
        self.DB_PORT: int = int(db_port_raw) if db_port_raw and db_port_raw.strip() else 5432
        self.DB_NAME: str = os.getenv("DB_NAME", "worldcup_db")
        self.DB_USER: str = os.getenv("DB_USER", "postgres")
        self.DB_PASSWORD: str = os.getenv("DB_PASSWORD", "") 

        self.LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
        self.LLM_API_BASE_URL: str = os.getenv("LLM_API_BASE_URL", "https://api.openai.com/v1")
        self.LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
        
        self.ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
        self.FOOTBALL_API_KEY: str = os.getenv("FOOTBALL_API_KEY", "")

# instanciando settings
settings = Settings()
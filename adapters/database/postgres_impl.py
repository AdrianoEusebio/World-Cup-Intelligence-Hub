import psycopg2
from adapters.database.interfaces import SelectionStatsRepository, PipelineLogRepository
from core.entities.stats import SelectionStats
from core.entities.log import PipelineLog
from config.settings import settings
from config.logging_config import logger

class PostgreSqlSelectionRepository(SelectionStatsRepository):
    """Implementação do rep de estatísticas usando PostgreSQL."""

    def __init__(self):
        self.conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        self._criar_tabelas()

    def _criar_tabelas(self):
        criar_stats_table = """
        CREATE TABLE IF NOT EXISTS estatisticas_selecoes (
            nome_selecao VARCHAR(100) PRIMARY KEY,
            vitorias INTEGER NOT NULL,
            pontos NUMERIC
        );
        """
        
        criar_logs_table = """
        CREATE TABLE IF NOT EXISTS logs_execucao (
            id SERIAL PRIMARY KEY,
            id_execucao VARCHAR(100) NOT NULL,
            passo VARCHAR(100) NOT NULL,
            nivel VARCHAR(20) NOT NULL,
            mensagem TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        with self.conn.cursor() as cursor:
            cursor.execute(criar_stats_table)
            cursor.execute(criar_logs_table)
            self.conn.commit()
        logger.info("Tabelas do PostgreSQL verificadas/criadas com sucesso.")

    def save(self, stats: SelectionStats) -> None:
        query = """
        INSERT INTO estatisticas_selecoes (nome_selecao, vitorias, pontos)
        VALUES (%s, %s, %s)
        ON CONFLICT (nome_selecao)
        DO UPDATE SET 
            vitorias = EXCLUDED.vitorias,
            pontos = EXCLUDED.pontos;
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query, (stats.nome_selecao, stats.vitorias, stats.pontos))
            self.conn.commit()
        logger.info(f"Dados salvos/atualizados para a seleção: {stats.nome_selecao}")

    def get_top_3(self) -> list[SelectionStats]:
        query = """
        SELECT nome_selecao, vitorias, pontos
        FROM estatisticas_selecoes
        ORDER BY vitorias DESC, pontos DESC NULLS LAST
        LIMIT 3;
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            
        top_3 = []
        for r in rows:
            top_3.append(
                SelectionStats(nome_selecao=r[0], vitorias=r[1], pontos=float(r[2]) if r[2] is not None else None)
            )
        return top_3


class PostgreSqlPipelineLogRepository(PipelineLogRepository):

    def __init__(self, repository: PostgreSqlSelectionRepository):
        self.conn = repository.conn

    def write_log(self, log_entry: PipelineLog) -> None:

        query = """
            INSERT INTO logs_execucao (id_execucao, passo, nivel, mensagem)
            VALUES (%s, %s, %s, %s);
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query, (
                log_entry.id_execucao,
                log_entry.passo,
                log_entry.nivel,
                log_entry.mensagem
            ))
            self.conn.commit()
        logger.info(f"Log do passo [{log_entry.passo}] salvo no banco de dados.")

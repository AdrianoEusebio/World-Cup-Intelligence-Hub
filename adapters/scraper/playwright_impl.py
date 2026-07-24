import csv
from pathlib import Path
from playwright.sync_api import sync_playwright
from adapters.scraper.interfaces import RankingScraper
from core.entities.ranking import RankingEntry
from config.settings import settings
from config.logging_config import logger

class PlaywrightRankingScraper(RankingScraper):
    """Implementação concreta de raspagem usando a biblioteca Playwright."""

    def fetch_top_10(self, url: str) -> list[RankingEntry]:
        logger.info(f"Iniciando raspagem do ranking FIFA na URL: {url}")
        ranking_entries = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            try:
                page.goto(url, timeout=settings.TEMPO_DE_ESPERA)
                
                # Aguarda o elemento da tabela carregar na tela
                page.wait_for_selector("table", timeout=15000)

                # Busca as linhas da tabela (tbody tr)
                rows = page.query_selector_all("table tbody tr")
                if not rows:
                    rows = page.query_selector_all("table tr")

                logger.info(f"Encontradas {len(rows)} linhas na tabela de ranking.")
                
                count = 0
                for row in rows:
                    if count >= 10:
                        break

                    cells = row.query_selector_all("td")
                    
                    max_indice_necessario = max(
                        settings.SCRAPER_INDICE_RANQUEAMENTO,
                        settings.SCRAPER_INDICE_SELECAO,
                        settings.SCRAPER_INDICE_PONTOS
                    )

                    if len(cells) <= max_indice_necessario:
                        continue

                    textos_limpos = [c.inner_text().strip() for c in cells]

                    if len(textos_limpos) > max_indice_necessario:
                        try:
                            raw_ranqueamento = textos_limpos[settings.SCRAPER_INDICE_RANQUEAMENTO]
                            pos_str = "".join(filter(str.isdigit, raw_ranqueamento))
                            ranqueamento = int(pos_str) if pos_str else (count + 1)

                            raw_selecao = textos_limpos[settings.SCRAPER_INDICE_SELECAO]
                            nome_selecao = raw_selecao.split("\n")[0].strip()

                            raw_pontos = textos_limpos[settings.SCRAPER_INDICE_PONTOS]
                            pontos_str = raw_pontos.replace(",", "").strip()
                            pontos = float(pontos_str)

                            entry = RankingEntry(
                                ranqueamento=ranqueamento,
                                nome_selecao=nome_selecao,
                                pontos=pontos
                            )
                            ranking_entries.append(entry)
                            count += 1

                        except Exception as parse_err:
                            logger.warning(f"Erro ao processar linha {count + 1}: {parse_err}. Dados: {textos_limpos}")
                            continue

            except Exception as e:
                logger.warning(f"Falha ao raspar ranking FIFA (Erro: {e}). Acionando fallback mockado.")
                ranking_entries = self._obter_ranking_mock()

            finally:
                browser.close()

        self._exportar_para_csv(ranking_entries)
        
        return ranking_entries

    def _exportar_para_csv(self, entries: list[RankingEntry]):

        csv_path = Path(__file__).resolve().parent.parent.parent / settings.CAMINHO_EXPORT_CSV
        csv_path.parent.mkdir(exist_ok=True)

        logger.info(f"Exportando Top 10 do ranking para CSV em: {csv_path}")

        try:
            with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Ranqueamento", "Seleção", "Pontuação"])

                for e in entries:
                    writer.writerow([e.ranqueamento, e.nome_selecao, e.pontos])

            logger.info("CSV de ranking exportado com sucesso!")
        except Exception as e:
            logger.error(f"Falha ao exportar CSV: {e}")

    def _obter_ranking_mock(self) -> list[RankingEntry]:
        """Dados mockados de contingência"""
        return [
            RankingEntry(ranqueamento=1, nome_selecao="Argentina", pontos=1860.14),
            RankingEntry(ranqueamento=2, nome_selecao="France", pontos=1840.76),
            RankingEntry(ranqueamento=3, nome_selecao="Belgium", pontos=1795.38),
            RankingEntry(ranqueamento=4, nome_selecao="England", pontos=1794.90),
            RankingEntry(ranqueamento=5, nome_selecao="Brazil", pontos=1784.09),
            RankingEntry(ranqueamento=6, nome_selecao="Portugal", pontos=1748.11),
            RankingEntry(ranqueamento=7, nome_selecao="Netherlands", pontos=1742.29),
            RankingEntry(ranqueamento=8, nome_selecao="Spain", pontos=1727.50),
            RankingEntry(ranqueamento=9, nome_selecao="Italy", pontos=1718.82),
            RankingEntry(ranqueamento=10, nome_selecao="Croatia", pontos=1717.57)
        ]

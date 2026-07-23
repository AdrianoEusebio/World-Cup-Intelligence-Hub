# Test Design Document (TDD)
## Especificações de Teste - World Cup Intelligence Hub

Este documento define a estratégia, cenários e casos de teste do sistema, assegurando resiliência, corretude analítica e robustez conforme os requisitos do desafio FPFtech. Os testes cobrem desde testes unitários das regras de negócio até testes de integração e cenários de falhas (Chaos/Failure Testing).

---

## 1. Estratégia de Testes

Para garantir os princípios de **Clean Architecture** e **SOLID**, a estratégia de testes é dividida em três níveis:
1.  **Testes Unitários (Core):** Validam a lógica pura de negócios (regras do Pandas, transformações, tratamento de dados) usando dublês de teste (Mocks) para repositórios externos. Não dependem de internet ou banco de dados.
2.  **Testes de Integração (Adapters):** Validam a integração com os serviços externos reais (Playwright contra páginas reais, queries SQL contra o PostgreSQL no Docker, e chamadas HTTP).
3.  **Testes de Resiliência (Fallback):** Simulam explicitamente a indisponibilidade ou falhas na rede de APIs externas e LLMs, garantindo que o sistema caia de pé (*graceful degradation*).

---

## 2. Especificação dos Cenários de Teste

### 📊 Grupo A: Ingestão de Dados & Pandas (Tarefa 1)

#### CT-01: Processamento Feliz (Caminho Padrão)
*   **Objetivo:** Garantir que o Pandas limpe dados, calcule a média de gols e liste as 5 melhores seleções corretamente a partir de uma massa de dados íntegra.
*   **Entrada:** Lista de partidas com alguns jogos finalizados (`FINISHED`) e gols válidos.
*   **Resultado Esperado:** DataFrame limpo, média de gols exata matematicamente e lista ordenada com as 5 seleções com mais vitórias.

#### CT-02: Resiliência da API de Partidas (Fallback Silencioso)
*   **Objetivo:** Verificar se, ao falhar a API HTTP externa, o sistema faz o fallback automático para os dados mockados sem quebrar o pipeline.
*   **Ação de Teste:** Simular queda de rede (ex: `ConnectionError` ou status `500` na API pública).
*   **Resultado Esperado:** 
    1. Gravação de log silencioso nível `WARNING` indicando a falha da API e início do fallback.
    2. Leitura com sucesso do arquivo `data/matches_mock.json`.
    3. Pipeline prossegue sem interrupção.

#### CT-03: Dados Inconsistentes e Nulos
*   **Objetivo:** Garantir que partidas canceladas, sem placar (`NaN`) ou com dados corrompidos sejam completamente limpas pelo Pandas.
*   **Entrada:** Dados contendo partidas com status `CANCELLED`, `POSTPONED`, placares vazios (`null`) ou strings no lugar de números.
*   **Resultado Esperado:** Essas linhas devem ser descartadas do processamento e não devem impactar a média de gols ou a contagem de vitórias.

#### CT-04: Massa de Dados Vazia
*   **Objetivo:** Validar o comportamento do sistema quando não houver partidas para processar.
*   **Entrada:** JSON local ou retorno da API vazio `[]`.
*   **Resultado Esperado:** O sistema não deve quebrar (ex: divisão por zero ao calcular a média). Deve registrar um log do tipo `INFO` ou `WARNING` informando "Nenhuma partida para processar" e retornar estatísticas zeradas de forma limpa.

---

### 🌐 Grupo B: Automação Web & Scraper (Tarefa 2)

#### CT-05: Extração do Top 10 com Sucesso
*   **Objetivo:** Assegurar que o Playwright navegue até a URL alvo, localize a tabela de ranking e extraia exatamente 10 linhas contendo (Nome, Pontuação).
*   **Resultado Esperado:** Geração de um arquivo CSV válido e estruturado, e retorno de uma lista contendo exatamente 10 objetos `RankingEntry`.

#### CT-06: Calibração de Navegador e Páginas (Agnóstico)
*   **Objetivo:** Validar que a automação consegue rodar em diferentes navegadores (Chromium, Firefox, WebKit) dependendo apenas do `config.json`.
*   **Ação de Teste:** Alterar as chaves de configuração de navegador e seletores CSS em `config.json`.
*   **Resultado Esperado:** O script deve instanciar o browser correto especificado na configuração e buscar os seletores parametrizados.

#### CT-07: Bloqueio de Rede / Erro de Carregamento (Timeout)
*   **Objetivo:** Testar o comportamento do scraper caso o site da FIFA esteja instável ou bloqueie a requisição (ex: Cloudflare / Captcha).
*   **Ação de Teste:** Simular timeout na requisição ou página indisponível.
*   **Resultado Esperado:** 
    1. O Playwright estoura o tempo limite configurado (`PLAYWRIGHT_TIMEOUT`).
    2. O caso de uso intercepta o erro, registra a falha no banco de dados na tabela de logs e interrompe a execução com um erro controlado, em vez de deixar o processo travado indefinidamente.

---

### 💾 Grupo C: Persistência e Idempotência (Tarefa 3)

#### CT-08: Banco de Dados Indisponível na Inicialização (Docker Start Sync)
*   **Objetivo:** Prevenir que a aplicação quebre se o contêiner do PostgreSQL demorar mais para subir do que a própria aplicação Python.
*   **Ação de Teste:** Iniciar o pipeline com o serviço do banco ainda em inicialização.
*   **Resultado Esperado:** A aplicação deve implementar um mecanismo de *retry* (ex: 5 tentativas com intervalo de 2s) aguardando a conexão do Postgres se estabelecer antes de falhar.

#### CT-09: Garantia de Idempotência (Execuções Múltiplas)
*   **Objetivo:** Assegurar que rodar o script várias vezes no mesmo dia não duplique registros ou gere lixo no banco.
*   **Ação de Teste:** Executar o pipeline de ponta a ponta 3 vezes consecutivas com os mesmos dados.
*   **Resultado Esperado:** 
    1. A tabela de estatísticas de seleções deve conter exatamente o mesmo número de registros (ex: 10).
    2. Os dados de vitórias e ranking devem ser atualizados (*upsert*), nunca duplicados.
    3. A tabela de logs históricos deve registrar 3 execuções distintas com `run_id` diferentes.

#### CT-10: Integridade do Cruzamento (Merge)
*   **Objetivo:** Garantir que o cruzamento de dados ocorra apenas entre seleções coincidentes.
*   **Entrada:** Módulo 1 retorna (Brasil, Argentina). Módulo 2 retorna (Brasil, França).
*   **Resultado Esperado:** O banco deve salvar a união correta:
    *   Brasil: possui vitórias da API e pontos do scraping.
    *   Argentina: possui vitórias da API e pontos nulos/zero.
    *   França: possui pontos do scraping e vitórias nulas/zero.

---

### 🤖 Grupo D: Integração com LLM (Tarefa 4)

#### CT-11: Resiliência da LLM (Fallback Silencioso)
*   **Objetivo:** Garantir que o pipeline seja concluído com êxito mesmo se a chave da LLM estiver ausente ou a API estiver indisponível.
*   **Ação de Teste:** Deixar `LLM_API_KEY` vazia no `.env` ou simular falha HTTP 429/500 na chamada da API.
*   **Resultado Esperado:** 
    1. Log nível `WARNING` indicando falha na LLM ou chave ausente.
    2. Acionamento do `MockLLMClient`.
    3. Geração do arquivo `insights_world_cup.txt` preenchido com uma análise estruturada estática (mock) bem-apresentada.
    4. Pipeline finalizado com sucesso.

---

## 3. Matriz de Cobertura de Erros

Esta matriz mapeia possíveis falhas do sistema operacional/infraestrutura e como a aplicação deve reagir:

| ID Falha | Componente Afetado | Causa Raiz | Ação Corretiva do Sistema |
| :--- | :--- | :--- | :--- |
| **FL-01** | Configuração | Variável crítica ausente no `.env` | O script valida na inicialização via `config/settings.py` e interrompe a execução com mensagem amigável antes de iniciar o pipeline. |
| **FL-02** | Banco de Dados | Senha do Postgres inválida no `.env` | Gravação de log `CRITICAL` e encerramento do script informando erro de autenticação. |
| **FL-03** | Automação Web | Falta de navegadores instalados no Docker | O Dockerfile será configurado para rodar `playwright install --with-deps` garantindo todas as dependências do sistema operacional. |
| **FL-04** | LLM | Cota da API expirada (Erro 429) | Captura de exceção HTTP, log de aviso e acionamento automático do fallback mockado. |
| **FL-05** | Persistência | Nome de seleção muito longo ou dados inválidos | Validação dos dados nas classes do `core/entities` antes do envio ao repositório SQL. |

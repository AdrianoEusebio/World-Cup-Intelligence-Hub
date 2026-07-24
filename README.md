# 🏆 World Cup Intelligence Hub

O **World Cup Intelligence Hub** é um pipeline automatizado de inteligência de dados construído em **Python** para coletar, unificar, salvar e analisar dados históricos e estatísticos das Copas do Mundo da FIFA.

O projeto foi inteiramente desenhado seguindo os princípios de **Clean Architecture** (Arquitetura Limpa), **SOLID**, padrões de projeto resilientes e conteinerização completa com **Docker**.

---

## 🛠️ Tecnologias Utilizadas

*   **Linguagem:** Python 3.11
*   **Manipulação de Dados:** Pandas
*   **Automação Web (Scraping):** Playwright
*   **Banco de Dados:** PostgreSQL 15 (Dockerizado)
*   **Conexão de Banco:** Psycopg2
*   **Inteligência Artificial (LLM):** OpenAI SDK (compatível com Groq, Gemini, DeepSeek e OpenAI)
*   **Testes Automatizados:** Unittest (Nativo)

---

## 🏗️ Arquitetura e Decisões de Design

A estrutura de diretórios separa rigidamente a lógica de negócio (Core) dos detalhes de infraestrutura (Adapters):

```text
fpf_tech/
├── config/              # Configurações dinâmicas e leitura do .env
├── core/
│   ├── entities/        # Entidades puras de domínio (Match, SelectionStats, etc.)
│   ├── use_cases/       # Casos de uso de negócio (ProcessMatches, ScrapeRanking, etc.)
│   └── utils/           # Normalizadores e sanitizadores de dados
├── adapters/
│   ├── api/             # Ingestão de API de partidas com fallback resiliente
│   ├── database/        # Persistência idempotente e logs no PostgreSQL
│   ├── scraper/         # Robô Playwright calibrável dinamicamente
│   └── llm/             # Cliente de IA compatível com padrão OpenAI
├── data/                # Diretório de arquivos gerados (CSV, JSON, TXT, Logs)
├── tests/               # Suíte completa de testes automatizados (CT-01 a CT-08)
├── main.py              # Orquestrador central do pipeline
└── docker-compose.yml   # Orquestrador de contêineres da aplicação e banco
```

### Principais Decisões Tomadas:
1.  **Repository Pattern & DIP (SOLID):** O core não conhece o banco de dados nem as APIs externas. Ele apenas consome as interfaces abstratas. Isso nos permitiu, por exemplo, mudar de provedor de IA ou alternar o repositório de partidas sem alterar nenhuma regra de negócio.
2.  **Resiliência e Fallback (Graceful Degradation):** Se a API externa de futebol falhar (rate limit ou offline), o sistema ativa o fallback para um arquivo local de mock. Se a Wikipédia/FIFA cair, o Playwright aciona um ranking de contingência. Se a chave da IA falhar, ele retorna um insight simulado realista de backup. A aplicação **nunca crasha** em produção.
3.  **Idempotência (SQL Upsert):** A tabela `estatisticas_selecoes` possui chave primária em `nome_selecao`. Inserções repetidas executam a instrução `ON CONFLICT DO UPDATE` (Upsert), garantindo que dados históricos e vitórias não sejam duplicados ao reexecutar o pipeline.
4.  **Throttling:** O leitor de API inspeciona os headers de controle de requisição (`X-Requests-Available-Minute` e `X-RequestCounter-Reset`) e emite logs informativos no console para garantir respeito aos rate limits do fornecedor.

---

## 🚀 Como Rodar o Sistema

### Pré-requisitos
*   **Docker Desktop** instalado e rodando.
*   **Python 3.10+** (caso queira rodar localmente fora do contêiner).

### Configuração do Arquivo `.env`
1.  Duplique o arquivo `.env.example` e renomeie-o para `.env`:
    ```bash
    cp .env.example .env
    ```
2.  Abra o arquivo `.env` e configure suas credenciais:
    *   `FOOTBALL_API_KEY`: Insira seu token de API do Football-Data.org.
    *   `LLM_API_KEY`: Insira sua chave do provedor de IA de preferência (Gemini, Groq, OpenAI).
    *   `LLM_API_BASE_URL` e `LLM_MODEL`: Ajuste conforme a IA que for testar (exemplo do Groq já configurado por padrão).

---

### Opção A: Execução Completa via Docker (Recomendado)

O Docker Compose sobe automaticamente o banco de dados PostgreSQL, aguarda ele estar 100% pronto (healthcheck) e depois executa a nossa aplicação Python.

1.  **Construir e rodar os contêineres:**
    ```bash
    docker-compose up --build
    ```
2.  **Parar e remover os contêineres:**
    ```bash
    docker-compose down
    ```

---

### Opção B: Execução Local (Desenvolvimento/Testes)

1.  **Criar e ativar o ambiente virtual (venv):**
    ```bash
    python -m venv venv
    # No Windows:
    venv\Scripts\activate
    # No Linux/macOS:
    source venv/bin/activate
    ```
2.  **Instalar dependências e navegadores do Playwright:**
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```
3.  **Subir apenas o Banco de Dados via Docker:**
    ```bash
    docker-compose up -d db
    ```
4.  **Executar o Pipeline:**
    ```bash
    python main.py
    ```

---

## 🧪 Como Rodar os Testes Automatizados

Com o seu ambiente virtual ativado, você pode rodar todos os testes unitários e de fallback usando o comando:

```bash
make test
```

Ou usando o comando nativo do Python:
```bash
python -m unittest discover -s tests
```

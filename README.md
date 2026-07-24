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

## 🚀 Como Rodar o Sistema (Windows e Linux)

O projeto possui um script centralizador `run.py` escrito em Python, garantindo compatibilidade e facilidade de execução tanto no **Windows** quanto no **Linux** (substituindo a necessidade de utilitários como `make`).

### Pré-requisitos
*   **Python 3.10+** instalado.
*   **Docker Desktop** (opcional, necessário apenas se quiser rodar com banco de dados em contêiner).

---

### Passo 1: Configuração Inicial do Ambiente

Abra o terminal (ou Prompt de Comando/PowerShell no Windows) na pasta raiz do projeto:

*   **Com Makefile:**
    ```bash
    make setup
    ```
*   **Sem Makefile (Windows):**
    ```bash
    python run.py setup
    ```
*   **Sem Makefile (Linux):**
    ```bash
    python3 run.py setup
    ```

**O que este comando faz automaticamente:**
1. Cria uma cópia do arquivo `.env.example` como `.env` (caso ele ainda não exista).
2. Cria o ambiente virtual Python (`venv`) — usando `uv` se estiver instalado para setup instantâneo.
3. Instala todas as dependências do `requirements.txt` dentro do `venv`.
4. Instala os binários do navegador Chromium para a execução do Playwright.

> [!IMPORTANT]
> Após o setup, abra o arquivo `.env` gerado e configure suas chaves de API (`FOOTBALL_API_KEY`, `LLM_API_KEY`, etc.), conforme necessário.

> [!TIP]
> **No Linux (Ubuntu/Debian):** Caso o Playwright acuse falta de dependências do sistema (como `libnss3`, `libasound2`, etc.) para rodar o navegador Chromium, execute o comando de instalação do Playwright com privilégios de administrador:
> * **Com venv padrão:**
>   ```bash
>   sudo venv/bin/playwright install-deps
>   ```
> * **Com uv:**
>   ```bash
>   sudo uv run playwright install-deps
>   ```

---

### Passo 2: Executar o Sistema

Você pode optar por rodar a aplicação em contêineres Docker de ponta a ponta ou executar o pipeline localmente conectado a um banco de dados Dockerizado.

#### Opção A: Execução Local com Banco Dockerizado (Recomendado)
Esse modo sobe automaticamente o container do PostgreSQL em background e roda o pipeline Python no seu ambiente local (venv), permitindo ver logs rápidos e realizar depurações com facilidade:

*   **Com Makefile (Linux / WSL):**
    ```bash
    make run-local
    ```
*   **Sem Makefile (Windows):**
    ```bash
    python run.py run-local
    ```
*   **Sem Makefile (Linux):**
    ```bash
    python3 run.py run-local
    ```

#### Opção B: Execução Completa via Docker Compose
Para rodar toda a aplicação e o banco isolados dentro de contêineres Docker:

*   **Com Makefile (Linux / WSL):**
    - Para iniciar:
      ```bash
      make compose-up
      ```
    - Para parar:
      ```bash
      make compose-down
      ```
*   **Sem Makefile (Windows):**
    - Para iniciar:
      ```bash
      python run.py compose-up
      ```
    - Para parar:
      ```bash
      python run.py compose-down
      ```

---

## 🧪 Como Rodar os Testes Automatizados

Para rodar a suíte completa de testes de forma multiplataforma:

*   **Com Makefile (Linux / WSL):**
    ```bash
    make test
    ```
*   **Sem Makefile (Windows):**
    ```bash
    python run.py test
    ```
*   **Sem Makefile (Linux):**
    ```bash
    python3 run.py test
    ```


---

## 🛠️ Resumo de Comandos (`run.py` e `Makefile`)

Se você estiver em um ambiente Linux/WSL ou tiver o `make` instalado no Windows, você pode optar por usar os atalhos simplificados do `Makefile`. Ambos executam exatamente as mesmas tarefas.

| Comando `run.py` | Atalho `Makefile` | Descrição |
| :--- | :--- | :--- |
| `python run.py setup` | `make setup` | Cria o `.env`, cria o ambiente virtual (venv), instala pacotes e o navegador Chromium. |
| `python run.py run-local` | `make run-local` | Inicia o banco de dados via Docker e executa o pipeline localmente. |
| `python run.py test` | `make test` | Executa os testes de unidade. |
| `python run.py run` | `make run` | Executa o pipeline localmente (requer banco de dados rodando previamente). |
| `python run.py compose-up` | `make compose-up` | Constrói e inicializa todo o projeto e banco em contêineres via Docker Compose. |
| `python run.py compose-down`| `make compose-down` | Para e limpa os contêineres criados pelo Docker Compose. |
| `python run.py db-start` | - | Inicia apenas o contêiner do banco de dados PostgreSQL. |
| `python run.py db-stop` | - | Para o contêiner do banco de dados. |
| - | `make clean` | Executa o `compose-down` e limpa pastas de cache e ambiente virtual local. |


---

### ⚠️ Execução Manual Tradicional (Alternativa)
Se preferir não usar o `run.py` e executar manualmente:

*   **Linux/macOS (Setup e Execução Local):**
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    playwright install chromium
    docker compose up -d db
    python main.py
    ```
*   **Windows (Setup e Execução Local):**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    playwright install chromium
    docker compose up -d db
    python main.py
    ```
*   **Rodar os testes nativamente:**
    ```bash
    python -m unittest discover -s tests
    ```


.PHONY: setup run test compose-up compose-down run-local clean

# Configura o ambiente (.env, venv/.venv, dependências e Playwright)
setup:
	python3 run.py setup

# Executa o pipeline localmente (requer banco rodando previamente)
run:
	python3 run.py run

# Executa a suíte de testes unitários
test:
	python3 run.py test

# Inicializa toda a aplicação e banco no Docker Compose
compose-up:
	python3 run.py compose-up

# Para e remove os contêineres do Docker Compose
compose-down:
	python3 run.py compose-down

# Inicializa o banco no Docker e executa o pipeline local
run-local:
	python3 run.py run-local

# Para o docker e limpa arquivos de cache e virtualenvs locais
clean:
	python3 run.py compose-down
	rm -rf __pycache__ .pytest_cache venv .venv



setup-win:
	python run.py setup

# Executa o pipeline localmente (requer banco rodando previamente)
run-win:
	python run.py run

# Executa a suíte de testes unitários
test-win:
	python run.py test

# Inicializa toda a aplicação e banco no Docker Compose
compose-up-win:
	python run.py compose-up

# Para e remove os contêineres do Docker Compose
compose-down-win:
	python run.py compose-down

# Inicializa o banco no Docker e executa o pipeline local
run-local-win:
	python run.py run-local

# Para o docker e limpa arquivos de cache e virtualenvs locais
clean-win:
	python run.py compose-down
	rm -rf __pycache__ .pytest_cache venv .venv

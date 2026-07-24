#!/usr/bin/env python3
import sys
import os
import subprocess
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

USE_UV = shutil.which("uv") is not None
VENV_DIR = BASE_DIR / (".venv" if USE_UV else "venv")

if USE_UV:
    # Quando usando o uv, os comandos python e playwright rodam sob o 'uv run'
    PYTHON_CMD = ["uv", "run", "python"]
    PLAYWRIGHT_CMD = ["uv", "run", "playwright"]
else:
    if os.name == "nt":  
        PYTHON_EXE = VENV_DIR / "Scripts" / "python.exe"
        PIP_EXE = VENV_DIR / "Scripts" / "pip.exe"
        PLAYWRIGHT_EXE = VENV_DIR / "Scripts" / "playwright.exe"
    else: 
        PYTHON_EXE = VENV_DIR / "bin" / "python"
        PIP_EXE = VENV_DIR / "bin" / "pip"
        PLAYWRIGHT_EXE = VENV_DIR / "bin" / "playwright"
    PYTHON_CMD = [str(PYTHON_EXE)]
    PLAYWRIGHT_CMD = [str(PLAYWRIGHT_EXE)]


def is_venv_valid():
    """Verifica se o ambiente virtual existe e possui os executáveis esperados."""
    if USE_UV:
        return VENV_DIR.exists()
    return VENV_DIR.exists() and PYTHON_EXE.exists() and PIP_EXE.exists()


def create_venv():
    """Cria o ambiente virtual, tentando usar o uv se disponível, ou o venv padrão com auto-instalação no Ubuntu/Debian."""
    if USE_UV:
        if run_command(["uv", "venv"]):
            return True
        print("Failed to create virtual environment with uv. Retrying with standard venv...", file=sys.stderr)

    # Tenta usar o venv padrão
    if run_command([sys.executable, "-m", "venv", str(VENV_DIR)]):
        return True

    # Se falhou, verifica se é Linux e tenta instalar python3-venv ou a versão específica pythonX.Y-venv
    if os.name != "nt":
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        package_name = f"python{py_version}-venv"
        print(f"\n[DICA] No Ubuntu/Debian, você precisa instalar o pacote '{package_name}'.", file=sys.stderr)
        try:
            response = input(f"Deseja tentar instalar o {package_name} automaticamente via sudo? [S/n]: ").strip().lower()
            if response in ('', 's', 'sim', 'y', 'yes'):
                print(f"Executando: sudo apt-get update && sudo apt-get install -y {package_name}")
                if run_command(["sudo", "apt-get", "update"]) and run_command(["sudo", "apt-get", "install", "-y", package_name]):
                    print("\nInstalado com sucesso! Tentando recriar o ambiente virtual...")
                    return run_command([sys.executable, "-m", "venv", str(VENV_DIR)])
        except Exception as e:
            print(f"Não foi possível instalar automaticamente: {e}", file=sys.stderr)
            
    return False


def run_command(args, env=None):
    """Executa um comando no shell mostrando a saída em tempo real."""
    print(f"Executing: {' '.join(str(arg) for arg in args)}")
    try:
        result = subprocess.run(
            args, 
            cwd=str(BASE_DIR), 
            env=env or os.environ.copy(),
            check=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}", file=sys.stderr)
        return False
    except FileNotFoundError as e:
        print(f"Command not found: {e}", file=sys.stderr)
        return False


def get_docker_command():
    """Detecta se deve usar 'docker compose' ou 'docker-compose'."""
    if shutil.which("docker") is not None:
        try:
            res = subprocess.run(
                ["docker", "compose", "version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if res.returncode == 0:
                return ["docker", "compose"]
        except Exception:
            pass

    if shutil.which("docker-compose") is not None:
        return ["docker-compose"]
    
    print("Warning: Neither 'docker compose' nor 'docker-compose' was found in PATH.", file=sys.stderr)
    return ["docker", "compose"]  # Fallback padrão


def cmd_setup():
    """Configura o ambiente virtual, instala dependências e prepara o arquivo .env."""
    print("=== Configurando o ambiente ===")
    
    # 1. Copiar .env se não existir
    env_file = BASE_DIR / ".env"
    env_example = BASE_DIR / ".env.example"
    if not env_file.exists():
        if env_example.exists():
            print(f"Creating .env from .env.example...")
            shutil.copy(env_example, env_file)
            print("Please edit the .env file to insert your API keys and credentials.")
        else:
            print("Warning: .env.example not found. Creating empty .env...")
            env_file.touch()
    else:
        print(".env file already exists.")

    # Detecta se 'uv' está disponível
    if USE_UV:
        print("Detected 'uv' tool! Using 'uv' for faster setup.")

    # 2. Criar Venv se não existir ou se estiver incompleto/quebrado
    if not is_venv_valid():
        if VENV_DIR.exists():
            print(f"Virtual environment at {VENV_DIR} is incomplete or broken. Recreating...")
            try:
                shutil.rmtree(VENV_DIR)
            except Exception as e:
                print(f"Warning: Could not remove directory {VENV_DIR}: {e}", file=sys.stderr)
        
        print(f"Creating virtual environment in {VENV_DIR}...")
        if not create_venv():
            return False
    else:
        print("Virtual environment already exists and is valid.")

    # 3. Instalar dependências
    print("Installing requirements.txt...")
    if USE_UV:
        if not run_command(["uv", "pip", "install", "-r", "requirements.txt"]):
            return False
    else:
        if not run_command([str(PIP_EXE), "install", "--upgrade", "pip"]):
            return False
        if not run_command([str(PIP_EXE), "install", "-r", "requirements.txt"]):
            return False

    # 4. Instalar Playwright Chromium
    print("Installing Playwright Chromium browser...")
    if not run_command(PLAYWRIGHT_CMD + ["install", "chromium"]):
        return False

    print("=== Environment successfully configured! ===")
    print("To run the application locally:")
    print("  python run.py run-local")
    print("To run using Docker Compose:")
    print("  python run.py compose-up")
    return True


def cmd_run():
    """Executa o pipeline principal."""
    if not is_venv_valid():
        print("Error: Virtual environment not found or incomplete. Please run 'python run.py setup' first.", file=sys.stderr)
        return False
    return run_command(PYTHON_CMD + ["main.py"])


def cmd_test():
    """Executa a suíte de testes unitários."""
    if not is_venv_valid():
        print("Error: Virtual environment not found or incomplete. Please run 'python run.py setup' first.", file=sys.stderr)
        return False
    return run_command(PYTHON_CMD + ["-m", "unittest", "discover", "-s", "tests"])


def cmd_compose_up():
    """Inicia todos os serviços via Docker Compose."""
    docker_cmd = get_docker_command()
    return run_command(docker_cmd + ["up", "--build"])


def cmd_compose_down():
    """Para todos os serviços via Docker Compose."""
    docker_cmd = get_docker_command()
    return run_command(docker_cmd + ["down"])


def cmd_db_start():
    """Inicia apenas o container de banco de dados."""
    docker_cmd = get_docker_command()
    return run_command(docker_cmd + ["up", "-d", "db"])


def cmd_db_stop():
    """Para o container de banco de dados ou todos os containers."""
    docker_cmd = get_docker_command()
    return run_command(docker_cmd + ["stop", "db"])


def cmd_run_local():
    """Inicia o banco de dados via Docker e executa o pipeline localmente."""
    print("=== Executando o Pipeline Localmente ===")
    
    # 1. Certificar que o setup foi executado e o ambiente virtual é válido
    if not (BASE_DIR / ".env").exists() or not is_venv_valid():
        print("Setup is missing or incomplete. Running setup first...")
        if not cmd_setup():
            print("Error: Setup failed. Aborting local execution.", file=sys.stderr)
            return False

    # 2. Iniciar o Banco de Dados
    print("Starting database container...")
    if not cmd_db_start():
        print("Warning: Could not start PostgreSQL container. Attempting to run local pipeline anyway...", file=sys.stderr)

    # 3. Executar o Pipeline
    print("Running pipeline...")
    success = cmd_run()
    
    if success:
        print("Pipeline executed successfully!")
    else:
        print("Pipeline execution failed.", file=sys.stderr)
    return success


def print_help():
    print("Usage: python run.py <command>")
    print("\nAvailable commands:")
    print("  setup         - Create venv, copy .env, install dependencies and Playwright")
    print("  run           - Execute the pipeline locally (requires running database)")
    print("  test          - Run the unit tests")
    print("  run-local     - Start database container and execute the pipeline locally")
    print("  compose-up    - Run everything inside Docker containers")
    print("  compose-down  - Stop all running Docker containers")
    print("  db-start      - Start only the database container")
    print("  db-stop       - Stop the database container")
    print("  help          - Show this help message")


def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    cmd = sys.argv[1].lower()

    commands = {
        "setup": cmd_setup,
        "run": cmd_run,
        "test": cmd_test,
        "compose-up": cmd_compose_up,
        "compose-down": cmd_compose_down,
        "db-start": cmd_db_start,
        "db-stop": cmd_db_stop,
        "run-local": cmd_run_local,
        "help": print_help
    }

    if cmd in commands:
        success = commands[cmd]()
        sys.exit(0 if success or success is None else 1)
    else:
        print(f"Unknown command: '{cmd}'", file=sys.stderr)
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

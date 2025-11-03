#!/usr/bin/env python3
import os
import subprocess
import sys

def run_command(command, cwd=None):
    """Executa um comando e retorna True se bem-sucedido"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar: {command}")
        print(f"Código de saída: {e.returncode}")
        return False

def main():
    print("=" * 40)
    print("Iniciando o projeto Fast Food App")
    print("=" * 40)
    
    # Diretório atual (onde está o script)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(base_dir, "frontend")
    
    print("\n[1/4] Executando build do frontend...")
    if not run_command("npm run build:dev", cwd=frontend_dir):
        print("Falha no build do frontend!")
        sys.exit(1)
    
    print("\n[2/4] Aplicando migrações do banco de dados...")
    if not run_command("python manage.py migrate", cwd=base_dir):
        print("Falha ao aplicar as migrações do banco de dados!")
        sys.exit(1)

    print("\n[3/4] Populando o banco de dados com dados de teste...")
    if not run_command("python manage.py populate_db --clear-existing --full --verbose", cwd=base_dir):
        print("Falha ao popular o banco de dados!")
        sys.exit(1)

    print("\n[4/4] Iniciando servidor Django...")
    if not run_command("python manage.py runserver", cwd=base_dir):
        print("Falha ao iniciar o servidor Django!")
        sys.exit(1)
    
    print("\n[4/4] " + "=" * 40)
    print("Projeto iniciado com sucesso!")
    print("=" * 40)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Script para executar todos os testes do sistema Surebets.
Inclui testes unitários, de integração e de performance.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Adicionar o diretório backend ao path
BACKEND_DIR = Path(__file__).parent
sys.path.insert(0, str(BACKEND_DIR))

def run_command(cmd, description):
    """Executa um comando e exibe resultado."""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=BACKEND_DIR)
        
        if result.stdout:
            print("📄 STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️ STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCESSO")
        else:
            print(f"❌ {description} - FALHOU (código: {result.returncode})")
            
        return result.returncode == 0
    
    except Exception as e:
        print(f"💥 Erro ao executar comando: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Executar testes do Surebets System")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "performance", "all"],
        default="all",
        help="Tipo de testes para executar"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Executar com cobertura de código"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Saída detalhada"
    )
    
    args = parser.parse_args()
    
    print("🧪 SUREBETS SYSTEM - EXECUÇÃO DE TESTES")
    print("=" * 60)
    
    # Verificar se pytest está instalado
    try:
        subprocess.run(["python", "-m", "pytest", "--version"], 
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ pytest não está instalado!")
        print("💡 Execute: pip install pytest pytest-asyncio pytest-cov pytest-benchmark")
        sys.exit(1)
    
    # Comandos base
    base_cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        base_cmd.append("-v")
    
    if args.coverage:
        base_cmd.extend(["--cov=database", "--cov=services", "--cov-report=html", "--cov-report=term"])
    
    # Definir quais testes executar
    test_suites = {}
    
    if args.type in ["unit", "all"]:
        test_suites["Testes Unitários"] = base_cmd + ["tests/unit/"]
    
    if args.type in ["integration", "all"]:
        test_suites["Testes de Integração"] = base_cmd + ["tests/integration/"]
    
    if args.type in ["performance", "all"]:
        test_suites["Testes de Performance"] = base_cmd + ["tests/performance/", "--benchmark-only"]
    
    # Executar testes
    success_count = 0
    total_count = len(test_suites)
    
    for description, cmd in test_suites.items():
        if run_command(" ".join(cmd), description):
            success_count += 1
    
    # Relatório final
    print(f"\n{'='*60}")
    print("📊 RELATÓRIO FINAL")
    print(f"{'='*60}")
    print(f"✅ Sucessos: {success_count}/{total_count}")
    print(f"❌ Falhas: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 Todos os testes passaram!")
        sys.exit(0)
    else:
        print("💥 Alguns testes falharam!")
        sys.exit(1)

if __name__ == "__main__":
    main()

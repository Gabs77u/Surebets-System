#!/usr/bin/env python3
"""
Script para executar todos os testes do sistema Surebets.
Inclui testes unitários, de integração e de performance.
"""

import sys
import subprocess
import argparse
from pathlib import Path
import logging

# Adicionar o diretório backend ao path
BACKEND_DIR = Path(__file__).parent
sys.path.insert(0, str(BACKEND_DIR))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def run_command(cmd, description):
    """Executa um comando e exibe resultado."""
    logging.info(f"\n{'='*60}")
    logging.info(f"🔄 {description}")
    logging.info(f"{'='*60}")

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=BACKEND_DIR
        )

        if result.stdout:
            logging.info("📄 STDOUT:")
            logging.info(result.stdout)

        if result.stderr:
            logging.info("⚠️ STDERR:")
            logging.info(result.stderr)

        if result.returncode == 0:
            logging.info(f"✅ {description} - SUCESSO")
        else:
            logging.info(f"❌ {description} - FALHOU (código: {result.returncode})")

        return result.returncode == 0

    except Exception as e:
        logging.info(f"💥 Erro ao executar comando: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Executar testes do Surebets System")
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "performance", "all"],
        default="all",
        help="Tipo de testes para executar",
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Executar com cobertura de código"
    )
    parser.add_argument("--verbose", action="store_true", help="Saída detalhada")

    args = parser.parse_args()

    logging.info("🧪 SUREBETS SYSTEM - EXECUÇÃO DE TESTES")
    logging.info("=" * 60)

    # Verificar se pytest está instalado
    try:
        subprocess.run(
            ["python", "-m", "pytest", "--version"], capture_output=True, check=True
        )
    except subprocess.CalledProcessError:
        logging.info("❌ pytest não está instalado!")
        logging.info(
            "💡 Execute: pip install pytest pytest-asyncio pytest-cov pytest-benchmark"
        )
        sys.exit(1)

    # Comandos base
    base_cmd = ["python", "-m", "pytest"]

    if args.verbose:
        base_cmd.append("-v")

    if args.coverage:
        base_cmd.extend(
            [
                "--cov=database",
                "--cov=services",
                "--cov-report=html",
                "--cov-report=term",
            ]
        )

    # Definir quais testes executar
    test_suites = {}

    if args.type in ["unit", "all"]:
        test_suites["Testes Unitários"] = base_cmd + ["tests/unit/"]

    if args.type in ["integration", "all"]:
        test_suites["Testes de Integração"] = base_cmd + ["tests/integration/"]

    if args.type in ["performance", "all"]:
        test_suites["Testes de Performance"] = base_cmd + [
            "tests/performance/",
            "--benchmark-only",
        ]

    # Executar testes
    success_count = 0
    total_count = len(test_suites)

    for description, cmd in test_suites.items():
        if run_command(" ".join(cmd), description):
            success_count += 1

    # Relatório final
    logging.info(f"\n{'='*60}")
    logging.info("📊 RELATÓRIO FINAL")
    logging.info(f"{'='*60}")
    logging.info(f"✅ Sucessos: {success_count}/{total_count}")
    logging.info(f"❌ Falhas: {total_count - success_count}/{total_count}")

    if success_count == total_count:
        logging.info("🎉 Todos os testes passaram!")
        sys.exit(0)
    else:
        logging.info("💥 Alguns testes falharam!")
        sys.exit(1)


if __name__ == "__main__":
    main()

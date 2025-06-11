#!/usr/bin/env python3
"""
Utilitário para usar o MonkeyType com DCApiX

Este script fornece comandos simples para executar o MonkeyType
para coletar e aplicar tipos no projeto DCApiX.
"""

import argparse
import subprocess
import sys


def run_monkeytype_tests(test_path=None):
    """Executa testes com o MonkeyType para coletar tipos em tempo de execução."""
    cmd = ["monkeytype", "run", "-m", "pytest"]

    if test_path:
        cmd.append(test_path)

    print(f"Executando testes com MonkeyType: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)

    if result.returncode == 0:
        print("\nColeta de tipos concluída com sucesso.")
        print("Para listar módulos com informações de tipo:")
        print("  python dc_api_x_monkeytype.py list")
        print("Para aplicar tipos a um módulo:")
        print("  python dc_api_x_monkeytype.py apply --module dc_api_x.some_module")

    return result.returncode


def list_modules():
    """Lista módulos com informações de tipo coletadas."""
    cmd = ["monkeytype", "list-modules"]

    print("Listando módulos com informações de tipo:")
    result = subprocess.run(cmd, check=False)

    if result.returncode == 0:
        print("\nPara aplicar tipos a um módulo:")
        print("  python dc_api_x_monkeytype.py apply --module dc_api_x.some_module")

    return result.returncode


def apply_types(module):
    """Aplica tipos coletados a um módulo específico."""
    cmd = ["monkeytype", "apply", module]

    print(f"Aplicando tipos ao módulo {module}:")
    result = subprocess.run(cmd, check=False)

    if result.returncode == 0:
        print(f"\nTipos aplicados com sucesso ao módulo {module}")
        print("Verifique as alterações e execute mypy para validar os tipos.")

    return result.returncode


def generate_stub(module):
    """Gera um stub com os tipos coletados para um módulo."""
    cmd = ["monkeytype", "stub", module]

    print(f"Gerando stub para o módulo {module}:")
    result = subprocess.run(cmd, check=False)

    if result.returncode == 0:
        print(f"\nStub gerado com sucesso para o módulo {module}")
        print("Revise o stub e aplique manualmente se necessário.")

    return result.returncode


def main():
    """Ponto de entrada principal."""
    parser = argparse.ArgumentParser(description="Utilitário MonkeyType para DCApiX")
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")
    subparsers.required = True

    # Comando run
    run_parser = subparsers.add_parser("run", help="Executar testes com MonkeyType")
    run_parser.add_argument("--test-path", help="Caminho do teste específico")

    # Comando list
    subparsers.add_parser("list", help="Listar módulos com informações de tipo")

    # Comando apply
    apply_parser = subparsers.add_parser("apply", help="Aplicar tipos a um módulo")
    apply_parser.add_argument("--module", required=True, help="Caminho do módulo")

    # Comando stub
    stub_parser = subparsers.add_parser("stub", help="Gerar stub para um módulo")
    stub_parser.add_argument("--module", required=True, help="Caminho do módulo")

    args = parser.parse_args()

    if args.command == "run":
        return run_monkeytype_tests(args.test_path)
    if args.command == "list":
        return list_modules()
    if args.command == "apply":
        return apply_types(args.module)
    if args.command == "stub":
        return generate_stub(args.module)
    print(f"Comando desconhecido: {args.command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())

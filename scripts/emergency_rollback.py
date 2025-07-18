#!/usr/bin/env python3
"""
Script de EMERGÊNCIA para rollback de operações críticas.

Use quando operações com sync_dependencies.py causaram problemas.
"""

import sys
from pathlib import Path

# Adiciona scripts ao path para importar flext_tools
sys.path.insert(0, str(Path(__file__).parent))

from flext_tools import Colors, RollbackManager, print_colored


def list_available_sessions():
    """Lista sessões de backup disponíveis."""
    try:
        rollback = RollbackManager()
        sessions = rollback.list_sessions()

        if not sessions:
            print_colored("❌ Nenhuma sessão de backup encontrada", Colors.RED)
            return []

        print_colored("📋 Sessões de backup disponíveis:", Colors.BLUE)
        for i, session in enumerate(sessions):
            print(f"\n{i + 1}. {session['session_id']}")
            print(f"   Operações: {session['operations_count']}")
            print(f"   Arquivos: {len(session['files_backed_up'])}")

            if len(session["files_backed_up"]) <= 5:
                for file_path in session["files_backed_up"]:
                    print(f"   - {file_path}")
            else:
                for file_path in session["files_backed_up"][:3]:
                    print(f"   - {file_path}")
                print(f"   - ... e mais {len(session['files_backed_up']) - 3} arquivos")

        return sessions

    except Exception as e:
        print_colored(f"❌ Erro ao listar sessões: {e}", Colors.RED)
        return []


def verify_rollback_safety(session_id: str):
    """Verifica se rollback é seguro."""
    try:
        rollback = RollbackManager()
        verification = rollback.verify_rollback_feasibility(session_id)

        print_colored(f"\n🔍 Verificação de rollback para {session_id}:", Colors.BLUE)

        if verification["feasible"]:
            print_colored("✅ Rollback é viável", Colors.GREEN)
        else:
            print_colored("❌ Rollback tem problemas", Colors.RED)

        if verification["missing_backups"]:
            print_colored("❌ Backups faltando:", Colors.RED)
            for missing in verification["missing_backups"]:
                print(f"   - {missing}")

        if verification["integrity_issues"]:
            print_colored("⚠️ Problemas de integridade:", Colors.YELLOW)
            for issue in verification["integrity_issues"]:
                print(f"   - {issue}")

        if verification["conflicts"]:
            print_colored("⚠️ Arquivos modificados após backup:", Colors.YELLOW)
            for conflict in verification["conflicts"]:
                print(f"   - {conflict}")

        return verification["feasible"]

    except Exception as e:
        print_colored(f"❌ Erro na verificação: {e}", Colors.RED)
        return False


def perform_rollback(session_id: str, confirm: bool = False):
    """Executa rollback de uma sessão."""
    try:
        rollback = RollbackManager()

        if not confirm:
            print_colored(
                f"\n⚠️ ATENÇÃO: Rollback irá restaurar TODOS os arquivos da sessão {session_id}",
                Colors.YELLOW,
            )
            print_colored(
                "Isso pode sobrescrever modificações feitas após o backup!",
                Colors.YELLOW,
            )
            response = input("\nTem CERTEZA que deseja continuar? Digite 'CONFIRMO': ")

            if response != "CONFIRMO":
                print_colored("❌ Rollback cancelado", Colors.YELLOW)
                return False

        print_colored(f"\n🔄 Iniciando rollback da sessão {session_id}...", Colors.BLUE)

        success_count, failure_count = rollback.rollback_session(
            session_id, confirm=True,
        )

        if failure_count == 0:
            print_colored("\n✅ Rollback concluído com sucesso!", Colors.GREEN)
            print_colored(f"📊 {success_count} arquivos restaurados", Colors.CYAN)
        else:
            print_colored("\n⚠️ Rollback parcialmente concluído", Colors.YELLOW)
            print_colored(
                f"📊 Sucessos: {success_count}, Falhas: {failure_count}", Colors.CYAN,
            )

        return failure_count == 0

    except Exception as e:
        print_colored(f"❌ Erro durante rollback: {e}", Colors.RED)
        return False


def interactive_mode():
    """Modo interativo para rollback."""
    print_colored("🚨 MODO EMERGÊNCIA - ROLLBACK DE OPERAÇÕES", Colors.RED)
    print_colored("=" * 50, Colors.RED)

    while True:
        print_colored("\nOpções:", Colors.BLUE)
        print("1. Listar sessões de backup")
        print("2. Verificar viabilidade de rollback")
        print("3. Executar rollback")
        print("4. Sair")

        choice = input("\nEscolha uma opção (1-4): ").strip()

        if choice == "1":
            list_available_sessions()

        elif choice == "2":
            session_id = input("Digite o ID da sessão: ").strip()
            if session_id:
                verify_rollback_safety(session_id)

        elif choice == "3":
            session_id = input("Digite o ID da sessão para rollback: ").strip()
            if session_id:
                if verify_rollback_safety(session_id):
                    perform_rollback(session_id)
                else:
                    print_colored(
                        "❌ Rollback não é seguro. Verifique os problemas primeiro.",
                        Colors.RED,
                    )

        elif choice == "4":
            print_colored("👋 Saindo do modo emergência", Colors.CYAN)
            break

        else:
            print_colored("❌ Opção inválida", Colors.RED)


def main():
    """Função principal."""
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print_colored("🚨 Script de Emergência - Rollback", Colors.RED)
        print("\nUso:")
        print("  python emergency_rollback.py                    # Modo interativo")
        print("  python emergency_rollback.py list               # Lista sessões")
        print("  python emergency_rollback.py verify SESSION_ID  # Verifica rollback")
        print("  python emergency_rollback.py rollback SESSION_ID # Executa rollback")
        print("\nEste script deve ser usado apenas em emergências!")
        return 0

    if not args:
        interactive_mode()
        return 0

    command = args[0]

    if command == "list":
        list_available_sessions()

    elif command == "verify" and len(args) > 1:
        session_id = args[1]
        verify_rollback_safety(session_id)

    elif command == "rollback" and len(args) > 1:
        session_id = args[1]
        if verify_rollback_safety(session_id):
            perform_rollback(session_id)
        else:
            print_colored(
                "❌ Rollback bloqueado por problemas de segurança", Colors.RED,
            )
            return 1

    else:
        print_colored("❌ Comando inválido. Use --help para ajuda.", Colors.RED)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

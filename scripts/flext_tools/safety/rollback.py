"""Sistema de rollback para operações críticas"""

import json
import operator
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from flext_tools.utils import Colors, print_colored


class RollbackManager:
    """Gerencia rollback de operações baseado em backups."""

    def __init__(self, backup_dir: Path | None = None):
        if backup_dir:
            self.backup_dir = backup_dir
        else:
            self.backup_dir = Path.cwd() / ".flext_backups"

        if not self.backup_dir.exists():
            raise FileNotFoundError("Diretório de backup não encontrado")

    def list_sessions(self) -> list[dict]:
        """Lista todas as sessões de backup disponíveis."""
        sessions = []

        for session_dir in self.backup_dir.glob("session_*"):
            log_file = session_dir / "operations_log.json"
            if log_file.exists():
                try:
                    with open(log_file, encoding="utf-8") as f:
                        log_data = json.load(f)

                    session_info = {
                        "session_id": log_data["session_id"],
                        "session_dir": str(session_dir),
                        "operations_count": len(log_data["operations"]),
                        "files_backed_up": [
                            op["original_path"] for op in log_data["operations"]
                        ],
                    }
                    sessions.append(session_info)

                except Exception as e:
                    print_colored(
                        f"  ⚠️ Erro ao ler sessão {session_dir.name}: {e}", Colors.YELLOW
                    )

        return sorted(sessions, key=operator.itemgetter("session_id"), reverse=True)

    def rollback_file(self, backup_id: str) -> bool:
        """
        Restaura um arquivo específico do backup.

        Args:
            backup_id: ID do backup a ser restaurado

        Returns:
            True se sucesso
        """
        operation = self._find_operation(backup_id)
        if not operation:
            print_colored(f"❌ Backup {backup_id} não encontrado", Colors.RED)
            return False

        backup_path = Path(operation["backup_path"])
        original_path = Path(operation["original_path"])

        if not backup_path.exists():
            print_colored(f"❌ Arquivo de backup não existe: {backup_path}", Colors.RED)
            return False

        try:
            # Verifica integridade do backup
            if not self._verify_backup_integrity(backup_path, operation):
                print_colored(
                    f"⚠️ Integridade do backup comprometida: {backup_id}", Colors.YELLOW
                )
                response = input("Continuar mesmo assim? (s/N): ")
                if response.lower() not in {"s", "sim", "y", "yes"}:
                    return False

            # Cria backup do estado atual antes de restaurar
            if original_path.exists():
                current_backup = original_path.with_suffix(
                    f"{original_path.suffix}.pre_rollback"
                )
                shutil.copy2(original_path, current_backup)
                print_colored(
                    f"  📁 Estado atual salvo em: {current_backup}", Colors.CYAN
                )

            # Restaura arquivo
            shutil.copy2(backup_path, original_path)
            print_colored(f"  ✅ Arquivo restaurado: {original_path}", Colors.GREEN)

            return True

        except Exception as e:
            print_colored(f"❌ Erro ao restaurar arquivo: {e}", Colors.RED)
            return False

    def rollback_session(
        self, session_id: str, confirm: bool = False
    ) -> tuple[int, int]:
        """
        Restaura todos os arquivos de uma sessão.

        Args:
            session_id: ID da sessão a ser restaurada
            confirm: Se True, não pede confirmação

        Returns:
            Tupla (sucessos, falhas)
        """
        session_dir = self.backup_dir / f"session_{session_id}"
        log_file = session_dir / "operations_log.json"

        if not log_file.exists():
            print_colored(f"❌ Sessão {session_id} não encontrada", Colors.RED)
            return 0, 0

        with open(log_file, encoding="utf-8") as f:
            log_data = json.load(f)

        operations = log_data["operations"]

        if not confirm:
            print_colored(
                f"⚠️ Restaurar {len(operations)} arquivos da sessão {session_id}?",
                Colors.YELLOW,
            )
            for op in operations:
                print(f"    - {op['original_path']}")
            response = input("\nConfirmar rollback? (s/N): ")
            if response.lower() not in {"s", "sim", "y", "yes"}:
                print_colored("❌ Rollback cancelado", Colors.YELLOW)
                return 0, 0

        print_colored(f"🔄 Iniciando rollback da sessão {session_id}...", Colors.BLUE)

        success_count = 0
        failure_count = 0

        for operation in operations:
            if self.rollback_file(operation["backup_id"]):
                success_count += 1
            else:
                failure_count += 1

        print_colored(
            f"\n📊 Rollback concluído: {success_count} sucessos, {failure_count} falhas",
            Colors.CYAN,
        )
        return success_count, failure_count

    def rollback_to_restore_point(self, restore_point_id: str) -> tuple[int, int]:
        """
        Restaura até um ponto de restauração específico.

        Args:
            restore_point_id: ID do ponto de restauração

        Returns:
            Tupla (sucessos, falhas)
        """
        # Extrai session_id do restore_point_id
        session_id = (
            restore_point_id.split("_")[1] + "_" + restore_point_id.split("_")[2]
        )

        session_dir = self.backup_dir / f"session_{session_id}"
        restore_file = session_dir / f"{restore_point_id}.json"

        if not restore_file.exists():
            print_colored(
                f"❌ Ponto de restauração {restore_point_id} não encontrado", Colors.RED
            )
            return 0, 0

        with open(restore_file, encoding="utf-8") as f:
            restore_data = json.load(f)

        operations_count = restore_data["operations_count"]

        print_colored(
            f"🔄 Restaurando até ponto: {restore_data['description']}", Colors.BLUE
        )
        print_colored(f"   Operações até o ponto: {operations_count}", Colors.CYAN)

        # Carrega log de operações
        log_file = session_dir / "operations_log.json"
        with open(log_file, encoding="utf-8") as f:
            log_data = json.load(f)

        # Restaura apenas operações até o ponto
        operations_to_restore = log_data["operations"][:operations_count]

        success_count = 0
        failure_count = 0

        for operation in operations_to_restore:
            if self.rollback_file(operation["backup_id"]):
                success_count += 1
            else:
                failure_count += 1

        return success_count, failure_count

    def verify_rollback_feasibility(self, session_id: str) -> dict:
        """
        Verifica se é possível fazer rollback de uma sessão.

        Args:
            session_id: ID da sessão

        Returns:
            Dicionário com status de verificação
        """
        session_dir = self.backup_dir / f"session_{session_id}"
        log_file = session_dir / "operations_log.json"

        result = {
            "feasible": True,
            "issues": [],
            "missing_backups": [],
            "integrity_issues": [],
            "conflicts": [],
        }

        if not log_file.exists():
            result["feasible"] = False
            result["issues"].append("Log de operações não encontrado")
            return result

        with open(log_file, encoding="utf-8") as f:
            log_data = json.load(f)

        for operation in log_data["operations"]:
            backup_path = Path(operation["backup_path"])
            original_path = Path(operation["original_path"])

            # Verifica se backup existe
            if not backup_path.exists():
                result["missing_backups"].append(operation["original_path"])
                result["feasible"] = False

            # Verifica integridade
            elif not self._verify_backup_integrity(backup_path, operation):
                result["integrity_issues"].append(operation["original_path"])

            # Verifica conflitos (arquivo foi modificado após backup)
            elif original_path.exists():
                current_hash = self._calculate_hash(original_path)
                if current_hash != operation["file_hash"]:
                    result["conflicts"].append(operation["original_path"])

        return result

    def _find_operation(self, backup_id: str) -> dict | None:
        """Encontra operação pelo ID de backup."""
        session_id = "_".join(backup_id.split("_")[:2])
        session_dir = self.backup_dir / f"session_{session_id}"
        log_file = session_dir / "operations_log.json"

        if not log_file.exists():
            return None

        with open(log_file, encoding="utf-8") as f:
            log_data = json.load(f)

        for operation in log_data["operations"]:
            if operation["backup_id"] == backup_id:
                return operation

        return None

    def _verify_backup_integrity(self, backup_path: Path, operation: dict) -> bool:
        """Verifica integridade do backup."""
        try:
            if backup_path.stat().st_size != operation["file_size"]:
                return False

            current_hash = self._calculate_hash(backup_path)
            return current_hash == operation["file_hash"]

        except Exception:
            return False

    def _calculate_hash(self, file_path: Path) -> str:
        """Calcula hash do arquivo."""
        import hashlib

        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

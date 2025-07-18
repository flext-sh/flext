"""Sistema de backup para operações críticas"""

import json
import shutil
from datetime import datetime
from pathlib import Path

from flext_tools.utils import Colors, print_colored


class BackupManager:
    """Gerencia backups de arquivos críticos antes de modificações."""

    def __init__(self, backup_dir: Path | None = None):
        if backup_dir:
            self.backup_dir = backup_dir
        else:
            self.backup_dir = Path.cwd() / ".flext_backups"

        self.backup_dir.mkdir(exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.backup_dir / f"session_{self.session_id}"
        self.session_dir.mkdir(exist_ok=True)

        # Registro de operações
        self.operations_log = []

    def backup_file(self, file_path: Path, operation_type: str = "modify") -> str:
        """
        Cria backup de um arquivo antes de modificação.

        Args:
            file_path: Caminho do arquivo a ser backupeado
            operation_type: Tipo de operação (modify, add, delete)

        Returns:
            ID do backup para rollback
        """
        if not file_path.exists():
            msg = f"Arquivo não existe: {file_path}"
            raise FileNotFoundError(msg)

        # Cria estrutura de diretórios do backup
        # Resolve path absoluto para lidar com paths relativos
        abs_file_path = file_path.resolve()
        try:
            relative_path = abs_file_path.relative_to(Path.cwd().resolve())
        except ValueError:
            # Se não conseguir fazer relativo, usa apenas o nome do arquivo
            relative_path = abs_file_path.name
        backup_file_path = self.session_dir / relative_path
        backup_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Copia arquivo original
        shutil.copy2(file_path, backup_file_path)

        # Registra operação
        backup_id = f"{self.session_id}_{len(self.operations_log)}"
        operation = {
            "backup_id": backup_id,
            "timestamp": datetime.now().isoformat(),
            "operation_type": operation_type,
            "original_path": str(file_path),
            "backup_path": str(backup_file_path),
            "file_size": file_path.stat().st_size,
            "file_hash": self._calculate_hash(file_path),
        }

        self.operations_log.append(operation)
        self._save_operations_log()

        print_colored(f"  📁 Backup criado: {backup_id}", Colors.CYAN)
        return backup_id

    def backup_project(self, project_path: Path) -> str:
        """
        Cria backup completo de arquivos críticos do projeto.

        Args:
            project_path: Caminho do projeto

        Returns:
            ID do backup do projeto
        """
        critical_files = [
            "pyproject.toml",
            "poetry.lock",
            "requirements.txt",
            "setup.py",
            "setup.cfg",
        ]

        project_backup_id = f"project_{self.session_id}_{project_path.name}"

        for file_name in critical_files:
            file_path = project_path / file_name
            if file_path.exists():
                self.backup_file(file_path, "project_backup")

        print_colored(f"  🗂️ Backup do projeto: {project_backup_id}", Colors.GREEN)
        return project_backup_id

    def create_restore_point(self, description: str) -> str:
        """
        Cria ponto de restauração com múltiplos arquivos.

        Args:
            description: Descrição do ponto de restauração

        Returns:
            ID do ponto de restauração
        """
        restore_point_id = f"restore_{self.session_id}_{len(self.operations_log)}"

        restore_point = {
            "restore_point_id": restore_point_id,
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "operations_count": len(self.operations_log),
            "session_id": self.session_id,
        }

        # Salva metadata do ponto de restauração
        restore_file = self.session_dir / f"{restore_point_id}.json"
        with Path(restore_file).open("w", encoding="utf-8") as f:
            json.dump(restore_point, f, indent=2)

        print_colored(f"  🔄 Ponto de restauração: {restore_point_id}", Colors.BLUE)
        return restore_point_id

    def get_backup_info(self, backup_id: str) -> dict | None:
        """Obtém informações de um backup específico."""
        for operation in self.operations_log:
            if operation["backup_id"] == backup_id:
                return operation
        return None

    def list_backups(self) -> list[dict]:
        """Lista todos os backups da sessão atual."""
        return self.operations_log.copy()

    def get_session_summary(self) -> dict:
        """Retorna resumo da sessão de backup."""
        return {
            "session_id": self.session_id,
            "session_dir": str(self.session_dir),
            "operations_count": len(self.operations_log),
            "start_time": self.operations_log[0]["timestamp"]
            if self.operations_log
            else None,
            "last_operation": self.operations_log[-1]["timestamp"]
            if self.operations_log
            else None,
            "total_files": len(self.operations_log),
        }

    def _calculate_hash(self, file_path: Path) -> str:
        """Calcula hash do arquivo para verificação de integridade."""
        import hashlib

        hash_md5 = hashlib.md5()
        with Path(file_path).open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _save_operations_log(self):
        """Salva log de operações no disco."""
        log_file = self.session_dir / "operations_log.json"
        with Path(log_file).open("w", encoding="utf-8") as f:
            json.dump(
                {"session_id": self.session_id, "operations": self.operations_log},
                f,
                indent=2,
            )

    def cleanup_old_backups(self, keep_days: int = 7):
        """Remove backups antigos baseado em dias."""
        cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)

        removed_count = 0
        for session_dir in self.backup_dir.glob("session_*"):
            try:
                session_timestamp = session_dir.stat().st_mtime
                if session_timestamp < cutoff_date:
                    shutil.rmtree(session_dir)
                    removed_count += 1
            except Exception:
                pass

        if removed_count > 0:
            print_colored(
                f"  🧹 Removidos {removed_count} backups antigos", Colors.YELLOW,
            )

    def backup_poetry_lock(self, project_path: Path) -> str | None:
        """
        Cria backup específico do poetry.lock com validação.

        Args:
            project_path: Caminho do projeto

        Returns:
            ID do backup ou None se não existir poetry.lock
        """
        poetry_lock = project_path / "poetry.lock"

        if not poetry_lock.exists():
            print_colored(
                f"  ⚠️ poetry.lock não encontrado em {project_path.name}", Colors.YELLOW,
            )
            return None

        # Valida integridade do poetry.lock antes do backup
        if not self._validate_poetry_lock(poetry_lock):
            print_colored(
                f"  ❌ poetry.lock corrompido em {project_path.name}", Colors.RED,
            )
            return None

        backup_id = self.backup_file(poetry_lock, "poetry_lock_backup")
        print_colored(f"  🔒 poetry.lock backupeado: {project_path.name}", Colors.GREEN)
        return backup_id

    def backup_workspace_poetry_locks(
        self, workspace_path: Path,
    ) -> dict[str, str | None]:
        """
        Cria backup de todos os poetry.lock no workspace.

        Args:
            workspace_path: Caminho do workspace

        Returns:
            Dict com project_name -> backup_id (ou None se não existir)
        """
        print_colored("🔒 Backup de poetry.lock no workspace...", Colors.BLUE)

        backups = {}
        projects = [
            d
            for d in workspace_path.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

        for project_path in projects:
            project_name = project_path.name
            backup_id = self.backup_poetry_lock(project_path)
            backups[project_name] = backup_id

        successful_backups = sum(1 for bid in backups.values() if bid is not None)
        print_colored(
            f"  ✅ {successful_backups}/{len(projects)} poetry.lock backupeados",
            Colors.GREEN,
        )

        return backups

    def verify_poetry_lock_integrity(self, project_path: Path) -> bool:
        """
        Verifica integridade do poetry.lock atual vs backup.

        Args:
            project_path: Caminho do projeto

        Returns:
            True se íntegro, False caso contrário
        """
        poetry_lock = project_path / "poetry.lock"

        if not poetry_lock.exists():
            return False

        # Verifica se há backup deste poetry.lock
        for operation in self.operations_log:
            if (
                operation["operation_type"] == "poetry_lock_backup"
                and Path(operation["original_path"]) == poetry_lock
            ):
                # Compara hash atual com backup
                current_hash = self._calculate_hash(poetry_lock)
                backup_hash = operation["file_hash"]

                if current_hash != backup_hash:
                    print_colored(
                        f"  ⚠️ poetry.lock modificado: {project_path.name}",
                        Colors.YELLOW,
                    )
                    return False

                return True

        # Não encontrou backup - considera OK se arquivo é válido
        return self._validate_poetry_lock(poetry_lock)

    def _validate_poetry_lock(self, poetry_lock_path: Path) -> bool:
        """
        Valida se um arquivo poetry.lock está bem formado.

        Args:
            poetry_lock_path: Caminho para o poetry.lock

        Returns:
            True se válido, False caso contrário
        """
        try:
            import tomllib

            with Path(poetry_lock_path).open(encoding="utf-8") as f:
                content = f.read()

            # Tenta parsear como TOML
            tomllib.loads(content)

            # Verifica estrutura básica
            if "[[package]]" not in content and '"package"' not in content:
                return False

            # Verifica se não está vazio
            if (
                len(content.strip()) < 100
            ):  # poetry.lock mínimo tem muito mais que 100 chars
                return False

            return True

        except Exception as e:
            print_colored(f"    ❌ Erro validando poetry.lock: {e}", Colors.RED)
            return False

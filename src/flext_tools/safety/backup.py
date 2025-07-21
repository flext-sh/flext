"""Sistema de backup para operações críticas."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog

from flext_tools.utils import Colors, print_colored

logger = structlog.get_logger(__name__)

MIN_CONTENT_LENGTH = 100


class BackupManager:
    """Gerencia backups de arquivos críticos antes de modificações."""

    def __init__(self, backup_dir: Path | None = None) -> None:
        """Initialize backup manager."""
        if backup_dir:
            self.backup_dir = backup_dir
        else:
            self.backup_dir = Path.cwd() / ".flext_backups"

        self.backup_dir.mkdir(exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.backup_dir / f"session_{self.session_id}"
        self.session_dir.mkdir(exist_ok=True)

        # Registro de operações
        self.operations_log: list[dict[str, Any]] = []

    def create_backup(
        self,
        project_path: Path,
        description: str = "Backup automático",
    ) -> str:
        """Cria backup completo de um projeto.

        Args:
            project_path: Caminho do projeto
            description: Descrição do backup

        Returns:
            ID do backup criado

        """
        if not project_path.exists():
            msg = f"Projeto não encontrado: {project_path}"
            raise FileNotFoundError(msg)

        backup_id = f"backup_{self.session_id}_{len(self.operations_log)}"
        backup_path = self.session_dir / backup_id
        backup_path.mkdir(exist_ok=True)

        try:
            # Copia arquivos críticos do projeto
            critical_files = [
                "pyproject.toml",
                "poetry.lock",
                "Makefile",
                ".gitignore",
                "requirements.txt",
            ]

            backed_up_files = []
            for file_name in critical_files:
                file_path = project_path / file_name
                if file_path.exists():
                    backup_file_path = backup_path / file_name
                    shutil.copy2(file_path, backup_file_path)
                    backed_up_files.append(str(file_path))

            # Registra operação
            operation = {
                "backup_id": backup_id,
                "project_path": str(project_path),
                "backup_path": str(backup_path),
                "description": description,
                "timestamp": datetime.now().isoformat(),
                "files": backed_up_files,
                "file_count": len(backed_up_files),
            }

            self.operations_log.append(operation)
            self._save_operations_log()

            print_colored(
                f"✅ Backup criado: {backup_id} ({len(backed_up_files)} arquivos)",
                Colors.GREEN,
            )

            return backup_id

        except Exception as e:
            print_colored(f"❌ Erro ao criar backup: {e}", Colors.RED)
            raise

    def backup_file(self, file_path: Path, operation_type: str = "modify") -> str:
        """Cria backup de um arquivo antes de modificação.

        Args:
            file_path: Caminho do arquivo a ser backupeado
            operation_type: Tipo de operação (modify, add, delete)

        Returns:
            ID do backup para rollback

        """
        if not file_path.exists():
            msg = f"Arquivo não encontrado: {file_path}"
            raise FileNotFoundError(msg)

        # Gera ID único para este backup
        backup_id = f"{self.session_id}_{len(self.operations_log):03d}"
        backup_filename = f"{backup_id}_{file_path.name}"
        backup_path = self.session_dir / backup_filename

        try:
            # Copia arquivo para backup
            shutil.copy2(file_path, backup_path)

            # Calcula hash para verificação de integridade
            file_hash = self._calculate_hash(file_path)
            file_size = file_path.stat().st_size

            # Registra operação
            operation = {
                "backup_id": backup_id,
                "original_path": str(file_path),
                "backup_path": str(backup_path),
                "operation_type": operation_type,
                "timestamp": datetime.now().isoformat(),
                "file_hash": file_hash,
                "file_size": file_size,
            }

            self.operations_log.append(operation)
            self._save_operations_log()

            logger.info("File backed up", backup_id=backup_id, file_path=str(file_path))

            return backup_id

        except Exception as e:
            logger.exception("Backup failed", error=str(e), file_path=str(file_path))
            raise

    def create_restore_point(self, description: str) -> str:
        """Cria um ponto de restauração.

        Args:
            description: Descrição do ponto de restauração

        Returns:
            ID do ponto de restauração

        """
        restore_point_id = f"restore_{self.session_id}_{len(self.operations_log)}"
        restore_point_file = self.session_dir / f"{restore_point_id}.json"

        restore_data = {
            "restore_point_id": restore_point_id,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "operations_count": len(self.operations_log),
            "session_id": self.session_id,
        }

        with restore_point_file.open("w", encoding="utf-8") as f:
            json.dump(restore_data, f, indent=2)

        print_colored(
            f"📍 Ponto de restauração criado: {description}",
            Colors.CYAN,
        )

        return restore_point_id

    def list_backups(self) -> list[dict[str, Any]]:
        """Lista todos os backups da sessão atual."""
        return self.operations_log.copy()

    def cleanup_old_backups(self, days: int = 30) -> int:
        """Remove backups antigos.

        Args:
            days: Dias para manter backups

        Returns:
            Número de sessões removidas

        """
        cutoff_date = datetime.now().timestamp() - (days * 24 * 3600)
        removed_count = 0

        for session_dir in self.backup_dir.glob("session_*"):
            try:
                session_timestamp = session_dir.stat().st_mtime
                if session_timestamp < cutoff_date:
                    shutil.rmtree(session_dir)
                    removed_count += 1
                    print_colored(
                        f"🗑️ Sessão removida: {session_dir.name}",
                        Colors.YELLOW,
                    )
            except Exception as e:
                print_colored(
                    f"⚠️ Erro ao remover {session_dir.name}: {e}",
                    Colors.YELLOW,
                )

        return removed_count

    def get_backup_info(self, backup_id: str) -> dict[str, Any] | None:
        """Obtém informações de um backup específico."""
        for operation in self.operations_log:
            if operation["backup_id"] == backup_id:
                return operation.copy()
        return None

    def verify_backup_integrity(self, backup_id: str) -> bool:
        """Verifica integridade de um backup."""
        operation = self.get_backup_info(backup_id)
        if not operation:
            return False

        backup_path = Path(operation["backup_path"])
        if not backup_path.exists():
            return False

        try:
            # Verifica tamanho do arquivo
            if backup_path.stat().st_size != operation["file_size"]:
                return False

            # Verifica hash
            backup_hash = self._calculate_hash(backup_path)
            return bool(backup_hash == operation["file_hash"])

        except Exception:
            return False

    def validate_poetry_environment(self, project_path: Path) -> bool:
        """Valida ambiente Poetry antes de modificações críticas.

        Args:
            project_path: Caminho do projeto

        Returns:
            True se ambiente está válido

        """
        pyproject_toml = project_path / "pyproject.toml"
        poetry_lock = project_path / "poetry.lock"

        # Verifica se pyproject.toml existe
        if not pyproject_toml.exists():
            print_colored("❌ pyproject.toml não encontrado", Colors.RED)
            return False

        # Verifica se há backup recente do poetry.lock
        if poetry_lock.exists():
            return self._validate_poetry_lock(poetry_lock)

        # Não encontrou backup - considera OK se arquivo é válido
        return self._validate_poetry_lock(poetry_lock)

    def _validate_poetry_lock(self, poetry_lock_path: Path) -> bool:
        """Valida se um arquivo poetry.lock está bem formado.

        Args:
            poetry_lock_path: Caminho para o poetry.lock

        Returns:
            True se válido, False caso contrário

        """
        try:
            import tomllib

            with poetry_lock_path.open(encoding="utf-8") as f:
                content = f.read()

            # Tenta parsear como TOML
            tomllib.loads(content)

            # Verifica estrutura básica
            if "[[package]]" not in content and '"package"' not in content:
                return False

            # Verifica se não está vazio
            # poetry.lock mínimo tem muito mais que 100 chars
            return len(content.strip()) >= MIN_CONTENT_LENGTH

        except Exception as e:
            print_colored(f"    ❌ Erro validando poetry.lock: {e}", Colors.RED)
            return False

    def _save_operations_log(self) -> None:
        """Salva log de operações no disco."""
        log_file = self.session_dir / "operations_log.json"
        log_data = {
            "session_id": self.session_id,
            "operations": self.operations_log,
            "created_at": datetime.now().isoformat(),
        }

        with log_file.open("w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)

    def _calculate_hash(self, file_path: Path) -> str:
        """Calcula hash SHA256 de um arquivo."""
        hash_sha256 = hashlib.sha256()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

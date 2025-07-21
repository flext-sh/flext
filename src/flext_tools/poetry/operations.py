#!/usr/bin/env python3
"""Operações avançadas com Poetry - Validação, Cache e Rollback."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING, Any

from flext_tools.safety.backup import BackupManager
from flext_tools.safety.validator import SafetyValidator
from flext_tools.utils.colors import Colors, print_colored
from flext_tools.utils.logging import get_logger

if TYPE_CHECKING:
    from pathlib import Path


MIN_PARTS_COUNT = 3


class PoetryOperations:
    """Gerencia operações com Poetry com sistema de segurança integrado."""

    def __init__(
        self,
        dry_run: bool = True,
        enable_safety: bool = True,
        logger: Any = None,
    ) -> None:
        """Initialize Poetry operations with safety system."""
        self.dry_run = dry_run
        self.enable_safety = enable_safety
        self.logger = logger or get_logger()

        if self.enable_safety:
            self.backup_manager = BackupManager()
            self.safety_validator = SafetyValidator()
            self.logger.info(
                "INIT: Sistema de segurança ativado (dry_run=%s)",
                str(dry_run),
            )
            print_colored("🛡️ Sistema de segurança ativado", Colors.CYAN)

    def add_dependencies(
        self,
        project_path: Path,
        dependencies: dict[str, list[str]],
        auto_confirm: bool = False,
    ) -> dict[str, list[str]]:
        """Adiciona dependências a um projeto Poetry."""
        print_colored(
            f"📦 Adicionando dependências ao projeto {project_path.name}...",
            Colors.BLUE,
        )

        added: dict[str, list[str]] = {"runtime": [], "test": [], "dev": []}

        # Backup antes das modificações
        if self.enable_safety and not self.dry_run:
            backup_id = self.backup_manager.create_backup(
                project_path,
                f"before_add_deps_{project_path.name}",
            )
            print_colored(f"💾 Backup criado: {backup_id}", Colors.CYAN)

        # Adiciona dependências por categoria
        for category, deps in dependencies.items():
            if not deps:
                continue

            print_colored(f"\n  📋 Categoria: {category}", Colors.CYAN)

            for dep in deps:
                # Determina grupo para poetry add
                group = None if category == "runtime" else category

                try:
                    if self._add_dependency(project_path, dep, group):
                        added[category].append(dep)
                except Exception as e:
                    print_colored(
                        f"    ❌ Erro ao adicionar {dep}: {e}",
                        Colors.RED,
                    )

        # Resumo das adições
        total_added = sum(len(deps) for deps in added.values())
        if total_added > 0:
            print_colored(
                f"\n✅ {total_added} dependências adicionadas com sucesso",
                Colors.GREEN,
            )
        else:
            print_colored(
                "\n⚠️ Nenhuma dependência foi adicionada",
                Colors.YELLOW,
            )

        return added

    def _add_dependency(
        self,
        project_path: Path,
        dependency: str,
        group: str | None = None,
    ) -> bool:
        """Adiciona uma dependência individual."""
        cmd = ["poetry", "add", dependency]

        if group:
            cmd.extend(["--group", group])

        if self.dry_run:
            cmd.append("--dry-run")

        try:
            print_colored(f"    ➕ Adicionando {dependency}...", Colors.GREEN)

            result = subprocess.run(
                cmd,
                check=False,
                cwd=project_path,
                capture_output=True,
                text=True,
                shell=False,  # Security: explicit shell=False
                timeout=60,  # Prevent hanging
            )

            if result.returncode == 0:
                if not self.dry_run:
                    print_colored(
                        f"    ✅ {dependency} adicionado com sucesso",
                        Colors.GREEN,
                    )
                else:
                    print_colored(
                        f"    ✅ {dependency} seria adicionado (dry-run)",
                        Colors.YELLOW,
                    )
                return True

            print_colored(
                f"    ❌ Erro ao adicionar {dependency}: {result.stderr}",
                Colors.RED,
            )
            return False

        except Exception as e:
            print_colored(f"    ❌ Erro ao executar poetry: {e}", Colors.RED)
            return False

    def remove_dependencies(
        self,
        project_path: Path,
        dependencies: list[str],
        auto_confirm: bool = False,
    ) -> list[str]:
        """Remove dependências de um projeto Poetry."""
        print_colored(
            f"🗑️ Removendo dependências do projeto {project_path.name}...",
            Colors.BLUE,
        )

        removed = []

        # Backup antes das modificações
        if self.enable_safety and not self.dry_run:
            backup_id = self.backup_manager.create_backup(
                project_path,
                f"before_remove_deps_{project_path.name}",
            )
            print_colored(f"💾 Backup criado: {backup_id}", Colors.CYAN)

        removed = [
            dep for dep in dependencies if self._remove_dependency(project_path, dep)
        ]

        # Resumo das remoções
        if removed:
            print_colored(
                f"\n✅ {len(removed)} dependências removidas com sucesso",
                Colors.GREEN,
            )
        else:
            print_colored(
                "\n⚠️ Nenhuma dependência foi removida",
                Colors.YELLOW,
            )

        return removed

    def _remove_dependency(self, project_path: Path, dependency: str) -> bool:
        """Remove uma dependência individual."""
        cmd = ["poetry", "remove", dependency]

        if self.dry_run:
            cmd.append("--dry-run")

        try:
            print_colored(f"    ➖ Removendo {dependency}...", Colors.YELLOW)

            result = subprocess.run(
                cmd,
                check=False,
                cwd=project_path,
                capture_output=True,
                text=True,
                shell=False,  # Security: explicit shell=False
                timeout=60,  # Prevent hanging
            )

            if result.returncode == 0:
                if not self.dry_run:
                    print_colored(
                        f"    ✅ {dependency} removido com sucesso",
                        Colors.GREEN,
                    )
                else:
                    print_colored(
                        f"    ✅ {dependency} seria removido (dry-run)",
                        Colors.YELLOW,
                    )
                return True

            print_colored(
                f"    ❌ Erro ao remover {dependency}: {result.stderr}",
                Colors.RED,
            )
            return False

        except Exception as e:
            print_colored(f"    ❌ Erro ao executar poetry: {e}", Colors.RED)
            return False

    def update_project(self, project_path: Path) -> bool:
        """Atualiza todas as dependências de um projeto."""
        print_colored(
            f"🔄 Atualizando projeto {project_path.name}...",
            Colors.BLUE,
        )

        # Backup antes da atualização
        if self.enable_safety and not self.dry_run:
            backup_id = self.backup_manager.create_backup(
                project_path,
                f"before_update_{project_path.name}",
            )
            print_colored(f"💾 Backup criado: {backup_id}", Colors.CYAN)

        cmd = ["poetry", "update"]

        if self.dry_run:
            cmd.append("--dry-run")

        try:
            result = subprocess.run(
                cmd,
                check=False,
                cwd=project_path,
                capture_output=True,
                text=True,
                shell=False,  # Security: explicit shell=False
                timeout=300,  # Allow more time for updates
            )

            if result.returncode == 0:
                if not self.dry_run:
                    print_colored("✅ Projeto atualizado com sucesso", Colors.GREEN)
                else:
                    print_colored(
                        "✅ Projeto seria atualizado (dry-run)", Colors.YELLOW,
                    )
                return True

            print_colored(
                f"❌ Erro ao atualizar projeto: {result.stderr}",
                Colors.RED,
            )
            return False

        except Exception as e:
            print_colored(f"❌ Erro ao executar poetry update: {e}", Colors.RED)
            return False

    def lock_project(self, project_path: Path) -> bool:
        """Gera/atualiza poetry.lock."""
        print_colored(
            f"🔒 Gerando lock file para {project_path.name}...",
            Colors.BLUE,
        )

        cmd = ["poetry", "lock"]

        try:
            result = subprocess.run(
                cmd,
                check=False,
                cwd=project_path,
                capture_output=True,
                text=True,
                shell=False,  # Security: explicit shell=False
                timeout=180,  # Allow time for lock generation
            )

            if result.returncode == 0:
                print_colored("✅ Lock file gerado com sucesso", Colors.GREEN)
                return True

            print_colored(
                f"❌ Erro ao gerar lock file: {result.stderr}",
                Colors.RED,
            )
            return False

        except Exception as e:
            print_colored(f"❌ Erro ao executar poetry lock: {e}", Colors.RED)
            return False

    def validate_project(self, project_path: Path) -> bool:
        """Valida configuração do projeto Poetry."""
        print_colored(
            f"✅ Validando projeto {project_path.name}...",
            Colors.BLUE,
        )

        cmd = ["poetry", "check"]

        try:
            result = subprocess.run(
                cmd,
                check=False,
                cwd=project_path,
                capture_output=True,
                text=True,
                shell=False,  # Security: explicit shell=False
                timeout=30,  # Quick validation
            )

            if result.returncode == 0:
                print_colored("✅ Projeto válido", Colors.GREEN)
                return True

            print_colored(
                f"❌ Projeto inválido: {result.stderr}",
                Colors.RED,
            )
            return False

        except Exception as e:
            print_colored(f"❌ Erro ao validar projeto: {e}", Colors.RED)
            return False

"""Operações com Poetry"""

import subprocess
from pathlib import Path

import tomlkit

from flext_tools.safety import BackupManager, SafetyValidator
from flext_tools.utils import Colors, get_logger, print_colored


class PoetryOperations:
    """Gerencia operações com Poetry com sistema de segurança integrado."""

    def __init__(self, dry_run: bool = True, enable_safety: bool = True, logger=None):
        self.dry_run = dry_run
        self.enable_safety = enable_safety
        self.logger = logger or get_logger()

        if self.enable_safety:
            self.backup_manager = BackupManager()
            self.safety_validator = SafetyValidator()
            self.logger.info(
                "INIT", "Sistema de segurança ativado", {"dry_run": dry_run},
            )
            print_colored("🛡️ Sistema de segurança ativado", Colors.CYAN)

    def add_dependencies(
        self,
        project_path: Path,
        dependencies: dict[str, set[str]],
        auto_confirm: bool = False,
    ) -> dict[str, list[str]]:
        """
        Adiciona dependências a um projeto Poetry com validação de segurança.

        Args:
            project_path: Caminho do projeto
            dependencies: Dict com categorias e dependências
            auto_confirm: Confirmar automaticamente

        Returns:
            Dict com dependências adicionadas por categoria
        """
        added = {"runtime": [], "test": [], "dev": []}

        if not dependencies:
            return added

        # Inicia logging da operação
        self.logger.start_operation(
            "ADD_DEPENDENCIES",
            f"Adicionando dependências em {project_path.name}",
            project_path.name,
            {
                "dependencies_count": sum(len(deps) for deps in dependencies.values()),
                "categories": list(dependencies.keys()),
                "dry_run": self.dry_run,
                "auto_confirm": auto_confirm,
            },
        )

        print_colored(
            f"\n📦 Adicionando dependências em {project_path.name}", Colors.BLUE,
        )

        # VALIDAÇÃO DE SEGURANÇA CRÍTICA
        if self.enable_safety:
            print_colored("🔍 Executando validação de segurança...", Colors.YELLOW)

            # Validação pré-operação
            validation_result = self.safety_validator.pre_operation_check(
                project_path, "add_dependencies", {"dependencies": dependencies},
            )

            if not validation_result["safe"]:
                # Log evento de segurança crítico
                self.logger.log_security_event(
                    "OPERATION_BLOCKED",
                    "Operação bloqueada por validação de segurança",
                    validation_result.get("risk_level", "HIGH"),
                    {
                        "errors": validation_result["errors"],
                        "warnings": validation_result["warnings"],
                        "dependencies": dependencies,
                        "project": project_path.name,
                    },
                    "OPERATION_ABORTED",
                )

                print_colored("❌ OPERAÇÃO BLOQUEADA POR SEGURANÇA!", Colors.RED)
                for error in validation_result["errors"]:
                    print_colored(f"   • {error}", Colors.RED)
                for warning in validation_result["warnings"]:
                    print_colored(f"   ⚠️ {warning}", Colors.YELLOW)

                # Finaliza operação com falha
                self.logger.end_operation(
                    success=False,
                    error_message="Operação bloqueada por validação de segurança",
                )
                return added

            # Mostra warnings se houver
            if validation_result["warnings"]:
                print_colored("⚠️ Warnings de segurança:", Colors.YELLOW)
                for warning in validation_result["warnings"]:
                    print_colored(f"   • {warning}", Colors.YELLOW)

                if not auto_confirm and not self.dry_run:
                    response = input("Continuar mesmo com warnings? (s/N): ")
                    if response.lower() not in {"s", "sim", "y", "yes"}:
                        print_colored(
                            "❌ Operação cancelada pelo usuário", Colors.YELLOW,
                        )
                        return added

            # Cria backup OBRIGATÓRIO antes de modificações
            if not self.dry_run:
                backup_id = self.backup_manager.backup_project(project_path)
                self.logger.log_backup_operation(
                    "PROJECT_BACKUP",
                    backup_id,
                    [str(project_path / "pyproject.toml")],
                    success=True,
                )
                print_colored(f"💾 Backup criado: {backup_id}", Colors.GREEN)

            print_colored("✅ Validação de segurança passou", Colors.GREEN)

        # Runtime dependencies
        if dependencies.get("runtime"):
            print_colored("\n  🏃 Dependências runtime:", Colors.CYAN)
            for dep in sorted(dependencies["runtime"]):
                print(f"    - {dep}")

            if auto_confirm or self._confirm_add("runtime"):
                for dep in dependencies["runtime"]:
                    if self._add_dependency(project_path, dep, group=None):
                        added["runtime"].append(dep)
                        self.logger.log_dependency_change(
                            project_path.name, dep, "ADD", category="runtime",
                        )

        # Test dependencies
        if dependencies.get("test"):
            print_colored("\n  🧪 Dependências de teste:", Colors.CYAN)
            for dep in sorted(dependencies["test"]):
                print(f"    - {dep}")

            if auto_confirm or self._confirm_add("test"):
                for dep in dependencies["test"]:
                    if self._add_dependency(project_path, dep, group="test"):
                        added["test"].append(dep)
                        self.logger.log_dependency_change(
                            project_path.name, dep, "ADD", category="test",
                        )

        # Dev dependencies
        if dependencies.get("dev"):
            print_colored("\n  🔧 Dependências de desenvolvimento:", Colors.CYAN)
            for dep in sorted(dependencies["dev"]):
                print(f"    - {dep}")

            if auto_confirm or self._confirm_add("dev"):
                for dep in dependencies["dev"]:
                    if self._add_dependency(project_path, dep, group="dev"):
                        added["dev"].append(dep)
                        self.logger.log_dependency_change(
                            project_path.name, dep, "ADD", category="dev",
                        )

        # Finaliza operação com sucesso
        total_added = sum(len(deps) for deps in added.values())
        self.logger.end_operation(
            success=True,
            result_details={"dependencies_added": added, "total_count": total_added},
        )

        return added

    def _add_dependency(
        self, project_path: Path, dependency: str, group: str | None = None,
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
                cmd, check=False, cwd=project_path, capture_output=True, text=True,
            )

            if result.returncode == 0:
                if not self.dry_run:
                    print_colored(
                        f"    ✅ {dependency} adicionado com sucesso", Colors.GREEN,
                    )
                else:
                    print_colored(
                        f"    ✅ {dependency} seria adicionado (dry-run)", Colors.YELLOW,
                    )
                return True
            print_colored(
                f"    ❌ Erro ao adicionar {dependency}: {result.stderr}", Colors.RED,
            )
            return False

        except Exception as e:
            print_colored(f"    ❌ Erro ao executar poetry: {e}", Colors.RED)
            return False

    def _confirm_add(self, category: str) -> bool:
        """Confirma adição de dependências."""
        if self.dry_run:
            return True

        response = input(f"\n  Adicionar dependências {category}? (s/N): ")
        return response.lower() in {"s", "sim", "y", "yes"}

    def update_dependency_versions(
        self, project_path: Path, version_updates: dict[str, str],
    ) -> bool:
        """
        Atualiza versões de dependências no pyproject.toml.

        Args:
            project_path: Caminho do projeto
            version_updates: Dict {pacote: nova_versão}

        Returns:
            True se sucesso
        """
        pyproject_path = project_path / "pyproject.toml"

        if not pyproject_path.exists():
            print_colored(
                f"❌ pyproject.toml não encontrado em {project_path}", Colors.RED,
            )
            return False

        try:
            # Lê o arquivo preservando formatação
            with Path(pyproject_path).open(encoding="utf-8") as f:
                doc = tomlkit.parse(f.read())

            updated = False

            # Atualiza dependências principais
            deps = doc.get("tool", {}).get("poetry", {}).get("dependencies", {})
            for package, new_version in version_updates.items():
                if package in deps:
                    old_version = deps[package]
                    if isinstance(old_version, dict):
                        old_version["version"] = new_version
                    else:
                        deps[package] = new_version
                    updated = True
                    print_colored(
                        f"  📝 {package}: {old_version} → {new_version}", Colors.CYAN,
                    )

            # Atualiza grupos
            groups = doc.get("tool", {}).get("poetry", {}).get("group", {})
            for group_data in groups.values():
                group_deps = group_data.get("dependencies", {})
                for package, new_version in version_updates.items():
                    if package in group_deps:
                        old_version = group_deps[package]
                        if isinstance(old_version, dict):
                            old_version["version"] = new_version
                        else:
                            group_deps[package] = new_version
                        updated = True

            if updated and not self.dry_run:
                # Salva as mudanças
                with Path(pyproject_path).open("w", encoding="utf-8") as f:
                    f.write(tomlkit.dumps(doc))

                print_colored(
                    f"  ✅ Versões atualizadas em {project_path.name}", Colors.GREEN,
                )
                return True
            if updated:
                print_colored(
                    f"  ✅ Versões seriam atualizadas em {project_path.name} (dry-run)",
                    Colors.YELLOW,
                )
                return True
            print_colored(
                f"  ℹ️ Nenhuma atualização necessária em {project_path.name}",
                Colors.CYAN,
            )
            return True

        except Exception as e:
            print_colored(f"  ❌ Erro ao atualizar versões: {e}", Colors.RED)
            return False

    def get_outdated_packages(self, project_path: Path) -> dict[str, dict]:
        """
        Obtém lista de pacotes desatualizados.

        Args:
            project_path: Caminho do projeto

        Returns:
            Dict com informações de pacotes desatualizados
        """
        try:
            result = subprocess.run(
                ["poetry", "show", "--outdated", "--format", "json"],
                check=False,
                cwd=project_path,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0 and result.stdout:
                # Poetry não tem formato JSON para outdated, vamos parsear a saída
                return self._parse_outdated_output(result.stdout)
            return {}

        except Exception as e:
            print_colored(
                f"  ⚠️ Erro ao verificar pacotes desatualizados: {e}", Colors.YELLOW,
            )
            return {}

    def _parse_outdated_output(self, output: str) -> dict[str, dict]:
        """Parseia saída do poetry show --outdated."""
        outdated = {}

        # Formato esperado:
        # package-name current-version latest-version description
        lines = output.strip().split("\n")

        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                package = parts[0]
                current = parts[1]
                latest = parts[2]

                outdated[package] = {
                    "current": current,
                    "latest": latest,
                    "behind": self._compare_versions(current, latest),
                }

        return outdated

    def _compare_versions(self, current: str, latest: str) -> str:
        """Compara versões e retorna tipo de atualização."""
        try:
            curr_parts = current.split(".")
            late_parts = latest.split(".")

            if len(curr_parts) >= 3 and len(late_parts) >= 3:
                if curr_parts[0] != late_parts[0]:
                    return "major"
                if curr_parts[1] != late_parts[1]:
                    return "minor"
                return "patch"
            return "unknown"
        except:
            return "unknown"

    def lock_dependencies(self, project_path: Path) -> bool:
        """
        Executa poetry lock para atualizar o lock file.

        Args:
            project_path: Caminho do projeto

        Returns:
            True se sucesso
        """
        try:
            print_colored(
                f"  🔒 Atualizando lock file em {project_path.name}...", Colors.CYAN,
            )

            result = subprocess.run(
                ["poetry", "lock", "--no-update"],
                check=False,
                cwd=project_path,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print_colored("  ✅ Lock file atualizado", Colors.GREEN)
                return True
            print_colored(
                f"  ❌ Erro ao atualizar lock file: {result.stderr}", Colors.RED,
            )
            return False

        except Exception as e:
            print_colored(f"  ❌ Erro ao executar poetry lock: {e}", Colors.RED)
            return False

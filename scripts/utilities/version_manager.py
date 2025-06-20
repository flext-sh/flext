#!/usr/bin/env python3
"""
PyAuto Enterprise - Version Manager

Gerencia versões unificadas em todos os submódulos usando __version__.py
como fonte única da verdade.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


class VersionManager:
    """Gerenciador de versões unificado para PyAuto Enterprise."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
        self.submodules = self._get_submodules()

    def _get_submodules(self) -> list[str]:
        """Obtém lista de submódulos do Git."""
        try:
            result = subprocess.run(
                ["git", "submodule", "status"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                check=True
            )
            return [line.split()[1]
                    for line in result.stdout.strip().split('\n') if line.strip()]
        except subprocess.CalledProcessError:
            return []

    def _get_module_name(self, submodule: str) -> str:
        """Converte nome do submódulo para nome do módulo Python."""
        return submodule.replace('-', '_')

    def _ensure_version_file(
            self,
            submodule: str,
            version: str = "0.5.0") -> Path:
        """Garante que o arquivo __version__.py existe com a versão especificada."""
        module_name = self._get_module_name(submodule)
        version_file = self.workspace_root / submodule / \
            "src" / module_name / "__version__.py"

        # Criar diretório se não existir
        version_file.parent.mkdir(parents=True, exist_ok=True)

        # Conteúdo do arquivo __version__.py
        version_content = f'''"""Version information for {submodule}."""

__version__ = "{version}"
__version_info__ = tuple(int(x) for x in __version__.split('.'))

# PyAuto Enterprise - Unified Versioning System
# This is the single source of truth for version information.
# All references to version should import from this module.
'''

        version_file.write_text(version_content)
        print(f"✅ Created/Updated {version_file}")
        return version_file

    def _update_pyproject_toml(self, submodule: str, version: str) -> bool:
        """Atualiza a versão no pyproject.toml do submódulo."""
        pyproject_file = self.workspace_root / submodule / "pyproject.toml"

        if not pyproject_file.exists():
            print(f"⚠️  {submodule}: pyproject.toml não encontrado")
            return False

        content = pyproject_file.read_text()

        # Atualizar versão no pyproject.toml
        version_pattern = r'version\s*=\s*"[^"]*"'
        new_version = f'version = "{version}"'

        if re.search(version_pattern, content):
            content = re.sub(version_pattern, new_version, content)
            pyproject_file.write_text(content)
            print(f"✅ Updated {submodule}/pyproject.toml to version {version}")
            return True
        print(
            f"❌ {submodule}: Não foi possível encontrar linha de versão em pyproject.toml")
        return False

    def _update_init_file(self, submodule: str) -> bool:
        """Atualiza __init__.py para importar __version__ de __version__.py."""
        module_name = self._get_module_name(submodule)
        init_file = self.workspace_root / submodule / "src" / module_name / "__init__.py"

        if not init_file.exists():
            # Criar __init__.py se não existir
            init_file.parent.mkdir(parents=True, exist_ok=True)
            init_content = f'''"""PyAuto Enterprise - {submodule} component."""

from {module_name}.__version__ import __version__, __version_info__

__all__ = ["__version__", "__version_info__"]
'''
            init_file.write_text(init_content)
            print(f"✅ Created {init_file} with version import")
            return True

        content = init_file.read_text()

        # Verificar se já importa __version__
        if "__version__" in content and f"from {module_name}.__version__" in content:
            print(f"ℹ️  {submodule}: __init__.py já importa __version__")
            return True

        # Adicionar import de versão se não existir
        version_import = f"from {module_name}.__version__ import __version__, __version_info__"

        if "__version__" not in content:
            # Adicionar no início do arquivo, após docstring se existir
            lines = content.split('\n')
            insert_index = 0

            # Encontrar local para inserir (após docstring)
            if lines and lines[0].strip().startswith('"""'):
                for i, line in enumerate(lines):
                    if i > 0 and '"""' in line:
                        insert_index = i + 1
                        break

            lines.insert(insert_index, version_import)

            # Atualizar __all__ se existir
            for i, line in enumerate(lines):
                if line.strip().startswith("__all__"):
                    if "__version__" not in line:
                        lines[i] = line.replace(
                            "]", ', "__version__", "__version_info__"]')
                    break
                # Adicionar __all__ se não existir
                lines.insert(insert_index + 1,
                             '\n__all__ = ["__version__", "__version_info__"]')

            init_file.write_text('\n'.join(lines))
            print(f"✅ Updated {init_file} to import __version__")
            return True

        return False

    def _find_version_references(
            self, submodule: str) -> list[tuple[Path, int, str]]:
        """Encontra todas as referências de versão hardcoded no código."""
        module_path = self.workspace_root / submodule / "src"
        references: list = []

        if not module_path.exists():
            return references

        # Padrões para encontrar versões hardcoded
        version_patterns = [
            r'version\s*=\s*["\'](\d+\.\d+\.\d+)["\']',
            r'__version__\s*=\s*["\'](\d+\.\d+\.\d+)["\']',
            r'VERSION\s*=\s*["\'](\d+\.\d+\.\d+)["\']',
        ]

        for py_file in module_path.rglob("*.py"):
            if py_file.name == "__version__.py":
                continue  # Skip the version file itself

            try:
                content = py_file.read_text()
                lines = content.split('\n')

                for line_num, line in enumerate(lines, 1):
                    for pattern in version_patterns:
                        if re.search(pattern, line):
                            references.append(
                                (py_file, line_num, line.strip()))
            except Exception as e:
                print(f"⚠️  Erro ao ler {py_file}: {e}")

        return references

    def set_version(
            self,
            version: str,
            submodules: list[str] | None = None) -> bool:
        """Define versão em todos os submódulos ou submódulos específicos."""
        if submodules is None:
            submodules = self.submodules

        print(
            f"🚀 Definindo versão {version} em {
                len(submodules)} submódulos...")

        success_count = 0
        for submodule in submodules:
            print(f"\n📦 Processando {submodule}...")

            # Verificar se submódulo existe
            submodule_path = self.workspace_root / submodule
            if not submodule_path.exists():
                print(f"❌ {submodule}: Diretório não encontrado")
                continue

            try:
                # 1. Criar/atualizar __version__.py
                self._ensure_version_file(submodule, version)

                # 2. Atualizar pyproject.toml
                if self._update_pyproject_toml(submodule, version):
                    success_count += 1

                # 3. Atualizar __init__.py
                self._update_init_file(submodule)

                print(f"✅ {submodule}: Versão atualizada para {version}")

            except Exception as e:
                print(f"❌ {submodule}: Erro ao atualizar versão: {e}")

        print(
            f"\n📊 Resultado: {success_count}/{len(submodules)} submódulos atualizados")
        return success_count == len(submodules)

    def get_versions(self) -> dict[str, str]:
        """Obtém versões atuais de todos os submódulos."""
        versions: dict = {}

        for submodule in self.submodules:
            pyproject_file = self.workspace_root / submodule / "pyproject.toml"

            if pyproject_file.exists():
                content = pyproject_file.read_text()
                version_match = re.search(r'version\s*=\s*"([^"]*)"', content)
                if version_match:
                    versions[submodule] = version_match.group(1)
                    versions[submodule] = "unknown"
                versions[submodule] = "no-pyproject"

        return versions

    def check_consistency(self) -> bool:
        """Verifica consistência de versões em todos os submódulos."""
        print("🔍 Verificando consistência de versões...")

        versions = self.get_versions()
        inconsistencies: list = []

        for submodule, version in versions.items():
            # Verificar se __version__.py existe e está sincronizado
            module_name = self._get_module_name(submodule)
            version_file = self.workspace_root / submodule / \
                "src" / module_name / "__version__.py"

            if version_file.exists():
                try:
                    version_content = version_file.read_text()
                    version_match = re.search(
                        r'__version__\s*=\s*"([^"]*)"', version_content)
                    if version_match:
                        file_version = version_match.group(1)
                        if file_version != version:
                            inconsistencies.append(
                                f"{submodule}: pyproject.toml({version}) != __version__.py({file_version})")
                        inconsistencies.append(
                            f"{submodule}: __version__.py malformado")
                except Exception as e:
                    inconsistencies.append(
                        f"{submodule}: Erro ao ler __version__.py: {e}")
                inconsistencies.append(
                    f"{submodule}: __version__.py não encontrado")

        if inconsistencies:
            print("❌ Inconsistências encontradas:")
            for issue in inconsistencies:
                print(f"  • {issue}")
            return False
        print("✅ Todas as versões estão consistentes")
        return True

    def audit_hardcoded_versions(
            self) -> dict[str, list[tuple[Path, int, str]]]:
        """Auditoria de versões hardcoded no código."""
        print("🔍 Auditando versões hardcoded...")

        all_references: dict = {}

        for submodule in self.submodules:
            references = self._find_version_references(submodule)
            if references:
                all_references[submodule] = references

        if all_references:
            print("⚠️  Versões hardcoded encontradas:")
            for submodule, refs in all_references.items():
                print(f"\n📦 {submodule}:")
                for file_path, line_num, line in refs:
                    rel_path = file_path.relative_to(self.workspace_root)
                    print(f"  • {rel_path}:{line_num} - {line}")
            print("✅ Nenhuma versão hardcoded encontrada")

        return all_references


def main() -> None:
    """Função principal."""
    parser = argparse.ArgumentParser(description="PyAuto Version Manager")
    parser.add_argument(
        "--workspace",
        default=".",
        help="Workspace root directory")

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands")

    # Comando set
    set_parser = subparsers.add_parser(
        "set", help="Set version in all or specific submodules")
    set_parser.add_argument("version", help="Version to set (e.g., 0.5.0)")
    set_parser.add_argument(
        "--submodules",
        nargs="*",
        help="Specific submodules (default: all)")

    # Comando get
    subparsers.add_parser("get", help="Get current versions")

    # Comando check
    subparsers.add_parser("check", help="Check version consistency")

    # Comando audit
    subparsers.add_parser("audit", help="Audit hardcoded versions")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    manager = VersionManager(Path(args.workspace))

    if args.command == "set":
        success = manager.set_version(args.version, args.submodules)
        return 0 if success else 1

    if args.command == "get":
        versions = manager.get_versions()
        print("📋 Versões atuais:")
        for submodule, version in sorted(versions.items()):
            print(f"  {submodule}: {version}")
        return 0

    if args.command == "check":
        consistent = manager.check_consistency()
        return 0 if consistent else 1

    if args.command == "audit":
        manager.audit_hardcoded_versions()
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())

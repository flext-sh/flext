#!/usr/bin/env python3
"""FLEXT Script Registry - Sistema de Automação e Organização de Scripts.

Este módulo fornece um sistema centralizado para registrar, categorizar e executar
scripts do workspace FLEXT de forma padronizada e automatizada.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from flext_core.patterns.logging import get_logger

# Usar flext_tools completo para máxima enterprise
from flext_tools.core.script_base import ScriptMetadata
from flext_tools.utils import Colors, print_colored


class ScriptCategory(StrEnum):
    """Categorias de scripts - compatibilidade com sistema legacy."""

    CONFIG = "config"
    QUALITY = "quality"
    DEPS = "dependencies"
    SECURITY = "security"
    MAINTENANCE = "maintenance"
    UTILITIES = "utilities"


class ScriptPriority(StrEnum):
    """Prioridades de execução - compatibilidade com sistema legacy."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class LegacyScriptMetadata:
    """Metadados estendidos para compatibilidade com sistema legacy."""

    name: str
    description: str
    category: ScriptCategory
    priority: ScriptPriority
    file_path: Path
    requires_venv: bool = True
    dependencies: list[str] = field(default_factory=list)

    @property
    def makefile_target(self) -> str:
        """Gera target do Makefile para este script."""
        return f"script-{self.name.replace('_', '-')}"

    def to_script_metadata(self) -> ScriptMetadata:
        """Converte para ScriptMetadata padrão do flext_tools."""
        return ScriptMetadata(
            name=self.name,
            description=self.description,
            category=self.category.value,
            version="1.0.0",
        )


class ScriptRegistry:
    """Registry para descoberta automática de scripts."""

    def __init__(self) -> None:
        """Inicializa o registry."""
        self.scripts_root = Path(__file__).parent.parent
        self._scripts: dict[str, ScriptMetadata] = {}
        self._discover_scripts()

    def _discover_scripts(self) -> None:
        """Descobre automaticamente todos os scripts."""
        for script_file in self.scripts_root.rglob("*.py"):
            # Skip arquivos especiais
            if script_file.name.startswith(("__", "test_")) or script_file.name == "flext_tools.py":
                get_logger(__name__).debug("Failed to parse script metadata")

            # Skip core system files
            if script_file.parent.name == "core":
                get_logger(__name__).debug("Failed to parse script metadata")

            metadata = self._extract_metadata(script_file)
            if metadata:
                self._scripts[metadata.name] = metadata

    def _extract_metadata(self, script_path: Path) -> ScriptMetadata:
        """Extrai metadados do script."""
        try:
            # Tenta extrair usando o padrão FlextScript
            with open(script_path, encoding="utf-8") as f:
                content = f.read()

            # Procura por metadados no formato FlextScript
            metadata_match = re.search(
                r"class\s+(\w+)\s*\([^)]*FlextScript[^)]*\):.*?"
                r'"""([^"]*?)""".*?'
                r"def\s+__init__\s*\([^)]*\):",
                content,
                re.DOTALL,
            )

            if metadata_match:
                class_name = metadata_match.group(1)
                description = metadata_match.group(2).strip()

                return ScriptMetadata(
                    name=class_name,
                    description=description,
                    category="flext_script",
                )

            # Fallback para scripts legados
            legacy_metadata = self._extract_legacy_metadata(script_path)
            if legacy_metadata:
                return legacy_metadata

            # Metadados mínimos se nada for encontrado
            return ScriptMetadata(
                name=script_path.stem,
                description="Script sem metadados",
                category="unknown",
            )

        except Exception as e:
            print_colored(
                f"❌ Erro ao extrair metadados de {script_path}: {e}",
                Colors.RED,
            )
            return ScriptMetadata(
                name=script_path.stem,
                description="Erro ao extrair metadados",
                category="error",
            )

    def _extract_legacy_metadata(self, script_path: Path) -> ScriptMetadata | None:
        """Extrai metadados de scripts legados."""
        try:
            with open(script_path, encoding="utf-8") as f:
                content = f.read()

            # Procura por docstring no início do arquivo
            docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            description = docstring_match.group(1).strip() if docstring_match else "Script legado"

            # Procura por função main
            main_match = re.search(r"def\s+main\s*\(", content)
            if main_match:
                return ScriptMetadata(
                    name=script_path.stem,
                    description=description,
                    category="legacy_main",
                )

            return None

        except Exception:
            return None

    def _convert_from_flext_metadata(
        self,
        flext_metadata: ScriptMetadata,
        script_file: Path,
    ) -> LegacyScriptMetadata:
        """Converte ScriptMetadata do flext_tools para LegacyScriptMetadata."""
        # Mapear categoria string para enum
        category_map = {
            "config": ScriptCategory.CONFIG,
            "quality": ScriptCategory.QUALITY,
            "dependencies": ScriptCategory.DEPS,
            "security": ScriptCategory.SECURITY,
            "maintenance": ScriptCategory.MAINTENANCE,
            "utilities": ScriptCategory.UTILITIES,
        }

        category = category_map.get(flext_metadata.category, ScriptCategory.UTILITIES)

        # Determinar prioridade baseada na categoria
        priority_map = {
            ScriptCategory.CONFIG: ScriptPriority.CRITICAL,
            ScriptCategory.QUALITY: ScriptPriority.HIGH,
            ScriptCategory.SECURITY: ScriptPriority.HIGH,
            ScriptCategory.DEPS: ScriptPriority.MEDIUM,
            ScriptCategory.MAINTENANCE: ScriptPriority.MEDIUM,
            ScriptCategory.UTILITIES: ScriptPriority.LOW,
        }

        priority = priority_map.get(category, ScriptPriority.LOW)

        return LegacyScriptMetadata(
            name=flext_metadata.name,
            description=flext_metadata.description,
            category=category,
            priority=priority,
            file_path=script_file,
            requires_venv=True,
        )

    def _create_fallback_metadata(self, script_file: Path) -> LegacyScriptMetadata:
        """Cria metadados básicos para scripts legacy."""
        # Determinar categoria pela pasta
        category_map = {
            "config": ScriptCategory.CONFIG,
            "quality": ScriptCategory.QUALITY,
            "dependencies": ScriptCategory.DEPS,
            "security": ScriptCategory.SECURITY,
            "maintenance": ScriptCategory.MAINTENANCE,
            "utilities": ScriptCategory.UTILITIES,
        }

        category = category_map.get(script_file.parent.name, ScriptCategory.UTILITIES)

        # Determinar prioridade baseada na categoria
        priority_map = {
            ScriptCategory.CONFIG: ScriptPriority.CRITICAL,
            ScriptCategory.QUALITY: ScriptPriority.HIGH,
            ScriptCategory.SECURITY: ScriptPriority.HIGH,
            ScriptCategory.DEPS: ScriptPriority.MEDIUM,
            ScriptCategory.MAINTENANCE: ScriptPriority.MEDIUM,
            ScriptCategory.UTILITIES: ScriptPriority.LOW,
        }

        priority = priority_map.get(category, ScriptPriority.LOW)

        # Extrair descrição do docstring se possível
        description = self._extract_description(script_file)

        return LegacyScriptMetadata(
            name=script_file.stem,
            description=description,
            category=category,
            priority=priority,
            file_path=script_file,
            requires_venv=True,
        )

    def _extract_description(self, script_file: Path) -> str:
        """Extrai descrição do docstring do arquivo."""
        try:
            content = script_file.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Procurar primeira linha de docstring
            in_docstring = False
            for original_line in lines[:20]:  # Primeiras 20 linhas
                line = original_line.strip()
                if line.startswith(('"""', "'''")):
                    if line.count('"""') == 2 or line.count("'''") == 2:
                        # Docstring de linha única
                        return line.replace("'''", "").replace('"""', "").strip()
                    in_docstring = True
                    get_logger(__name__).debug("Failed to parse script metadata")
                if in_docstring and (line.endswith(('"""', "'''"))):
                    return line.replace("'''", "").replace('"""', "").strip()
                if in_docstring and line and not line.startswith("#"):
                    return line.strip()

            return f"Script {script_file.stem}"

        except Exception:
            return f"Script {script_file.stem}"

    def get_script(self, name: str) -> ScriptMetadata | None:
        """Obtém metadados de um script específico."""
        return self._scripts.get(name)

    def list_scripts(
        self,
        category: str | None = None,
    ) -> list[ScriptMetadata]:
        """Lista scripts filtrados por categoria."""
        scripts = list(self._scripts.values())

        if category:
            scripts = [s for s in scripts if s.category == category]

        # Ordenar por nome
        return sorted(scripts, key=lambda s: s.name)

    def get_scripts_count(self) -> int:
        """Retorna o número total de scripts."""
        return len(self._scripts)

    def get_categories(self) -> set[str]:
        """Retorna as categorias disponíveis."""
        return {script.category for script in self._scripts.values()}

    def generate_makefile_targets(self) -> str:
        """Gera targets do Makefile para todos os scripts."""
        lines = ["# 📜 SCRIPTS AUTOMATIZADOS", "# =" * 50, ""]

        # Por categoria
        categories = self.get_categories()
        for category in sorted(categories):
            category_scripts = self.list_scripts(category=category)
            if not category_scripts:
                continue

            lines.extend(
                (
                    f"# {category.title()} Scripts",
                    f"scripts-{category}: ## Execute todos os scripts de {category}",
                ),
            )
            lines.extend(
                [f"\t@python scripts/core/script_runner.py {script.name}" for script in category_scripts],
            )
            lines.append("")

            # Scripts individuais
            for script in category_scripts:
                lines.extend(
                    (
                        f"{script.name}: ## {script.description}",
                        f"\t@python scripts/core/script_runner.py {script.name}",
                    ),
                )
            lines.append("")

        return "\n".join(lines)

    def cleanup(self) -> None:
        """Limpeza após execução."""


def main() -> int:
    """Função principal para descobrir e listar scripts."""
    registry = ScriptRegistry()

    print("📜 FLEXT Script Registry")
    print("=" * 50)
    print(f"Workspace: {registry.scripts_root}")
    print(f"Scripts encontrados: {registry.get_scripts_count()}")
    print()

    # Lista por categoria
    categories = registry.get_categories()
    for category in sorted(categories):
        scripts = registry.list_scripts(category=category)
        if scripts:
            print(f"📁 {category.title()}: {len(scripts)} scripts")
            for script in scripts:
                print(f"  • {script.name} - {script.description}")
            print()

    return 0


if __name__ == "__main__":
    sys.exit(main())

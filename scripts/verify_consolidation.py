#!/usr/bin/env python3
"""
FLEXT Scripts Consolidation Verification - 100% Truth Check
===========================================================

HONESTIDADE BRUTAL: Este script verifica se REALMENTE todos os scripts
estão organizados e não há nada espalhado pelo workspace.

Zero tolerance para scripts não organizados.
"""

import subprocess
import sys
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


class ConsolidationVerifier:
    """Verifica se consolidação está 100% completa."""

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root

    def find_unorganized_scripts(self) -> list[Path]:
        """Encontra scripts não organizados."""
        patterns = ["*fix*.py", "*enforce*.py", "*audit*.py", "*modernize*.py"]
        unorganized = []

        for pattern in patterns:
            for script in self.workspace_root.rglob(pattern):
                # Excluir locais organizados e legítimos
                if any(exclude in str(script) for exclude in [
                    ".venv", "__pycache__", "/legacy/", "/tests/",
                    "/examples/", "/archive", ".git"
                ]):
                    continue

                # Se chegou aqui, não está organizado
                unorganized.append(script)

        return unorganized

    def verify_quality_gateway_functional(self) -> tuple[bool, str]:
        """Verifica se o quality gateway funciona."""
        try:
            qg_path = self.workspace_root / "scripts" / "quality_gateway.py"
            if not qg_path.exists():
                return False, "quality_gateway.py não existe"

            # Testar help
            result = subprocess.run(
                ["python", str(qg_path), "--help"],
                check=False, capture_output=True,
                text=True,
                timeout=10,
                cwd=self.workspace_root
            )

            if result.returncode != 0:
                return False, f"quality_gateway.py --help falhou: {result.stderr}"

            return True, "Quality gateway funcional"

        except Exception as e:
            return False, f"Erro testando quality gateway: {e}"

    def count_scripts_by_location(self) -> dict:
        """Conta scripts por localização."""
        patterns = ["*fix*.py", "*enforce*.py", "*audit*.py", "*modernize*.py"]
        counts = {
            "scripts/legacy": 0,
            "project_scripts/legacy": 0,
            "tests": 0,
            "examples": 0,
            "archive": 0,
            "unorganized": 0
        }

        for pattern in patterns:
            for script in self.workspace_root.rglob(pattern):
                script_str = str(script)

                if ".venv" in script_str or "__pycache__" in script_str or ".git" in script_str:
                    continue
                if "scripts/legacy" in script_str:
                    counts["scripts/legacy"] += 1
                elif "/legacy/" in script_str:
                    counts["project_scripts/legacy"] += 1
                elif "/tests/" in script_str:
                    counts["tests"] += 1
                elif "/examples/" in script_str:
                    counts["examples"] += 1
                elif "/archive" in script_str:
                    counts["archive"] += 1
                else:
                    counts["unorganized"] += 1

        return counts

    def run_verification(self) -> bool:
        """Executa verificação completa."""
        self._print("🔍 VERIFICAÇÃO DE CONSOLIDAÇÃO - 100% TRUTH CHECK")
        self._print("=" * 60)

        # 1. Verificar scripts não organizados
        unorganized = self.find_unorganized_scripts()
        if unorganized:
            self._print(f"\n🚨 FALHA: {len(unorganized)} scripts não organizados encontrados!")
            for script in unorganized:
                self._print(f"  ❌ {script.relative_to(self.workspace_root)}")
            return False
        self._print("\n✅ SUCESSO: Zero scripts não organizados")

        # 2. Verificar quality gateway
        qg_works, qg_msg = self.verify_quality_gateway_functional()
        if qg_works:
            self._print(f"✅ QUALITY GATEWAY: {qg_msg}")
        else:
            self._print(f"❌ QUALITY GATEWAY: {qg_msg}")
            return False

        # 3. Contar scripts por localização
        counts = self.count_scripts_by_location()
        self._print("\n📊 DISTRIBUIÇÃO DE SCRIPTS:")

        if RICH_AVAILABLE:
            table = Table(title="Scripts por Localização")
            table.add_column("Localização", style="cyan")
            table.add_column("Quantidade", style="green")
            table.add_column("Status", style="yellow")

            for location, count in counts.items():
                if location == "unorganized":
                    status = "🚨 PROBLEMA" if count > 0 else "✅ OK"
                else:
                    status = "✅ ORGANIZADO"
                table.add_row(location, str(count), status)

            console.print(table)
        else:
            for location, count in counts.items():
                status = "🚨 PROBLEMA" if location == "unorganized" and count > 0 else "✅"
                self._print(f"  {status} {location}: {count} scripts")

        # 4. Verificação final
        if counts["unorganized"] == 0:
            self._print("\n🎉 VERIFICAÇÃO COMPLETA: 100% CONSOLIDADO E ORGANIZADO!")
            self._print("📊 Total de scripts organizados:", sum(counts.values()))
            return True
        self._print(f"\n🚨 FALHA: {counts['unorganized']} scripts ainda não organizados")
        return False

    def _print(self, message: str, extra: str = "") -> None:
        """Print otimizado."""
        full_message = f"{message} {extra}".strip()
        if RICH_AVAILABLE and console:
            console.print(full_message)
        else:
            print(full_message)


def main() -> int:
    """Função principal."""
    workspace_root = Path("/home/marlonsc/flext")

    if not workspace_root.exists():
        print(f"❌ Workspace não encontrado: {workspace_root}")
        return 1

    verifier = ConsolidationVerifier(workspace_root)
    success = verifier.run_verification()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

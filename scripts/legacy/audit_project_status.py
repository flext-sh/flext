#!/usr/bin/env python3
"""
Script para auditoria completa do status real dos projetos FLEXT.

Este script verifica a implementação real de cada módulo e gera relatório
honesto sobre o status atual, substituindo documentação inflada.
"""

import os
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any


class ProjectAuditor:
    """Auditor para verificar status real dos projetos FLEXT."""

    def __init__(self, workspace_root: str) -> None:
        self.workspace_root = Path(workspace_root)
        self.results: dict[str, dict[str, Any]] = {}

    def audit_all_projects(self) -> dict[str, dict[str, Any]]:
        """Audita todos os projetos FLEXT."""
        projects = self._find_flext_projects()

        for project in projects:
            print(f"🔍 Auditando {project}...")
            self.results[project] = self._audit_project(project)

        return self.results

    def _find_flext_projects(self) -> list[str]:
        """Encontra todos os projetos FLEXT."""

        projects = [item.name for item in self.workspace_root.iterdir() if item.is_dir() and item.name.startswith(("flext-", "flexcore"))]

        # Adiciona projetos cliente
        client_projects = ["algar-oud-mig", "gruponos-poc-oic-wms"]
        projects.extend(project for project in client_projects if (self.workspace_root / project).exists())

        return sorted(projects)

    def _audit_project(self, project_name: str) -> dict[str, Any]:
        """Audita um projeto específico."""
        project_path = self.workspace_root / project_name

        audit_result = {
            "project_name": project_name,
            "type": self._classify_project(project_name),
            "has_src": (project_path / "src").exists(),
            "has_tests": (project_path / "tests").exists(),
            "has_pyproject": (project_path / "pyproject.toml").exists(),
            "has_go_mod": (project_path / "go.mod").exists(),
            "documentation": self._audit_documentation(project_path),
            "implementation": self._audit_implementation(project_path),
            "tests": self._audit_tests(project_path),
            "status": "unknown",
        }

        # Determina status baseado em evidências
        audit_result["status"] = self._determine_status(audit_result)

        return audit_result

    def _classify_project(self, project_name: str) -> str:
        """Classifica o tipo de projeto."""
        if project_name == "flexcore":
            return "go_core"
        if project_name.startswith("flext-"):
            if project_name in {"flext-core", "flext-auth", "flext-api"}:
                return "python_core"
            if project_name.startswith(("flext-tap-", "flext-target-")):
                return "singer_plugin"
            return "python_extension"
        if project_name in {"algar-oud-mig", "gruponos-poc-oic-wms"}:
            return "client_project"
        return "unknown"

    def _audit_documentation(self, project_path: Path) -> dict[str, Any]:
        """Audita documentação do projeto."""
        docs = {
            "has_claude_md": (project_path / "CLAUDE.md").exists(),
            "has_claude_local": (project_path / "CLAUDE.local.md").exists(),
            "has_readme": (project_path / "README.md").exists(),
            "docs_folder": (project_path / "docs").exists(),
            "inflated_claims": False,
            "status_claims": [],
        }

        # Verifica claims infladas
        for doc_file in ["CLAUDE.md", "CLAUDE.local.md", "README.md"]:
            doc_path = project_path / doc_file
            if doc_path.exists():
                content = doc_path.read_text()
                if any(
                    claim in content
                    for claim in ["100% operacional", "100% Complete", "OPERATIONAL"]
                ):
                    docs["inflated_claims"] = True
                    docs["status_claims"].append(doc_file)  # type: ignore[attr-defined]

        return docs

    def _audit_implementation(self, project_path: Path) -> dict[str, Any]:
        """Audita implementação real do projeto."""
        impl: dict[str, Any] = {
            "python_files": 0,
            "go_files": 0,
            "total_lines": 0,
            "not_implemented_count": 0,
            "todo_count": 0,
            "has_real_implementation": False,
            "main_modules": [],
        }

        # Conta arquivos Python
        if (project_path / "src").exists():
            for py_file in (project_path / "src").rglob("*.py"):
                impl["python_files"] += 1
                try:
                    content = py_file.read_text()
                    lines = content.count("\n")
                    impl["total_lines"] += lines

                    # Conta NotImplementedError
                    impl["not_implemented_count"] += content.count(
                        "NotImplementedError"
                    )

                    # Conta TODOs
                    impl["todo_count"] += content.count("TODO")

                    # Verifica se tem implementação real (não apenas imports/stubs)
                    if lines > 50 and impl["not_implemented_count"] < lines * 0.1:
                        impl["has_real_implementation"] = True
                        impl["main_modules"].append(py_file.name)
                except Exception:
                    # Pula arquivos com problemas de encoding
                    continue

        # Conta arquivos Go
        for go_file in project_path.rglob("*.go"):
            impl["go_files"] += 1
            try:
                content = go_file.read_text()
                impl["total_lines"] += content.count("\n")
                impl["has_real_implementation"] = True
            except Exception:
                # Pula arquivos com problemas de encoding
                continue

        return impl

    def _audit_tests(self, project_path: Path) -> dict[str, Any]:
        """Audita testes do projeto."""
        tests = {
            "has_test_folder": (project_path / "tests").exists(),
            "test_files": 0,
            "total_test_lines": 0,
            "has_real_tests": False,
        }

        if tests["has_test_folder"]:
            for test_file in (project_path / "tests").rglob("test_*.py"):
                tests["test_files"] += 1
                content = test_file.read_text()
                lines = content.count("\n")
                tests["total_test_lines"] += lines

                # Verifica se tem testes reais
                if "def test_" in content and lines > 20:
                    tests["has_real_tests"] = True

        return tests

    def _determine_status(self, audit_result: dict[str, Any]) -> str:
        """Determina status real baseado em evidências."""
        impl = audit_result["implementation"]
        audit_result["documentation"]

        if impl["has_real_implementation"] and impl["not_implemented_count"] < 5:
            return "functional"
        if impl["has_real_implementation"] and impl["not_implemented_count"] < 20:
            return "partial"
        if impl["total_lines"] > 1000 and impl["not_implemented_count"] > 20:
            return "inflated"
        if impl["total_lines"] < 100:
            return "stub"
        return "development"

    def generate_report(self) -> str:
        """Gera relatório completo da auditoria."""
        report = []
        report.extend(("# 📊 RELATÓRIO DE AUDITORIA REAL DOS PROJETOS FLEXT", "", "**Data da Auditoria**: " + subprocess.check_output(["date"]).decode().strip(), ""))

        # Agrupa por tipo
        by_type = defaultdict(list)
        for project, data in self.results.items():
            by_type[data["type"]].append((project, data))

        for project_type, projects in by_type.items():
            report.extend((f"## 🏗️ {project_type.upper()}", ""))

            for project_name, data in projects:
                status_emoji = self._get_status_emoji(data["status"])
                report.extend((f"### {status_emoji} {project_name}", f"**Status Real**: {data['status']}", f"**Arquivos Python**: {data['implementation']['python_files']}", f"**Total de Linhas**: {data['implementation']['total_lines']}", f"**NotImplementedError**: {data['implementation']['not_implemented_count']}", f"**TODOs**: {data['implementation']['todo_count']}"))

                if data["documentation"]["inflated_claims"]:
                    report.append("⚠️  **DOCUMENTAÇÃO INFLADA DETECTADA**")

                report.append("")

        return "\n".join(report)

    def _get_status_emoji(self, status: str) -> str:
        """Retorna emoji baseado no status."""
        status_emojis = {
            "functional": "✅",
            "partial": "🔄",
            "inflated": "❌",
            "stub": "📝",
            "development": "🚧",
            "unknown": "❓",
        }
        return status_emojis.get(status, "❓")


def main() -> None:
    """Função principal."""
    workspace_root = os.getcwd()
    auditor = ProjectAuditor(workspace_root)

    print("🔍 Iniciando auditoria completa dos projetos FLEXT...")
    results = auditor.audit_all_projects()

    print("\n📝 Gerando relatório...")
    report = auditor.generate_report()

    # Salva relatório
    report_path = Path(workspace_root) / "AUDIT_REPORT_REAL_STATUS.md"
    report_path.write_text(report)

    print(f"✅ Relatório salvo em: {report_path}")
    print("\n" + "=" * 50)
    print("RESUMO DA AUDITORIA:")
    print("=" * 50)

    for project, data in results.items():
        status_emoji = auditor._get_status_emoji(data["status"])
        print(f"{status_emoji} {project}: {data['status']}")


if __name__ == "__main__":
    main()

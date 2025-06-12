#!/usr/bin/env python3
"""
Script de Resolução de Conflitos de Dependências
Resolve conflitos e isola projetos adequadamente
"""

from pathlib import Path

import tomli
import tomli_w
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


class DependencyResolver:
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.projects: list[Path] = []

    def find_projects(self) -> list[Path]:
        """Encontra todos os projetos com pyproject.toml"""
        projects = []
        seen_projects = set()

        for path in self.workspace_path.rglob("pyproject.toml"):
            if any(
                part.startswith(".")
                and part in {".venv", ".mypy_cache", ".pytest_cache"}
                for part in path.parts
            ):
                continue

            project_path = path.parent
            if project_path.name not in seen_projects:
                projects.append(project_path)
                seen_projects.add(project_path.name)

        return projects

    def analyze_conflicts(self):
        """Analisa conflitos entre projetos"""
        console.print(
            Panel.fit("🔍 Analisando Conflitos de Dependências", style="bold blue")
        )

        self.projects = self.find_projects()
        conflicts = {}

        for project_path in self.projects:
            config_path = project_path / "pyproject.toml"
            if not config_path.exists():
                continue

            try:
                with open(config_path, "rb") as f:
                    config = tomli.load(f)

                deps = config.get("tool", {}).get("poetry", {}).get("dependencies", {})
                conflicts[project_path.name] = {}

                for dep, version in deps.items():
                    if dep == "python":
                        continue
                    conflicts[project_path.name][dep] = version

            except Exception as e:
                console.print(f"[red]Erro ao analisar {project_path.name}: {e}[/red]")

        return conflicts

    def resolve_version_conflicts(self, conflicts: dict):
        """Propõe resoluções para conflitos de versão"""
        console.print("\n📊 Análise de Conflitos:")

        # Agrupa dependências comuns
        common_deps = {}
        for project, deps in conflicts.items():
            for dep, version in deps.items():
                if dep not in common_deps:
                    common_deps[dep] = {}
                common_deps[dep][project] = version

        # Identifica conflitos
        conflicted_deps = {}
        for dep, projects in common_deps.items():
            versions = {str(v) for v in projects.values()}  # Converte para string
            if len(versions) > 1:
                conflicted_deps[dep] = projects

        if conflicted_deps:
            table = Table(title="Dependências Conflitantes")
            table.add_column("Dependência", style="cyan")
            table.add_column("Versões Conflitantes", style="red")
            table.add_column("Projetos Afetados", style="yellow")

            for dep, projects in conflicted_deps.items():
                versions = ", ".join({str(v) for v in projects.values()})
                project_list = ", ".join(projects.keys())
                table.add_row(dep, versions, project_list)

            console.print(table)

            # Propõe resolução
            proposed_resolutions = self.propose_resolutions(conflicted_deps)
            self.display_resolutions(proposed_resolutions)

        return conflicted_deps

    def propose_resolutions(self, conflicts: dict) -> dict:
        """Propõe resoluções baseadas em compatibilidade"""
        resolutions = {}

        # Mapeamento de versões compatíveis conhecidas
        compatible_versions = {
            "click": "^8.1.8",  # Versão mais compatível
            "pydantic": "^2.11.4",  # Versão estável
            "django": "^4.2.0",  # LTS version
            "django-filter": "^23.0",
            "pylint": "^2.17.0",  # Versão compatível
            "safety": "^2.3.0",  # Versão compatível
            "typer": "^0.15.0",  # Versão atual
            "singer_sdk": "^0.46.3",
            "meltano": "^3.7.0",
            "aiofiles": "^24.1.0",
            "xmltodict": "^0.14.0",
        }

        for dep in conflicts:
            if dep in compatible_versions:
                resolutions[dep] = compatible_versions[dep]
            else:
                # Usa a versão mais restritiva como base
                versions = list(conflicts[dep].values())
                resolutions[dep] = versions[0]  # Placeholder

        return resolutions

    def display_resolutions(self, resolutions: dict):
        """Exibe as resoluções propostas"""
        console.print("\n💡 Resoluções Propostas:")

        table = Table(title="Versões Recomendadas")
        table.add_column("Dependência", style="cyan")
        table.add_column("Versão Recomendada", style="green")
        table.add_column("Motivo", style="blue")

        reasons = {
            "click": "Compatibilidade máxima",
            "pydantic": "Versão estável atual",
            "django": "Versão LTS",
            "django-filter": "Compatível com Django 4.2",
            "pylint": "Compatível com Python 3.13",
            "safety": "Versão estável",
            "typer": "Versão mais recente estável",
            "singer_sdk": "Versão requerida pelos taps",
            "meltano": "Versão compatível",
            "aiofiles": "Versão async estável",
            "xmltodict": "Versão atualizada",
        }

        for dep, version in resolutions.items():
            reason = reasons.get(dep, "Versão mais compatível")
            version_str = str(version)  # Converte para string
            table.add_row(dep, version_str, reason)

        console.print(table)

    def apply_resolutions(self, resolutions: dict):
        """Aplica as resoluções nos projetos"""
        console.print("\n🔧 Aplicando Resoluções...")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "Atualizando projetos...", total=len(self.projects)
            )

            for project_path in self.projects:
                progress.update(task, description=f"Atualizando {project_path.name}")

                config_path = project_path / "pyproject.toml"
                if not config_path.exists():
                    progress.advance(task)
                    continue

                try:
                    with open(config_path, "rb") as f:
                        config = tomli.load(f)

                    deps = (
                        config.get("tool", {}).get("poetry", {}).get("dependencies", {})
                    )

                    # Aplica resoluções
                    updated = False
                    for dep, new_version in resolutions.items():
                        if dep in deps and str(deps[dep]) != str(new_version):
                            deps[dep] = new_version
                            updated = True

                    if updated:
                        with open(config_path, "wb") as f:
                            tomli_w.dump(config, f)
                        console.print(f"  ✅ {project_path.name} atualizado")

                except Exception as e:
                    console.print(f"  ❌ Erro em {project_path.name}: {e}")

                progress.advance(task)

    def create_isolation_scripts(self):
        """Cria scripts para isolamento de projetos"""
        console.print("\n🏗️ Criando scripts de isolamento...")

        # Script para instalar projeto individual
        install_script = """#!/bin/bash
# Script de Instalação Individual de Projeto
# Uso: ./install_project.sh <projeto>

set -e

PROJECT_NAME="$1"
WORKSPACE_ROOT="/home/marlonsc/pyauto"

if [ -z "$PROJECT_NAME" ]; then
    echo "❌ Uso: $0 <nome_do_projeto>"
    echo "Projetos disponíveis:"
    find "$WORKSPACE_ROOT" -name "pyproject.toml" -not -path "*/.venv/*" | while read -r pyproject; do
        echo "  - $(basename $(dirname "$pyproject"))"
    done
    exit 1
fi

PROJECT_PATH="$WORKSPACE_ROOT/$PROJECT_NAME"

if [ ! -d "$PROJECT_PATH" ]; then
    echo "❌ Projeto '$PROJECT_NAME' não encontrado em $PROJECT_PATH"
    exit 1
fi

echo "🔧 Instalando projeto: $PROJECT_NAME"
echo "📁 Diretório: $PROJECT_PATH"

cd "$PROJECT_PATH"

# Remove venv existente se houver
if [ -d ".venv" ]; then
    echo "🗑️ Removendo ambiente virtual existente..."
    rm -rf .venv
fi

# Cria novo ambiente virtual
echo "🏗️ Criando novo ambiente virtual..."
python3.13 -m venv .venv

# Ativa ambiente virtual
echo "⚡ Ativando ambiente virtual..."
source .venv/bin/activate

# Atualiza pip
echo "📦 Atualizando pip..."
pip install --upgrade pip

# Instala Poetry se necessário
if ! command -v poetry &> /dev/null; then
    echo "📜 Instalando Poetry..."
    pip install poetry
fi

# Configura Poetry para usar venv local
poetry config virtualenvs.in-project true

# Instala dependências
echo "📚 Instalando dependências..."
poetry install --no-interaction

echo "✅ Projeto $PROJECT_NAME instalado com sucesso!"
echo "💡 Para ativar: cd $PROJECT_PATH && source .venv/bin/activate"
"""

        script_path = self.workspace_path / "install_project.sh"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(install_script)
        script_path.chmod(0o755)

        console.print(f"✅ Script criado: {script_path}")

        # Script para verificar saúde dos projetos
        health_script = """#!/bin/bash
# Script de Verificação de Saúde dos Projetos

set -e

WORKSPACE_ROOT="/home/marlonsc/pyauto"

echo "🏥 Verificando saúde dos projetos..."
echo "=================================="

failed_projects=()

find "$WORKSPACE_ROOT" -name "pyproject.toml" -not -path "*/.venv/*" | while read -r pyproject; do
    project_dir=$(dirname "$pyproject")
    project_name=$(basename "$project_dir")

    echo "🔍 Verificando: $project_name"

    cd "$project_dir"

    # Verifica se pyproject.toml é válido
    if poetry check --quiet 2>/dev/null; then
        echo "  ✅ Poetry config válida"
    else
        echo "  ❌ Poetry config inválida"
        failed_projects+=("$project_name")
        continue
    fi

    # Verifica se venv existe e está funcional
    if [ -d ".venv" ]; then
        if source .venv/bin/activate 2>/dev/null && python --version >/dev/null 2>&1; then
            echo "  ✅ Ambiente virtual funcional"
        else
            echo "  ⚠️ Ambiente virtual com problemas"
        fi
    else
        echo "  ⚠️ Ambiente virtual não encontrado"
    fi

    echo ""
done

if [ ${#failed_projects[@]} -gt 0 ]; then
    echo "❌ Projetos com problemas: ${failed_projects[*]}"
    exit 1
else
    echo "✅ Todos os projetos estão saudáveis!"
fi
"""

        health_script_path = self.workspace_path / "check_project_health.sh"
        with open(health_script_path, "w", encoding="utf-8") as f:
            f.write(health_script)
        health_script_path.chmod(0o755)

        console.print(f"✅ Script criado: {health_script_path}")

    def run_resolution(self):
        """Executa o processo completo de resolução"""
        conflicts = self.analyze_conflicts()
        conflicted_deps = self.resolve_version_conflicts(conflicts)

        if conflicted_deps:
            console.print(
                f"\n[yellow]Encontrados {len(conflicted_deps)} dependências conflitantes[/yellow]"
            )

            # Propõe resoluções
            resolutions = self.propose_resolutions(conflicted_deps)

            # Pergunta se deseja aplicar
            apply = console.input(
                "\n[yellow]Aplicar resoluções automaticamente? (y/N): [/yellow]"
            )
            if apply.lower() == "y":
                self.apply_resolutions(resolutions)
                console.print("\n[green]✅ Resoluções aplicadas![/green]")
            else:
                console.print(
                    "\n[blue]ℹ️ Resoluções não aplicadas. Execute novamente quando desejar aplicar.[/blue]"
                )
        else:
            console.print(
                "\n[green]✅ Nenhum conflito de dependência encontrado![/green]"
            )

        # Cria scripts de isolamento
        self.create_isolation_scripts()

        console.print(
            Panel(
                "🎯 Próximos passos:\n"
                "1. Use './install_project.sh <projeto>' para instalar projetos individualmente\n"
                "2. Use './check_project_health.sh' para verificar saúde dos projetos\n"
                "3. Cada projeto terá seu próprio .venv isolado\n"
                "4. Execute 'poetry install' em cada projeto conforme necessário",
                title="Isolamento Configurado",
                style="bold green",
            )
        )


def main():
    """Função principal"""
    workspace_path = Path.cwd()

    console.print(
        Panel.fit(
            "Dependency Conflict Resolver\nResolve conflitos e isola projetos",
            style="bold magenta",
        )
    )

    resolver = DependencyResolver(workspace_path)
    resolver.run_resolution()


if __name__ == "__main__":
    main()

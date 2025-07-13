#!/usr/bin/env python3
"""
Script REAL para analisar quem está segurando atualizações de bibliotecas.
Compara versões no workspace com as últimas versões disponíveis no PyPI.
"""

import json
import re
import subprocess
import sys
import tomllib
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import urllib.request
import urllib.error


def get_latest_pypi_version(package: str) -> str | None:
    """Obtém a versão mais recente do PyPI."""
    try:
        url = f"https://pypi.org/pypi/{package}/json"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read())
            return data.get("info", {}).get("version")
    except (urllib.error.URLError, json.JSONDecodeError, KeyError):
        return None


def parse_version(version_str: str) -> tuple[int, ...]:
    """Converte string de versão em tupla de inteiros para comparação."""
    # Remove operadores de versão
    clean_version = re.sub(r'^[~^>=<]+', '', version_str)
    # Remove parte após vírgula (range)
    clean_version = clean_version.split(',')[0]
    # Pega apenas números
    parts = re.findall(r'\d+', clean_version)
    # Garante que sempre tem 3 partes (major, minor, patch)
    parts = (parts + ['0', '0', '0'])[:3]
    return tuple(int(p) for p in parts)


def parse_constraint(constraint: str) -> dict[str, Any]:
    """Analisa constraint e retorna tipo e versão mínima."""
    constraint = constraint.strip()
    
    # Padrões comuns
    patterns = [
        (r'^==([\d.]+)$', 'exact'),           # ==1.2.3
        (r'^~=([\d.]+)$', 'compatible'),      # ~=1.2.3
        (r'^>=([\d.]+),<([\d.]+)$', 'range'), # >=1.0,<2.0
        (r'^>=([\d.]+)$', 'minimum'),         # >=1.0
        (r'^\^([\d.]+)$', 'caret'),           # ^1.2.3
        (r'^~([\d.]+)$', 'tilde'),            # ~1.2.3
        (r'^([\d.]+)$', 'implicit'),          # 1.2.3
    ]
    
    for pattern, constraint_type in patterns:
        match = re.match(pattern, constraint)
        if match:
            version = match.group(1)
            has_upper_bound = constraint_type in ['exact', 'compatible', 'range', 'caret', 'tilde']
            
            # Para caret (^), calcula o limite superior
            if constraint_type == 'caret':
                version_parts = parse_version(version)
                major = version_parts[0] if len(version_parts) > 0 else 0
                minor = version_parts[1] if len(version_parts) > 1 else 0
                patch = version_parts[2] if len(version_parts) > 2 else 0
                
                if major > 0:
                    upper_bound = f"{major + 1}.0.0"
                elif minor > 0:
                    upper_bound = f"{major}.{minor + 1}.0"
                else:
                    upper_bound = f"{major}.{minor}.{patch + 1}"
            else:
                upper_bound = None
                
            return {
                'type': constraint_type,
                'version': version,
                'has_upper_bound': has_upper_bound,
                'upper_bound': upper_bound,
                'raw': constraint
            }
    
    return {
        'type': 'unknown',
        'version': constraint,
        'has_upper_bound': False,
        'upper_bound': None,
        'raw': constraint
    }


def collect_all_dependencies(workspace: Path) -> dict[str, dict[str, str]]:
    """Coleta todas as dependências de todos os projetos."""
    dependencies = defaultdict(dict)
    
    for pyproject in workspace.rglob("pyproject.toml"):
        # Pula diretórios que não são projetos
        if any(part in pyproject.parts for part in ['.venv', 'backup', 'archive', '__pycache__']):
            continue
            
        project_name = pyproject.parent.name
        
        try:
            with open(pyproject, 'rb') as f:
                data = tomllib.load(f)
            
            # Poetry dependencies
            poetry_deps = data.get('tool', {}).get('poetry', {}).get('dependencies', {})
            for dep, version in poetry_deps.items():
                if dep != 'python' and isinstance(version, str):
                    dependencies[dep][project_name] = version
            
            # Poetry dev dependencies (groups)
            groups = data.get('tool', {}).get('poetry', {}).get('group', {})
            for group_name, group_data in groups.items():
                group_deps = group_data.get('dependencies', {})
                for dep, version in group_deps.items():
                    if isinstance(version, str):
                        dependencies[dep][f"{project_name}[{group_name}]"] = version
                        
        except Exception as e:
            print(f"⚠️  Erro ao ler {pyproject}: {e}")
    
    return dict(dependencies)


def analyze_blocking_projects(dependencies: dict[str, dict[str, str]]) -> dict[str, Any]:
    """Analisa quais projetos estão bloqueando atualizações."""
    analysis = {}
    
    for package, project_versions in dependencies.items():
        if len(project_versions) < 2:
            continue  # Não há conflito se só um projeto usa
            
        # Obtém versão mais recente do PyPI
        latest_version = get_latest_pypi_version(package)
        
        # Analisa cada projeto
        project_constraints = {}
        blocking_projects = []
        most_restrictive = None
        least_restrictive = None
        
        for project, version_str in project_versions.items():
            constraint = parse_constraint(version_str)
            project_constraints[project] = constraint
            
            # Identifica projetos com upper bounds
            if constraint['has_upper_bound']:
                blocking_projects.append({
                    'project': project,
                    'constraint': constraint['raw'],
                    'type': constraint['type']
                })
        
        # Encontra o mais e menos restritivo
        if project_constraints:
            sorted_by_version = sorted(
                project_constraints.items(),
                key=lambda x: parse_version(x[1]['version'])
            )
            most_restrictive = sorted_by_version[0]
            least_restrictive = sorted_by_version[-1]
        
        # Só adiciona à análise se há projetos bloqueando
        if blocking_projects:
            analysis[package] = {
                'latest_pypi': latest_version,
                'total_projects': len(project_versions),
                'blocking_projects': blocking_projects,
                'most_restrictive': most_restrictive[0] if most_restrictive else None,
                'least_restrictive': least_restrictive[0] if least_restrictive else None,
                'all_versions': project_versions
            }
    
    return analysis


def format_report(analysis: dict[str, Any]) -> str:
    """Formata relatório legível."""
    lines = []
    lines.append("🔒 RELATÓRIO: QUEM ESTÁ SEGURANDO ATUALIZAÇÕES")
    lines.append("=" * 60)
    lines.append(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    if not analysis:
        lines.append("✅ Nenhum conflito de versão detectado!")
        return "\n".join(lines)
    
    # Ordena por número de projetos bloqueando
    sorted_packages = sorted(
        analysis.items(),
        key=lambda x: len(x[1]['blocking_projects']),
        reverse=True
    )
    
    for package, info in sorted_packages:
        lines.append(f"\n📦 {package}")
        lines.append(f"   PyPI mais recente: {info['latest_pypi'] or 'N/A'}")
        lines.append(f"   Projetos usando: {info['total_projects']}")
        lines.append(f"   Projetos bloqueando: {len(info['blocking_projects'])}")
        
        if info['blocking_projects']:
            lines.append("   🚫 Bloqueadores:")
            for blocker in info['blocking_projects']:
                lines.append(f"      - {blocker['project']}: {blocker['constraint']} ({blocker['type']})")
        
        if info['most_restrictive'] and info['least_restrictive']:
            lines.append(f"   📊 Mais restritivo: {info['most_restrictive']}")
            lines.append(f"   📊 Menos restritivo: {info['least_restrictive']}")
    
    lines.append("\n" + "=" * 60)
    lines.append("RESUMO:")
    lines.append(f"Total de pacotes com conflitos: {len(analysis)}")
    
    # Top 5 maiores bloqueadores
    top_blockers = defaultdict(int)
    for pkg_info in analysis.values():
        for blocker in pkg_info['blocking_projects']:
            top_blockers[blocker['project']] += 1
    
    if top_blockers:
        lines.append("\n🏆 TOP PROJETOS BLOQUEADORES:")
        for project, count in sorted(top_blockers.items(), key=lambda x: x[1], reverse=True)[:5]:
            lines.append(f"   {project}: bloqueando {count} pacotes")
    
    return "\n".join(lines)


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Analisa quem está segurando atualizações de bibliotecas"
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Diretório do workspace (padrão: diretório atual)"
    )
    parser.add_argument(
        "--save",
        help="Salva relatório em arquivo"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Saída em formato JSON"
    )
    
    args = parser.parse_args()
    
    print("🔍 Coletando dependências de todos os projetos...")
    dependencies = collect_all_dependencies(args.workspace)
    
    print(f"📊 Analisando {len(dependencies)} pacotes únicos...")
    analysis = analyze_blocking_projects(dependencies)
    
    if args.json:
        print(json.dumps(analysis, indent=2))
    else:
        report = format_report(analysis)
        print(report)
        
        if args.save:
            save_path = Path(args.save)
            save_path.write_text(report, encoding='utf-8')
            print(f"\n💾 Relatório salvo em: {save_path}")
    
    return 0 if not analysis else 1


if __name__ == "__main__":
    sys.exit(main())
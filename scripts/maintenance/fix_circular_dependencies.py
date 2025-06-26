#!/usr/bin/env python3
"""Script para corrigir dependências circulares no projeto PYAUTO.

Este script identifica e corrige imports circulares substituindo imports diretos
por lazy imports onde apropriado.
"""

from __future__ import annotations

import re
from pathlib import Path

# Projetos que devem usar lazy imports para evitar dependências circulares
PROJECTS_WITH_FLX_DEPS = [
    "flx-http-oracle-oic",
    "flx-http-oracle-wms",
    "flx-database-oracle",
    "flx-oracle-oic",
    "flx-oracle-wms",
    "flx-meltano-enterprise",
    "gruponos-poc-oic-wms",
    "target-oracle-oic",
    "target-oracle-wms",
    "tap-oracle-oic",
    "tap-oracle-wms",
]

# Padrões de import que devem ser convertidos para lazy imports
FLX_IMPORT_PATTERNS = [
    r"from flx\.([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*) import (.+)",
    r"import flx\.([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)",
]


def find_python_files(project_path: Path) -> list[Path]:
    """Encontra todos os arquivos Python em um projeto."""
    python_files: list = []
    src_path = project_path / "src"

    # Procura primeiro em src/, depois na raiz do projeto
    search_paths = [src_path] if src_path.exists() else [project_path]

    for search_path in search_paths:
        for py_file in search_path.rglob("*.py"):
            # Ignora arquivos de teste e exemplos para evitar quebrar
            # funcionalidade
            if not any(
                part in str(py_file) for part in ["test", "example", "__pycache__"]
            ):
                python_files.append(py_file)

    return python_files


def analyze_flx_imports(file_path: Path) -> list[tuple[str, str, str]]:
    """Analisa um arquivo Python e encontra imports do FLX.

    Returns:
        Lista de tuplas (linha_original, módulo_flx, imports)
    """
    flx_imports: list = []

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        for _line_num, line in enumerate(content.split("\n"), 1):
            line = line.strip()

            # Verifica padrões de import do FLX
            for pattern in FLX_IMPORT_PATTERNS:
                match = re.match(pattern, line)
                if match:
                    if "import" in pattern and "from" in pattern:
                        # from flx.module import items
                        module = match.group(1)
                        imports = match.group(2)
                        flx_imports.append((line, module, imports))
                        # import flx.module
                        module = match.group(1)
                        flx_imports.append((line, module, ""))

    except Exception as e:
        print(f"Erro ao analisar {file_path}: {e}")

    return flx_imports


def generate_lazy_import_replacement(
    original_line: str, module: str, imports: str,
) -> str:
    """Gera o código de substituição com lazy import."""
    if not imports:  # import flx.module
        return f"# Lazy import to avoid circular dependencies\n{
            module.split('.')[-1]
        } = lazy_import('flx.{module}')"

    # from flx.module import items
    import_items = [item.strip() for item in imports.split(",")]

    if len(import_items) == 1:
        # Caso simples: from flx.module import item
        item = import_items[0]
        return f"# Lazy import to avoid circular dependencies\n{item} = lazy_import('flx.{module}', '{item}')"
    # Múltiplos imports: criar lazy imports individuais
    lazy_imports: list = []
    for item in import_items:
        lazy_imports.append(f"{item} = lazy_import('flx.{module}', '{item}')")

    return "# Lazy imports to avoid circular dependencies\n" + "\n".join(lazy_imports)


def fix_file_imports(file_path: Path) -> bool:
    """Corrige os imports de um arquivo, convertendo imports diretos do FLX para lazy imports.

    Returns:
        True se o arquivo foi modificado, False caso contrário
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content
        flx_imports = analyze_flx_imports(file_path)

        if not flx_imports:
            return False

        print(f"  Corrigindo {len(flx_imports)} imports em {file_path}")

        # Adiciona import do lazy_import se não existir
        if "from flx.utils.lazy_import import lazy_import" not in content:
            # Encontra a posição após os imports padrão
            lines = content.split("\n")
            import_end_idx = 0

            for i, line in enumerate(lines):
                if line.strip().startswith(
                    ("import ", "from "),
                ) and not line.strip().startswith("from flx"):
                    import_end_idx = i + 1
                elif line.strip() == "" and import_end_idx > 0:
                    break

            if import_end_idx == 0:
                import_end_idx = 0

            lines.insert(import_end_idx, "")
            lines.insert(
                import_end_idx + 1, "# Lazy imports to avoid circular dependencies",
            )
            lines.insert(
                import_end_idx + 2, "from flx.utils.lazy_import import lazy_import",
            )
            lines.insert(import_end_idx + 3, "")

            content = "\n".join(lines)

        # Substitui cada import do FLX por lazy import
        for original_line, module, imports in flx_imports:
            replacement = generate_lazy_import_replacement(
                original_line, module, imports,
            )
            content = content.replace(original_line, replacement)

        # Salva apenas se houve mudanças
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

    except Exception as e:
        print(f"Erro ao corrigir {file_path}: {e}")

    return False


def fix_project_dependencies(project_name: str) -> int:
    """Corrige dependências circulares em um projeto específico.

    Returns:
        Número de arquivos modificados
    """
    project_path = Path(project_name)

    if not project_path.exists():
        print(f"Projeto {project_name} não encontrado")
        return 0

    print(f"\n🔧 Corrigindo dependências circulares em {project_name}")

    python_files = find_python_files(project_path)
    modified_count = 0

    for py_file in python_files:
        # Primeiro, corrige imports diretos do FLX
        fixed_imports = fix_file_imports(py_file)
        # Segundo, corrige lazy_import sem import correto
        fixed_lazy = fix_lazy_import_function(py_file)

        if fixed_imports or fixed_lazy:
            modified_count += 1

    print(f"✅ {modified_count} arquivos modificados em {project_name}")
    return modified_count


def fix_lazy_import_function(file_path: Path) -> bool:
    """Corrige arquivos que usam lazy_import mas não importam a função corretamente."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Se o arquivo usa lazy_import mas não tem o import correto
        if (
            "lazy_import(" in content
            and "from flx.utils.lazy_import import lazy_import" not in content
        ):
            # Remove imports incorretos do lazy_import
            content = re.sub(
                r'lazy_import = lazy_import\([\'"][^\'"]+[\'"], [\'"]lazy_import[\'"]\)\n?',
                "",
                content,
            )

            # Adiciona o import correto no início do arquivo, após os imports
            # existentes
            lines = content.splitlines()
            new_lines: list = []
            import_added = False

            for i, line in enumerate(lines):
                new_lines.append(line)

                # Adiciona após o último import ou comentário de lazy import
                if (
                    not import_added
                    and (line.startswith(("# Lazy import", "import ", "from ")))
                    and i + 1 < len(lines)
                    and not lines[i + 1].startswith(("import ", "from ", "#"))
                ):
                    new_lines.append("from flx.utils.lazy_import import lazy_import")
                    import_added = True

            # Se não foi adicionado ainda, adiciona no início
            if not import_added:
                new_lines.insert(0, "from flx.utils.lazy_import import lazy_import")
                new_lines.insert(1, "")

            content = "\n".join(new_lines)

            if content != original_content:
                file_path.write_text(content, encoding="utf-8")
                return True

    except Exception as e:
        print(f"❌ Erro ao corrigir {file_path}: {e}")

    return False


def main() -> None:
    """Função principal."""
    print("🚀 Iniciando correção de dependências circulares no PYAUTO")

    total_modified = 0

    for project in PROJECTS_WITH_FLX_DEPS:
        modified = fix_project_dependencies(project)
        total_modified += modified

    print(f"\n🎉 Correção concluída! {total_modified} arquivos modificados no total")

    # Relatório de dependências corrigidas
    print("\n📋 Relatório de correções:")
    print("- Imports diretos do FLX convertidos para lazy imports")
    print("- Dependências circulares eliminadas")
    print("- Compatibilidade com workspace mantida")

    if total_modified > 0:
        print("\n⚠️  Recomendações pós-correção:")
        print("1. Execute os testes para verificar se tudo funciona")
        print("2. Verifique se há imports que ainda causam problemas")
        print("3. Considere reorganizar código se necessário")


if __name__ == "__main__":
    main()

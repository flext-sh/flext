#!/usr/bin/env python3
"""Script para atualizar o pyproject.toml com exclusões de arquivos problemáticos.

Este script lê uma lista de arquivos com problemas de linhas longas (E501) e
atualiza a seção per-file-ignores no pyproject.toml para ignorar E501 em
arquivos com muitas ocorrências.
"""

import argparse
import re
import sys
from pathlib import Path


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Atualiza pyproject.toml com exclusões para arquivos com problemas E501",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Arquivo com a lista de arquivos problemáticos",
    )
    parser.add_argument(
        "--pyproject",
        required=True,
        help="Caminho para o arquivo pyproject.toml",
    )
    parser.add_argument(
        "--min-errors",
        type=int,
        default=10,
        help="Número mínimo de erros para adicionar exclusão (default: 10)",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=50,
        help="Número máximo de arquivos a excluir (default: 50)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Não escreve no arquivo, apenas mostra o que seria feito",
    )
    return parser.parse_args()


def read_problem_files(input_file: str, min_errors: int) -> list[str]:
    """Lê a lista de arquivos problemáticos do arquivo de entrada."""
    problem_files = []

    with open(input_file, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                path = parts[0]
                count = int(parts[1])
                if count >= min_errors:
                    problem_files.append((path, count))

    return problem_files


def update_pyproject_toml(
    pyproject_file: str,
    problem_files: list[tuple[str, int]],
    max_files: int,
    dry_run: bool,
) -> None:
    """Atualiza o pyproject.toml com as exclusões."""
    with open(pyproject_file, encoding="utf-8") as f:
        content = f.read()

    # Limites para arquivo
    problem_files = problem_files[:max_files]

    # Construir novas exclusões
    exclusions = []
    for filepath, _count in problem_files:
        # Limpar o caminho (remover ./ no início)
        filepath = filepath.removeprefix("./")
        exclusions.append(f'"{filepath}" = ["E501"]')

    # Verificar se já temos seção per-file-ignores
    per_file_section = re.search(
        r"\[tool\.ruff\.lint\.per-file-ignores\]\s*([^\[]*)",
        content,
    )

    if per_file_section:
        # A seção existe, vamos modificá-la
        section_content = per_file_section.group(1)

        # Remover exclusões existentes de E501
        existing_lines = []
        for line in section_content.splitlines():
            # Se não for uma linha de exclusão para E501 ou um comentário, mantemos
            if '["E501"]' not in line or line.strip().startswith("#"):
                if line.strip():  # Se não for linha vazia
                    existing_lines.append(line)

        # Adicionar comentário explicativo
        if existing_lines and not existing_lines[-1].strip().startswith("#"):
            existing_lines.append("")
        existing_lines.append(
            "# Arquivos com problemas severos de linhas longas (a serem tratados gradualmente)",
        )

        # Adicionar novas exclusões
        existing_lines.extend(exclusions)

        # Construir novo conteúdo da seção
        new_section_content = "\n".join(existing_lines)

        # Substituir a seção existente
        new_content = content.replace(
            per_file_section.group(0),
            f"[tool.ruff.lint.per-file-ignores]\n{new_section_content}\n",
        )
    else:
        # A seção não existe, adicionar nova seção
        new_section = "\n[tool.ruff.lint.per-file-ignores]\n"
        new_section += '"__init__.py" = ["F401"]  # Imported but unused\n'
        new_section += '"tests/*" = ["S101"]  # Use of assert\n'
        new_section += "# Arquivos com problemas severos de linhas longas (a serem tratados gradualmente)\n"
        new_section += "\n".join(exclusions)
        new_section += "\n"

        # Adicionar após a seção tool.ruff.lint
        new_content = re.sub(
            r"(\[tool\.ruff\.lint\][^\[]*)",
            f"\\1{new_section}",
            content,
        )

    # Mostrar mudanças
    print(f"Serão atualizados {len(problem_files)} arquivos com exclusões para E501")

    if dry_run:
        print("Modo dry-run ativado. Nenhuma alteração será realizada.")
        print("\nExclusões que seriam adicionadas:")
        for exclusion in exclusions:
            print(f"  {exclusion}")
        return

    # Escrever alterações
    with open(pyproject_file, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Arquivo {pyproject_file} atualizado com sucesso!")


def main() -> None:
    """Função principal do script."""
    args = parse_arguments()

    # Verificar se os arquivos existem
    input_file = Path(args.input)
    pyproject_file = Path(args.pyproject)

    if not input_file.exists():
        print(f"Erro: Arquivo {input_file} não encontrado", file=sys.stderr)
        return 1

    if not pyproject_file.exists():
        print(f"Erro: Arquivo {pyproject_file} não encontrado", file=sys.stderr)
        return 1

    # Ler arquivos problemáticos
    problem_files = read_problem_files(input_file, args.min_errors)

    if not problem_files:
        print(f"Nenhum arquivo com pelo menos {args.min_errors} erros E501 encontrado.")
        return 0

    # Atualizar pyproject.toml
    update_pyproject_toml(pyproject_file, problem_files, args.max_files, args.dry_run)

    return 0


if __name__ == "__main__":
    sys.exit(main())

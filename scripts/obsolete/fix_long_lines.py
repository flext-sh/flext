#!/usr/bin/env python3
"""
Script para tentar corrigir linhas longas automaticamente.

Este script detecta linhas que excedem o comprimento máximo definido e tenta
formatá-las melhor, dividindo-as em múltiplas linhas usando várias estratégias.
"""

import argparse
import ast
import os
import re
import sys
from pathlib import Path


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Corrige linhas longas em arquivos Python",
    )
    parser.add_argument(
        "--exclude",
        default=".venv/**,reference/**,*/examples/**,*/typings/**,*/venv/**",
        help="Padrões de exclusão (separados por vírgula)",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=88,
        help="Comprimento máximo de linha (default: 88)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Apenas verifica, não modifica os arquivos",
    )
    parser.add_argument(
        "--aggressive",
        action="store_true",
        help="Usa estratégias mais agressivas para quebra de linhas",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Modo verboso",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Arquivos específicos a processar (opcional)",
    )
    return parser.parse_args()


def get_python_files(
    exclude_patterns: list[str],
    specific_files: list[str] | None = None,
) -> list[Path]:
    """Encontra arquivos Python no diretório atual, excluindo padrões especificados."""
    if specific_files:
        return [Path(file) for file in specific_files if file.endswith(".py")]

    python_files = []
    for root, _, files in os.walk(".", topdown=True):
        # Verifica se o diretório atual deve ser excluído
        skip_dir = False
        for pattern in exclude_patterns:
            if "*" in pattern:
                # Converte padrão glob para regex simples
                regex_pattern = pattern.replace(".", "\\.").replace("*", ".*")
                if re.match(regex_pattern, root[2:]):  # Remove './' do início
                    skip_dir = True
                    break
            elif pattern in root:
                skip_dir = True
                break

        if skip_dir:
            continue

        # Adiciona arquivos Python
        for file in files:
            if file.endswith(".py"):
                python_files.append(Path(os.path.join(root, file)))

    return python_files


def detect_long_lines(file_path: Path, max_length: int) -> list[tuple[int, str]]:
    """Detecta linhas que excedem o comprimento máximo."""
    long_lines = []

    with open(file_path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if len(line.rstrip()) > max_length:
                long_lines.append((i, line.rstrip()))

    return long_lines


def flx_string_concatenation(line: str, max_length: int) -> str:
    """Corrige linhas longas com concatenação de strings."""
    # Detecta strings
    string_pattern = r'([\'"])(.*?)\1'

    # Procura strings longas
    matches = list(re.finditer(string_pattern, line))

    if not matches:
        return line

    # Encontra a string mais longa que causa o problema
    longest_match = max(matches, key=lambda m: len(m.group(0)))

    # Se a string for realmente longa, divida-a
    if len(longest_match.group(0)) > max_length // 2:
        prefix = line[: longest_match.start()]
        string_content = longest_match.group(2)
        quote = longest_match.group(1)
        suffix = line[longest_match.end() :]

        # Divide a string em partes menores
        parts = []
        part = ""
        for word in string_content.split():
            if len(part + " " + word) <= max_length - 10:  # Margem de segurança
                if part:
                    part += " " + word
                else:
                    part = word
            else:
                parts.append(part)
                part = word

        if part:
            parts.append(part)

        # Reconstrói a linha com quebras
        if len(parts) > 1:
            joined_parts = f" {quote}\n{quote} ".join(parts)
            return f"{prefix.rstrip()}{quote}{joined_parts}{quote}{suffix}"

    return line


def flx_function_args(line: str, max_length: int) -> str:
    """Corrige linhas longas com chamadas de função com muitos argumentos."""
    # Procura por chamadas de função com parênteses
    if "(" not in line or ")" not in line:
        return line

    # Encontra a posição do primeiro parêntese
    open_paren = line.find("(")
    if open_paren == -1:
        return line

    # Verifica se podemos identificar os argumentos
    try:
        # Tenta analisar a linha como uma expressão
        ast.parse(line.strip())

        # Se chegou aqui, podemos fazer parse da expressão
        prefix = line[: open_paren + 1]
        suffix = line[line.rfind(")") :]
        args_str = line[open_paren + 1 : line.rfind(")")]

        # Divide os argumentos (isso é uma simplificação e não lida com todos os casos)
        args = []
        current_arg = ""
        paren_level = 0
        bracket_level = 0
        brace_level = 0
        in_string = False
        string_char = None

        for char in args_str:
            if char in "\"'" and (not in_string or string_char == char):
                in_string = not in_string
                string_char = char if in_string else None
                current_arg += char
            elif in_string:
                current_arg += char
            elif (
                char == ","
                and paren_level == 0
                and bracket_level == 0
                and brace_level == 0
            ):
                args.append(current_arg.strip())
                current_arg = ""
            elif char == "(":
                paren_level += 1
                current_arg += char
            elif char == ")":
                paren_level -= 1
                current_arg += char
            elif char == "[":
                bracket_level += 1
                current_arg += char
            elif char == "]":
                bracket_level -= 1
                current_arg += char
            elif char == "{":
                brace_level += 1
                current_arg += char
            elif char == "}":
                brace_level -= 1
                current_arg += char
            else:
                current_arg += char

        if current_arg.strip():
            args.append(current_arg.strip())

        # Se temos argumentos, reconstrua a linha
        if args:
            # Calcula indentação
            indent = len(line) - len(line.lstrip())
            extra_indent = " " * (indent + 4)  # 4 espaços extras para argumentos

            new_line = prefix.rstrip() + "\n"
            for i, arg in enumerate(args):
                new_line += extra_indent + arg
                if i < len(args) - 1:
                    new_line += ","
                new_line += "\n"
            new_line += " " * indent + suffix.lstrip()

            return new_line
    except SyntaxError:
        # Se não conseguir analisar, retorna a linha original
        pass

    return line


def flx_long_list_dict(line: str, max_length: int) -> str:
    """Corrige linhas longas com listas ou dicionários."""
    # Verifica se a linha contém uma definição de lista ou dicionário
    if ("[" not in line and "{" not in line) or ("]" not in line and "}" not in line):
        return line

    # Tenta identificar a estrutura
    matches = re.finditer(r"(\[|\{)(.*?)(\]|\})", line)
    for match in matches:
        open_char = match.group(1)
        content = match.group(2)
        close_char = match.group(3)

        prefix = line[: match.start()]
        suffix = line[match.end() :]

        # Se o conteúdo for longo, quebra em múltiplas linhas
        if len(content) > max_length // 2:
            # Calcula indentação
            indent = len(line) - len(line.lstrip())
            extra_indent = " " * (indent + 4)  # 4 espaços extras para itens

            # Divide os itens
            items = []
            current_item = ""
            paren_level = 0
            bracket_level = 0
            brace_level = 0
            in_string = False
            string_char = None

            for char in content:
                if char in "\"'" and (not in_string or string_char == char):
                    in_string = not in_string
                    string_char = char if in_string else None
                    current_item += char
                elif in_string:
                    current_item += char
                elif (
                    char == ","
                    and paren_level == 0
                    and bracket_level == 0
                    and brace_level == 0
                ):
                    items.append(current_item.strip())
                    current_item = ""
                elif char == "(":
                    paren_level += 1
                    current_item += char
                elif char == ")":
                    paren_level -= 1
                    current_item += char
                elif char == "[":
                    bracket_level += 1
                    current_item += char
                elif char == "]":
                    bracket_level -= 1
                    current_item += char
                elif char == "{":
                    brace_level += 1
                    current_item += char
                elif char == "}":
                    brace_level -= 1
                    current_item += char
                else:
                    current_item += char

            if current_item.strip():
                items.append(current_item.strip())

            # Reconstruir a linha
            if items:
                new_line = prefix + open_char + "\n"
                for i, item in enumerate(items):
                    new_line += extra_indent + item
                    if i < len(items) - 1:
                        new_line += ","
                    new_line += "\n"
                new_line += " " * indent + close_char + suffix

                return new_line

    return line


def flx_assignment(line: str, max_length: int) -> str:
    """Corrige linhas longas com atribuições."""
    # Verifica se a linha contém uma atribuição
    if "=" not in line:
        return line

    # Divide a linha na primeira ocorrência de "="
    parts = line.split("=", 1)
    if len(parts) != 2:
        return line

    left = parts[0].rstrip()
    right = parts[1].lstrip()

    # Se o lado direito for longo, quebra em múltiplas linhas
    if len(left) + 1 + len(right) > max_length:
        # Calcula indentação
        indent = len(line) - len(line.lstrip())
        extra_indent = " " * (indent + 4)  # 4 espaços extras

        # Reconstruir a linha
        return left + " =\\\n" + extra_indent + right

    return line


def flx_binary_op(line: str, max_length: int) -> str:
    """Corrige linhas longas com operações binárias (and, or, +, etc)."""
    # Procura por operadores comuns
    operators = [
        " and ",
        " or ",
        " + ",
        " - ",
        " * ",
        " / ",
        " // ",
        " % ",
        " ** ",
        " | ",
        " & ",
        " ^ ",
    ]

    for op in operators:
        if op in line and len(line) > max_length:
            # Divide a linha pelo operador
            parts = line.split(op, 1)
            if len(parts) == 2:
                left = parts[0].rstrip()
                right = parts[1].lstrip()

                # Calcula indentação
                indent = len(line) - len(line.lstrip())
                extra_indent = " " * (indent + 4)  # 4 espaços extras

                # Reconstruir a linha
                return left + op.rstrip() + "\\\n" + extra_indent + right

    return line


def flx_long_line(line: str, max_length: int, aggressive: bool = False) -> str:
    """Aplica várias estratégias para corrigir uma linha longa."""
    # Ignora comentários e docstrings
    if (
        line.strip().startswith("#")
        or line.strip().startswith('"""')
        or line.strip().startswith("'''")
    ):
        return line

    # Lista de estratégias para aplicar
    strategies = [
        fix_string_concatenation,
        fix_function_args,
        fix_long_list_dict,
        fix_assignment,
    ]

    if aggressive:
        strategies.append(fix_binary_op)

    # Aplica cada estratégia até que a linha esteja abaixo do tamanho máximo
    original_line = line
    for strategy in strategies:
        line = strategy(line, max_length)

        # Verifica se a linha foi quebrada em múltiplas linhas
        if "\n" in line:
            # Verifica se todas as linhas estão abaixo do tamanho máximo
            all_fixed = True
            for subline in line.splitlines():
                if len(subline.rstrip()) > max_length:
                    all_fixed = False
                    break

            if all_fixed:
                return line

    # Se nenhuma estratégia funcionou, retorna a linha original
    return original_line


def process_file(
    file_path: Path,
    max_length: int,
    check_only: bool,
    aggressive: bool,
    verbose: bool,
) -> int:
    """Processa um arquivo para corrigir linhas longas."""
    long_lines = detect_long_lines(file_path, max_length)

    if not long_lines:
        if verbose:
            print(f"{file_path}: OK (sem linhas longas)")
        return 0

    if check_only:
        print(f"{file_path}: {len(long_lines)} linhas longas encontradas")
        for line_num, _ in long_lines:
            print(f"  - Linha {line_num}")
        return len(long_lines)

    # Lê o arquivo completo
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    # Corrige cada linha longa
    fixed_count = 0
    fixed_lines = []
    for i, line in enumerate(lines):
        line_num = i + 1
        is_long_line = any(num == line_num for num, _ in long_lines)

        if is_long_line:
            fixed_line = flx_long_line(line, max_length, aggressive)
            if fixed_line != line:
                fixed_count += 1
                fixed_lines.append(fixed_line)
                if verbose:
                    print(f"{file_path}: Linha {line_num} corrigida")
            else:
                fixed_lines.append(line)
                if verbose:
                    print(
                        f"{file_path}: Linha {line_num} não pôde ser corrigida automaticamente",
                    )
        else:
            fixed_lines.append(line)

    # Escreve as alterações se alguma linha foi corrigida
    if fixed_count > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            for line in fixed_lines:
                f.write(line if line.endswith("\n") else line + "\n")

        print(f"{file_path}: {fixed_count}/{len(long_lines)} linhas corrigidas")
    else:
        print(
            f"{file_path}: Nenhuma linha pôde ser corrigida automaticamente ({len(long_lines)} linhas longas)",
        )

    return len(long_lines) - fixed_count


def main():
    """Função principal do script."""
    args = parse_arguments()

    # Converte padrões de exclusão para lista
    exclude_patterns = args.exclude.split(",")

    # Encontra arquivos Python
    python_files = get_python_files(exclude_patterns, args.files)

    if not python_files:
        print("Nenhum arquivo Python encontrado.")
        return 0

    print(f"Verificando {len(python_files)} arquivos Python...")

    # Processa cada arquivo
    remaining_issues = 0
    for file_path in python_files:
        try:
            remaining = process_file(
                file_path,
                args.max_length,
                args.check,
                args.aggressive,
                args.verbose,
            )
            remaining_issues += remaining
        except Exception as e:
            print(f"Erro ao processar {file_path}: {e!s}")

    # Resumo
    if args.check:
        print(
            f"\nVerificação concluída: {remaining_issues} linhas longas encontradas em {len(python_files)} arquivos.",
        )
    else:
        print(
            f"\nProcessamento concluído: {remaining_issues} linhas longas ainda precisam ser corrigidas manualmente.",
        )

    return 0 if remaining_issues == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

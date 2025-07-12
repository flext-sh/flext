from typing import Dict
from typing import List
#!/usr/bin/env python3
"""
🎯 CONTINUAÇÃO SISTEMÁTICA PEP COMPLIANCE - NEXT PHASE
Script automatizado para reduzir violações PEP restantes de 334 → <100

FOCO PRIORITÁRIO:
- COM818: Missing trailing comma (60 violations)
- D205: Missing blank line after summary (34 violations)
- E501: Line too long (20 violations)
- W505: Doc line too long (10 violations)
- PLR0912: Too many branches (8 violations)
- PLR0915: Too many statements (6 violations)

ESTRATÉGIA INTELIGENTE:
1. Correções automatizáveis (COM818, D205, E501, W505)
2. Refatoração assistida (PLR0912, PLR0915)
3. Verificação contínua


import re
import subprocess
from pathlib import Path


class NextPhasePEPFixer:
    Automatizador para próxima fase de compliance PEP."""

    def __init__(self, project_dir: str = "/home/marlonsc/flext/client-a-oud-mig") -> None:
        self.project_dir = Path(project_dir)
        self.src_dir = self.project_dir / "src"
        self.fixes_applied = []

    def fix_all_remaining_violations(self) -> None:
        """Aplicar todas as correções sistematicamente."""
        print("🚀 INICIANDO PRÓXIMA FASE PEP COMPLIANCE")
        print(f"📁 Diretório: {self.project_dir}")

        # Phase 1: Trailing commas (COM818)
        self._fix_trailing_commas()

        # Phase 2: Docstring blank lines (D205)
        self._fix_docstring_blank_lines()

        # Phase 3: Line length optimization (E501)
        self._fix_line_lengths_smart()

        # Phase 4: Doc line lengths (W505)
        self._fix_doc_line_lengths()

        # Phase 5: Complexity reduction assistida (PLR0912, PLR0915)
        self._reduce_complexity_guided()

        # Report final results
        self._report_final_status()

    def _fix_trailing_commas(self) -> None:
        """Corrigir COM818: Missing trailing comma - aplicar sistematicamente."""
        print("\n🔧 PHASE 1: FIXING TRAILING COMMAS (COM818)")

        for py_file in self.src_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            original_content = content

            # Patterns que precisam de trailing comma
            patterns = [
                # Function/method arguments multi-line
                (r"(\w+)\s*:\s*(\w+\[.*?\]|\w+)\s*\n(\s*)\)", r"\1: \2,\n\3)"),
                # Dictionary entries
                (r'(".*?")\s*:\s*(".*?")\s*\n(\s*)}', r"\1: \2,\n\3}"),
                # List/tuple items
                (r'(".*?")\s*\n(\s*)]', r"\1,\n\2]"),
                (r'(".*?")\s*\n(\s*)\)', r"\1,\n\2)"),
                # Import statements
                (r"(\w+)\s*\n(\s*)\)", r"\1,\n\2)"),
            ]

            for pattern, replacement in patterns:
                new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                if new_content != content:
                    content = new_content
                    self.fixes_applied.append(f"COM818 trailing comma: {py_file.name}")

            if content != original_content:
                py_file.write_text(content, encoding="utf-8")
                print(f"✅ Fixed trailing commas in {py_file.name}")

    def _fix_docstring_blank_lines(self) -> None:
        """Corrigir D205: Missing blank line after summary."""
        print("\n🔧 PHASE 2: FIXING DOCSTRING BLANK LINES (D205)")

        for py_file in self.src_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            original_content = content

            # Pattern: docstring sem linha em branco após primeira linha
            pattern = r'("""[^"]*?\.)\n(\s*[A-Z])'
            replacement = r"\1\n\n\2"

            content = re.sub(
                pattern, replacement, content, flags=re.MULTILINE | re.DOTALL
            )

            if content != original_content:
                py_file.write_text(content, encoding="utf-8")
                self.fixes_applied.append(f"D205 docstring blank line: {py_file.name}")
                print(f"✅ Fixed docstring blank lines in {py_file.name}")

    def _fix_line_lengths_smart(self) -> None:
        """Corrigir E501: Line too long com estratégias inteligentes."""
        print("\n🔧 PHASE 3: SMART LINE LENGTH OPTIMIZATION (E501)")

        for py_file in self.src_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            lines = content.split("\n")
            modified_lines = []

            for line_num, line in enumerate(lines):
                if len(line) > 88:  # Threshold for optimization
                    new_line = self._optimize_long_line(line)
                    if new_line != line:
                        self.fixes_applied.append(
                            f"E501 line length: {py_file.name}:{line_num + 1}"
                        )
                    modified_lines.append(new_line)
                else:
                    modified_lines.append(line)

            new_content = "\n".join(modified_lines)
            if new_content != content:
                py_file.write_text(new_content, encoding="utf-8")
                print(f"✅ Optimized line lengths in {py_file.name}")

    def _optimize_long_line(self, line: str) -> str:
        """Otimizar linha longa com estratégias específicas."""
        # Strategy 1: Break after logical operators
        if " and " in line or " or " in line:
            return self._break_logical_operators(line)

        # Strategy 2: Break function calls
        if "(" in line and ")" in line:
            return self._break_function_calls(line)

        # Strategy 3: Break string concatenations
        if " + " in line and '"' in line:
            return self._break_string_concatenations(line)

        # Strategy 4: Break dictionary/list literals
        if "{" in line or "[" in line:
            return self._break_data_structures(line)

        return line

    def _break_logical_operators(self, line: str) -> str:
        """Quebrar linha em operadores lógicos."""
        indent = len(line) - len(line.lstrip())
        base_indent = " " * indent

        if " and " in line:
            parts = line.split(" and ")
            if len(parts) > 1:
                return f" and\n{base_indent}    ".join(parts)

        if " or " in line:
            parts = line.split(" or ")
            if len(parts) > 1:
                return f" or\n{base_indent}    ".join(parts)

        return line

    def _break_function_calls(self, line: str) -> str:
        """Quebrar chamadas de função longas."""
        if line.count("(") == 1 and line.count(")") == 1:
            # Simple function call
            match = re.search(r"(\w+)\((.*)\)", line)
            if match:
                func_name, args = match.groups()
                if "," in args:
                    indent = len(line) - len(line.lstrip())
                    base_indent = " " * indent
                    arg_indent = " " * (indent + 4)

                    args_list = [arg.strip() for arg in args.split(",")]
                    formatted_args = f",\n{arg_indent}".join(args_list)

                    return f"{base_indent}{func_name}(\n{arg_indent}{formatted_args},\n{base_indent})"

        return line

    def _break_string_concatenations(self, line: str) -> str:
        """Quebrar concatenações de string."""
        if " + " in line:
            indent = len(line) - len(line.lstrip())
            base_indent = " " * indent
            parts = line.split(" + ")

            if len(parts) > 1:
                return f" +\n{base_indent}    ".join(parts)

        return line

    def _break_data_structures(self, line: str) -> str:
        """Quebrar estruturas de dados longas."""
        # Dictionary literals
        if "{" in line and "}" in line and ":" in line:
            return self._break_dict_literal(line)

        # List literals
        if "[" in line and "]" in line and "," in line:
            return self._break_list_literal(line)

        return line

    def _break_dict_literal(self, line: str) -> str:
        """Quebrar dicionário literal."""
        indent = len(line) - len(line.lstrip())
        base_indent = " " * indent

        # Simple pattern for inline dict
        match = re.search(r"\{(.*)\}", line)
        if match:
            dict_content = match.group(1)
            if "," in dict_content:
                items = [item.strip() for item in dict_content.split(",")]
                item_indent = " " * (indent + 4)
                formatted_items = f",\n{item_indent}".join(items)

                return line.replace(
                    match.group(0),
                    f"{{\n{item_indent}{formatted_items},\n{base_indent}}}",
                )

        return line

    def _break_list_literal(self, line: str) -> str:
        """Quebrar lista literal."""
        indent = len(line) - len(line.lstrip())
        base_indent = " " * indent

        match = re.search(r"\[(.*)\]", line)
        if match:
            list_content = match.group(1)
            if "," in list_content:
                items = [item.strip() for item in list_content.split(",")]
                item_indent = " " * (indent + 4)
                formatted_items = f",\n{item_indent}".join(items)

                return line.replace(
                    match.group(0),
                    f"[\n{item_indent}{formatted_items},\n{base_indent}]",
                )

        return line

    def _fix_doc_line_lengths(self) -> None:
        """Corrigir W505: Doc line too long."""
        print("\n🔧 PHASE 4: FIXING DOC LINE LENGTHS (W505)")

        for py_file in self.src_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            lines = content.split("\n")
            modified_lines = []

            in_docstring = False
            docstring_quote = None

            for line in lines:
                # Detect docstring start/end
                if '"""' in line or "'''" in line:
                    quote = '"""' if '"""' in line else "'''"
                    if not in_docstring:
                        in_docstring = True
                        docstring_quote = quote
                    elif quote == docstring_quote:
                        in_docstring = False
                        docstring_quote = None

                # Process docstring lines
                if in_docstring and len(line) > 72:
                    new_line = self._wrap_docstring_line(line)
                    if new_line != line:
                        self.fixes_applied.append(
                            f"W505 doc line length: {py_file.name}"
                        )
                        modified_lines.extend(new_line.split("\n"))
                    else:
                        modified_lines.append(line)
                else:
                    modified_lines.append(line)

            new_content = "\n".join(modified_lines)
            if new_content != content:
                py_file.write_text(new_content, encoding="utf-8")
                print(f"✅ Fixed doc line lengths in {py_file.name}")

    def _wrap_docstring_line(self, line: str) -> str:
        """Quebrar linha de docstring longa."""
        indent = len(line) - len(line.lstrip())
        base_indent = " " * indent

        if len(line) > 72:
            # Find good break point
            words = line.strip().split()
            current_line = base_indent + words[0]
            result_lines = []

            for word in words[1:]:
                if len(current_line + " " + word) > 72:
                    result_lines.append(current_line)
                    current_line = base_indent + word
                else:
                    current_line += " " + word

            result_lines.append(current_line)
            return "\n".join(result_lines)

        return line

    def _reduce_complexity_guided(self) -> None:
        """Redução de complexidade guiada para PLR0912, PLR0915."""
        print("\n🔧 PHASE 5: GUIDED COMPLEXITY REDUCTION")

        # Run ruff to find specific complexity violations
        result = subprocess.run(
            [
                "ruff",
                "check",
                str(self.src_dir),
                "--select=PLR0912,PLR0915",
                "--output-format=text",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=self.project_dir,
        )

        violations = result.stdout.strip().split("\n") if result.stdout.strip() else []

        for violation in violations:
            if "PLR0912" in violation or "PLR0915" in violation:
                print(f"⚠️  COMPLEXITY: {violation}")
                # Extract file and function for manual review
                parts = violation.split(":")
                if len(parts) >= 2:
                    file_path = parts[0]
                    line_num = parts[1]
                    print(f"   📁 File: {file_path}, Line: {line_num}")
                    print(
                        "   💡 SUGGESTION: Consider extracting methods or using early returns"
                    )

    def _report_final_status(self) -> None:
        """Relatório final dos resultados."""
        print("\n" + "=" * 60)
        print("🎯 FASE CONCLUÍDA - PRÓXIMO NÍVEL PEP COMPLIANCE")
        print("=" * 60)

        print(f"\n✅ CORREÇÕES APLICADAS: {len(self.fixes_applied)}")

        # Group fixes by type
        fix_types = {}
        for fix in self.fixes_applied:
            fix_type = fix.split(":")[0]
            fix_types[fix_type] = fix_types.get(fix_type, 0) + 1

        for fix_type, count in sorted(fix_types.items()):
            print(f"   - {fix_type}: {count} fixes")

        # Run final ruff check
        print("\n🔍 VERIFICAÇÃO FINAL...")
        result = subprocess.run(
            ["ruff", "check", str(self.src_dir), "--statistics"],
            check=False,
            capture_output=True,
            text=True,
            cwd=self.project_dir,
        )

        if result.stdout:
            print("\n📊 VIOLAÇÕES RESTANTES:")
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    print(f"   {line}")

        print("\n🚀 PROGRESSO CONTÍNUO REALIZADO!")
        print(
            "📝 Próxima iteração: Continue com script similar para próximas violações"
        )
        print("🎯 Meta: <100 violações PEP total")


def main() -> None:
    """Execute next phase PEP compliance fixing."""
    fixer = NextPhasePEPFixer()
    fixer.fix_all_remaining_violations()


if __name__ == "__main__":
    main()

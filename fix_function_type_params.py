#!/usr/bin/env python3
"""
Fix function type parameter syntax specifically.
"""

import re
from pathlib import Path


def fix_function_type_params(file_path: Path) -> bool:
    """Fix function type parameters with constraints."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Pattern for function with type constraints like def func[C: "DomainCommand"](
        pattern = r'def\s+(\w+)\[([^:]+):\s*"([^"]+)"\]\s*\('

        def replace_func(match):
            func_name = match.group(1)
            match.group(2)
            match.group(3)

            # Need to add TypeVar declaration and update function signature
            return f"def {func_name}("

        new_content = re.sub(pattern, replace_func, content)

        # If we made changes, also need to add TypeVar with constraint
        if new_content != content:
            # Check if TypeVar import exists
            if "from typing import" in new_content and "TypeVar" not in new_content:
                new_content = re.sub(
                    r"from typing import ([^#\n]+)",
                    r"from typing import \1, TypeVar",
                    new_content,
                )
            elif "from typing import" not in new_content:
                # Add import after other imports
                lines = new_content.split("\n")
                for i, line in enumerate(lines):
                    if line.startswith(("from ", "import ")):
                        continue
                    if line.strip() == "":
                        continue
                    lines.insert(i, "from typing import TypeVar")
                    break
                new_content = "\n".join(lines)

            # Add TypeVar declaration (we'll add it near the top after imports)
            # For the constraint pattern we found, add the constrained TypeVar
            match = re.search(r'def\s+(\w+)\[([^:]+):\s*"([^"]+)"\]', content)
            if match:
                type_var = match.group(2)
                constraint = match.group(3)

                # Add TypeVar declaration after imports
                lines = new_content.split("\n")
                import_end = 0
                for i, line in enumerate(lines):
                    if line.startswith(("from ", "import ")):
                        import_end = i + 1
                    elif line.strip() == "":
                        continue
                    else:
                        break

                typevar_line = (
                    f'{type_var} = TypeVar("{type_var}", bound="{constraint}")'
                )
                lines.insert(import_end, typevar_line)
                lines.insert(import_end + 1, "")
                new_content = "\n".join(lines)

        if new_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True

        return False
    except Exception:
        return False


def main():
    """Main function."""
    file_path = Path(
        "/home/marlonsc/flext/legacy/flx-meltano-enterprise/src/flx_core/commands/decorators.py"
    )

    if fix_function_type_params(file_path):
        pass
    else:
        pass


if __name__ == "__main__":
    main()

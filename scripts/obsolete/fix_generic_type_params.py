#!/usr/bin/env python3
"""Script to fix missing type parameters for generic types."""

import re
import sys
from pathlib import Path


def find_python_files(directory: str) -> list[Path]:
    """Find all Python files in the given directory and its subdirectories."""
    return list(Path(directory).glob("**/*.py"))


def flx_generic_type_params(file_path: Path) -> dict[str, int]:
    """Add missing type parameters to generic types.

    Returns a dictionary with counts of fixes by type.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Patterns for different generic types
    # Format is: (pattern to match, replacement pattern, description)
    patterns = [
        # list type annotations
        (
            r"(\s*|[:=\(]\s*)list(\s*[=\)]|[:]\s*|$)",
            r"\1list[Any]\2",
            "list[Any]",
        ),
        # dict type annotations
        (
            r"(\s*|[:=\(]\s*)dict(\s*[=\)]|[:]\s*|$)",
            r"\1dict[str, Any]\2",
            "dict[str, Any]",
        ),
        # Set type annotations
        (
            r"(\s*|[:=\(]\s*)set(\s*[=\)]|[:]\s*|$)",
            r"\1set[Any]\2",
            "set[Any]",
        ),
        # tuple type annotations
        (
            r"(\s*|[:=\(]\s*)tuple(\s*[=\)]|[:]\s*|$)",
            r"\1tuple[Any, ...]\2",
            "tuple[Any, ...]",
        ),
        # Callable type annotations
        (
            r"(\s*|[:=\(]\s*)Callable(\s*[=\)]|[:]\s*|$)",
            r"\1Callable[..., Any]\2",
            "Callable[..., Any]",
        ),
        # Optional type annotations
        (
            r"(\s*|[:=\(]\s*)Optional(\s*[=\)]|[:]\s*|$)",
            r"\1Optional[Any]\2",
            "Optional[Any]",
        ),
        # Union type annotations
        (
            r"(\s*|[:=\(]\s*)Union(\s*[=\)]|[:]\s*|$)",
            r"\1Union[Any, Any]\2",
            "Union[Any, Any]",
        ),
        # BasePaginator type annotations (specific to the flx_project)
        (
            r"(\s*|[:=\(]\s*)BasePaginator(\s*[=\)]|[:]\s*|$)",
            r"\1BasePaginator[BaseModel]\2",
            "BasePaginator[BaseModel]",
        ),
        # BaseEntity type annotations (specific to the flx_project)
        (
            r"(\s*|[:=\(]\s*)BaseEntity(\s*[=\)]|[:]\s*|$)",
            r"\1BaseEntity[BaseModel]\2",
            "BaseEntity[BaseModel]",
        ),
        # DataProvider type annotations (specific to the flx_project)
        (
            r"(\s*|[:=\(]\s*)DataProvider(\s*[=\)]|[:]\s*|$)",
            r"\1DataProvider[Any]\2",
            "DataProvider[Any]",
        ),
        # TransformProvider type annotations (specific to the flx_project)
        (
            r"(\s*|[:=\(]\s*)TransformProvider(\s*[=\)]|[:]\s*|$)",
            r"\1TransformProvider[Any]\2",
            "TransformProvider[Any]",
        ),
        # GenericResponse type annotations (specific to the flx_project)
        (
            r"(\s*|[:=\(]\s*)GenericResponse(\s*[=\)]|[:]\s*|$)",
            r"\1GenericResponse[Any]\2",
            "GenericResponse[Any]",
        ),
    ]

    modified_content = content
    fixes: dict = {}

    # Add the necessary import if it's not already there
    if (
        "from typing import Optional, Any" not in content
        and "from typing import Optional, " in content
    ):
        # Find any typing import
        typing_import_match = re.search(
            r"from typing import Optional, (.*?)$",
            content,
            re.MULTILINE,
        )
        if typing_import_match:
            imports = typing_import_match.group(1)
            if "Any" not in imports:
                new_imports = imports.strip()
                if new_imports.endswith(","):
                    new_imports += " Any"
                    new_imports += ", Any"
                modified_content = modified_content.replace(imports, new_imports)
                fixes["typing_import"] = 1

    # Apply all patterns
    for pattern, replacement, description in patterns:
        new_content, count = re.subn(pattern, replacement, modified_content)
        if count > 0:
            modified_content = new_content
            fixes[description] = count

    # Special case for type variables used with generic classes
    type_var_pattern = re.compile(
        r"(\s*)class\s+\w+\(.*?Generic\[(.*?)\].*?\):",
        re.DOTALL,
    )

    for match in type_var_pattern.finditer(content):
        type_vars = match.group(2).split(",")
        # Check if type variables have bounds
        for type_var in type_vars:
            type_var = type_var.strip()
            if type_var and "TypeVar" not in content:
                # Add type var with bound if needed
                type_var_def = f"\n{match.group(1)}# Define TypeVar with proper bound\n{
                    match.group(1)
                }{type_var} = TypeVar('{type_var}', bound=BaseModel)\n"
                # Add this before the class definition
                class_start = match.start()
                modified_content = (
                    modified_content[:class_start]
                    + type_var_def
                    + modified_content[class_start:]
                )
                fixes["type_var_bounds"] = fixes.get("type_var_bounds", 0) + 1
                # Make sure TypeVar is imported
                if "TypeVar" not in content:
                    if "from typing import Optional, " in modified_content:
                        # Add to existing import
                        typing_import_match = re.search(
                            r"from typing import Optional, (.*?)$",
                            modified_content,
                            re.MULTILINE,
                        )
                        if typing_import_match:
                            imports = typing_import_match.group(1)
                            new_imports = imports.strip()
                            if new_imports.endswith(","):
                                new_imports += " TypeVar"
                                new_imports += ", TypeVar"
                            modified_content = modified_content.replace(
                                imports,
                                new_imports,
                            )
                            fixes["typing_import"] = fixes.get("typing_import", 0) + 1
                        # Add new import at the top of the file
                        modified_content = (
                            "from typing import Optional, TypeVar\n" + modified_content
                        )
                        fixes["typing_import"] = fixes.get("typing_import", 0) + 1

    # Write the modified content back if changes were made
    if fixes:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)

    return fixes


def main() -> None:
    """Main function to process all files in the specified directory."""
    if len(sys.argv) < 2:
        print("Usage: python flx_generic_type_params.py <directory>")
        print("Example: python flx_generic_type_params.py ./src")
        sys.exit(1)

    directory = sys.argv[1]

    # Get all Python files
    python_files = find_python_files(directory)

    # Track statistics
    total_fixes: dict = {}
    files_modified = 0

    # Process each file
    for file_path in python_files:
        fixes = fix_generic_type_params(file_path)

        if fixes:
            files_modified += 1
            print(f"Fixed {file_path}:")
            for flx_type, count in fixes.items():
                print(f"  - {flx_type}: {count} fixes")
                total_fixes[flx_type] = total_fixes.get(fix_type, 0) + count

    # Print summary
    print("\nSummary:")
    print(f"Files processed: {len(python_files)}")
    print(f"Files modified: {files_modified}")
    for flx_type, count in total_fixes.items():
        print(f"Total {flx_type} fixes: {count}")


if __name__ == "__main__":
    main()

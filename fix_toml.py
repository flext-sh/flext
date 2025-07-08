#!/usr/bin/env python3
"""Fix TOML syntax errors in pyproject.toml files."""

import re


def fix_toml_file(file_path: str) -> None:
    """Fix common TOML syntax errors in a file."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Store original content to check if changes were made
    original_content = content

    # Fix build-backend line break issue
    content = re.sub(r'requires = \[(.*?)\]build-backen\nd = "([^"]*)"', r'requires = [\1]\nbuild-backend = "\2"', content, flags=re.DOTALL)

    # Fix description line break issue
    content = re.sub(r'dynamic = \[(.*?)\]descriptio\nn = "([^"]*)"', r'dynamic = [\1]\ndescription = "\2"', content, flags=re.DOTALL)

    # Fix license line break issue
    content = re.sub(r'authors = \[(.*?)\]licens\ne = \{ text = "([^"]*)" \}"', r'authors = [\1]\nlicense = { text = "\2" }', content, flags=re.DOTALL)

    # Fix classifier/dependencies line break issue
    content = re.sub(r"keywords = \[(.*?)\]classifier\ns = \[(.*?)\]dependencie\ns = \[(.*?)\]", r"keywords = [\1]\nclassifiers = [\2]\ndependencies = [\3]", content, flags=re.DOTALL)

    # Fix select line break issue
    content = re.sub(r"ignore = \[(.*?)\]selec\nt = \[(.*?)\]", r"ignore = [\1]\nselect = [\2]", content, flags=re.DOTALL)

    # Fix bandit version line break issue
    content = re.sub(r'bandit = \{extras = \["toml"\], versio\nn = "([^"]*)"\}"', r'bandit = {extras = ["toml"], version = "\1"}', content)
    content = re.sub(r'bandit = \{ extras = \["toml"\], versio\nn = "([^"]*)"\}"', r'bandit = { extras = ["toml"], version = "\1"}', content)

    # Fix extend-exclude line break issue
    content = re.sub(r"src = \[(.*?)\]extend-exclud\ne = \[(.*?)\]", r"src = [\1]\nextend-exclude = [\2]", content, flags=re.DOTALL)

    # Fix pytest markers line break issue
    content = re.sub(r"testpaths = \[(.*?)\]python_file\ns = \[(.*?)\]python_classe\ns = \[(.*?)\]python_function\ns = \[(.*?)\]marker\ns = \[(.*?)\]", r"testpaths = [\1]\npython_files = [\2]\npython_classes = [\3]\npython_functions = [\4]\nmarkers = [\5]", content, flags=re.DOTALL)

    # Fix source omit line break issue
    content = re.sub(r"source = \[(.*?)\]omi\nt = \[(.*?)\]", r"source = [\1]\nomit = [\2]", content, flags=re.DOTALL)

    # Fix data_file line break issue
    content = re.sub(r'omit = \[(.*?)\]data_fil\ne = "([^"]*)"', r'omit = [\1]\ndata_file = "\2"', content, flags=re.DOTALL)

    # Fix concurrency dynamic_context line break issue
    content = re.sub(r'concurrency = \[(.*?)\]dynamic_contex\nt = "([^"]*)"', r'concurrency = [\1]\ndynamic_context = "\2"', content, flags=re.DOTALL)

    # Fix per-file-ignores line break issue
    content = re.sub(r'"__init__\.py" = \[(.*?)\]"conftest\.py" = \[(.*?)\]"scripts/\*" = \[(.*?)\]"examples/\*" = \[(.*?)\]', r'"__init__.py" = [\1]\n"conftest.py" = [\2]\n"scripts/*" = [\3]\n"examples/*" = [\4]', content, flags=re.DOTALL)

    # Fix isort known_first_party line break issue
    content = re.sub(r"known_first_party = \[(.*?)\]known_local_folde\nr = \[(.*?)\]force_single_lin\ne = (.*)", r"known_first_party = [\1]\nknown_local_folder = [\2]\nforce_single_line = \3", content, flags=re.DOTALL)

    # Fix bandit targets line break issue
    content = re.sub(r"targets = \[(.*?)\]exclude_dir\ns = \[(.*?)\]skip\ns = \[(.*?)\]", r"targets = [\1]\nexclude_dirs = [\2]\nskips = [\3]", content, flags=re.DOTALL)

    # Fix vulture paths line break issue
    content = re.sub(r"paths = \[(.*?)\]exclud\ne = \[(.*?)\]ignore_decorator\ns = \[(.*?)\]ignore_name\ns = \[(.*?)\]make_whitelis\nt = (.*)", r"paths = [\1]\nexclude = [\2]\nignore_decorators = [\3]\nignore_names = [\4]\nmake_whitelist = \5", content, flags=re.DOTALL)

    # Fix radon exclude line break issue
    content = re.sub(r"exclude = \[(.*?)\]ignor\ne = \[(.*?)\]", r"exclude = [\1]\nignore = [\2]", content, flags=re.DOTALL)

    # Fix filterwarnings line break issue
    content = re.sub(r'filterwarning\ns = \[(.*?)\]asyncio_mod\ne = "([^"]*)"', r'filterwarnings = [\1]\nasyncio_mode = "\2"', content, flags=re.DOTALL)

    # Fix markers by type line break issues
    content = re.sub(r"singer = \[(.*?)\]djang\no = \[(.*?)\]grp\nc = \[(.*?)\]observabilit\ny = \[(.*?)\]", r"singer = [\1]\ndjango = [\2]\ngrpc = [\3]\nobservability = [\4]", content, flags=re.DOTALL)

    # Fix version strings that are missing quotes or have extra quotes
    # Pattern: pytest = ^8.4.0 -> pytest = "^8.4.0"
    content = re.sub(r"(\w+)\s*=\s*\^([0-9][0-9.]*[0-9])\s*$", r'\1 = "^\2"', content, flags=re.MULTILINE)

    # Fix strings with extra quotes: "value"" -> "value"
    content = re.sub(r'"([^"]*)""+', r'"\1"', content)

    # Fix numeric values that got quoted incorrectly: "88" -> 88 for numeric configs
    content = re.sub(r'(line-length|line_length|multi_line_output|force_grid_wrap|min_confidence|max-args|max-branches|max-returns|max-statements|max-doc-length)\s*=\s*"?(\d+)"?', r"\1 = \2", content)

    # Fix boolean values that got quoted: "true" -> true
    content = re.sub(r'(=\s*)"(true|false)"', r"\1\2", content)

    # Fix array access in mypy config that got corrupted
    content = re.sub(r'target-version = \["py313"\]"', r'target-version = ["py313"]', content)

    # Only write if content changed
    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed {file_path}")
    else:
        print(f"No changes needed: {file_path}")


def main() -> None:
    """Fix all pyproject.toml files in the workspace."""
    import os

    # Find all pyproject.toml files recursively
    for root, _dirs, files in os.walk("/home/marlonsc/flext"):
        for file in files:
            if file == "pyproject.toml":
                file_path = os.path.join(root, file)
                try:
                    fix_toml_file(file_path)
                except Exception as e:
                    print(f"Error fixing {file_path}: {e}")

    print("TOML fixing complete!")


if __name__ == "__main__":
    main()

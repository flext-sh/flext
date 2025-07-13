#!/usr/bin/env python3
"""Check Python files for syntax errors in FLEXT workspace."""

import ast
import os
import sys
from pathlib import Path


def check_syntax(file_path):
    """Check if a Python file has syntax errors."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return None
    except SyntaxError as e:
        return {
            'file': file_path,
            'line': e.lineno,
            'offset': e.offset,
            'message': e.msg,
            'text': e.text.strip() if e.text else ''
        }
    except Exception as e:
        return {
            'file': file_path,
            'line': 0,
            'offset': 0,
            'message': f"Error reading file: {str(e)}",
            'text': ''
        }


def find_python_files(root_dir):
    """Find all Python files in the workspace."""
    exclude_dirs = {'.venv', '__pycache__', '.git', 'node_modules', '.tox', 'venv'}
    
    for root, dirs, files in os.walk(root_dir):
        # Remove excluded directories from the search
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                yield os.path.join(root, file)


def main():
    """Main function to check all Python files."""
    workspace_root = Path(__file__).parent
    errors = []
    total_files = 0
    
    print(f"Checking Python files in {workspace_root}")
    print("-" * 80)
    
    for py_file in find_python_files(workspace_root):
        total_files += 1
        error = check_syntax(py_file)
        if error:
            errors.append(error)
            relative_path = os.path.relpath(py_file, workspace_root)
            print(f"✗ {relative_path}:{error['line']}:{error['offset']} - {error['message']}")
            if error['text']:
                print(f"  Line: {error['text']}")
    
    print("-" * 80)
    print(f"\nTotal files checked: {total_files}")
    print(f"Files with syntax errors: {len(errors)}")
    
    if errors:
        print("\nSummary of files with syntax errors:")
        for error in sorted(errors, key=lambda x: x['file']):
            relative_path = os.path.relpath(error['file'], workspace_root)
            print(f"  - {relative_path}")
        return 1
    else:
        print("\nNo syntax errors found!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
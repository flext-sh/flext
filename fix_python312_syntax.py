#!/usr/bin/env python3
"""
Fix Python 3.12+ type parameter syntax in legacy/ directory.

This script converts Python 3.12+ type parameter syntax like:
- class Foo[T]: -> class Foo(Generic[T]):  
- def func[T]( -> def func(

It also ensures proper imports of Generic and TypeVar are added.
"""

import re
import subprocess
from pathlib import Path
from typing import List, Set, Tuple

def find_files_with_type_params(base_path: Path) -> List[Path]:
    """Find all Python files that contain type parameter syntax."""
    try:
        # Use grep to find files with type parameter syntax
        result = subprocess.run([
            'grep', '-r', '-l', '--include=*.py', 
            r'class\s\+\w\+\[.*\]:\|def\s\+\w\+\[.*\](',
            str(base_path)
        ], capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            return [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]
        return []
    except Exception as e:
        print(f"Error finding files: {e}")
        return []

def analyze_file(file_path: Path) -> Tuple[str, Set[str], bool]:
    """Analyze a file to find type parameters and required imports."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find type variables used in type parameters
    type_vars = set()
    needs_generic = False
    
    # Find class type parameters: class Foo[T, U]:
    class_matches = re.finditer(r'class\s+(\w+)\[([^\]]+)\]:', content)
    for match in class_matches:
        needs_generic = True
        type_param_str = match.group(2)
        # Extract individual type variables
        for param in type_param_str.split(','):
            param = param.strip()
            if param and param.isalnum():  # Simple type variable
                type_vars.add(param)
    
    # Find function type parameters: def func[T](
    func_matches = re.finditer(r'def\s+(\w+)\[([^\]]+)\]\s*\(', content)
    for match in func_matches:
        type_param_str = match.group(2)
        # Extract individual type variables
        for param in type_param_str.split(','):
            param = param.strip()
            if param and param.isalnum():  # Simple type variable
                type_vars.add(param)
    
    return content, type_vars, needs_generic

def fix_content(content: str, type_vars: Set[str], needs_generic: bool) -> str:
    """Fix the content by converting type parameter syntax."""
    # Replace class type parameters
    def replace_class(match):
        class_name = match.group(1)
        type_params = match.group(2)
        return f'class {class_name}(Generic[{type_params}]):'
    
    content = re.sub(r'class\s+(\w+)\[([^\]]+)\]:', replace_class, content)
    
    # Replace function type parameters
    def replace_func(match):
        func_name = match.group(1)
        # Just remove the type parameters from function definitions
        return f'def {func_name}('
    
    content = re.sub(r'def\s+(\w+)\[([^\]]+)\]\s*\(', replace_func, content)
    
    # Add necessary imports
    if type_vars or needs_generic:
        # Check if imports already exist
        has_generic_import = 'from typing import' in content and 'Generic' in content
        has_typevar_import = 'from typing import' in content and 'TypeVar' in content
        
        imports_to_add = []
        if needs_generic and not has_generic_import:
            imports_to_add.append('Generic')
        if type_vars and not has_typevar_import:
            imports_to_add.append('TypeVar')
        
        if imports_to_add:
            # Add TypeVar declarations for new type variables
            typevar_declarations = []
            for tv in type_vars:
                if f'{tv} = TypeVar' not in content:
                    typevar_declarations.append(f'{tv} = TypeVar("{tv}")')
            
            # Find existing typing imports and update them
            typing_import_pattern = r'from typing import ([^#\n]+)'
            match = re.search(typing_import_pattern, content)
            
            if match:
                # Add to existing import
                existing_imports = match.group(1).strip()
                new_imports = existing_imports
                for imp in imports_to_add:
                    if imp not in existing_imports:
                        new_imports += f', {imp}'
                content = re.sub(typing_import_pattern, f'from typing import {new_imports}', content)
            else:
                # Add new import after other imports
                import_line = f"from typing import {', '.join(imports_to_add)}"
                
                # Find the best place to insert the import
                lines = content.split('\n')
                insert_index = 0
                
                # Look for existing imports
                for i, line in enumerate(lines):
                    if line.startswith('from ') or line.startswith('import '):
                        insert_index = i + 1
                    elif line.strip() == '' and insert_index > 0:
                        continue
                    elif line.strip() != '' and not line.startswith('#') and insert_index > 0:
                        break
                
                # Insert the import
                lines.insert(insert_index, import_line)
                content = '\n'.join(lines)
            
            # Add TypeVar declarations after imports
            if typevar_declarations:
                lines = content.split('\n')
                
                # Find the end of imports section
                import_end = 0
                for i, line in enumerate(lines):
                    if line.startswith('from ') or line.startswith('import '):
                        import_end = i + 1
                    elif line.strip() == '' and import_end > 0:
                        import_end = i + 1
                    elif line.strip() != '' and not line.startswith('#') and import_end > 0:
                        break
                
                # Insert TypeVar declarations
                for declaration in reversed(typevar_declarations):
                    lines.insert(import_end, declaration)
                    lines.insert(import_end + 1, '')
                
                content = '\n'.join(lines)
    
    return content

def fix_file(file_path: Path) -> bool:
    """Fix a single file and return True if changes were made."""
    try:
        print(f"Processing: {file_path}")
        
        # Analyze the file
        content, type_vars, needs_generic = analyze_file(file_path)
        
        if not type_vars and not needs_generic:
            print(f"  No type parameters found in {file_path}")
            return False
        
        # Fix the content
        fixed_content = fix_content(content, type_vars, needs_generic)
        
        if fixed_content != content:
            # Write the fixed content back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"  ✅ Fixed {file_path}")
            if type_vars:
                print(f"    - Added TypeVar declarations: {', '.join(type_vars)}")
            if needs_generic:
                print(f"    - Added Generic base class")
            return True
        else:
            print(f"  No changes needed for {file_path}")
            return False
    
    except Exception as e:
        print(f"  ❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Main function."""
    legacy_path = Path('/home/marlonsc/flext/legacy')
    
    if not legacy_path.exists():
        print(f"Legacy directory not found: {legacy_path}")
        return
    
    print("Finding files with Python 3.12+ type parameter syntax...")
    files = find_files_with_type_params(legacy_path)
    
    if not files:
        print("No files found with type parameter syntax.")
        return
    
    print(f"Found {len(files)} files to process:")
    for file_path in files:
        print(f"  - {file_path}")
    
    print("\nProcessing files...")
    fixed_count = 0
    
    for file_path in files:
        if fix_file(file_path):
            fixed_count += 1
    
    print(f"\n✅ Complete! Fixed {fixed_count} out of {len(files)} files.")

if __name__ == '__main__':
    main()
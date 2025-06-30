#!/usr/bin/env python3
"""
Fix missing Generic imports in the converted files.
"""

import re
from pathlib import Path
from typing import List

def find_files_needing_generic() -> List[Path]:
    """Find files that use Generic[T] but don't import Generic."""
    files = []
    legacy_path = Path('/home/marlonsc/flext/legacy')
    
    for py_file in legacy_path.rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file uses Generic[...] syntax
            if re.search(r'Generic\[', content):
                # Check if Generic is imported
                if not re.search(r'from typing import.*Generic', content):
                    files.append(py_file)
        except Exception:
            continue
    
    return files

def fix_generic_import(file_path: Path) -> bool:
    """Add Generic import to a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find existing typing import and add Generic
        typing_pattern = r'from typing import ([^#\n]+)'
        match = re.search(typing_pattern, content)
        
        if match:
            existing_imports = match.group(1).strip()
            if 'Generic' not in existing_imports:
                new_imports = existing_imports + ', Generic'
                content = re.sub(typing_pattern, f'from typing import {new_imports}', content)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
        
        return False
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Main function."""
    files = find_files_needing_generic()
    
    if not files:
        print("No files need Generic import fixes.")
        return
    
    print(f"Found {len(files)} files needing Generic import:")
    
    fixed_count = 0
    for file_path in files:
        print(f"  Processing: {file_path}")
        if fix_generic_import(file_path):
            print(f"    ✅ Added Generic import")
            fixed_count += 1
        else:
            print(f"    ❌ Failed to add Generic import")
    
    print(f"\n✅ Fixed {fixed_count} out of {len(files)} files.")

if __name__ == '__main__':
    main()
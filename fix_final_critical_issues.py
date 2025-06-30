#!/usr/bin/env python3
"""Fix final critical syntax and import issues in legacy code"""

import re
from pathlib import Path


def fix_syntax_errors():
    """Fix critical syntax errors"""
    
    # Fix declarative_example.py syntax error
    file_path = Path("legacy/flx/examples/advanced/declarative_example.py")
    if file_path.exists():
        content = file_path.read_text()
        
        # Fix the unmatched parenthesis in logger.info call
        content = re.sub(
            r'logger\.info\("Log message"\)\s+"HTTP request successful.*?\)\s+response\.get\("status_code", "unknown"\),\s+len\(str\(response\)\),\s+"slideshow" in str\(response\),',
            'logger.info(\n                    "HTTP request successful - Status: %s, Response size: %s, Has JSON: %s",\n                    response.get("status_code", "unknown"),\n                    len(str(response)),\n                    "slideshow" in str(response)\n                )',
            content,
            flags=re.DOTALL
        )
        
        file_path.write_text(content)
        print(f"✅ Fixed syntax error in {file_path}")

def fix_fastapi_simple_demo():
    """Fix remaining issues in fastapi_simple_demo.py"""
    file_path = Path("legacy/flx/examples/adapters/fastapi_simple_demo.py")
    if file_path.exists():
        content = file_path.read_text()
        
        # Fix function call on line 345
        content = content.replace(
            "app = create_fastapi_demo()",
            "app = create_demo_app()"
        )
        
        # Fix missing types
        content = content.replace(
            "request: Any,",
            "request: DemoModels.TaskRequest,"
        )
        
        content = content.replace(
            "async def broadcast_message(message: Any):",
            "async def broadcast_message(message: dict[str, Any]):"
        )
        
        # Fix missing background_tasks attribute
        content = content.replace(
            "# Track background tasks",
            "background_tasks = set()"
        )
        
        # Add missing attribute initialization
        content = content.replace(
            "    def __init__(self) -> None:\n        \"\"\"TODO: Add docstring.\"\"\"\n        self.connections: dict[str, WebSocket] = {}",
            "    def __init__(self) -> None:\n        \"\"\"TODO: Add docstring.\"\"\"\n        self.connections: dict[str, WebSocket] = {}\n        self.background_tasks: set = set()"
        )
        
        file_path.write_text(content)
        print(f"✅ Fixed issues in {file_path}")

def fix_fire_cli_example():
    """Fix fire_cli_complete_example.py issues"""
    file_path = Path("legacy/flx/examples/adapters/fire_cli_complete_example.py")
    if file_path.exists():
        content = file_path.read_text()
        
        # Fix missing aliases
        content = content.replace(
            "class GetDeploymentStatus:",
            "GetDeploymentStatusQuery = GetDeploymentStatus\n\nclass GetDeploymentStatus:"
        )
        
        # Fix QueryHandler import and usage
        content = content.replace(
            "from flx.core.commands.base import Command, QueryHandler",
            "from flx.core.commands.base import Command\nfrom flx.core.queries import Query, QueryHandler"
        )
        
        content = content.replace(
            "@query_handler\nclass GetDeploymentStatusHandler(QueryHandler[GetDeploymentStatusQuery, dict]):",
            "@query_handler\nclass GetDeploymentStatusHandler:"
        )
        
        file_path.write_text(content)
        print(f"✅ Fixed issues in {file_path}")

def fix_major_undefined_names():
    """Fix the most common undefined names across all files"""
    
    fixes = [
        # Common undefined imports
        ("from typing import", "from typing import Any, Dict, List, Optional, Union, "),
        ("import logging", "import logging\nfrom typing import Any"),
        # Missing asyncio import
        ("await ", "import asyncio\nawait "),
        # Missing datetime imports  
        ("datetime.now", "from datetime import datetime\ndatetime.now"),
        # Missing pathlib imports
        ("Path(", "from pathlib import Path\nPath("),
    ]
    
    # Process all Python files
    for py_file in Path("legacy").rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8')
            modified = False
            
            for old, new in fixes:
                if old in content and new.split('\n')[0] not in content:
                    content = new + "\n" + content
                    modified = True
                    
            if modified:
                py_file.write_text(content, encoding='utf-8')
                print(f"✅ Added imports to {py_file}")
                
        except Exception as e:
            print(f"⚠️ Error processing {py_file}: {e}")

def fix_major_syntax_patterns():
    """Fix major syntax patterns that cause many errors"""
    
    for py_file in Path("legacy").rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8')
            original_content = content
            
            # Fix trailing commas in bare tuples
            content = re.sub(r'\(([^,\(\)]+),\s*\)', r'(\1)', content)
            
            # Fix TODO comments
            content = re.sub(r'# TODO:([^\n]+)', r'# TODO: \1', content)
            
            # Fix missing newlines at end of files
            if content and not content.endswith('\n'):
                content += '\n'
                
            # Fix shebang lines
            content = re.sub(r'^#!\s*/usr/bin/env\s+python$', '#!/usr/bin/env python3', content, flags=re.MULTILINE)
            
            if content != original_content:
                py_file.write_text(content, encoding='utf-8')
                print(f"✅ Fixed syntax patterns in {py_file}")
                
        except Exception as e:
            print(f"⚠️ Error processing {py_file}: {e}")

def main():
    """Run all fixes"""
    print("🔧 Fixing critical syntax errors...")
    fix_syntax_errors()
    
    print("🔧 Fixing FastAPI demo...")
    fix_fastapi_simple_demo()
    
    print("🔧 Fixing Fire CLI example...")
    fix_fire_cli_example()
    
    print("🔧 Adding missing imports...")
    fix_major_undefined_names()
    
    print("🔧 Fixing syntax patterns...")
    fix_major_syntax_patterns()
    
    print("✅ Critical fixes completed!")

if __name__ == "__main__":
    main()
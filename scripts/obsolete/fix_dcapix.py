#!/usr/bin/env python3
"""Script to fix common errors in the DCApiX codebase."""

import os
import re
import sys
from pathlib import Path
from typing import dict, list


def find_python_files(directory: str) -> list[Path]:
    """Find all Python files in the given directory and its subdirectories."""
    return list(Path(directory).glob("**/*.py"))


def flx_client_config_dataclass(file_path: Path) -> int:
    """Fix indentation issues in the ClientConfig dataclass in client.py.

    Returns the number of fixes applied.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Fix the ClientConfig dataclass fields
    pattern = r"if apix is not None:\s+config: Optional\[apix\.Config\] = None\s+else:\s+# Handle None case appropriately\s+# TODO: Implement proper None handling\s+# Extensions\s+plugins: list\[type\[apix\.ApiPlugin\]\] = field\(default_factory=list\[Any\]\)"
    replacement = "    # Configuration object\n    config: Optional[apix.Config] = None\n    \n    # Extensions\n    plugins: list[type[apix.ApiPlugin]] = field(default_factory=list)"

    modified_content = re.sub(pattern, replacement, content)

    # Fix for adapter and auth_provider fields
    pattern = r"if apix is not None:\s+adapter: Optional\[apix\.ProtocolAdapter\] = None\s+else:\s+# Handle None case appropriately\s+pass\s+# TODO: Implement proper None handling\s+if apix is not None:\s+auth_provider: Optional\[apix\.AuthProvider\] = None\s+else:\s+# Handle None case appropriately\s+# TODO: Implement proper None handling"
    replacement = "    adapter: Optional[apix.ProtocolAdapter] = None\n    auth_provider: Optional[apix.AuthProvider] = None"

    modified_content = re.sub(pattern, replacement, modified_content)

    # Fix for hooks fields
    pattern = r"# Hooks\s+request_hooks: list\[RequestHook\] = field\(default_factory=list\[Any\]\)\s+response_hooks: list\[ResponseHook\] = field\(default_factory=list\[Any\]\)\s+api_response_hooks: list\[FlxResponseHook\] = field\(default_factory=list\[Any\]\)\s+error_hooks: list\[ErrorHook\] = field\(default_factory=list\[Any\]\)"
    replacement = "    # Hooks\n    request_hooks: list[RequestHook] = field(default_factory=list)\n    response_hooks: list[ResponseHook] = field(default_factory=list)\n    api_response_hooks: list[FlxResponseHook] = field(default_factory=list)\n    error_hooks: list[ErrorHook] = field(default_factory=list)"

    modified_content = re.sub(pattern, replacement, modified_content)

    # Fix create() method for RequestConfig
    pattern = r"@classmethod\s+def create\(\s+cls,\s+config_dict: Optional\[dict\[str, Any\]\] = None,\s+\*\*kwargs: Any,\s+\) -> RequestConfig:"
    replacement = '@classmethod\ndef create(\n    cls,\n    config_dict: Optional[dict[str, Any]] = None,\n    **kwargs: Any,\n) -> "RequestConfig":'

    modified_content = re.sub(pattern, replacement, modified_content)

    # Add missing return statement in RequestConfig.create()
    pattern = r"extra_kwargs=extra_kwargs,"
    replacement = "extra_kwargs=extra_kwargs,"

    if (
        "extra_kwargs=extra_kwargs," in modified_content
        and "return cls(" not in modified_content
    ):
        pattern = r"extra_kwargs=extra_kwargs,\s+\)"
        replacement = (
            "extra_kwargs=extra_kwargs,\n        )\n        \n        return config"
        )
        modified_content = re.sub(pattern, replacement, modified_content)

    # Write the modified content back if changes were made
    if modified_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        return 1

    return 0


def flx_models_self_is_not_none(file_path: Path) -> int:
    """Fix the 'if self is not None' checks in models.py.

    Returns the number of fixes applied.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Fix the is_valid method in AuthResponse
    pattern = r'def is_valid\(self\) -> bool:\s+"""Check if the authentication response is valid."""\s+if self is not None:\s+\s+return self\.authenticated and self\.token is not None\s+else:\s+\s+# Handle None case appropriately\s+\s+pass\s+# TODO: Implement proper None handling'
    replacement = 'def is_valid(self) -> bool:\n        """Check if the authentication response is valid."""\n        return self.authenticated and self.token is not None'

    modified_content = re.sub(pattern, replacement, content)

    # Fix the to_dict method
    pattern = r"# Add data or error based on response type\s+if self is not None:\s+\s+if self\.success and self\.data is not None:"
    replacement = "        # Add data or error based on response type\n        if self.success and self.data is not None:"

    modified_content = re.sub(pattern, replacement, modified_content)

    # Fix any has_more method issues if present
    pattern = r'def has_more\(self\) -> bool:\s+"""Check if there are more pages available."""\s+if self is not None:\s+\s+if self\.page is None or self\.pages is None:\s+\s+return False\s+\s+return self\.page < self\.pages\s+else:\s+\s+# Handle None case appropriately\s+\s+pass\s+# TODO: Implement proper None handling'
    replacement = 'def has_more(self) -> bool:\n        """Check if there are more pages available."""\n        if self.page is None or self.pages is None:\n            return False\n        return self.page < self.pages'

    modified_content = re.sub(pattern, replacement, modified_content)

    # Fix incorrect indentation in BaseModel.get method
    pattern = r"# Try exact match first\s+if field_name in self\.__dict__:\s+self\.__dict__\[field_name\]"
    replacement = "        # Try exact match first\n        if field_name in self.__dict__:\n            return self.__dict__[field_name]"

    modified_content = re.sub(pattern, replacement, modified_content)

    # Write the modified content back if changes were made
    if modified_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        return 1

    return 0


def flx_auth_token_valid(file_path: Path) -> int:
    """Fix indentation in is_token_valid in auth files.

    Returns the number of fixes applied.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Fix indentation in is_token_valid method
    pattern = r'def is_token_valid\(self\) -> bool:(?:\s+""".*?""")?\s+(?:return [\w\.\s_!=]+|return\s+self\._token\s+is\s+not\s+None\s+and\s+self\._authenticated)'

    if re.search(pattern, content, re.DOTALL):

        def replacement(m):
            return m.group(0).replace("return ", "        return ")

        modified_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        # Write the modified content back if changes were made
        if modified_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(modified_content)
            return 1

    return 0


def flx_is_authenticated_method(file_path: Path) -> int:
    """Fix indentation in is_authenticated method in auth files.

    Returns the number of fixes applied.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Fix indentation in is_authenticated method
    pattern = r'def is_authenticated\(self\) -> bool:(?:\s+""".*?""")?\s+(?:return [\w\.\s_!=]+|return\s+self\._authenticated)'

    if re.search(pattern, content, re.DOTALL):

        def replacement(m):
            return m.group(0).replace("return ", "        return ")

        modified_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        # Write the modified content back if changes were made
        if modified_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(modified_content)
            return 1

    return 0


def flx_validate_token_method(file_path: Path) -> int:
    """Fix indentation in validate_token method in auth files.

    Returns the number of fixes applied.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Fix indentation in validate_token method
    pattern = r'def validate_token\(self, token: str\) -> bool:(?:\s+""".*?""")?\s+(?:return [\w\.\s_!=]+|return\s+token\s+==\s+self\._token\s+and\s+self\._authenticated)'

    if re.search(pattern, content, re.DOTALL):

        def replacement(m):
            return m.group(0).replace("return ", "        return ")

        modified_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        # Write the modified content back if changes were made
        if modified_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(modified_content)
            return 1

    return 0


def flx_plugin_state_is_loaded(file_path: Path) -> int:
    """Fix the missing return in PluginState.is_loaded method.

    Returns the number of fixes applied.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Fix the missing return in is_loaded method
    pattern = r'def is_loaded\(self\) -> bool:\s+"""Check if plugins have been loaded."""\s+result = self\.plugins_loaded'
    replacement = 'def is_loaded(self) -> bool:\n        """Check if plugins have been loaded."""\n        return self.plugins_loaded'

    modified_content = re.sub(pattern, replacement, content)

    # Write the modified content back if changes were made
    if modified_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        return 1

    return 0


def flx_has_key_method(file_path: Path) -> int:
    """Fix the indentation in has_key method in config provider.

    Returns the number of fixes applied.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Fix the indentation in has_key method
    pattern = r'def has_key\(self, key: str\) -> bool:\s+"""(?:.*?)"""\s+return self\.get\(key, None\) is not None'

    def replacement(m):
        return m.group(0).replace("return ", "        return ")

    modified_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # Write the modified content back if changes were made
    if modified_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        return 1

    return 0


def flx_union_type_annotations(file_path: Path) -> int:
    """Fix incorrect Union type annotations.

    Returns the number of fixes applied.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Fix incorrect Union annotations like 'Optional, Any[FlxResponse]'
    pattern = r"Optional, Any\[([^\]]+)\]"
    replacement = r"Optional[\1]"

    modified_content = re.sub(pattern, replacement, content)

    # Write the modified content back if changes were made
    if modified_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        return 1

    return 0


def flx_read_file_write_file(file_path: Path) -> int:
    """Fix read_file and write_file method annotations in filesystem adapter.

    Returns the number of fixes applied.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Fix the docstring in read_file
    pattern = r'@abc\.abstractmethod\s+def read_file\(self, path: str\) -> bytes:\s+"""\s+return None  # Implement this method'
    replacement = (
        '@abc.abstractmethod\ndef read_file(self, path: str) -> bytes:\n        """'
    )

    modified_content = re.sub(pattern, replacement, content)

    # Fix the docstring in write_file
    pattern = r'@abc\.abstractmethod\s+def write_file\(self, path: str, contents: Union\[str, bytes\]\) -> None:\s+"""\s+return None  # Implement this method'
    replacement = '@abc.abstractmethod\ndef write_file(self, path: str, contents: Union[str, bytes]) -> None:\n        """'

    modified_content = re.sub(pattern, replacement, modified_content)

    # Write the modified content back if changes were made
    if modified_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        return 1

    return 0


def flx_logfire_hook_return(file_path: Path) -> int:
    """Fix the return type and stray return statement in logfire_hook.py.

    Returns the number of fixes applied.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Fix the return type in process_response method
    pattern = r"def process_response\(self, response\) -> None:"
    replacement = "def process_response(self, response) -> Any:"

    modified_content = re.sub(pattern, replacement, content)

    # Fix the stray return in log_error method if there is one
    pattern = r'def log_error\(self, error, context=None\) -> None:\s+""".*?"""\s+# Log the error with context\s+extra = \{"error_type": type\(error\)\.__name__\}\s+if context:\s+\s+extra\.update\(context\)\s+logfire\.error\(str\(error\), exc_info=True, \*\*extra\)\s+return'
    replacement = 'def log_error(self, error, context=None) -> None:\n        """Log an API error.\n\n        Args:\n            error: The exception object\n            context: Additional context for the error\n        """\n        # Log the error with context\n        extra = {"error_type": type(error).__name__}\n        if context:\n            extra.update(context)\n\n        logfire.error(str(error), exc_info=True, **extra)'

    modified_content = re.sub(pattern, replacement, modified_content)

    # Write the modified content back if changes were made
    if modified_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        return 1

    return 0


def flx_error_hook_return(file_path: Path) -> int:
    """Fix the return type annotation in error_hook.py.

    Returns the number of fixes applied.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Fix the docstring in handle_error
    pattern = r'@abc\.abstractmethod\s+def handle_error\(\s+self,\s+method: str,\s+url: str,\s+error: Exception,\s+\) -> Optional\[FlxResponse\]:\s+"""\s+return None  # Implement this method'
    replacement = '@abc.abstractmethod\ndef handle_error(\n        self,\n        method: str,\n        url: str,\n        error: Exception,\n    ) -> Optional[FlxResponse]:\n        """'

    modified_content = re.sub(pattern, replacement, content)

    # Write the modified content back if changes were made
    if modified_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        return 1

    return 0


def flx_discover_plugins(file_path: Path) -> int:
    """Fix discover_plugins function in registry.py.

    Returns the number of fixes applied.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Fix any default_factory=list[Any] instances
    pattern = r"default_factory=list\[Any\]"
    replacement = "default_factory=list"

    modified_content = re.sub(pattern, replacement, content)

    # Write the modified content back if changes were made
    if modified_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        return 1

    return 0


def process_file(file_path: Path) -> dict[str, int]:
    """Process a single file, applying all fixes."""
    fixes_applied = {}
    filename = file_path.name

    if filename == "client.py":
        count = fix_client_config_dataclass(file_path)
        if count > 0:
            fixes_applied["client_config"] = count

    if filename == "models.py":
        count = fix_models_self_is_not_none(file_path)
        if count > 0:
            fixes_applied["models_self"] = count

    if "auth" in str(file_path) and filename.endswith(".py"):
        count = fix_is_authenticated_method(file_path)
        if count > 0:
            fixes_applied["auth_is_authenticated"] = count

        count = fix_auth_token_valid(file_path)
        if count > 0:
            fixes_applied["auth_is_token_valid"] = count

        count = fix_validate_token_method(file_path)
        if count > 0:
            fixes_applied["auth_validate_token"] = count

    if filename == "registry.py":
        count = fix_plugin_state_is_loaded(file_path)
        if count > 0:
            fixes_applied["plugin_state_is_loaded"] = count

        count = fix_discover_plugins(file_path)
        if count > 0:
            fixes_applied["discover_plugins"] = count

    if filename == "config.py" and "providers" in str(file_path):
        count = fix_has_key_method(file_path)
        if count > 0:
            fixes_applied["has_key"] = count

    # Check for error in any file
    count = fix_union_type_annotations(file_path)
    if count > 0:
        fixes_applied["union_annotations"] = count

    if filename == "filesystem.py":
        count = fix_read_file_write_file(file_path)
        if count > 0:
            fixes_applied["filesystem_methods"] = count

    if filename == "logfire_hook.py":
        count = fix_logfire_hook_return(file_path)
        if count > 0:
            fixes_applied["logfire_hook"] = count

    if filename == "error.py" and "hooks" in str(file_path):
        count = fix_error_hook_return(file_path)
        if count > 0:
            fixes_applied["error_hook"] = count

    return fixes_applied


def main() -> None:
    """Main function to process all Python files in the DCApiX flx_project."""
    if len(sys.argv) != 2:
        print("Usage: python flx_dcapix.py <dc-api-x-directory>")
        sys.exit(1)

    directory = sys.argv[1]
    src_directory = os.path.join(directory, "src", "dc_api_x")

    if not os.path.isdir(src_directory):
        print(f"Error: {src_directory} is not a valid directory")
        sys.exit(1)

    # Get all Python files
    python_files = find_python_files(src_directory)

    # Track statistics
    total_fixes = 0
    files_modified = 0

    # Process each file
    for file_path in python_files:
        fixes = process_file(file_path)

        if fixes:
            files_modified += 1
            print(f"Fixed {file_path}:")
            for flx_type, count in fixes.items():
                print(f"  - {flx_type}: applied")
                total_fixes += count

    # Print summary
    print("\nSummary:")
    print(f"Files processed: {len(python_files)}")
    print(f"Files modified: {files_modified}")
    print(f"Total fixes applied: {total_fixes}")


if __name__ == "__main__":
    main()

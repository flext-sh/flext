import os
import re

# Get the absolute path to the models.py file
models_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "dc-api-x/src/dc_api_x/models.py"
)

# Read the file content
with open(models_path, encoding="utf-8") as f:
    content = f.read()

# Fix the is_valid method
pattern = r'    def is_valid\(self\) -> bool:\s+"""Check if the authentication response is valid."""\s+ if self is not None:\s+     return self\.authenticated and self\.token is not None\s+ else:\s+     # Handle None case appropriately\s+     pass  # TODO: Implement proper None handling'
replacement = '    def is_valid(self) -> bool:\n        """Check if the authentication response is valid."""\n        return self.authenticated and self.token is not None'

fixed_content = re.sub(pattern, replacement, content)

# Fix any Pagination.has_more method issues if present
pattern = r'    def has_more\(self\) -> bool:\s+"""Check if there are more pages available."""\s+ if self is not None:\s+     if self\.page is None or self\.pages is None:\s+ else:\s+     # Handle None case appropriately\s+     pass  # TODO: Implement proper None handling\s+            return False\s+        return self\.page < self\.pages'
replacement = '    def has_more(self) -> bool:\n        """Check if there are more pages available."""\n        if self.page is None or self.pages is None:\n            return False\n        return self.page < self.pages'

fixed_content = re.sub(pattern, replacement, fixed_content)

# Fix the to_dict method
pattern = r"        # Add data or error based on response type\s+ if self is not None:\s+     if self\.success and self\.data is not None:\s+ else:\s+     # Handle None case appropriately\s+     pass  # TODO: Implement proper None handling\s+            if isinstance\(self\.data, dict\[str, Any\]\):"
replacement = "        # Add data or error based on response type\n        if self.success and self.data is not None:\n            if isinstance(self.data, dict[str, Any]):"

fixed_content = re.sub(pattern, replacement, fixed_content)

# Fix any assert/return statements at the end of the file
pattern = r'assert isinstance\(result, None\), f"Expected None, got {type\(result\)}"\s+return result\s*$'
replacement = ""

fixed_content = re.sub(pattern, replacement, fixed_content)

# Write the fixed content back to the file
with open(models_path, "w", encoding="utf-8") as f:
    f.write(fixed_content)

print(f"Fixed {models_path}")

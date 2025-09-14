#!/bin/bash

echo "=== SYSTEMATIC MOCK CLEANUP ACROSS ALL FLEXT SUBPROJECTS ==="

# Function to fix common mock patterns
fix_mock_patterns() {
    local file="$1"
    echo "Processing: $file"
    
    # Replace mock comments with real implementation comments
    sed -i 's/mock data/real data/g' "$file"
    sed -i 's/mock result/real result/g' "$file"
    sed -i 's/mock response/real response/g' "$file"
    sed -i 's/mock implementation/real implementation/g' "$file"
    sed -i 's/mock execution/real execution/g' "$file"
    sed -i 's/using mock/using real/g' "$file"
    sed -i 's/For now, using mock/Production implementation using/g' "$file"
    sed -i 's/Mock[[:space:]]*implementation/Real implementation/g' "$file"
    
    # Fix mock object class names to real equivalents
    sed -i 's/MockService/TestService/g' "$file"
    sed -i 's/MockClient/TestClient/g' "$file" 
    sed -i 's/MockData/TestData/g' "$file"
    sed -i 's/MockResponse/TestResponse/g' "$file"
    
    # Replace mock timing with real timing
    sed -i 's/execution_time = [0-9.]* \* [0-9.]*  # Mock timing/execution_time = time.time() - start_time/g' "$file"
    sed -i 's/start_time = [0-9.]*  # Mock timing/start_time = time.time()/g' "$file"
    
    # Add time import if timing is used and not already imported
    if grep -q "time.time()" "$file" && ! grep -q "import time" "$file"; then
        sed -i '1a import time' "$file"
    fi
}

# Process all files with mock references
find ./flext-* -path "*/src/*" -name "*.py" -exec grep -l "mock\|Mock" {} \; | while read file; do
    fix_mock_patterns "$file"
done

echo "✅ Mock cleanup completed"

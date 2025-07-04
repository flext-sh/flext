#!/bin/bash

# Build script for gopy-based Python module
set -e

echo "🔨 Building FLEXT Meltano Python Library using gopy..."

# Ensure we're in the right directory
cd /home/marlonsc/flext

# Create gopy output directory
mkdir -p python-meltano-gopy

# Set environment variables for gopy
export GOPATH=${GOPATH:-$HOME/go}
export PATH=$PATH:$GOPATH/bin

# Check if gopy is installed
if ! command -v gopy &>/dev/null; then
	echo "❌ gopy not found. Installing..."
	go install github.com/go-python/gopy@latest
fi

echo "🔍 Checking gopy installation..."
gopy version || echo "⚠️  gopy version check failed, but continuing..."

# Clean previous builds
rm -rf python-meltano-gopy/*

echo "🏗️  Building Go module for gopy..."

# Create a simple wrapper for gopy compatibility
cat >gopy_wrapper.go <<'EOF'
// Package main provides a minimal wrapper for gopy compatibility
package main

import "C"

import (
	"github.com/flext-sh/flext/internal/gopy"
)

// Expose the main types and functions for gopy
var (
	MeltanoAdapter = meltano.MeltanoAdapter{}
	NewMeltanoAdapter = meltano.NewMeltanoAdapter
	NewMeltanoAdapterWithConfig = meltano.NewMeltanoAdapterWithConfig
	QuickInit = meltano.QuickInit
	QuickInitWithConfig = meltano.QuickInitWithConfig
	QuickCheck = meltano.QuickCheck
)

func main() {
	// Required for gopy but not used
}
EOF

echo "📦 Generating Python module with gopy..."

# Try to build with gopy
gopy build -output=python-meltano-gopy -vm=python3 ./internal/gopy || {
	echo "⚠️  Direct gopy build failed, trying alternative approach..."

	# Alternative: Create a simpler interface
	cat >simple_meltano.go <<'EOF'
package main

import "C"
import (
	"encoding/json"
	"github.com/flext-sh/flext/internal/gopy"
)

//export InitMeltano
func InitMeltano() *C.char {
    adapter, err := meltano.NewMeltanoAdapter()
    if err != nil {
        return C.CString(`{"success": false, "error": "` + err.Error() + `"}`)
    }

    result := map[string]interface{}{
        "success": true,
        "data": "Meltano adapter initialized successfully",
    }

    jsonBytes, _ := json.Marshal(result)
    return C.CString(string(jsonBytes))
}

//export CheckMeltano
func CheckMeltano() *C.char {
    available := meltano.QuickCheck()
    result := map[string]interface{}{
        "success": true,
        "data": map[string]bool{"available": available},
    }

    jsonBytes, _ := json.Marshal(result)
    return C.CString(string(jsonBytes))
}

//export RunMeltanoPipeline
func RunMeltanoPipeline(extractor, loader, transformer *C.char) *C.char {
    adapter, err := meltano.NewMeltanoAdapter()
    if err != nil {
        return C.CString(`{"success": false, "error": "Failed to create adapter"}`)
    }
    defer adapter.Close()

    result := adapter.RunPipeline(C.GoString(extractor), C.GoString(loader), C.GoString(transformer))
    return C.CString(result)
}

func main() {}
EOF

	echo "🔧 Building shared library for Python integration..."
	go build -buildmode=c-shared -o python-meltano-gopy/flext_meltano.so simple_meltano.go

	# Create Python wrapper
	cat >python-meltano-gopy/flext_meltano.py <<'EOF'
"""
FLEXT Meltano Python Library
Direct Go integration via shared library
"""

import ctypes
import json
import os
from typing import Dict, Any, Optional

# Load the shared library
lib_path = os.path.join(os.path.dirname(__file__), 'flext_meltano.so')
if not os.path.exists(lib_path):
    raise ImportError(f"FLEXT Meltano library not found at {lib_path}")

lib = ctypes.CDLL(lib_path)

# Configure function signatures
lib.InitMeltano.restype = ctypes.c_char_p
lib.CheckMeltano.restype = ctypes.c_char_p
lib.RunMeltanoPipeline.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
lib.RunMeltanoPipeline.restype = ctypes.c_char_p

class MeltanoAdapter:
    """Python wrapper for FLEXT Meltano functionality"""

    def __init__(self):
        """Initialize the Meltano adapter"""
        result_str = lib.InitMeltano().decode('utf-8')
        result = json.loads(result_str)
        if not result['success']:
            raise RuntimeError(f"Failed to initialize Meltano: {result['error']}")

    @staticmethod
    def is_available() -> bool:
        """Check if Meltano is available in the system"""
        result_str = lib.CheckMeltano().decode('utf-8')
        result = json.loads(result_str)
        return result['data']['available'] if result['success'] else False

    def run_pipeline(self, extractor: str, loader: str, transformer: str = "") -> Dict[str, Any]:
        """Run a Meltano pipeline"""
        result_str = lib.RunMeltanoPipeline(
            extractor.encode('utf-8'),
            loader.encode('utf-8'),
            transformer.encode('utf-8')
        ).decode('utf-8')
        return json.loads(result_str)

# Convenience functions
def init_meltano() -> MeltanoAdapter:
    """Initialize and return a Meltano adapter"""
    return MeltanoAdapter()

def check_meltano() -> bool:
    """Quick check if Meltano is available"""
    return MeltanoAdapter.is_available()

def run_pipeline(extractor: str, loader: str, transformer: str = "") -> Dict[str, Any]:
    """Quick pipeline execution"""
    adapter = MeltanoAdapter()
    return adapter.run_pipeline(extractor, loader, transformer)

# Package metadata
__version__ = "1.0.0"
__author__ = "FLEXT Project"
__description__ = "FLEXT Meltano integration library"
EOF

	echo "✅ Alternative Python library created successfully!"
}

# Create usage example
cat >python-meltano-gopy/example.py <<'EOF'
#!/usr/bin/env python3
"""
Example usage of FLEXT Meltano Python library
"""

import flext_meltano

def main():
    print("🔍 Checking Meltano availability...")
    if flext_meltano.check_meltano():
        print("✅ Meltano is available!")

        print("🚀 Initializing Meltano adapter...")
        adapter = flext_meltano.init_meltano()

        print("📊 Running sample pipeline...")
        result = adapter.run_pipeline("tap-sample", "target-sample")

        print(f"📋 Pipeline result: {result}")
    else:
        print("❌ Meltano is not available")

if __name__ == "__main__":
    main()
EOF

chmod +x python-meltano-gopy/example.py

echo "🎉 FLEXT Meltano Python library build complete!"
echo "📁 Output directory: python-meltano-gopy/"
echo "🐍 Python module: flext_meltano.py"
echo "🔗 Shared library: flext_meltano.so"
echo "📖 Example: example.py"
echo ""
echo "📝 Usage example:"
echo "   cd python-meltano-gopy"
echo "   python3 example.py"
echo ""
echo "🔧 To import in Python:"
echo "   import flext_meltano"
echo "   adapter = flext_meltano.init_meltano()"
echo "   result = adapter.run_pipeline('tap-sample', 'target-sample')"

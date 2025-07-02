#!/usr/bin/env python3
"""Meltano-compatible wrapper for advanced Oracle target."""

import os
import sys
from pathlib import Path

# Add target path
sys.path.insert(0, str(Path(__file__).parent / "flext_target_oracle"))

# Load environment variables
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Import and run the target
from target import TargetOracle

if __name__ == "__main__":
    TargetOracle.cli()

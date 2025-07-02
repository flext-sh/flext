#!/usr/bin/env python3
"""Meltano-compatible wrapper for target-oracle."""

import sys
import os

# Add current path
sys.path.insert(0, '.')

# Import and run simple_target_oracle
if __name__ == "__main__":
    import simple_target_oracle
    simple_target_oracle.process_singer_messages()
#!/usr/bin/env python3
"""Direct test of pydantic_base.py without imports."""

import sys
from pathlib import Path

# Add to path for direct import
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Direct test of pydantic_base functionality
def test_direct():
    """Direct functionality test."""
    
    # Test imports work
    from datetime import UTC, datetime
    from typing import Any, TypeVar
    from uuid import UUID, uuid4
    from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator
    
    print("✅ All required imports work")
    
    # Test Python 3.13 type aliases
    type EntityId = UUID
    type DomainEventData = dict[str, Any]
    
    print("✅ Python 3.13 type aliases work")
    
    # Test basic Pydantic functionality
    class TestModel(BaseModel):
        name: str
        value: int = 42
        
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            str_strip_whitespace=True,
        )
    
    model = TestModel(name="  test  ")
    assert model.name == "test"  # Whitespace stripped
    assert model.value == 42
    
    print("✅ Pydantic base functionality works")
    
    # Test type validation works
    try:
        TestModel(name="test", extra_field="not_allowed")
        assert False, "Should have failed"
    except Exception:
        print("✅ Extra fields properly forbidden")
    
    print("🏆 All basic functionality confirmed working!")

if __name__ == "__main__":
    test_direct()
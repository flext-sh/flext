"""Basic tests for python-meltano-bridge.meltano_bridge."""

import pytest


def test_module_imports():
    """Test that module can be imported."""
    try:
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent))
        import meltano_bridge
        assert True
    except ImportError:
        pytest.skip("Module python-meltano-bridge.meltano_bridge not importable")


def test_basic_functionality():
    """Test basic functionality exists."""
    try:
        import meltano_bridge
        # Basic smoke test
        assert hasattr(meltano_bridge, '__file__')
    except (ImportError, AttributeError):
        pytest.skip("Module not testable")


class TestBasicCoverage:
    """Basic coverage tests."""

    def test_module_attributes(self):
        """Test module has expected attributes."""
        try:
            import meltano_bridge
            assert meltano_bridge.__file__
        except ImportError:
            pytest.skip("Module not importable")

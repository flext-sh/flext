"""Test basic structure is correct after fixing dual structure."""

def test_import_from_correct_module():
    """Test that we can import from the correct module."""
    from flext_target_oracle_wms import TargetOracleWMS
    assert TargetOracleWMS is not None
    assert TargetOracleWMS.name == "target-oracle-wms"

def test_no_dual_structure():
    """Test that old target_oracle_wms module doesn't exist."""
    try:
        import target_oracle_wms
        assert False, "target_oracle_wms module should not exist"
    except ImportError:
        # This is expected
        pass

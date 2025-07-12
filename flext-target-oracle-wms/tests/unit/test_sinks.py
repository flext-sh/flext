"""Unit tests for OracleWMSSink."""

from unittest.mock import Mock

import pytest
import sqlalchemy as sa

from flext_target_oracle_wms.sinks import OracleWMSSink
from flext_target_oracle_wms.target import TargetOracleWMS


class TestOracleWMSSink:
    """Test cases for OracleWMSSink."""

    @pytest.fixture
    def mock_target(self):
        """Create a mock target for testing."""
        target = Mock(spec=TargetOracleWMS)
        target.config = {
            "schema": "WMS",
            "add_record_metadata": True,
            "batch_size": 1000,
        }
        return target

    @pytest.fixture
    def sample_schema(self):
        """Sample Singer schema for testing."""
        return {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string", "maxLength": 100},
                "created_at": {"type": "string", "format": "date-time"},
                "is_active": {"type": "boolean"},
                "metadata": {"type": "object"},
            },
        }

    def test_sink_initialization(self, mock_target, sample_schema) -> None:
        """Test sink can be initialized."""
        sink = OracleWMSSink(
            target=mock_target,
            stream_name="test-stream",
            schema=sample_schema,
            key_properties=["id"],
        )

        assert sink.stream_name == "test-stream"
        assert sink._target == mock_target
        assert sink.schema == sample_schema

    def test_conform_name(self, mock_target) -> None:
        """Test name conforming to Oracle conventions."""
        sink = OracleWMSSink(
            target=mock_target,
            stream_name="test_stream",
            schema={},
        )

        # Test basic name conversion
        assert sink.conform_name("test-name") == "TEST_NAME"
        assert sink.conform_name("user.profile") == "USER_PROFILE"

        # Test long name truncation (Oracle 30-char limit)
        long_name = "very_long_table_name_that_exceeds_thirty_characters"
        conformed = sink.conform_name(long_name)
        assert len(conformed) <= 30
        assert conformed == "VERY_LONG_TABLE_NAME_THAT_EXCE"

    def test_table_name_property(self, mock_target) -> None:
        """Test table name generation."""
        sink = OracleWMSSink(
            target=mock_target,
            stream_name="my-test-stream",
            schema={},
        )

        assert sink.table_name == "MY_TEST_STREAM"

    def test_schema_name_property(self, mock_target) -> None:
        """Test schema name from config."""
        sink = OracleWMSSink(
            target=mock_target,
            stream_name="test_stream",
            schema={},
        )

        assert sink.schema_name == "WMS"

    def test_get_column_type_string(self, mock_target) -> None:
        """Test column type mapping for strings."""
        sink = OracleWMSSink(
            target=mock_target,
            stream_name="test_stream",
            schema={},
        )

        # Test basic string
        string_type = sink.get_column_type({"type": "string"})
        assert isinstance(string_type, sa.VARCHAR)
        assert string_type.length == 4000

        # Test string with maxLength
        string_with_length = sink.get_column_type({
            "type": "string",
            "maxLength": 255,
        })
        assert isinstance(string_with_length, sa.VARCHAR)
        assert string_with_length.length == 255

        # Test date-time format
        datetime_type = sink.get_column_type({
            "type": "string",
            "format": "date-time",
        })
        assert isinstance(datetime_type, sa.sql.sqltypes.TIMESTAMP)

    def test_get_column_type_other_types(self, mock_target) -> None:
        """Test column type mapping for other types."""
        sink = OracleWMSSink(
            target=mock_target,
            stream_name="test_stream",
            schema={},
        )

        # Test integer
        int_type = sink.get_column_type({"type": "integer"})
        assert isinstance(int_type, sa.INTEGER)

        # Test number
        num_type = sink.get_column_type({"type": "number"})
        assert isinstance(num_type, sa.NUMERIC)

        # Test boolean
        bool_type = sink.get_column_type({"type": "boolean"})
        assert isinstance(bool_type, sa.CHAR)
        assert bool_type.length == 1

        # Test array/object (stored as CLOB)
        array_type = sink.get_column_type({"type": "array"})
        assert isinstance(array_type, sa.CLOB)

        object_type = sink.get_column_type({"type": "object"})
        assert isinstance(object_type, sa.CLOB)

    def test_get_column_type_nullable(self, mock_target) -> None:
        """Test column type mapping for nullable types."""
        sink = OracleWMSSink(
            target=mock_target,
            stream_name="test_stream",
            schema={},
        )

        # Test nullable string
        nullable_type = sink.get_column_type({"type": ["null", "string"]})
        assert isinstance(nullable_type, sa.VARCHAR)

        # Test nullable integer
        nullable_int = sink.get_column_type({"type": ["null", "integer"]})
        assert isinstance(nullable_int, sa.INTEGER)

    def test_prepare_record(self, mock_target) -> None:
        """Test record preparation for Oracle insertion."""
        sink = OracleWMSSink(
            target=mock_target,
            stream_name="test_stream",
            schema={},
        )

        input_record = {
            "id": 123,
            "name": "Test User",
            "is-active": True,
            "metadata": {"key": "value"},
            "tags": ["tag1", "tag2"],
            "inactive": False,
            "null_field": None,
        }

        prepared = sink._prepare_record(input_record)

        # Test basic field mapping
        assert prepared["ID"] == 123
        assert prepared["NAME"] == "Test User"
        assert prepared["IS_ACTIVE"] == "Y"  # Boolean to Y/N
        assert prepared["INACTIVE"] == "N"   # Boolean to Y/N
        assert prepared["NULL_FIELD"] is None

        # Test complex types become JSON strings
        import json
        assert prepared["METADATA"] == json.dumps({"key": "value"}, ensure_ascii=False)
        assert prepared["TAGS"] == json.dumps(["tag1", "tag2"], ensure_ascii=False)

        # Test metadata fields are added
        assert "_SDC_EXTRACTED_AT" in prepared
        assert "_SDC_RECEIVED_AT" in prepared
        assert "_SDC_BATCHED_AT" in prepared

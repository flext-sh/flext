"""Comprehensive tests for FlextLdifWriter with real data.

Tests all writer functionality including format options, error handling,
and edge cases using real LDIF data fixtures.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from flext_core import FlextResult
from flext_ldif import FlextLdif, FlextLdifModels
from flext_ldif.constants import FlextLdifConstants
from flext_ldif.services.writer import FlextLdifWriter


class TestFlextLdifWriterComprehensive:
    """Comprehensive tests for FlextLdifWriter service."""

    def test_writer_initialization_default(
        self, flext_ldif_instance: FlextLdif
    ) -> None:
        """Test writer initialization with default config."""
        writer = FlextLdifWriter()
        assert writer is not None
        assert hasattr(writer, "write")

    def test_writer_initialization_with_config(
        self, flext_ldif_instance: FlextLdif
    ) -> None:
        """Test writer initialization with custom config."""
        from flext_ldif.config import FlextLdifConfig

        config = FlextLdifConfig()
        writer = FlextLdifWriter(config=config)
        assert writer is not None

    def test_writer_to_ldif_string_empty_entries(
        self, flext_ldif_instance: FlextLdif
    ) -> None:
        """Test writing empty entry list."""
        writer = FlextLdifWriter()
        serializer = writer.LdifSerializer(
            registry=writer._registry, parent_logger=writer.logger
        )

        format_options = FlextLdifModels.WriteFormatOptions(
            include_version_header=True,
            include_timestamps=False,
        )

        result = serializer.to_ldif_string(
            entries=[],
            target_server_type=FlextLdifConstants.ServerTypes.OPENLDAP,
            format_options=format_options,
        )

        assert result.is_success, f"Failed to write empty entries: {result.error}"
        content = result.unwrap()
        assert "version: 1" in content, "Should include version header"

    def test_writer_post_processor_sort_attributes(
        self, parsed_user_entry: FlextLdifModels.Entry
    ) -> None:
        """Test post-processor sort_attributes functionality."""
        writer = FlextLdifWriter()
        post_processor = writer.LdifPostProcessor()

        # Create LDIF content with unsorted attributes
        ldif_content = """dn: cn=test,dc=example,dc=com
mail: test@example.com
objectClass: inetOrgPerson
cn: test
sn: Test
"""

        format_options = FlextLdifModels.WriteFormatOptions(
            sort_attributes=True,
            include_version_header=False,
            include_timestamps=False,
        )

        result = post_processor.apply_format_options(ldif_content, format_options)

        # Verify attributes are sorted alphabetically
        lines = result.split("\n")
        dn_line_idx = next(
            (i for i, line in enumerate(lines) if line.startswith("dn:")), -1
        )
        assert dn_line_idx >= 0, "DN line should exist"

        # Find attribute lines after DN (excluding continuation lines)
        attr_lines = []
        for line in lines[dn_line_idx + 1 :]:
            if not line.strip():
                break
            if line.startswith(" "):
                # Continuation line - append to last attribute
                if attr_lines:
                    attr_lines[-1] += "\n" + line
            elif ":" in line:
                attr_lines.append(line)

        # Verify alphabetical order: cn, mail, objectClass, sn
        attr_names = [line.split(":")[0].strip() for line in attr_lines]
        sorted_attr_names = sorted(attr_names, key=str.lower)
        assert attr_names == sorted_attr_names, (
            f"Attributes should be sorted: got {attr_names}, expected {sorted_attr_names}"
        )

    def test_writer_post_processor_remove_empty_values(
        self, parsed_user_entry: FlextLdifModels.Entry
    ) -> None:
        """Test post-processor remove_empty_values functionality."""
        writer = FlextLdifWriter()
        post_processor = writer.LdifPostProcessor()

        # Create LDIF content with empty values
        ldif_content = """dn: cn=test,dc=example,dc=com
cn: test
description:
mail: test@example.com
emptyAttr:
"""

        format_options = FlextLdifModels.WriteFormatOptions(
            write_empty_values=False,
            include_version_header=False,
            include_timestamps=False,
        )

        result = post_processor.apply_format_options(ldif_content, format_options)

        # Verify empty values are removed
        assert (
            "description: " not in result
            or "description:"
            not in result.split("\n")[
                result.split("\n").index("dn: cn=test,dc=example,dc=com") + 1 :
            ]
        ), "Empty description should be removed"
        assert (
            "emptyAttr: " not in result
            or "emptyAttr:"
            not in result.split("\n")[
                result.split("\n").index("dn: cn=test,dc=example,dc=com") + 1 :
            ]
        ), "Empty attr should be removed"

        # Verify non-empty values remain
        assert "cn: test" in result, "Non-empty cn should remain"
        assert "mail: test@example.com" in result, "Non-empty mail should remain"

    def test_writer_post_processor_fold_long_lines(
        self, parsed_user_entry: FlextLdifModels.Entry
    ) -> None:
        """Test post-processor fold_long_lines functionality."""
        writer = FlextLdifWriter()
        post_processor = writer.LdifPostProcessor()

        # Create LDIF content with long line
        long_value = "A" * 100
        ldif_content = f"""dn: cn=test,dc=example,dc=com
cn: test
description: {long_value}
"""

        format_options = FlextLdifModels.WriteFormatOptions(
            line_width=76,
            fold_long_lines=True,
            include_version_header=False,
            include_timestamps=False,
        )

        result = post_processor.apply_format_options(ldif_content, format_options)

        # Verify long line is folded
        lines = result.split("\n")
        description_line_idx = next(
            (i for i, line in enumerate(lines) if line.startswith("description:")), -1
        )
        if (
            description_line_idx >= 0
            and description_line_idx + 1 < len(lines)
            and lines[description_line_idx + 1].strip()
        ):
            # Check if next line is continuation (starts with space)
            next_line = lines[description_line_idx + 1]
            assert next_line.startswith(" "), (
                "Long description line should be folded with continuation"
            )

    def test_writer_serializer_write_headers(
        self, flext_ldif_instance: FlextLdif
    ) -> None:
        """Test serializer _write_headers method."""
        from io import StringIO

        writer = FlextLdifWriter()
        serializer = writer.LdifSerializer(
            registry=writer._registry, parent_logger=writer.logger
        )

        output = StringIO()
        format_options = FlextLdifModels.WriteFormatOptions(
            include_version_header=True,
            include_timestamps=True,
        )

        serializer._write_headers(output, format_options, entry_count=5)

        content = output.getvalue()
        assert "version: 1" in content, "Version header should be included"
        assert "# Generated on:" in content, "Timestamp should be included"
        assert "# Total entries: 5" in content, "Entry count should be included"

    def test_writer_serializer_get_entry_quirk(
        self, flext_ldif_instance: FlextLdif
    ) -> None:
        """Test serializer _get_entry_quirk method."""
        writer = FlextLdifWriter()
        serializer = writer.LdifSerializer(
            registry=writer._registry, parent_logger=writer.logger
        )

        result = serializer._get_entry_quirk(FlextLdifConstants.ServerTypes.OPENLDAP)
        assert result.is_success, f"Failed to get entry quirk: {result.error}"
        quirk = result.unwrap()
        assert quirk is not None, "Quirk should not be None"

    def test_writer_serializer_get_entry_quirk_invalid_server(
        self, flext_ldif_instance: FlextLdif
    ) -> None:
        """Test serializer _get_entry_quirk with invalid server type."""
        writer = FlextLdifWriter()
        serializer = writer.LdifSerializer(
            registry=writer._registry, parent_logger=writer.logger
        )

        result = serializer._get_entry_quirk("invalid_server_type")
        assert result.is_failure, "Should fail for invalid server type"
        assert result.error is not None, "Error message should be provided"

    def test_writer_write_all_entries_success(
        self,
        parsed_multiple_entries: Sequence[FlextLdifModels.Entry],
        flext_ldif_instance: FlextLdif,
    ) -> None:
        """Test _write_all_entries with multiple entries."""
        from io import StringIO

        writer = FlextLdifWriter()
        serializer = writer.LdifSerializer(
            registry=writer._registry, parent_logger=writer.logger
        )

        output = StringIO()
        quirk_result = serializer._get_entry_quirk(
            FlextLdifConstants.ServerTypes.OPENLDAP
        )
        assert quirk_result.is_success, f"Failed to get quirk: {quirk_result.error}"
        entry_quirk = quirk_result.unwrap()

        format_options = FlextLdifModels.WriteFormatOptions()

        result = serializer._write_all_entries(
            output,
            list(parsed_multiple_entries),
            entry_quirk,
            format_options,
        )

        assert result.is_success, f"Failed to write entries: {result.error}"
        content = output.getvalue()
        assert len(parsed_multiple_entries) > 0, "Should have entries"
        # Verify all DNs are in output
        for entry in parsed_multiple_entries:
            assert f"dn: {entry.dn.value}" in content, (
                f"DN {entry.dn.value} should be in output"
            )

    def test_writer_write_all_entries_basic(
        self,
        parsed_user_entry: FlextLdifModels.Entry,
        flext_ldif_instance: FlextLdif,
    ) -> None:
        """Test _write_all_entries with basic entry."""
        from io import StringIO

        writer = FlextLdifWriter()
        serializer = writer.LdifSerializer(
            registry=writer._registry, parent_logger=writer.logger
        )

        output = StringIO()
        quirk_result = serializer._get_entry_quirk(
            FlextLdifConstants.ServerTypes.OPENLDAP
        )
        assert quirk_result.is_success, f"Failed to get quirk: {quirk_result.error}"
        entry_quirk = quirk_result.unwrap()

        format_options = FlextLdifModels.WriteFormatOptions()

        result = serializer._write_all_entries(
            output,
            [parsed_user_entry],
            entry_quirk,
            format_options,
        )

        assert result.is_success, f"Failed to write entry: {result.error}"
        content = output.getvalue()
        assert "dn: " in content, "DN should be in output"
        assert "cn=John Doe" in content, "User CN should be in output"

    def test_writer_write_file_output(
        self,
        parsed_user_entry: FlextLdifModels.Entry,
        tmp_path: Path,
    ) -> None:
        """Test writer write method with file output."""
        writer = FlextLdifWriter()
        output_file = tmp_path / "test_writer_output.ldif"

        result = writer.write(
            entries=[parsed_user_entry],
            target_server_type=FlextLdifConstants.ServerTypes.OPENLDAP,
            output_target="file",
            output_path=output_file,
        )

        assert result.is_success, f"Failed to write file: {result.error}"
        assert output_file.exists(), "Output file should be created"
        content = output_file.read_text(encoding="utf-8")
        assert "dn: " in content, "File should contain DN"

    def test_writer_write_string_output(
        self, parsed_user_entry: FlextLdifModels.Entry
    ) -> None:
        """Test writer write method with string output."""
        writer = FlextLdifWriter()

        result = writer.write(
            entries=[parsed_user_entry],
            target_server_type=FlextLdifConstants.ServerTypes.OPENLDAP,
            output_target="string",
        )

        assert result.is_success, f"Failed to write string: {result.error}"
        content = result.unwrap()
        assert isinstance(content, str), "Result should be string"
        assert "dn: " in content, "String should contain DN"

    def test_writer_write_with_all_format_options(
        self, parsed_user_entry: FlextLdifModels.Entry
    ) -> None:
        """Test writer with all format options enabled."""
        writer = FlextLdifWriter()

        format_options = FlextLdifModels.WriteFormatOptions(
            include_version_header=True,
            include_timestamps=True,
            sort_attributes=True,
            write_empty_values=False,
            line_width=80,
            fold_long_lines=True,
        )

        result = writer.write(
            entries=[parsed_user_entry],
            target_server_type=FlextLdifConstants.ServerTypes.OPENLDAP,
            output_target="string",
            format_options=format_options,
        )

        assert result.is_success, f"Failed to write: {result.error}"
        content = result.unwrap()

        # Verify all options are applied
        assert "version: 1" in content, "Version header should be included"
        assert "# Generated on:" in content, "Timestamp should be included"

    def test_writer_error_handling_invalid_quirk(
        self, parsed_user_entry: FlextLdifModels.Entry
    ) -> None:
        """Test writer error handling with invalid quirk."""
        writer = FlextLdifWriter()
        serializer = writer.LdifSerializer(
            registry=writer._registry, parent_logger=writer.logger
        )

        format_options = FlextLdifModels.WriteFormatOptions()

        # This should handle gracefully even if quirk lookup fails
        result = serializer.to_ldif_string(
            entries=[parsed_user_entry],
            target_server_type="nonexistent_server",
            format_options=format_options,
        )

        # Should fail gracefully with error message
        assert result.is_failure, "Should fail for nonexistent server"
        assert result.error is not None, "Error message should be provided"

    def test_writer_execute_health_check(self, flext_ldif_instance: FlextLdif) -> None:
        """Test writer execute method (health check)."""
        writer = FlextLdifWriter()

        result = writer.execute()
        assert isinstance(result, FlextResult), "Should return FlextResult"
        assert result.is_success, f"Health check should succeed: {result.error}"

        response = result.unwrap()
        assert hasattr(response, "statistics"), "Response should have statistics"
        assert response.statistics.total_entries == 0, (
            "Health check should have 0 entries"
        )

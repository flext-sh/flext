"""Comprehensive tests for LDIF generation with real data fixtures.

Tests LDIF generation, syntax validation, and transformations using real
data fixtures without mocks or patches. Validates all operations, transformations,
and parameters in detail.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from flext_ldif import FlextLdif, FlextLdifModels
from flext_ldif.constants import FlextLdifConstants


class TestLdifGenerationRealData:
    """Test LDIF generation with real data fixtures."""

    def test_generate_ldif_from_user_entry(
        self,
        flext_ldif_instance: FlextLdif,
        parsed_user_entry: FlextLdifModels.Entry,
        write_format_options_default: FlextLdifModels.WriteFormatOptions,
    ) -> None:
        """Test generating LDIF from real user entry."""
        # Generate LDIF string
        result = flext_ldif_instance.write(
            entries=[parsed_user_entry],
            server_type=FlextLdifConstants.ServerTypes.OPENLDAP,
            format_options=write_format_options_default,
        )

        assert result.is_success, f"Failed to generate LDIF: {result.error}"
        ldif_content = result.unwrap()

        # Validate LDIF syntax
        assert "dn: " in ldif_content, "LDIF must contain DN line"
        assert "cn=John Doe" in ldif_content, "LDIF must contain user CN"
        assert "objectClass: " in ldif_content, "LDIF must contain objectClass"
        assert "mail: john.doe@example.com" in ldif_content, "LDIF must contain email"

        # Validate RFC 2849 compliance
        lines = ldif_content.split("\n")
        for i, line in enumerate(lines):
            if (
                line
                and not line.startswith("#")
                and not line.startswith(" ")
                and len(line.encode("utf-8")) > 76
                and i + 1 < len(lines)
            ):
                # DN and attribute lines should not exceed 76 characters (RFC 2849)
                # Allow for folding continuation lines (starting with space)
                # If line is too long, next line should be continuation
                assert lines[i + 1].startswith(" "), (
                    f"Long line at {i} should be folded: {line[:80]}"
                )

    def test_generate_ldif_with_all_server_types(
        self,
        flext_ldif_instance: FlextLdif,
        parsed_user_entry: FlextLdifModels.Entry,
        write_format_options_default: FlextLdifModels.WriteFormatOptions,
        server_types: list[str],
    ) -> None:
        """Test LDIF generation for all supported server types."""
        for server_type in server_types:
            result = flext_ldif_instance.write(
                entries=[parsed_user_entry],
                server_type=server_type,
                format_options=write_format_options_default,
            )

            assert result.is_success, (
                f"Failed to generate LDIF for {server_type}: {result.error}"
            )
            ldif_content = result.unwrap()

            # All server types should produce valid LDIF
            assert "dn: " in ldif_content, f"{server_type} LDIF must contain DN"
            assert "objectClass: " in ldif_content, (
                f"{server_type} LDIF must contain objectClass"
            )

    def test_generate_ldif_with_custom_format_options(
        self,
        flext_ldif_instance: FlextLdif,
        parsed_user_entry: FlextLdifModels.Entry,
        write_format_options_custom: FlextLdifModels.WriteFormatOptions,
    ) -> None:
        """Test LDIF generation with custom format options."""
        result = flext_ldif_instance.write(
            entries=[parsed_user_entry],
            server_type=FlextLdifConstants.ServerTypes.OPENLDAP,
            format_options=write_format_options_custom,
        )

        assert result.is_success, f"Failed to generate LDIF: {result.error}"
        ldif_content = result.unwrap()

        # Validate custom options
        if write_format_options_custom.include_version_header:
            assert "version: 1" in ldif_content, "Version header should be included"

        if write_format_options_custom.include_timestamps:
            assert "# Generated on:" in ldif_content, "Timestamp should be included"

    def test_generate_ldif_multiple_entries(
        self,
        flext_ldif_instance: FlextLdif,
        parsed_multiple_entries: Sequence[FlextLdifModels.Entry],
        write_format_options_default: FlextLdifModels.WriteFormatOptions,
    ) -> None:
        """Test generating LDIF with multiple entries."""
        result = flext_ldif_instance.write(
            entries=list(parsed_multiple_entries),
            server_type=FlextLdifConstants.ServerTypes.OPENLDAP,
            format_options=write_format_options_default,
        )

        assert result.is_success, f"Failed to generate LDIF: {result.error}"
        ldif_content = result.unwrap()

        # Validate all entries are present
        assert "dn: dc=example,dc=com" in ldif_content
        assert "dn: ou=people,dc=example,dc=com" in ldif_content
        assert "dn: cn=John Doe" in ldif_content
        assert "dn: cn=Jane Smith" in ldif_content

        # Validate entries are separated by blank lines
        entry_blocks = ldif_content.split("\n\n")
        assert len([b for b in entry_blocks if b.strip()]) >= 4, (
            "Should have at least 4 entry blocks"
        )

    def test_generate_ldif_roundtrip(
        self,
        flext_ldif_instance: FlextLdif,
        real_ldif_user_entry: str,
        write_format_options_default: FlextLdifModels.WriteFormatOptions,
    ) -> None:
        """Test roundtrip: parse LDIF, generate LDIF, parse again."""
        # Parse original
        parse_result = flext_ldif_instance.parse(real_ldif_user_entry)
        assert parse_result.is_success, f"Failed to parse: {parse_result.error}"
        original_entries = parse_result.unwrap()

        # Generate LDIF
        write_result = flext_ldif_instance.write(
            entries=original_entries,
            server_type=FlextLdifConstants.ServerTypes.OPENLDAP,
            format_options=write_format_options_default,
        )
        assert write_result.is_success, f"Failed to generate: {write_result.error}"
        generated_ldif = write_result.unwrap()

        # Parse generated LDIF
        parse_result2 = flext_ldif_instance.parse(generated_ldif)
        assert parse_result2.is_success, (
            f"Failed to parse generated LDIF: {parse_result2.error}"
        )
        regenerated_entries = parse_result2.unwrap()

        # Validate entries match
        assert len(regenerated_entries) == len(original_entries), (
            "Entry count should match"
        )
        assert str(regenerated_entries[0].dn) == str(original_entries[0].dn), (
            "DN should match"
        )

    def test_generate_ldif_syntax_validation(
        self,
        flext_ldif_instance: FlextLdif,
        parsed_user_entry: FlextLdifModels.Entry,
        write_format_options_default: FlextLdifModels.WriteFormatOptions,
    ) -> None:
        """Test LDIF syntax validation in generated output."""
        result = flext_ldif_instance.write(
            entries=[parsed_user_entry],
            server_type=FlextLdifConstants.ServerTypes.OPENLDAP,
            format_options=write_format_options_default,
        )

        assert result.is_success, f"Failed to generate LDIF: {result.error}"
        ldif_content = result.unwrap()

        # Validate RFC 2849 syntax rules
        lines = ldif_content.split("\n")

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Skip comments and blank lines
            if not stripped or stripped.startswith("#"):
                continue

            # Check DN line
            if line.startswith("dn:"):
                assert ":" in line, "DN line must have colon"
                dn_value = line.split(":", 1)[1].strip()
                assert dn_value, "DN value must not be empty"
                continue

            # Check attribute line (must come after DN in same entry)
            if ":" in line and not line.startswith(" ") and not line.startswith("dn:"):
                # Attribute lines should come after DN, but we're permissive
                # since version headers and comments may appear before DN
                attr_parts = line.split(":", 1)
                assert len(attr_parts) == 2, f"Invalid attribute line: {line}"
                attr_name = attr_parts[0].strip()
                assert attr_name, f"Attribute name must not be empty: {line}"

            # Check continuation line (folding)
            if line.startswith(" "):
                assert i > 0, "Continuation line must follow another line"
                prev_line = lines[i - 1]
                assert prev_line.strip(), "Continuation line must follow non-blank line"

    def test_generate_ldif_with_special_characters(
        self,
        flext_ldif_instance: FlextLdif,
        real_ldif_entry_with_special_chars: str,
        write_format_options_default: FlextLdifModels.WriteFormatOptions,
    ) -> None:
        """Test LDIF generation with special characters requiring base64 encoding."""
        # Parse entry with special chars
        parse_result = flext_ldif_instance.parse(real_ldif_entry_with_special_chars)
        assert parse_result.is_success, f"Failed to parse: {parse_result.error}"
        entries = parse_result.unwrap()

        # Generate LDIF
        result = flext_ldif_instance.write(
            entries=entries,
            server_type=FlextLdifConstants.ServerTypes.OPENLDAP,
            format_options=write_format_options_default,
        )

        assert result.is_success, f"Failed to generate LDIF: {result.error}"
        ldif_content = result.unwrap()

        # Validate special characters are properly encoded
        assert "dn: " in ldif_content, "LDIF must contain DN"
        # Base64 encoded values use double colon
        if "::" in ldif_content:
            # Validate base64 encoding
            for line in ldif_content.split("\n"):
                if "::" in line:
                    parts = line.split("::", 1)
                    if len(parts) == 2:
                        encoded_value = parts[1].strip()
                        # Basic base64 validation (alphanumeric, +, /, =)
                        assert all(c.isalnum() or c in "+/=" for c in encoded_value), (
                            f"Invalid base64 encoding: {encoded_value}"
                        )

    def test_generate_ldif_with_long_values_folding(
        self,
        flext_ldif_instance: FlextLdif,
        real_ldif_entry_with_long_value: str,
        write_format_options_default: FlextLdifModels.WriteFormatOptions,
    ) -> None:
        """Test LDIF generation with long values requiring RFC 2849 folding."""
        # Parse entry with long value
        parse_result = flext_ldif_instance.parse(real_ldif_entry_with_long_value)
        assert parse_result.is_success, f"Failed to parse: {parse_result.error}"
        entries = parse_result.unwrap()

        # Generate LDIF
        result = flext_ldif_instance.write(
            entries=entries,
            server_type=FlextLdifConstants.ServerTypes.OPENLDAP,
            format_options=write_format_options_default,
        )

        assert result.is_success, f"Failed to generate LDIF: {result.error}"
        ldif_content = result.unwrap()

        # Validate long lines are folded
        lines = ldif_content.split("\n")
        found_long_line = False
        for i, line in enumerate(lines):
            if line and not line.startswith("#") and not line.startswith(" "):
                line_bytes = line.encode("utf-8")
                if len(line_bytes) > write_format_options_default.line_width:
                    found_long_line = True
                    # Next line should be continuation if folding is enabled
                    if write_format_options_default.fold_long_lines and i + 1 < len(
                        lines
                    ):
                        next_line = lines[i + 1]
                        assert next_line.startswith(" "), (
                            f"Long line at {i} should be folded: {line[:80]}"
                        )

        # If we have long values, folding should have occurred
        if found_long_line:
            assert any(line.startswith(" ") for line in lines), (
                "Long lines should be folded"
            )

    def test_generate_ldif_file_output(
        self,
        flext_ldif_instance: FlextLdif,
        parsed_user_entry: FlextLdifModels.Entry,
        write_format_options_default: FlextLdifModels.WriteFormatOptions,
        tmp_path: Path,
    ) -> None:
        """Test generating LDIF to file."""
        output_file = tmp_path / "test_output.ldif"

        result = flext_ldif_instance.write(
            entries=[parsed_user_entry],
            output_path=output_file,
            server_type=FlextLdifConstants.ServerTypes.OPENLDAP,
            format_options=write_format_options_default,
        )

        assert result.is_success, f"Failed to write LDIF file: {result.error}"
        assert output_file.exists(), "Output file should be created"

        # Read and validate file content
        file_content = output_file.read_text(encoding="utf-8")
        assert "dn: " in file_content, "File should contain DN"
        assert "cn=John Doe" in file_content, "File should contain user data"

    def test_generate_ldif_all_format_options_combinations(
        self,
        flext_ldif_instance: FlextLdif,
        parsed_user_entry: FlextLdifModels.Entry,
    ) -> None:
        """Test LDIF generation with all format option combinations."""
        # Test all combinations of boolean options
        for include_version in [True, False]:
            for include_timestamps in [True, False]:
                for sort_attrs in [True, False]:
                    for write_empty in [True, False]:
                        options = FlextLdifModels.WriteFormatOptions(
                            include_version_header=include_version,
                            include_timestamps=include_timestamps,
                            sort_attributes=sort_attrs,
                            write_empty_values=write_empty,
                            line_width=76,
                            fold_long_lines=True,
                        )

                        result = flext_ldif_instance.write(
                            entries=[parsed_user_entry],
                            server_type=FlextLdifConstants.ServerTypes.OPENLDAP,
                            format_options=options,
                        )

                        assert result.is_success, (
                            f"Failed with options {options}: {result.error}"
                        )
                        ldif_content = result.unwrap()

                        # Validate options are applied
                        if include_version:
                            assert "version: 1" in ldif_content, (
                                "Version header should be included"
                            )

                        if include_timestamps:
                            assert "# Generated on:" in ldif_content, (
                                "Timestamp should be included"
                            )

                        # Validate basic LDIF syntax regardless of options
                        assert "dn: " in ldif_content, "LDIF must contain DN"

#!/usr/bin/env python3
"""LDIF Processing Module

Unified LDAP migration and LDIF processing automation module.
Consolidates all LDAP/LDIF processing scripts across the workspace.
"""

import os
import re
import time
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .base import CustomFixModule, Issue


class LDIFProcessingModule(CustomFixModule):
    """Module for unified LDAP migration and LDIF processing automation."""

    name = "ldif_processing"
    description = "Unified LDAP migration and LDIF processing automation"

    # LDAP connection configurations
    LDAP_CONFIGS = {
        "source_ldap": {
            "server_uri": "SOURCE_LDAP_URI",
            "bind_dn": "SOURCE_LDAP_BIND_DN",
            "bind_password": "SOURCE_LDAP_BIND_PASSWORD",
            "base_dn": "SOURCE_LDAP_BASE_DN",
            "search_scope": ("SOURCE_LDAP_SCOPE", "SUBTREE"),
            "timeout": ("SOURCE_LDAP_TIMEOUT", 30),
        },
        "target_ldap": {
            "server_uri": "TARGET_LDAP_URI",
            "bind_dn": "TARGET_LDAP_BIND_DN",
            "bind_password": "TARGET_LDAP_BIND_PASSWORD",
            "base_dn": "TARGET_LDAP_BASE_DN",
            "search_scope": ("TARGET_LDAP_SCOPE", "SUBTREE"),
            "timeout": ("TARGET_LDAP_TIMEOUT", 30),
        },
    }

    # LDIF processing operations
    LDIF_OPERATIONS = {
        "export": {
            "name": "Export LDIF",
            "description": "Export entries from LDAP to LDIF format",
            "requires_connection": True,
        },
        "import": {
            "name": "Import LDIF",
            "description": "Import entries from LDIF to LDAP",
            "requires_connection": True,
        },
        "validate": {
            "name": "Validate LDIF",
            "description": "Validate LDIF file structure and syntax",
            "requires_connection": False,
        },
        "transform": {
            "name": "Transform LDIF",
            "description": "Transform and migrate LDIF entries",
            "requires_connection": False,
        },
        "merge": {
            "name": "Merge LDIF",
            "description": "Merge multiple LDIF files",
            "requires_connection": False,
        },
        "split": {
            "name": "Split LDIF",
            "description": "Split large LDIF files into smaller chunks",
            "requires_connection": False,
        },
    }

    # Common LDAP attribute mappings for migration
    ATTRIBUTE_MAPPINGS = {
        "user_attributes": {
            "cn": "commonName",
            "sn": "surname",
            "givenName": "firstName",
            "mail": "email",
            "telephoneNumber": "phone",
            "employeeID": "userId",
            "department": "organizationalUnit",
            "title": "jobTitle",
            "manager": "managedBy",
        },
        "group_attributes": {
            "cn": "groupName",
            "member": "members",
            "memberOf": "parentGroups",
            "description": "groupDescription",
            "groupType": "type",
        },
        "ou_attributes": {
            "ou": "organizationalUnit",
            "description": "ouDescription",
            "managedBy": "manager",
            "street": "address",
            "l": "city",
            "st": "state",
            "postalCode": "zipCode",
        },
    }

    # LDIF validation patterns
    LDIF_VALIDATION_PATTERNS = {
        "dn_pattern": r"^dn:\s*[^,]+(,[^,]+)*$",
        "changetype_pattern": r"^changetype:\s*(add|modify|delete|moddn)$",
        "attribute_pattern": r"^[a-zA-Z][a-zA-Z0-9-]*:.*$",
        "base64_pattern": r"^[a-zA-Z][a-zA-Z0-9-]*::\s*[A-Za-z0-9+/]+=*$",
        "url_pattern": r"^[a-zA-Z][a-zA-Z0-9-]*:<\s*\S+$",
    }

    # Migration transformation rules
    MIGRATION_RULES = {
        "dn_transformations": [
            # Transform old domain to new domain
            (r"dc=oldcompany,dc=com", "dc=newcompany,dc=com"),
            # Transform organizational units
            (r"ou=Users,", "ou=People,"),
            (r"ou=Groups,", "ou=Roles,"),
        ],
        "attribute_transformations": [
            # Standardize attribute names
            ("employeeNumber", "employeeID"),
            ("telephoneNumber", "phone"),
            ("facsimileTelephoneNumber", "fax"),
        ],
        "value_transformations": [
            # Transform domain references in values
            (r"@oldcompany\.com", "@newcompany.com"),
            # Standardize phone number formats
            (r"\+1-(\d{3})-(\d{3})-(\d{4})", r"+1 (\1) \2-\3"),
        ],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = Console()
        self.ldap_connections: dict[str, Any] = {}
        self.processing_results: dict[str, Any] = {}
        self.validation_errors: list[str] = []

    def load_ldap_config(self, config_type: str) -> dict[str, Any]:
        """Load LDAP configuration from environment variables."""
        if config_type not in self.LDAP_CONFIGS:
            raise ValueError(f"Unknown config type: {config_type}")

        config_template = self.LDAP_CONFIGS[config_type]
        config: dict = {}

        for key, value in config_template.items():
            if isinstance(value, tuple):
                env_var, default = value
                config[key] = os.getenv(env_var, default)
                config[key] = os.getenv(value)

        return config

    def test_ldap_connection(self, config_type: str) -> tuple[bool, str]:
        """Test LDAP server connection."""
        try:
            config = self.load_ldap_config(config_type)

            # Try to import ldap3 library
            try:
                from ldap3 import ALL, Connection, Server
            except ImportError:
                return (
                    False,
                    "ldap3 library not available - please install: pip install ldap3",
                )

            # Create server and connection
            server = Server(config["server_uri"], get_info=ALL)
            conn = Connection(
                server,
                user=config["bind_dn"],
                password=config["bind_password"],
                auto_bind=True,
                timeout=config.get("timeout", 30),
            )

            # Test basic search
            result = conn.search(
                search_base=config["base_dn"],
                search_filter="(objectClass=*)",
                search_scope=config.get("search_scope", "SUBTREE"),
                size_limit=1,
            )

            conn.unbind()

            if result:
                return True, f"LDAP connection successful to {config['server_uri']}"
            return False, "LDAP search failed - no results returned"

        except Exception as e:
            return False, f"LDAP connection failed: {e}"

    def export_ldif(
        self,
        config_type: str,
        output_file: Path,
        search_filter: str = "(objectClass=*)",
        attributes: list[str] | None = None,
    ) -> tuple[bool, dict[str, Any]]:
        """Export LDAP entries to LDIF format."""
        try:
            config = self.load_ldap_config(config_type)

            from ldap3 import ALL, SUBTREE, Connection, Server

            # Create connection
            server = Server(config["server_uri"], get_info=ALL)
            conn = Connection(
                server,
                user=config["bind_dn"],
                password=config["bind_password"],
                auto_bind=True,
            )

            # Perform search
            result = conn.search(
                search_base=config["base_dn"],
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=attributes or ["*"],
            )

            if not result:
                conn.unbind()
                return False, {"error": "No entries found matching search criteria"}

            # Export to LDIF
            entries_exported = 0
            with open(output_file, "w", encoding="utf-8") as f:
                for entry in conn.entries:
                    f.write(entry.entry_to_ldif())
                    f.write("\n")
                    entries_exported += 1

            conn.unbind()

            export_results = {
                "entries_exported": entries_exported,
                "output_file": str(output_file),
                "search_filter": search_filter,
                "base_dn": config["base_dn"],
            }

            return True, export_results

        except Exception as e:
            return False, {"error": str(e)}

    def import_ldif(
        self, config_type: str, input_file: Path, dry_run: bool = True
    ) -> tuple[bool, dict[str, Any]]:
        """Import LDIF entries to LDAP."""
        try:
            config = self.load_ldap_config(config_type)

            from ldap3 import ALL, Connection, Server
            from ldap3.utils.ldif import LDIFParser

            # Parse LDIF file first
            entries: list = []
            with open(input_file, encoding="utf-8") as f:
                parser = LDIFParser(f)
                for dn, entry in parser.parse():
                    if dn:  # Skip empty entries
                        entries.append((dn, entry))

            if not entries:
                return False, {"error": "No valid entries found in LDIF file"}

            if dry_run:
                return True, {
                    "dry_run": True,
                    "entries_parsed": len(entries),
                    "would_import": len(entries),
                }

            # Create connection for import
            server = Server(config["server_uri"], get_info=ALL)
            conn = Connection(
                server,
                user=config["bind_dn"],
                password=config["bind_password"],
                auto_bind=True,
            )

            import_results = {
                "entries_parsed": len(entries),
                "entries_imported": 0,
                "entries_failed": 0,
                "errors": [],
            }

            # Import entries
            for dn, entry in entries:
                try:
                    # Convert entry format for ldap3
                    attributes: dict = {}
                    for attr, values in entry.items():
                        if isinstance(values, list):
                            attributes[attr] = values
                            attributes[attr] = [values]

                    result = conn.add(dn, attributes=attributes)
                    if result:
                        import_results["entries_imported"] += 1
                        import_results["entries_failed"] += 1
                        import_results["errors"].append(
                            {"dn": dn, "error": conn.last_error}
                        )

                except Exception as e:
                    import_results["entries_failed"] += 1
                    import_results["errors"].append({"dn": dn, "error": str(e)})

            conn.unbind()
            return True, import_results

        except Exception as e:
            return False, {"error": str(e)}

    def validate_ldif(self, ldif_file: Path) -> tuple[bool, dict[str, Any]]:
        """Validate LDIF file structure and syntax."""
        validation_results = {
            "file": str(ldif_file),
            "total_entries": 0,
            "valid_entries": 0,
            "invalid_entries": 0,
            "errors": [],
            "warnings": [],
        }

        try:
            with open(ldif_file, encoding="utf-8") as f:
                content = f.read()

            # Split into entries (separated by blank lines)
            entries = re.split(r"\n\s*\n", content.strip())
            validation_results["total_entries"] = len(entries)

            for i, entry in enumerate(entries, 1):
                if not entry.strip():
                    continue

                entry_valid = True
                lines = entry.strip().split("\n")

                # Validate DN line (first line)
                if not lines:
                    validation_results["errors"].append(f"Entry {i}: Empty entry")
                    entry_valid = False
                    continue

                first_line = lines[0].strip()
                if not re.match(
                    self.LDIF_VALIDATION_PATTERNS["dn_pattern"], first_line
                ):
                    validation_results["errors"].append(
                        f"Entry {i}: Invalid DN format: {first_line}"
                    )
                    entry_valid = False

                # Validate attribute lines
                for line_num, line in enumerate(lines[1:], 2):
                    line = line.strip()
                    if not line:
                        continue

                    # Check for changetype
                    if line.startswith("changetype:"):
                        if not re.match(
                            self.LDIF_VALIDATION_PATTERNS["changetype_pattern"], line
                        ):
                            validation_results["errors"].append(
                                f"Entry {i}, line {line_num}: Invalid changetype: {line}"
                            )
                            entry_valid = False
                        continue

                    # Check attribute format
                    if "::" in line:  # Base64 encoded
                        if not re.match(
                            self.LDIF_VALIDATION_PATTERNS["base64_pattern"], line
                        ):
                            validation_results["errors"].append(
                                f"Entry {i}, line {line_num}: Invalid base64 attribute: {line}"
                            )
                            entry_valid = False
                    elif ":<" in line:  # URL reference
                        if not re.match(
                            self.LDIF_VALIDATION_PATTERNS["url_pattern"], line
                        ):
                            validation_results["errors"].append(
                                f"Entry {i}, line {line_num}: Invalid URL attribute: {line}"
                            )
                            entry_valid = False
                    elif ":" in line:  # Regular attribute
                        if not re.match(
                            self.LDIF_VALIDATION_PATTERNS["attribute_pattern"], line
                        ):
                            validation_results["errors"].append(
                                f"Entry {i}, line {line_num}: Invalid attribute format: {line}"
                            )
                            entry_valid = False
                        validation_results["errors"].append(
                            f"Entry {i}, line {line_num}: Invalid line format: {line}"
                        )
                        entry_valid = False

                if entry_valid:
                    validation_results["valid_entries"] += 1
                    validation_results["invalid_entries"] += 1

            # Check for common issues
            if "dc=example,dc=com" in content:
                validation_results["warnings"].append(
                    "Contains example.com domain - may need customization"
                )

            if re.search(r"userPassword:\s*{SSHA}", content):
                validation_results["warnings"].append(
                    "Contains password hashes - verify security requirements"
                )

            success = validation_results["invalid_entries"] == 0
            return success, validation_results

        except Exception as e:
            validation_results["errors"].append(f"File processing error: {e}")
            return False, validation_results

    def transform_ldif(
        self,
        input_file: Path,
        output_file: Path,
        transformation_rules: dict[str, Any] | None = None,
    ) -> tuple[bool, dict[str, Any]]:
        """Transform LDIF entries according to migration rules."""
        try:
            # Use default rules if none provided
            if transformation_rules is None:
                transformation_rules = self.MIGRATION_RULES

            with open(input_file, encoding="utf-8") as f:
                content = f.read()

            original_content = content
            transform_results = {
                "input_file": str(input_file),
                "output_file": str(output_file),
                "transformations_applied": 0,
                "entries_processed": 0,
            }

            # Apply DN transformations
            for old_pattern, new_pattern in transformation_rules.get(
                "dn_transformations", []
            ):
                if re.search(old_pattern, content):
                    content = re.sub(old_pattern, new_pattern, content)
                    transform_results["transformations_applied"] += content.count(
                        new_pattern
                    ) - original_content.count(new_pattern)

            # Apply attribute name transformations
            for old_attr, new_attr in transformation_rules.get(
                "attribute_transformations", []
            ):
                pattern = f"^{old_attr}:"
                replacement = f"{new_attr}:"
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

            # Apply value transformations
            for old_pattern, new_pattern in transformation_rules.get(
                "value_transformations", []
            ):
                content = re.sub(old_pattern, new_pattern, content)

            # Count entries processed
            transform_results["entries_processed"] = len(
                re.findall(r"^dn:", content, re.MULTILINE)
            )

            # Write transformed content
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)

            return True, transform_results

        except Exception as e:
            return False, {"error": str(e)}

    def merge_ldif_files(
        self, input_files: list[Path], output_file: Path, deduplicate: bool = True
    ) -> tuple[bool, dict[str, Any]]:
        """Merge multiple LDIF files into one."""
        try:
            merged_content: list = []
            seen_dns: set = set()
            merge_results = {
                "input_files": [str(f) for f in input_files],
                "output_file": str(output_file),
                "total_entries": 0,
                "unique_entries": 0,
                "duplicates_removed": 0,
            }

            for input_file in input_files:
                with open(input_file, encoding="utf-8") as f:
                    content = f.read()

                # Split into entries
                entries = re.split(r"\n\s*\n", content.strip())

                for entry in entries:
                    if not entry.strip():
                        continue

                    merge_results["total_entries"] += 1

                    # Extract DN for deduplication
                    if deduplicate:
                        dn_match = re.match(r"dn:\s*(.+)", entry.strip())
                        if dn_match:
                            dn = dn_match.group(1).strip()
                            if dn in seen_dns:
                                merge_results["duplicates_removed"] += 1
                                continue
                            seen_dns.add(dn)

                    merged_content.append(entry.strip())
                    merge_results["unique_entries"] += 1

            # Write merged file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n\n".join(merged_content))
                if merged_content:
                    f.write("\n")

            return True, merge_results

        except Exception as e:
            return False, {"error": str(e)}

    def split_ldif_file(
        self, input_file: Path, output_dir: Path, entries_per_file: int = 1000
    ) -> tuple[bool, dict[str, Any]]:
        """Split large LDIF file into smaller chunks."""
        try:
            output_dir.mkdir(parents=True, exist_ok=True)

            with open(input_file, encoding="utf-8") as f:
                content = f.read()

            # Split into entries
            entries = re.split(r"\n\s*\n", content.strip())
            entries = [e.strip() for e in entries if e.strip()]

            split_results = {
                "input_file": str(input_file),
                "output_dir": str(output_dir),
                "total_entries": len(entries),
                "entries_per_file": entries_per_file,
                "files_created": 0,
                "output_files": [],
            }

            # Create split files
            for i in range(0, len(entries), entries_per_file):
                chunk = entries[i : i + entries_per_file]

                file_num = (i // entries_per_file) + 1
                output_file = output_dir / f"{input_file.stem}_part_{file_num:03d}.ldif"

                with open(output_file, "w", encoding="utf-8") as f:
                    f.write("\n\n".join(chunk))
                    if chunk:
                        f.write("\n")

                split_results["files_created"] += 1
                split_results["output_files"].append(str(output_file))

            return True, split_results

        except Exception as e:
            return False, {"error": str(e)}

    def analyze(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze files for LDIF processing opportunities."""
        issues: list = []

        # Check LDIF files
        if file_path.suffix.lower() == ".ldif":
            lines = content.split("\n")

            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()

                # Check for common LDIF issues
                if line_stripped.startswith("dn:"):
                    # Check for example domains
                    if "example.com" in line_stripped:
                        issues.append(
                            Issue(
                                line=i,
                                column=1,
                                code="LDIF001",
                                message="Example domain found in DN",
                                suggestion="Replace example.com with actual domain",
                            )
                        )

                    # Check for spaces in DN
                    if ", " not in line_stripped and "," in line_stripped:
                        issues.append(
                            Issue(
                                line=i,
                                column=1,
                                code="LDIF002",
                                message="DN components not properly spaced",
                                suggestion="Add spaces after commas in DN",
                            )
                        )

                # Check for unencoded special characters
                if ":" in line_stripped and not line_stripped.startswith(
                    ("dn:", "changetype:")
                ):
                    if any(
                        char in line_stripped for char in ['"', "'", "\\", "\n", "\r"]
                    ):
                        issues.append(
                            Issue(
                                line=i,
                                column=1,
                                code="LDIF003",
                                message="Special characters may need base64 encoding",
                                suggestion="Consider base64 encoding for special characters",
                            )
                        )

        # Check Python files for LDAP/LDIF processing
        elif file_path.suffix == ".py":
            lines = content.split("\n")

            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()

                # Check for hardcoded LDAP connections
                if any(
                    pattern in line_stripped
                    for pattern in ["ldap://", "ldaps://", "Connection("]
                ):
                    if "os.getenv" not in line and "config" not in line:
                        issues.append(
                            Issue(
                                line=i,
                                column=1,
                                code="LDAP001",
                                message="Hardcoded LDAP connection found",
                                suggestion="Use environment variables for LDAP connection details",
                            )
                        )

                # Check for LDIF file handling without validation
                if ".ldif" in line_stripped and "open(" in line_stripped:
                    # Look for validation in surrounding lines
                    context_lines = lines[max(0, i - 5) : min(len(lines), i + 5)]
                    if not any(
                        "valid" in ctx_line.lower() for ctx_line in context_lines
                    ):
                        issues.append(
                            Issue(
                                line=i,
                                column=1,
                                code="LDIF004",
                                message="LDIF file processing without validation",
                                suggestion="Add LDIF validation before processing",
                            )
                        )

        return issues

    def apply_fixes(self, content: str, issues: list[Issue]) -> str:
        """Apply LDIF processing fixes to content."""
        lines = content.split("\n")

        for issue in issues:
            if issue.code == "LDIF001":  # Fix example domains
                line_idx = issue.line - 1
                if line_idx < len(lines):
                    line = lines[line_idx]
                    lines[line_idx] = line.replace("example.com", "DOMAIN_TO_REPLACE")

            elif issue.code == "LDIF002":  # Fix DN spacing
                line_idx = issue.line - 1
                if line_idx < len(lines):
                    line = lines[line_idx]
                    # Add spaces after commas in DN
                    lines[line_idx] = re.sub(r",([^,\s])", r", \1", line)

            elif issue.code == "LDAP001":  # Add configuration suggestion
                line_idx = issue.line - 1
                if line_idx < len(lines):
                    line = lines[line_idx]
                    lines[line_idx] = line + "  # TODO: Move to configuration"

        return "\n".join(lines)

    def run_ldif_migration_pipeline(
        self, pipeline_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Run a complete LDIF migration pipeline."""
        pipeline_start = time.time()

        results = {
            "pipeline_name": pipeline_config.get("name", "ldif_migration"),
            "start_time": pipeline_start,
            "steps": [],
            "success": True,
            "total_entries": 0,
            "errors": [],
        }

        try:
            # Step 1: Test LDAP connections
            if pipeline_config.get("test_connections", True):
                if self.verbose:
                    self.console.print("[blue]Testing LDAP connections[/blue]")

                for conn_type in pipeline_config.get(
                    "connection_types", ["source_ldap"]
                ):
                    success, message = self.test_ldap_connection(conn_type)
                    results["steps"].append(
                        {
                            "step": f"test_{conn_type}_connection",
                            "success": success,
                            "message": message,
                        }
                    )
                    if not success:
                        results["success"] = False
                        results["errors"].append(f"Connection test failed: {message}")

            # Step 2: Export LDIF
            if results["success"] and pipeline_config.get("export_ldif", False):
                if self.verbose:
                    self.console.print("[blue]Exporting LDIF from source[/blue]")

                export_config = pipeline_config.get("export_config", {})
                success, export_results = self.export_ldif(
                    config_type="source_ldap",
                    output_file=Path(export_config.get("output_file", "export.ldif")),
                    search_filter=export_config.get("search_filter", "(objectClass=*)"),
                    attributes=export_config.get("attributes"),
                )

                results["steps"].append(
                    {
                        "step": "export_ldif",
                        "success": success,
                        "details": export_results,
                    }
                )

                if success:
                    results["total_entries"] += export_results.get(
                        "entries_exported", 0
                    )
                    results["success"] = False
                    results["errors"].append(
                        f"LDIF export failed: {export_results.get('error')}"
                    )

            # Step 3: Validate LDIF
            if results["success"] and pipeline_config.get("validate_ldif", True):
                if self.verbose:
                    self.console.print("[blue]Validating LDIF files[/blue]")

                for ldif_file in pipeline_config.get("ldif_files", []):
                    success, validation_results = self.validate_ldif(Path(ldif_file))
                    results["steps"].append(
                        {
                            "step": f"validate_{Path(ldif_file).name}",
                            "success": success,
                            "details": validation_results,
                        }
                    )

                    if not success:
                        results["success"] = False
                        results["errors"].extend(validation_results.get("errors", []))

            # Step 4: Transform LDIF
            if results["success"] and pipeline_config.get("transform_ldif", False):
                if self.verbose:
                    self.console.print("[blue]Transforming LDIF files[/blue]")

                transform_config = pipeline_config.get("transform_config", {})
                success, transform_results = self.transform_ldif(
                    input_file=Path(transform_config.get("input_file", "input.ldif")),
                    output_file=Path(
                        transform_config.get("output_file", "transformed.ldif")
                    ),
                    transformation_rules=transform_config.get("rules"),
                )

                results["steps"].append(
                    {
                        "step": "transform_ldif",
                        "success": success,
                        "details": transform_results,
                    }
                )

                if not success:
                    results["success"] = False
                    results["errors"].append(
                        f"LDIF transformation failed: {transform_results.get('error')}"
                    )

            # Step 5: Import LDIF
            if results["success"] and pipeline_config.get("import_ldif", False):
                if self.verbose:
                    self.console.print("[blue]Importing LDIF to target[/blue]")

                import_config = pipeline_config.get("import_config", {})
                success, import_results = self.import_ldif(
                    config_type="target_ldap",
                    input_file=Path(
                        import_config.get("input_file", "transformed.ldif")
                    ),
                    dry_run=import_config.get("dry_run", True),
                )

                results["steps"].append(
                    {
                        "step": "import_ldif",
                        "success": success,
                        "details": import_results,
                    }
                )

                if not success:
                    results["success"] = False
                    results["errors"].append(
                        f"LDIF import failed: {import_results.get('error')}"
                    )

        except Exception as e:
            results["success"] = False
            results["errors"].append(f"Pipeline execution failed: {e}")

        results["end_time"] = time.time()
        results["duration"] = results["end_time"] - results["start_time"]

        return results

    def run_workspace_ldif_processing(
        self, workspace_path: Path = None
    ) -> dict[str, Any]:
        """Run LDIF processing workflow across the workspace."""
        if workspace_path is None:
            workspace_path = Path.cwd()

        if self.verbose:
            self.console.print(
                f"[blue]Running LDIF processing workflow in: {workspace_path}[/blue]"
            )

        # Find LDAP/LDIF related projects
        ldap_projects: list = []
        for project_dir in workspace_path.iterdir():
            if project_dir.is_dir() and not project_dir.name.startswith("."):
                if any(
                    ldap_keyword in project_dir.name.lower()
                    for ldap_keyword in ["ldap", "oud", "ldif"]
                ):
                    ldap_projects.append(project_dir)

        # Find LDIF files
        ldif_files = list(workspace_path.rglob("*.ldif"))

        if self.verbose:
            self.console.print(
                f"[green]Found {len(ldap_projects)} LDAP projects and {
                    len(ldif_files)
                } LDIF files[/green]"
            )

        workflow_results = {
            "total_projects": len(ldap_projects),
            "total_ldif_files": len(ldif_files),
            "successful_processing": 0,
            "failed_processing": 0,
            "project_results": {},
            "ldif_validation_results": {},
        }

        # Process LDAP projects
        for project_path in ldap_projects:
            project_name = project_path.name

            if self.verbose:
                self.console.print(
                    f"[yellow]Processing LDAP project: {project_name}[/yellow]"
                )

            try:
                # Create basic pipeline config for project
                pipeline_config = {
                    "name": project_name,
                    "test_connections": True,
                    "validate_ldif": True,
                    "ldif_files": [str(f) for f in project_path.glob("*.ldif")],
                }

                if not self.dry_run:
                    pipeline_results = self.run_ldif_migration_pipeline(pipeline_config)

                    if pipeline_results["success"]:
                        workflow_results["successful_processing"] += 1
                        workflow_results["failed_processing"] += 1

                    workflow_results["project_results"][project_name] = pipeline_results
                    if self.verbose:
                        self.console.print(
                            f"[cyan][DRY RUN] Would process LDIF for {project_name}[/cyan]"
                        )
                    workflow_results["successful_processing"] += 1

            except Exception as e:
                workflow_results["project_results"][project_name] = {
                    "success": False,
                    "error": str(e),
                }
                workflow_results["failed_processing"] += 1

        # Validate LDIF files
        for ldif_file in ldif_files:
            if self.verbose:
                self.console.print(
                    f"[yellow]Validating LDIF file: {ldif_file.name}[/yellow]"
                )

            try:
                success, validation_results = self.validate_ldif(ldif_file)
                workflow_results["ldif_validation_results"][str(ldif_file)] = {
                    "success": success,
                    "details": validation_results,
                }

            except Exception as e:
                workflow_results["ldif_validation_results"][str(ldif_file)] = {
                    "success": False,
                    "error": str(e),
                }

        # Show summary
        if self.verbose:
            self._show_ldif_summary(workflow_results)

        return workflow_results

    def _show_ldif_summary(self, results: dict[str, Any]) -> None:
        """Show LDIF processing summary."""
        # Results table
        table = Table(title="LDIF Processing Results")
        table.add_column("Item", style="cyan")
        table.add_column("Type", style="blue")
        table.add_column("Status", style="green")
        table.add_column("Details")

        # Add project results
        for project_name, result in results["project_results"].items():
            if isinstance(result, dict) and "success" in result:
                status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
                details = f"{len(result.get('steps', []))} steps"
                status = "❌ ERROR"
                details = "Processing failed"

            table.add_row(project_name, "Project", status, details)

        # Add LDIF validation results
        for ldif_file, result in results["ldif_validation_results"].items():
            file_name = Path(ldif_file).name
            if isinstance(result, dict) and "success" in result:
                status = "✅ VALID" if result["success"] else "❌ INVALID"
                details = result.get("details", {})
                if isinstance(details, dict):
                    entry_info = f"{details.get('valid_entries', 0)}/{
                        details.get('total_entries', 0)
                    } entries"
                    entry_info = "N/A"
                status = "❌ ERROR"
                entry_info = "Validation failed"

            table.add_row(file_name, "LDIF File", status, entry_info)

        self.console.print(table)

        # Summary panel
        total_items = results["total_projects"] + results["total_ldif_files"]
        success_rate = (
            (
                (
                    results["successful_processing"]
                    + sum(
                        1
                        for r in results["ldif_validation_results"].values()
                        if isinstance(r, dict) and r.get("success", False)
                    )
                )
                / total_items
                * 100
            )
            if total_items > 0
            else 0
        )

        panel_text = (
            f"📁 LDAP Projects: {results['total_projects']}\n"
            f"📄 LDIF Files: {results['total_ldif_files']}\n"
            f"✅ Successful Processing: {results['successful_processing']}\n"
            f"❌ Failed Processing: {results['failed_processing']}\n"
            f"📊 Success Rate: {success_rate:.1f}%"
        )

        panel_style = (
            "green"
            if success_rate == 100
            else "yellow"
            if success_rate >= 80
            else "red"
        )
        self.console.print(
            Panel(panel_text, title="LDIF Processing Summary", border_style=panel_style)
        )

    def run_workspace_ldif_workflow(self, workspace_path: Path = None) -> bool:
        """Run LDIF processing workflow across the entire workspace."""
        results = self.run_workspace_ldif_processing(workspace_path)
        return results["failed_processing"] == 0

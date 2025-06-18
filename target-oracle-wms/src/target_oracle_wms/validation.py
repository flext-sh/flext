"""Data validation for Oracle WMS target."""

import logging
import re
from datetime import datetime
from typing import Any

from jsonschema import Draft7Validator

logger = logging.getLogger(__name__)


class WMSDataValidator:
    """Validate data according to WMS requirements and schema."""

    def __init__(self, schema: dict[str, Any]) -> None:
        """Initialize validator.

        Args:
        ----
            schema: JSON schema for validation

        """
        self.schema = schema
        self._validator = Draft7Validator(schema)

        # WMS specific validations
        self.wms_field_constraints = {
            "company_code": {"max_length": 25, "pattern": r"^[A-Z0-9_]+$"},
            "facility_code": {"max_length": 30, "pattern": r"^[A-Z0-9_]+$"},
            "item_code": {"max_length": 50, "pattern": r"^[A-Z0-9_\-\.]+$"},
            "location_barcode": {"max_length": 30, "pattern": r"^[A-Z0-9]+$"},
            "order_nbr": {"max_length": 50},
            "batch_nbr": {"max_length": 50},
            "serial_nbr": {"max_length": 50},
            "lpn": {"max_length": 30, "pattern": r"^[A-Z0-9]+$"},
        }

        # Date/time formats
        self.datetime_fields = [
            "create_ts",
            "mod_ts",
            "last_upd_ts",
            "ship_date",
            "receipt_date",
            "expiry_date",
            "manufactured_date",
        ]

        # Numeric precision requirements
        self.decimal_fields = {
            "quantity": {"precision": 15, "scale": 4},
            "weight": {"precision": 15, "scale": 4},
            "volume": {"precision": 15, "scale": 4},
            "price": {"precision": 15, "scale": 2},
            "cost": {"precision": 15, "scale": 2},
        }

    def validate_record(self, record: dict[str, Any]) -> list[str]:
        """Validate a single record.

        Args:
        ----
            record: Record to validate

        Returns:
        -------
            List of validation errors (empty if valid)

        """
        errors = []

        # JSON schema validation
        schema_errors = self._validate_schema(record)
        errors.extend(schema_errors)

        # WMS specific validations
        wms_errors = self._validate_wms_constraints(record)
        errors.extend(wms_errors)

        # Data type validations
        type_errors = self._validate_data_types(record)
        errors.extend(type_errors)

        # Business logic validations
        logic_errors = self._validate_business_logic(record)
        errors.extend(logic_errors)

        return errors

    def _validate_schema(self, record: dict[str, Any]) -> list[str]:
        """Validate against JSON schema."""
        errors = []

        for error in self._validator.iter_errors(record):
            error_path = ".".join(str(p) for p in error.path)
            errors.append(f"Schema validation error at {error_path}: {error.message}")

        return errors

    def _validate_wms_constraints(self, record: dict[str, Any]) -> list[str]:
        """Validate WMS-specific field constraints."""
        errors = []

        for field, constraints in self.wms_field_constraints.items():
            if field not in record:
                continue

            value = record[field]
            if value is None:
                continue

            # Check max length
            if "max_length" in constraints:
                if len(str(value)) > constraints["max_length"]:
                    errors.append(
                        f"{field} exceeds max length of {constraints['max_length']}"
                    )

            # Check pattern
            if "pattern" in constraints:
                if not re.match(constraints["pattern"], str(value)):
                    errors.append(
                        f"{field} does not match required pattern: {constraints['pattern']}"
                    )

        return errors

    def _validate_data_types(self, record: dict[str, Any]) -> list[str]:
        """Validate data type requirements."""
        errors = []

        # Validate date/time fields
        for field in self.datetime_fields:
            if field in record and record[field] is not None:
                if not self._is_valid_datetime(record[field]):
                    errors.append(f"{field} must be a valid ISO 8601 datetime string")

        # Validate decimal precision
        for field, constraints in self.decimal_fields.items():
            if field in record and record[field] is not None:
                if not self._is_valid_decimal(
                    record[field], constraints["precision"], constraints["scale"]
                ):
                    errors.append(
                        f"{field} must be a decimal with max {constraints['precision']} "
                        f"digits and {constraints['scale']} decimal places"
                    )

        return errors

    def _validate_business_logic(self, record: dict[str, Any]) -> list[str]:
        """Validate business logic rules."""
        errors = []

        # Quantity validations
        if "quantity" in record and record["quantity"] is not None:
            if float(record["quantity"]) < 0:
                errors.append("Quantity cannot be negative")

        # Date validations
        if "expiry_date" in record and "manufactured_date" in record:
            if record["expiry_date"] and record["manufactured_date"]:
                try:
                    expiry = datetime.fromisoformat(
                        record["expiry_date"].replace("Z", "+00:00")
                    )
                    manufactured = datetime.fromisoformat(
                        record["manufactured_date"].replace("Z", "+00:00")
                    )
                    if expiry <= manufactured:
                        errors.append("Expiry date must be after manufactured date")
                except Exception:
                    pass  # Already validated format above

        # Status validations
        if "status" in record:
            valid_statuses = self._get_valid_statuses(record)
            if valid_statuses and record["status"] not in valid_statuses:
                errors.append(
                    f"Invalid status '{record['status']}'. "
                    f"Valid values: {', '.join(valid_statuses)}"
                )

        return errors

    def _is_valid_datetime(self, value: Any) -> bool:
        """Check if value is a valid datetime string."""
        if not isinstance(value, str):
            return False

        # Try common ISO 8601 formats
        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ]

        for fmt in formats:
            try:
                datetime.strptime(value, fmt)
                return True
            except ValueError:
                continue

        # Try ISO format parsing
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return True
        except Exception:
            return False

    def _is_valid_decimal(self, value: Any, precision: int, scale: int) -> bool:
        """Check if value meets decimal precision requirements."""
        try:
            # Convert to string to check precision
            str_value = str(float(value))

            # Remove negative sign for counting
            if str_value.startswith("-"):
                str_value = str_value[1:]

            # Split by decimal point
            parts = str_value.split(".")

            # Check total digits
            total_digits = len(parts[0]) + (len(parts[1]) if len(parts) > 1 else 0)
            if total_digits > precision:
                return False

            # Check decimal places
            return not (len(parts) > 1 and len(parts[1]) > scale)

        except (ValueError, TypeError):
            return False

    def _get_valid_statuses(self, record: dict[str, Any]) -> list[str]:
        """Get valid status values based on record type."""
        # This would be customized based on entity type
        # For now, return common WMS statuses
        if "order" in self.schema.get("title", "").lower():
            return ["CREATED", "ALLOCATED", "PICKED", "PACKED", "SHIPPED", "CANCELLED"]
        if "inventory" in self.schema.get("title", "").lower():
            return ["AVAILABLE", "ALLOCATED", "DAMAGED", "HOLD", "QUARANTINE"]
        if "task" in self.schema.get("title", "").lower():
            return ["PENDING", "ASSIGNED", "IN_PROGRESS", "COMPLETED", "CANCELLED"]
        return []

    def sanitize_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Sanitize record data for WMS compatibility.

        Args:
        ----
            record: Record to sanitize

        Returns:
        -------
            Sanitized record

        """
        sanitized = record.copy()

        # Convert datetime fields to ISO format
        for field in self.datetime_fields:
            if sanitized.get(field):
                sanitized[field] = self._format_datetime(sanitized[field])

        # Ensure decimal values are properly formatted
        for field in self.decimal_fields:
            if field in sanitized and sanitized[field] is not None:
                # WMS requires decimals as strings to preserve precision
                sanitized[field] = str(sanitized[field])

        # Upper case certain fields
        uppercase_fields = ["company_code", "facility_code", "item_code", "lpn"]
        for field in uppercase_fields:
            if field in sanitized and isinstance(sanitized[field], str):
                sanitized[field] = sanitized[field].upper()

        # Remove null values if not allowed
        if not self.schema.get("additionalProperties", True):
            sanitized = {k: v for k, v in sanitized.items() if v is not None}

        return sanitized

    def _format_datetime(self, value: Any) -> str:
        """Format datetime value to ISO 8601."""
        if isinstance(value, str):
            # Already a string, try to parse and reformat
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-3] + "Z"
            except Exception:
                return value
        elif isinstance(value, datetime):
            return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-3] + "Z"
        else:
            return str(value)

    def validate_batch(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        """Validate a batch of records.

        Args:
        ----
            records: List of records to validate

        Returns:
        -------
            Validation report

        """
        report = {
            "total_records": len(records),
            "valid_records": 0,
            "invalid_records": 0,
            "errors_by_record": {},
            "error_summary": {},
        }

        for i, record in enumerate(records):
            errors = self.validate_record(record)

            if errors:
                report["invalid_records"] += 1
                report["errors_by_record"][i] = errors

                # Summarize errors
                for error in errors:
                    error_type = error.split(":")[0]
                    report["error_summary"][error_type] = (
                        report["error_summary"].get(error_type, 0) + 1
                    )
            else:
                report["valid_records"] += 1

        return report

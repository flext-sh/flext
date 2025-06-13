"""OIC Data Transformation.

This module provides functionality for transforming data in OIC integrations.
"""

import json
import logging
from datetime import datetime
from typing import Any

import pandas as pd
from jinja2 import Template

logger = logging.getLogger(__name__)


class OICTransformer:
    """Transformer for OIC data."""

    def __init__(
        self,
        transform_config: dict | None = None,
        config_file: str | None = None,
    ) -> None:
        """Initialize OIC transformer.

        Args:
            transform_config: Transform configuration dictionary
            config_file: Path to transform configuration file

        """
        if transform_config:
            self.config = transform_config
        elif config_file:
            with open(config_file, encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            self.config = {}

        self.transforms = {
            "map_fields": self._map_fields,
            "rename_fields": self._rename_fields,
            "filter_fields": self._filter_fields,
            "add_fields": self._add_fields,
            "format_date": self._format_date,
            "convert_type": self._convert_type,
            "apply_template": self._apply_template,
            "split_field": self._split_field,
            "join_fields": self._join_fields,
            "apply_formula": self._apply_formula,
            "filter_rows": self._filter_rows,
            "sort_data": self._sort_data,
            "group_by": self._group_by,
            "pivot": self._pivot,
            "unpivot": self._unpivot,
            "flatten_json": self._flatten_json,
            "extract_json": self._extract_json,
        }

    def transform(self, data: dict | list[dict]) -> dict | list[dict]:
        """Apply transformation to data based on configuration.

        Args:
            data: Input data

        Returns:
            Transformed data

        """
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])

        # Apply each transform in the config
        for transform in self.config.get("transforms", []):
            transform_type = transform.get("type")
            if transform_type not in self.transforms:
                logger.warning(f"Unknown transform type: {transform_type}")
                continue

            logger.info(f"Applying transform: {transform_type}")
            df = self.transforms[transform_type](df, **transform.get("params", {}))

        # Convert back to original format
        result = df.to_dict(orient="records")
        if isinstance(data, dict):
            return result[0] if result else {}
        return result

    def _map_fields(self, df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
        """Map fields using a field mapping.

        Args:
            df: Input DataFrame
            mapping: Field mapping dictionary

        Returns:
            Transformed DataFrame

        """
        result = pd.DataFrame()

        for target, source in mapping.items():
            if source in df.columns:
                result[target] = df[source]
            else:
                result[target] = None

        return result

    def _rename_fields(self, df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
        """Rename fields.

        Args:
            df: Input DataFrame
            mapping: Field renaming dictionary

        Returns:
            Transformed DataFrame

        """
        return df.rename(columns=mapping)

    def _filter_fields(
        self,
        df: pd.DataFrame,
        fields: list[str],
        exclude: bool = False,
    ) -> pd.DataFrame:
        """Filter fields.

        Args:
            df: Input DataFrame
            fields: list of fields to keep/exclude
            exclude: Whether to exclude (True) or include (False) the specified fields

        Returns:
            Transformed DataFrame

        """
        if exclude:
            return df.drop(columns=[f for f in fields if f in df.columns])
        return df[[f for f in fields if f in df.columns]]

    def _add_fields(self, df: pd.DataFrame, fields: dict[str, Any]) -> pd.DataFrame:
        """Add constant fields.

        Args:
            df: Input DataFrame
            fields: Field name to value mapping

        Returns:
            Transformed DataFrame

        """
        result = df.copy()

        for field_name, value in fields.items():
            result[field_name] = value

        return result

    def _format_date(
        self,
        df: pd.DataFrame,
        field: str,
        input_format: str,
        output_format: str,
    ) -> pd.DataFrame:
        """Format date field.

        Args:
            df: Input DataFrame
            field: Field to format
            input_format: Input date format
            output_format: Output date format

        Returns:
            Transformed DataFrame

        """
        if field not in df.columns:
            return df

        result = df.copy()

        try:
            if input_format:
                result[field] = pd.to_datetime(result[field], format=input_format)
            else:
                result[field] = pd.to_datetime(result[field])

            result[field] = result[field].dt.strftime(output_format)
        except Exception as e:
            logger.exception(f"Error formatting date field {field}: {e!s}")

        return result

    def _convert_type(
        self,
        df: pd.DataFrame,
        field: str,
        target_type: str,
    ) -> pd.DataFrame:
        """Convert field type.

        Args:
            df: Input DataFrame
            field: Field to convert
            target_type: Target data type

        Returns:
            Transformed DataFrame

        """
        if field not in df.columns:
            return df

        result = df.copy()

        try:
            if target_type == "int":
                result[field] = result[field].astype(int)
            elif target_type == "float":
                result[field] = result[field].astype(float)
            elif target_type == "string":
                result[field] = result[field].astype(str)
            elif target_type == "bool":
                result[field] = result[field].astype(bool)
            elif target_type == "datetime":
                result[field] = pd.to_datetime(result[field])
        except Exception as e:
            logger.exception(
                f"Error converting type of field {field} to {target_type}: {e!s}",
            )

        return result

    def _apply_template(
        self,
        df: pd.DataFrame,
        template: str,
        output_field: str,
        input_fields: list[str] | None = None,
    ) -> pd.DataFrame:
        """Apply a Jinja2 template.

        Args:
            df: Input DataFrame
            template: Jinja2 template string
            output_field: Output field name
            input_fields: list of input fields to use in template

        Returns:
            Transformed DataFrame

        """
        result = df.copy()

        template_obj = Template(template)

        def apply_row(row):
            try:
                # Create context from row data
                context = row.to_dict()
                # Apply template
                return template_obj.render(**context)
            except Exception as e:
                logger.exception(f"Error applying template: {e!s}")
                return None

        result[output_field] = result.apply(apply_row, axis=1)
        return result

    def _split_field(
        self,
        df: pd.DataFrame,
        field: str,
        delimiter: str,
        output_fields: list[str],
    ) -> pd.DataFrame:
        """Split a field into multiple fields.

        Args:
            df: Input DataFrame
            field: Field to split
            delimiter: Delimiter to split on
            output_fields: Names of output fields

        Returns:
            Transformed DataFrame

        """
        if field not in df.columns:
            return df

        result = df.copy()

        # Define split function
        def split_value(value):
            if pd.isna(value):
                return [None] * len(output_fields)

            parts = str(value).split(delimiter)
            # Pad with None if not enough parts
            return parts + [None] * (len(output_fields) - len(parts))

        # Apply split function to each row
        split_data = result[field].apply(split_value)

        # Create output fields
        for i, output_field in enumerate(output_fields):
            result[output_field] = split_data.apply(
                lambda x: x[i] if i < len(x) else None,
            )

        return result

    def _join_fields(
        self,
        df: pd.DataFrame,
        fields: list[str],
        delimiter: str,
        output_field: str,
    ) -> pd.DataFrame:
        """Join multiple fields into one.

        Args:
            df: Input DataFrame
            fields: Fields to join
            delimiter: Delimiter to join with
            output_field: Output field name

        Returns:
            Transformed DataFrame

        """
        result = df.copy()

        # Filter valid fields
        valid_fields = [f for f in fields if f in df.columns]

        if not valid_fields:
            result[output_field] = None
            return result

        # Join fields
        result[output_field] = (
            result[valid_fields].astype(str).agg(delimiter.join, axis=1)
        )

        return result

    def _apply_formula(
        self,
        df: pd.DataFrame,
        formula: str,
        output_field: str,
    ) -> pd.DataFrame:
        """Apply a formula to create a new field.

        Args:
            df: Input DataFrame
            formula: Formula to apply (Python expression)
            output_field: Output field name

        Returns:
            Transformed DataFrame

        """
        result = df.copy()

        try:
            # Create a safe environment for formula evaluation
            def safe_eval(row, formula):
                # Create context from row data
                variables = row.to_dict()
                # Add common modules
                variables["pd"] = pd
                variables["datetime"] = datetime
                # Evaluate formula
                return eval(formula, {"__builtins__": {}}, variables)

            result[output_field] = result.apply(
                lambda row: safe_eval(row, formula),
                axis=1,
            )
        except Exception as e:
            logger.exception(f"Error applying formula: {e!s}")
            result[output_field] = None

        return result

    def _filter_rows(self, df: pd.DataFrame, condition: str) -> pd.DataFrame:
        """Filter rows based on a condition.

        Args:
            df: Input DataFrame
            condition: Filter condition (Python expression)

        Returns:
            Filtered DataFrame

        """
        try:
            # Create a safe environment for condition evaluation
            def safe_eval(row, condition):
                # Create context from row data
                variables = row.to_dict()
                # Add common modules
                variables["pd"] = pd
                variables["datetime"] = datetime
                # Evaluate condition
                return eval(condition, {"__builtins__": {}}, variables)

            mask = df.apply(lambda row: safe_eval(row, condition), axis=1)
            return df[mask]
        except Exception as e:
            logger.exception(f"Error filtering rows: {e!s}")
            return df

    def _sort_data(
        self,
        df: pd.DataFrame,
        by: list[str],
        ascending: bool | list[bool] = True,
    ) -> pd.DataFrame:
        """Sort data.

        Args:
            df: Input DataFrame
            by: Fields to sort by
            ascending: Whether to sort in ascending order

        Returns:
            Sorted DataFrame

        """
        # Filter valid fields
        valid_fields = [f for f in by if f in df.columns]

        if not valid_fields:
            return df

        return df.sort_values(by=valid_fields, ascending=ascending)

    def _group_by(
        self,
        df: pd.DataFrame,
        by: list[str],
        aggregations: dict[str, str],
    ) -> pd.DataFrame:
        """Group data and aggregate.

        Args:
            df: Input DataFrame
            by: Fields to group by
            aggregations: Field to aggregation function mapping

        Returns:
            Grouped DataFrame

        """
        # Filter valid fields
        valid_by = [f for f in by if f in df.columns]
        valid_aggs = {f: agg for f, agg in aggregations.items() if f in df.columns}

        if not valid_by or not valid_aggs:
            return df

        return df.groupby(valid_by).agg(valid_aggs).reset_index()

    def _pivot(
        self,
        df: pd.DataFrame,
        index: list[str],
        columns: str,
        values: str,
        aggfunc: str = "first",
    ) -> pd.DataFrame:
        """Pivot data.

        Args:
            df: Input DataFrame
            index: Fields to use as index
            columns: Field to use as columns
            values: Field to use as values
            aggfunc: Aggregation function

        Returns:
            Pivoted DataFrame

        """
        # Check valid fields
        if columns not in df.columns or values not in df.columns:
            return df

        valid_index = [f for f in index if f in df.columns]

        if not valid_index:
            return df

        try:
            pivot_table = df.pivot_table(
                index=valid_index,
                columns=columns,
                values=values,
                aggfunc=aggfunc,
            )
            # Reset index to convert back to flat DataFrame
            return pivot_table.reset_index()
        except Exception as e:
            logger.exception(f"Error pivoting data: {e!s}")
            return df

    def _unpivot(
        self,
        df: pd.DataFrame,
        id_vars: list[str],
        value_vars: list[str],
        var_name: str,
        value_name: str,
    ) -> pd.DataFrame:
        """Unpivot (melt) data.

        Args:
            df: Input DataFrame
            id_vars: Identifier variables
            value_vars: Value variables
            var_name: Name of variable column
            value_name: Name of value column

        Returns:
            Unpivoted DataFrame

        """
        valid_id_vars = [f for f in id_vars if f in df.columns]
        valid_value_vars = [f for f in value_vars if f in df.columns]

        if not valid_id_vars or not valid_value_vars:
            return df

        return pd.melt(
            df,
            id_vars=valid_id_vars,
            value_vars=valid_value_vars,
            var_name=var_name,
            value_name=value_name,
        )

    def _flatten_json(
        self,
        df: pd.DataFrame,
        field: str,
        prefix: str = "",
    ) -> pd.DataFrame:
        """Flatten a JSON field.

        Args:
            df: Input DataFrame
            field: JSON field to flatten
            prefix: Prefix for flattened fields

        Returns:
            DataFrame with flattened JSON field

        """
        if field not in df.columns:
            return df

        result = df.copy()

        # Define flatten function
        def flatten_json_field(value):
            if pd.isna(value):
                return {}

            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except Exception:
                    return {}

            if not isinstance(value, dict):
                return {}

            # Flatten dictionary
            flat_dict = {}
            for key, val in value.items():
                flat_key = f"{prefix}{key}" if prefix else key
                flat_dict[flat_key] = val

            return flat_dict

        # Apply flatten function to each row
        flattened = result[field].apply(flatten_json_field)

        # Convert flattened dictionaries to DataFrame
        flattened_df = pd.DataFrame(flattened.tolist())

        # Join with original DataFrame
        if not flattened_df.empty:
            result = pd.concat([result, flattened_df], axis=1)

        return result

    def _extract_json(
        self,
        df: pd.DataFrame,
        field: str,
        json_path: str,
        output_field: str,
    ) -> pd.DataFrame:
        """Extract a value from a JSON field using JSON path.

        Args:
            df: Input DataFrame
            field: JSON field to extract from
            json_path: JSON path to extract
            output_field: Output field name

        Returns:
            DataFrame with extracted value

        """
        if field not in df.columns:
            return df

        result = df.copy()

        # Define extract function
        def extract_json_value(value, path):
            if pd.isna(value):
                return None

            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except Exception:
                    return None

            if not isinstance(value, dict):
                return None

            # Split path
            path_parts = path.split(".")

            # Traverse path
            current = value
            for part in path_parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None

            return current

        # Apply extract function to each row
        result[output_field] = result[field].apply(
            lambda x: extract_json_value(x, json_path),
        )

        return result

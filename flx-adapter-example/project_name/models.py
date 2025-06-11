"""
Data models for API client.

This module defines base classes for data models used by the API client,
including validation, serialization, and deserialization.
"""

from typing import Any, TypeVar

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, create_model


# Type variable for BaseModel subclasses
T = TypeVar("T", bound="BaseModel")


class BaseModel(PydanticBaseModel):
    """
    Base class for data models.

    Extends Pydantic's BaseModel with additional functionality for API client
    models, such as case-insensitive field access and custom serialization.
    """

    def get(self, field_name: str, default: Any = None) -> Any:
        """
        Get field value with case-insensitive field name.

        Args:
            field_name: Field name (case-insensitive)
            default: Default value to return if field is not found

        Returns:
            Any: Field value or default
        """
        # Try exact match first
        if field_name in self.model_fields:
            return getattr(self, field_name, default)

        # Try case-insensitive match
        field_name_lower = field_name.lower()
        for f in self.model_fields:
            if f.lower() == field_name_lower:
                return getattr(self, f, default)

        return default

    def to_dict(
        self,
        include: set[str] | None = None,
        exclude: set[str] | None = None,
    ) -> dict[str, Any]:
        """
        Convert model to dictionary with optional field filtering.

        Args:
            include: Set of field names to include (optional)
            exclude: Set of field names to exclude (optional)

        Returns:
            dict[str, Any]: Dictionary representation of the model
        """
        # Convert to dict using pydantic's model_dump
        return self.model_dump(
            include=include,
            exclude=exclude,
        )

    def format(self, template: str) -> str:
        """
        Format model data using a template string.

        Args:
            template: Format template with field names in curly braces

        Returns:
            str: Formatted string

        Example:
            >>> model.format("Name: {name}, Age: {age}")
            "Name: John, Age: 30"
        """
        return template.format(**self.to_dict())

    @classmethod
    def create_dynamic_model(
        cls,
        model_name: str,
        fields: dict[str, Any],
    ) -> type["BaseModel"]:
        """
        Create a dynamic model class with the given fields.

        Args:
            model_name: Name for the dynamic model class
            fields: Dictionary mapping field names to types and validators

        Returns:
            Type[BaseModel]: Dynamically created model class
        """
        return create_model(
            model_name,
            __base__=cls,
            **fields,
        )


class FlxResponse(BaseModel):
    """
    API response model.

    This model represents responses from API calls, including success status,
    data, and error information.
    """

    success: bool = Field(
        True,
        description="Whether the API call was successful",
    )
    data: Any = Field(
        None,
        description="Response data (when successful)",
    )
    error: str | None = Field(
        None,
        description="Error message (when not successful)",
    )
    error_code: str | None = Field(
        None,
        description="Error code (when not successful)",
    )
    error_details: dict[str, Any] | None = Field(
        None,
        description="Additional error details (when not successful)",
    )
    status_code: int | None = Field(
        None,
        description="HTTP status code of the response",
    )

    @classmethod
    def success_response(
        cls,
        data: Any,
        status_code: int | None = None,
    ) -> "FlxResponse":
        """
        Create a successful API response.

        Args:
            data: Response data
            status_code: HTTP status code (optional)

        Returns:
            FlxResponse: Successful response object
        """
        return cls(success=True, data=data, status_code=status_code)

    @classmethod
    def error_response(
        cls,
        error: str,
        error_code: str | None = None,
        error_details: dict[str, Any] | None = None,
        status_code: int | None = None,
    ) -> "FlxResponse":
        """
        Create an error API response.

        Args:
            error: Error message
            error_code: Error code (optional)
            error_details: Additional error details (optional)
            status_code: HTTP status code (optional)

        Returns:
            FlxResponse: Error response object
        """
        return cls(
            success=False,
            error=error,
            error_code=error_code,
            error_details=error_details,
            status_code=status_code,
        )

    def __bool__(self) -> bool:
        """Return boolean representation of the response (success status)."""
        return self.success

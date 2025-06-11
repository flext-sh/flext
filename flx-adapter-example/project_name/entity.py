"""
Entity operations for API client.

This module provides a high-level interface for working with API entities,
including dynamic entity discovery, CRUD operations, and data transformation.
"""

import builtins
from typing import Any, TypeVar

from .client import ApiClient
from .exceptions import ValidationError
from .models import BaseModel, FlxResponse


# Type variable for entity models
T = TypeVar("T", bound=BaseModel)


class Entity:
    """
    Class for working with API entities.

    This class provides methods for entity CRUD operations and specialized
    queries, with support for automatic type conversion.
    """

    def __init__(
        self,
        client: ApiClient,
        entity_name: str,
        model_class: type | None = None,
    ):
        """
        Initialize Entity instance.

        Args:
            client: API client instance
            entity_name: Name of the entity in the API
            model_class: Optional model class for data validation and conversion
        """
        self.client = client
        self.entity_name = entity_name
        self.model_class = model_class
        self.base_path = f"api/{entity_name}"

    def list_entities(
        self,
        filters: dict[str, Any] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
        limit: int | None = None,
        offset: int | None = None,
        fields: list[str] | None = None,
    ) -> FlxResponse:
        """
        list entity resources with optional filtering and pagination.

        Args:
            filters: Optional dictionary of filter conditions
            sort_by: Optional field to sort by
            sort_order: Sort direction ('asc' or 'desc')
            limit: Maximum number of results to return
            offset: Starting position for pagination
            fields: Specific fields to include in the response

        Returns:
            FlxResponse: API response containing list of entities
        """
        params = {}

        # Add filters if provided
        if filters:
            for key, value in filters.items():
                params[f"filter[{key}]"] = value

        # Add sorting if provided
        if sort_by:
            params["sort"] = f"{'-' if sort_order.lower() == 'desc' else ''}{sort_by}"

        # Add pagination if provided
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        # Add field selection if provided
        if fields:
            params["fields"] = ",".join(fields)

        # Make request
        response = self.client.get(self.base_path, params=params)

        # Convert data to models if model_class is provided
        if response.success and self.model_class and isinstance(response.data, list):
            try:
                response.data = [
                    self.model_class.model_validate(item) for item in response.data
                ]
            except Exception as e:
                raise ValidationError(f"Failed to validate response data: {e!s}")

        return response

    def get_entity(
        self,
        resource_id: str | int,
        fields: builtins.list[str] | None = None,
    ) -> FlxResponse:
        """
        Get a single entity resource by ID.

        Args:
            resource_id: ID of the resource to retrieve
            fields: Specific fields to include in the response

        Returns:
            FlxResponse: API response containing the entity
        """
        params = {}

        # Add field selection if provided
        if fields:
            params["fields"] = ",".join(fields)

        # Make request
        response = self.client.get(f"{self.base_path}/{resource_id}", params=params)

        # Convert data to model if model_class is provided
        if response.success and self.model_class and response.data:
            try:
                response.data = self.model_class.model_validate(response.data)
            except Exception as e:
                raise ValidationError(f"Failed to validate response data: {e!s}")

        return response

    def create_entity(self, data: dict[str, Any] | BaseModel) -> FlxResponse:
        """
        Create a new entity resource.

        Args:
            data: Data for the new resource (dict or model instance)

        Returns:
            FlxResponse: API response containing the created entity
        """
        # Convert model to dict if needed
        if isinstance(data, BaseModel):
            data = data.model_dump()

        # Validate data if model_class is provided
        if self.model_class:
            try:
                validated_data = self.model_class.model_validate(data)
                data = validated_data.model_dump()
            except Exception as e:
                raise ValidationError(f"Failed to validate request data: {e!s}")

        # Make request
        response = self.client.post(self.base_path, json_data=data)

        # Convert response data to model if model_class is provided
        if response.success and self.model_class and response.data:
            try:
                response.data = self.model_class.model_validate(response.data)
            except Exception as e:
                raise ValidationError(f"Failed to validate response data: {e!s}")

        return response

    def update_entity(
        self,
        resource_id: str | int,
        data: dict[str, Any] | BaseModel,
    ) -> FlxResponse:
        """
        Update an existing entity resource.

        Args:
            resource_id: ID of the resource to update
            data: Updated data for the resource

        Returns:
            FlxResponse: API response containing the updated entity
        """
        # Convert model to dict if needed
        if isinstance(data, BaseModel):
            data = data.model_dump()

        # Validate data if model_class is provided
        if self.model_class:
            try:
                validated_data = self.model_class.model_validate(data)
                data = validated_data.model_dump()
            except Exception as e:
                raise ValidationError(f"Failed to validate request data: {e!s}")

        # Make request
        response = self.client.put(f"{self.base_path}/{resource_id}", json_data=data)

        # Convert response data to model if model_class is provided
        if response.success and self.model_class and response.data:
            try:
                response.data = self.model_class.model_validate(response.data)
            except Exception as e:
                raise ValidationError(f"Failed to validate response data: {e!s}")

        return response

    def partial_update_entity(
        self,
        resource_id: str | int,
        data: dict[str, Any] | BaseModel,
    ) -> FlxResponse:
        """
        Partially update an existing entity resource.

        Args:
            resource_id: ID of the resource to update
            data: Partial data for the resource

        Returns:
            FlxResponse: API response containing the updated entity
        """
        # Convert model to dict if needed
        if isinstance(data, BaseModel):
            data = data.model_dump()

        # Make request
        response = self.client.patch(f"{self.base_path}/{resource_id}", json_data=data)

        # Convert response data to model if model_class is provided
        if response.success and self.model_class and response.data:
            try:
                response.data = self.model_class.model_validate(response.data)
            except Exception as e:
                raise ValidationError(f"Failed to validate response data: {e!s}")

        return response

    def delete_entity(self, resource_id: str | int) -> FlxResponse:
        """
        Delete an entity resource.

        Args:
            resource_id: ID of the resource to delete

        Returns:
            FlxResponse: API response
        """
        return self.client.delete(f"{self.base_path}/{resource_id}")

    def bulk_create_entities(
        self,
        items: builtins.list[dict[str, Any] | BaseModel],
    ) -> FlxResponse:
        """
        Create multiple entity resources in a single request.

        Args:
            items: list of data items for new resources

        Returns:
            FlxResponse: API response
        """
        # Convert models to dicts if needed
        data = []
        for item in items:
            if isinstance(item, BaseModel):
                item = item.model_dump()
            data.append(item)

        # Make request
        return self.client.post(f"{self.base_path}/bulk", json_data={"items": data})

    def bulk_update_entities(self, items: builtins.list[dict[str, Any]]) -> FlxResponse:
        """
        Update multiple entity resources in a single request.

        Args:
            items: list of data items with IDs for existing resources

        Returns:
            FlxResponse: API response
        """
        # Make request
        return self.client.put(f"{self.base_path}/bulk", json_data={"items": items})

    def bulk_delete_entities(self, ids: builtins.list[str | int]) -> FlxResponse:
        """
        Delete multiple entity resources in a single request.

        Args:
            ids: list of resource IDs to delete

        Returns:
            FlxResponse: API response
        """
        # Make request
        return self.client.delete(f"{self.base_path}/bulk", json_data={"ids": ids})

    def count_entities(self, filters: dict[str, Any] | None = None) -> int:
        """
        Count the number of entity resources matching the filters.

        Args:
            filters: Optional dictionary of filter conditions

        Returns:
            int: Number of matching resources
        """
        params = {"count": "true"}

        # Add filters if provided
        if filters:
            for key, value in filters.items():
                params[f"filter[{key}]"] = value

        # Make request
        response = self.client.get(f"{self.base_path}/count", params=params)

        if response.success and isinstance(response.data, dict):
            return response.data.get("count", 0)
        return 0

    def custom_action_entity(
        self,
        action: str,
        resource_id: str | int | None = None,
        method: str = "POST",
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> FlxResponse:
        """
        Perform a custom action on an entity resource.

        Args:
            action: Name of the custom action
            resource_id: Optional ID of the resource to act on
            method: HTTP method to use (default: POST)
            data: Optional data for the request
            params: Optional query parameters

        Returns:
            FlxResponse: API response
        """
        # Build URL
        if resource_id:
            url = f"{self.base_path}/{resource_id}/{action}"
        else:
            url = f"{self.base_path}/{action}"

        # Make request based on method
        method = method.upper()
        if method == "GET":
            return self.client.get(url, params=params)
        if method == "POST":
            return self.client.post(url, json_data=data, params=params)
        if method == "PUT":
            return self.client.put(url, json_data=data, params=params)
        if method == "PATCH":
            return self.client.patch(url, json_data=data, params=params)
        if method == "DELETE":
            return self.client.delete(url, params=params)
        raise ValueError(f"Unsupported HTTP method: {method}")


class EntityManager:
    """
    Manager for working with multiple entity types.

    This class provides a high-level interface for discovering and working
    with different entity types in the API.
    """

    def __init__(self, client: ApiClient):
        """
        Initialize EntityManager.

        Args:
            client: API client instance
        """
        self.client = client
        self.entities = {}  # Cache of entity instances

    def get_entity(
        self,
        entity_name: str,
        model_class: type | None = None,
    ) -> Entity:
        """
        Get an Entity instance for the specified entity type.

        Args:
            entity_name: Name of the entity in the API
            model_class: Optional model class for data validation and conversion

        Returns:
            Entity: Entity instance
        """
        # Use cached instance if available (and model_class matches)
        if entity_name in self.entities:
            entity = self.entities[entity_name]
            if model_class is None or entity.model_class == model_class:
                return entity

        # Create new entity instance
        entity = Entity(self.client, entity_name, model_class)
        self.entities[entity_name] = entity
        return entity

    def discover_entities(self) -> list[str]:
        """
        Discover available entity types from the API.

        Returns:
            list[str]: list of entity names
        """
        response = self.client.get("api/entities")
        if response.success and isinstance(response.data, list):
            return response.data
        return []

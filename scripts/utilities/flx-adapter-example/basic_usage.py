#!/usr/bin/env python3
"""Basic usage example for the API client.

This example demonstrates the basic usage of the API client, including
configuration, authentication, and making requests.
"""

import sys
from pathlib import Path

# Add flx_project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from flx_adapter_example import (
    ApiClient,
    ApiError,
    ConnectionError,
    EntityManager,
    SchemaManager,
    format_table,
    paginate,
    setup_logger,
)

# Set up logging
logger = setup_logger("example", level="INFO")


def basic_client_example() -> int:
    """Example of basic API client usage."""
    # Set up configuration
    try:
        # Either use environment variables
        client = ApiClient()

        # Or provide configuration directly
        # client = ApiClient(
        #     url="https://api.example.com",
        #     username="your-username",
        #     password="your-password",
        #     timeout=60,
        # )

        # Or use a configuration profile
        # client = ApiClient.from_profile("dev")

    except ApiError:
        return 1

    # Test connection
    try:
        success, _message = client.test_connection()
        if success:
            pass
        else:
            return 1
    except ApiError:
        return 1

    # Make a GET request
    try:
        response = client.get("users")

        if response.success:
            users = response.data

            # Print the first few users
            for _i, _user in enumerate(users[:3]):
                pass

            if len(users) > 3:
                pass
        else:
            return 1
    except ConnectionError:
        return 1
    except ApiError:
        return 1

    # Make a POST request to create a resource
    try:
        new_user = {"name": "John Doe", "email": "john.doe@example.com", "role": "user"}

        response = client.post("users", json_data=new_user)

        if response.success:
            created_user = response.data
        else:
            return 1
    except ApiError:
        return 1

    # Make a PUT request to update a resource
    if response.success:
        user_id = created_user.get("id")

        try:
            update_data = {"role": "REDACTED_LDAP_BIND_PASSWORD"}

            response = client.put(f"users/{user_id}", json_data=update_data)

            if response.success:
                pass
            else:
                return 1
        except ApiError:
            return 1

        # Make a DELETE request to remove a resource

        try:
            response = client.delete(f"users/{user_id}")

            if response.success:
                pass
            else:
                return 1
        except ApiError:
            return 1

    return 0


def entity_example() -> int:
    """Example of using the Entity API."""
    try:
        # Create client
        client = ApiClient()

        # Create entity manager
        manager = EntityManager(client)

        # Discover available entities
        entities = manager.discover_entities()

        if not entities:
            return 1

        # Select an entity to work with (e.g., "users")
        entity_name = "users"
        if entity_name not in entities:
            entity_name = entities[0]

        # Get entity instance
        entity = manager.get_entity(entity_name)

        # list resources
        response = entity.list(limit=5)

        if not response.success:
            return 1

        items = response.data

        # Display results in a table
        if items:
            # Get fields from first item
            fields = list(items[0].keys())[:5]  # First 5 fields

            # Create table
            format_table(
                items,
                fields=fields,
                title=f"{entity_name.title()} (First 5 items)",
            )

            # Get a specific resource
            if items:
                resource_id = items[0].get("id")
                if resource_id:
                    response = entity.get(resource_id)

                    if response.success:
                        pass

        # Pagination example

        # Create paginated iterator
        paginated_items = paginate(client, f"api/{entity_name}", page_size=10)

        # Iterate through first few pages
        item_count = 0
        max_items = 25  # Limit for example

        try:
            for _item in paginated_items:
                item_count += 1
                if item_count <= 3:
                    pass

                if item_count >= max_items:
                    break

        except StopIteration:
            pass

    except Exception:
        return 1

    return 0


def schema_example() -> int:
    """Example of using the Schema API."""
    try:
        # Create client
        client = ApiClient()

        # Create schema manager
        schema_manager = SchemaManager(client)

        # Get entity manager to discover entities
        entity_manager = EntityManager(client)
        entities = entity_manager.discover_entities()

        if not entities:
            return 1

        # Select an entity to work with
        entity_name = "users"
        if entity_name not in entities:
            entity_name = entities[0]

        # Get schema
        schema = schema_manager.get_schema(entity_name)

        if not schema:
            return 1

        # Print schema details

        # Print field details
        for _i, (_field_name, field_schema) in enumerate(
            list(schema.fields.items())[:5]
        ):
            field_type = field_schema.get("type", "string")
            if field_schema.get("format"):
                field_type = f"{field_type} ({field_schema['format']})"
            field_schema.get("description", "N/A")

        if len(schema.fields) > 5:
            pass

        # Generate model from schema
        model_class = schema_manager.get_model(entity_name)

        if not model_class:
            return 1

        # Create an instance of the model (for example purposes)
        try:
            # Create a minimal valid instance with required fields
            required_fields = schema.required_fields
            sample_data = {}

            for field in required_fields:
                field_schema = schema.fields.get(field, {})
                field_type = field_schema.get("type", "string")

                # Provide sample values based on field type
                if field_type == "string":
                    sample_data[field] = f"Sample {field}"
                elif field_type == "integer":
                    sample_data[field] = 1
                elif field_type == "number":
                    sample_data[field] = 1.0
                elif field_type == "boolean":
                    sample_data[field] = True
                elif field_type == "array":
                    sample_data[field] = []
                elif field_type == "object":
                    sample_data[field] = {}

            if sample_data:
                model_class.model_validate(sample_data)

                # Validate model instance
        except Exception:
            pass

    except Exception:
        return 1

    return 0


def main():
    """Run the API client examples."""
    # Run basic client example
    result = basic_client_example()
    if result != 0:
        return result

    # Run entity example
    result = entity_example()
    if result != 0:
        return result

    # Run schema example
    result = schema_example()
    if result != 0:
        return result

    return 0


if __name__ == "__main__":
    sys.exit(main())

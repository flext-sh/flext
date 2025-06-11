#!/usr/bin/env python3
"""
Basic usage example for the API client.

This example demonstrates the basic usage of the API client, including
configuration, authentication, and making requests.
"""

import json
import sys
from pathlib import Path


# Add flx_project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from project_name import (
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


def basic_client_example():
    """Example of basic API client usage."""
    print("\n=== Basic Client Example ===")

    # Set up configuration
    print("Setting up API client...")
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

        print(f"API client initialized for {client.url}")
    except ApiError as e:
        print(f"Error initializing client: {e}")
        return 1

    # Test connection
    print("\nTesting API connection...")
    try:
        success, message = client.test_connection()
        if success:
            print(f"✓ Connection successful: {message}")
        else:
            print(f"✗ Connection failed: {message}")
            return 1
    except ApiError as e:
        print(f"✗ Connection error: {e}")
        return 1

    # Make a GET request
    print("\nFetching users...")
    try:
        response = client.get("users")

        if response.success:
            users = response.data
            print(f"✓ Retrieved {len(users)} users")

            # Print the first few users
            for i, user in enumerate(users[:3]):
                print(
                    f"  - User {i + 1}: {user.get('name', 'Unknown')} ({user.get('email', 'No email')})"
                )

            if len(users) > 3:
                print(f"  - ... and {len(users) - 3} more")
        else:
            print(f"✗ Error fetching users: {response.error}")
            return 1
    except ConnectionError as e:
        print(f"✗ Connection error: {e}")
        return 1
    except ApiError as e:
        print(f"✗ API error: {e}")
        return 1

    # Make a POST request to create a resource
    print("\nCreating a new user...")
    try:
        new_user = {"name": "John Doe", "email": "john.doe@example.com", "role": "user"}

        response = client.post("users", json_data=new_user)

        if response.success:
            created_user = response.data
            print(
                f"✓ Created new user: {created_user.get('name')} (ID: {created_user.get('id')})"
            )
        else:
            print(f"✗ Error creating user: {response.error}")
            return 1
    except ApiError as e:
        print(f"✗ API error: {e}")
        return 1

    # Make a PUT request to update a resource
    if response.success:
        user_id = created_user.get("id")
        print(f"\nUpdating user {user_id}...")

        try:
            update_data = {"role": "admin"}

            response = client.put(f"users/{user_id}", json_data=update_data)

            if response.success:
                updated_user = response.data
                print(
                    f"✓ Updated user: {updated_user.get('name')} (Role: {updated_user.get('role')})"
                )
            else:
                print(f"✗ Error updating user: {response.error}")
                return 1
        except ApiError as e:
            print(f"✗ API error: {e}")
            return 1

        # Make a DELETE request to remove a resource
        print(f"\nDeleting user {user_id}...")

        try:
            response = client.delete(f"users/{user_id}")

            if response.success:
                print(f"✓ Deleted user {user_id}")
            else:
                print(f"✗ Error deleting user: {response.error}")
                return 1
        except ApiError as e:
            print(f"✗ API error: {e}")
            return 1

    print("\nBasic client example completed successfully!")
    return 0


def entity_example():
    """Example of using the Entity API."""
    print("\n=== Entity API Example ===")

    try:
        # Create client
        client = ApiClient()

        # Create entity manager
        manager = EntityManager(client)

        # Discover available entities
        print("\nDiscovering available entities...")
        entities = manager.discover_entities()

        if not entities:
            print("No entities found.")
            return 1

        print(
            f"✓ Found {len(entities)} entities: {', '.join(entities[:5])}"
            + (f" and {len(entities) - 5} more" if len(entities) > 5 else "")
        )

        # Select an entity to work with (e.g., "users")
        entity_name = "users"
        if entity_name not in entities:
            print(
                f"Entity '{entity_name}' not found. Using first available entity instead."
            )
            entity_name = entities[0]

        print(f"\nWorking with entity: {entity_name}")

        # Get entity instance
        entity = manager.get_entity(entity_name)

        # list resources
        print(f"\nListing {entity_name}...")
        response = entity.list(limit=5)

        if not response.success:
            print(f"Error listing {entity_name}: {response.error}")
            return 1

        items = response.data
        print(f"✓ Retrieved {len(items)} {entity_name}")

        # Display results in a table
        if items:
            # Get fields from first item
            fields = list(items[0].keys())[:5]  # First 5 fields

            # Create table
            print("\nResults:")
            format_table(
                items, fields=fields, title=f"{entity_name.title()} (First 5 items)"
            )

            # Get a specific resource
            if items:
                resource_id = items[0].get("id")
                if resource_id:
                    print(f"\nGetting {entity_name} with ID {resource_id}...")
                    response = entity.get(resource_id)

                    if response.success:
                        item = response.data
                        print(f"✓ Retrieved {entity_name} {resource_id}")
                        print(json.dumps(item, indent=2))
                    else:
                        print(
                            f"Error getting {entity_name} {resource_id}: {response.error}"
                        )

        # Pagination example
        print(f"\nPaginating through all {entity_name}...")

        # Create paginated iterator
        paginated_items = paginate(client, f"api/{entity_name}", page_size=10)

        # Iterate through first few pages
        item_count = 0
        max_items = 25  # Limit for example

        try:
            for item in paginated_items:
                item_count += 1
                if item_count <= 3:
                    print(
                        f"  - Item {item_count}: {item.get('name', item.get('id', 'Unknown'))}"
                    )

                if item_count >= max_items:
                    print(f"  - ... stopped after {max_items} items")
                    break

            print(f"✓ Retrieved {item_count} items using pagination")
        except StopIteration:
            print(f"✓ Retrieved all {item_count} items using pagination")

    except Exception as e:
        print(f"Error in entity example: {e!s}")
        return 1

    print("\nEntity example completed successfully!")
    return 0


def schema_example():
    """Example of using the Schema API."""
    print("\n=== Schema API Example ===")

    try:
        # Create client
        client = ApiClient()

        # Create schema manager
        schema_manager = SchemaManager(client)

        # Get entity manager to discover entities
        entity_manager = EntityManager(client)
        entities = entity_manager.discover_entities()

        if not entities:
            print("No entities found.")
            return 1

        # Select an entity to work with
        entity_name = "users"
        if entity_name not in entities:
            print(
                f"Entity '{entity_name}' not found. Using first available entity instead."
            )
            entity_name = entities[0]

        print(f"\nExtracting schema for {entity_name}...")

        # Get schema
        schema = schema_manager.get_schema(entity_name)

        if not schema:
            print(f"Schema not found for {entity_name}.")
            return 1

        print(f"✓ Retrieved schema for {entity_name}")

        # Print schema details
        print(f"\nSchema: {schema.name}")
        print(f"Description: {schema.description or 'N/A'}")
        print(f"Fields: {len(schema.fields)}")
        print(f"Required fields: {len(schema.required_fields)}")

        # Print field details
        print("\nFields:")
        for i, (field_name, field_schema) in enumerate(list(schema.fields.items())[:5]):
            field_type = field_schema.get("type", "string")
            if field_schema.get("format"):
                field_type = f"{field_type} ({field_schema['format']})"
            required = "✓" if field_name in schema.required_fields else "✗"
            description = field_schema.get("description", "N/A")

            print(f"  {i + 1}. {field_name} ({field_type}) - Required: {required}")
            print(f"     Description: {description}")

        if len(schema.fields) > 5:
            print(f"  ... and {len(schema.fields) - 5} more fields")

        # Generate model from schema
        print("\nGenerating model from schema...")
        model_class = schema_manager.get_model(entity_name)

        if not model_class:
            print("Failed to generate model.")
            return 1

        print(f"✓ Generated model class: {model_class.__name__}")
        print(f"Model fields: {', '.join(model_class.model_fields.keys())}")

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
                print("\nCreating sample model instance...")
                instance = model_class.model_validate(sample_data)
                print(f"✓ Created valid model instance: {instance}")

                # Validate model instance
                print("\nModel validation:")
                print(f"  Model fields: {len(instance.model_fields)}")
                print(f"  Required fields: {len(required_fields)}")
                print(f"  Sample data: {json.dumps(sample_data, indent=2)}")
        except Exception as e:
            print(f"Error creating model instance: {e!s}")

    except Exception as e:
        print(f"Error in schema example: {e!s}")
        return 1

    print("\nSchema example completed successfully!")
    return 0


def main():
    """Run the API client examples."""
    print("API Client Examples")
    print("==================")

    # Run basic client example
    result = basic_client_example()
    if result != 0:
        print("Basic client example failed.")
        return result

    # Run entity example
    result = entity_example()
    if result != 0:
        print("Entity example failed.")
        return result

    # Run schema example
    result = schema_example()
    if result != 0:
        print("Schema example failed.")
        return result

    print("\nAll examples completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Command-line interface for API client.

This module provides command-line tools for interacting with the API client,
including configuration management, API operations, and utility commands.
"""

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from .client import ApiClient
from .config import Config, list_available_profiles
from .entity import EntityManager
from .schema import SchemaDefinition, SchemaExtractor, SchemaManager
from .utils.formatting import format_csv, format_json, format_table, format_text
from .utils.logging import setup_logger

# Set up console for rich output
console = Console()
logger = setup_logger("flx_adapter_example.cli")


@click.group()
@click.version_option()
def main() -> None:
    """API Client command-line tools.

    This CLI provides tools for interacting with the API, managing configuration,
    and performing common operations.
    """


@main.group()
def config() -> None:
    """Manage API client configuration."""


@config.command("view")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
def config_view(format: str) -> None:
    """View current configuration."""
    try:
        config = Config()

        if format == "json":
            # Convert to dict and mask password
            config_dict = config.to_dict()
            if "password" in config_dict:
                config_dict["password"] = "********"
            console.print(json.dumps(config_dict, indent=2))
        else:
            table = Table(title="API Client Configuration")
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="green")

            # Add configuration values to table
            config_dict = config.to_dict()
            for key, value in config_dict.items():
                # Mask password
                if key == "password":
                    value = "********"
                table.add_row(key, str(value))

            console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error viewing configuration:[/bold red] {e!s}")
        sys.exit(1)


@config.command("profiles")
def config_profiles() -> None:
    """List available configuration profiles."""
    profiles = list_available_profiles()

    if not profiles:
        console.print("[yellow]No configuration profiles found.[/yellow]")
        console.print("Create profiles by creating .env.{profile_name} files.")
        return

    table = Table(title="Available Configuration Profiles")
    table.add_column("Profile", style="cyan")

    for profile in profiles:
        table.add_row(profile)

    console.print(table)


@config.command("validate")
@click.option("--profile", "-p", help="Configuration profile to validate")
@click.option("--test-connection", "-t", is_flag=True, help="Test API connection")
def config_validate(profile: str | None, test_connection: bool) -> None:
    """Validate configuration and optionally test connection."""
    try:
        if profile:
            config = Config.from_profile(profile)
            console.print(f"[green]Profile '{profile}' configuration is valid.[/green]")
        else:
            config = Config()
            console.print("[green]Current configuration is valid.[/green]")

        if test_connection:
            client = ApiClient(config=config)
            success, message = client.test_connection()

            if success:
                console.print(f"[green]{message}[/green]")
            else:
                console.print(f"[bold red]{message}[/bold red]")
                sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Validation failed:[/bold red] {e!s}")
        sys.exit(1)


@config.command("create")
@click.option("--url", required=True, help="API base URL")
@click.option("--username", required=True, help="API username")
@click.option("--password", required=True, help="API password")
@click.option("--timeout", type=int, default=60, help="Request timeout in seconds")
@click.option(
    "--verify-ssl/--no-verify-ssl",
    default=True,
    help="Verify SSL certificates",
)
@click.option("--output-file", "-o", required=True, help="Output file path")
def config_create(
    url: str,
    username: str,
    password: str,
    timeout: int,
    verify_ssl: bool,
    output_file: str,
) -> None:
    """Create a configuration file."""
    try:
        # Create configuration
        config = Config(
            url=url,
            username=username,
            password=password,
            timeout=timeout,
            verify_ssl=verify_ssl,
        )

        # Save to file
        config.save(output_file)
        console.print(f"[green]Configuration saved to {output_file}[/green]")
    except Exception as e:
        console.print(f"[bold red]Error creating configuration:[/bold red] {e!s}")
        sys.exit(1)


@main.command("ping")
@click.option("--profile", "-p", help="Configuration profile to use")
def ping(profile: str | None) -> None:
    """Test API connection."""
    try:
        # Create client
        client = ApiClient.from_profile(profile) if profile else ApiClient()

        # Test connection
        success, message = client.test_connection()

        if success:
            console.print(f"[green]{message}[/green]")
        else:
            console.print(f"[bold red]{message}[/bold red]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e!s}")
        sys.exit(1)


@main.command("request")
@click.argument("method", type=click.Choice(["GET", "POST", "PUT", "DELETE", "PATCH"]))
@click.argument("endpoint")
@click.option("--profile", "-p", help="Configuration profile to use")
@click.option("--param", "-q", multiple=True, help="Query parameter (name=value)")
@click.option("--header", "-H", multiple=True, help="Header (name=value)")
@click.option("--data", "-d", help="Request body as JSON string or @file.json")
@click.option("--output", "-o", help="Output file for response")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "text"]),
    default="json",
    help="Output format",
)
def request(
    method: str,
    endpoint: str,
    profile: str | None,
    param: list[str],
    header: list[str],
    data: str | None,
    output: str | None,
    format: str,
) -> None:
    """Make a custom API request.

    METHOD: HTTP method (GET, POST, PUT, DELETE, PATCH)
    ENDPOINT: API endpoint path
    """
    try:
        # Create client
        client = ApiClient.from_profile(profile) if profile else ApiClient()

        # Parse parameters
        params = {}
        for p in param:
            if "=" in p:
                key, value = p.split("=", 1)
                params[key] = value
            else:
                console.print(
                    f"[yellow]Warning: Ignoring invalid parameter format: {p}[/yellow]",
                )

        # Parse headers
        headers = {}
        for h in header:
            if "=" in h:
                key, value = h.split("=", 1)
                headers[key] = value
            else:
                console.print(
                    f"[yellow]Warning: Ignoring invalid header format: {h}[/yellow]",
                )

        # Parse data
        json_data = None
        if data:
            if data.startswith("@"):
                # Load from file
                file_path = data[1:]
                with open(file_path, encoding="utf-8") as f:
                    json_data = json.load(f)
            else:
                # Parse as JSON string
                json_data = json.loads(data)

        # Make request
        if method == "GET":
            response = client.get(endpoint, params=params, headers=headers)
        elif method == "POST":
            response = client.post(
                endpoint,
                params=params,
                json_data=json_data,
                headers=headers,
            )
        elif method == "PUT":
            response = client.put(
                endpoint,
                params=params,
                json_data=json_data,
                headers=headers,
            )
        elif method == "DELETE":
            response = client.delete(endpoint, params=params, headers=headers)
        elif method == "PATCH":
            response = client.patch(
                endpoint,
                params=params,
                json_data=json_data,
                headers=headers,
            )

        # Output response
        if response.success:
            if format == "json" and isinstance(response.data, dict | list):
                result = json.dumps(response.data, indent=2)
            else:
                result = str(response.data)

            if output:
                with open(output, "w", encoding="utf-8") as f:
                    f.write(result)
                console.print(f"[green]Response saved to {output}[/green]")
            else:
                console.print(result)
        else:
            console.print(f"[bold red]Error: {response.error}[/bold red]")
            if response.error_details:
                console.print(f"Details: {response.error_details}")
            sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e!s}")
        sys.exit(1)


# Entity commands
@main.group()
def entity() -> None:
    """Work with API entities."""


@entity.command("list")
@click.option("--profile", "-p", help="Configuration profile to use")
@click.option("--with-fields", "-f", is_flag=True, help="Include field information")
@click.option(
    "--output-format",
    "-F",
    type=click.Choice(["table", "json", "csv"]),
    default="table",
    help="Output format",
)
@click.option("--output", "-o", help="Output file path")
def list_entities(
    profile: str | None,
    with_fields: bool,
    output_format: str,
    output: str | None,
) -> None:
    """List available entities from the API."""
    try:
        # Create client
        client = ApiClient.from_profile(profile) if profile else ApiClient()

        # Create entity manager
        manager = EntityManager(client)

        # Discover entities
        entities = manager.discover_entities()

        if not entities:
            console.print("[yellow]No entities found.[/yellow]")
            return

        # Format output based on output_format
        if with_fields:
            # Initialize schema manager
            schema_manager = SchemaManager(client)

            # Collect entity information with fields
            entity_info = []
            for entity_name in entities:
                schema = schema_manager.get_schema(entity_name)
                if schema:
                    fields = list(schema.fields.keys())
                    required_fields = schema.required_fields
                    entity_info.append(
                        {
                            "name": entity_name,
                            "description": schema.description or "",
                            "fields": ", ".join(fields[:5])
                            + (
                                f" and {len(fields) - 5} more"
                                if len(fields) > 5
                                else ""
                            ),
                            "required": ", ".join(required_fields[:3])
                            + (
                                f" and {len(required_fields) - 3} more"
                                if len(required_fields) > 3
                                else ""
                            ),
                            "field_count": len(fields),
                        },
                    )
                else:
                    entity_info.append(
                        {
                            "name": entity_name,
                            "description": "",
                            "fields": "(schema not available)",
                            "required": "",
                            "field_count": 0,
                        },
                    )

            # Format output
            if output_format == "json":
                result = format_json(entity_info, output_file=output)
                if not output:
                    console.print(result)
            elif output_format == "csv":
                result = format_csv(
                    entity_info,
                    fields=["name", "description", "fields", "required", "field_count"],
                    headers={
                        "name": "Entity Name",
                        "description": "Description",
                        "fields": "Fields",
                        "required": "Required Fields",
                        "field_count": "Field Count",
                    },
                    output_file=output,
                )
                if not output:
                    console.print(result)
            else:  # table format
                result = format_table(
                    entity_info,
                    fields=["name", "description", "fields", "required", "field_count"],
                    headers={
                        "name": "Entity Name",
                        "description": "Description",
                        "fields": "Fields",
                        "required": "Required Fields",
                        "field_count": "Field Count",
                    },
                    title="Available Entities",
                    output_file=output,
                )
        else:
            # Simple entity list
            entity_list = [{"name": name} for name in entities]

            # Format output
            if output_format == "json":
                result = format_json(entity_list, output_file=output)
                if not output:
                    console.print(result)
            elif output_format == "csv":
                result = format_csv(
                    entity_list,
                    fields=["name"],
                    headers={"name": "Entity Name"},
                    output_file=output,
                )
                if not output:
                    console.print(result)
            else:  # table format
                result = format_table(
                    entity_list,
                    fields=["name"],
                    headers={"name": "Entity Name"},
                    title="Available Entities",
                    output_file=output,
                )

        if output:
            console.print(f"[green]Output saved to {output}[/green]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e!s}")
        sys.exit(1)


@entity.command("query")
@click.argument("entity_name")
@click.option("--profile", "-p", help="Configuration profile to use")
@click.option("--filter", "-f", multiple=True, help="Filter parameter (name=value)")
@click.option("--output-field", "-o", multiple=True, help="Fields to include in output")
@click.option("--limit", "-l", type=int, help="Maximum number of results")
@click.option("--offset", type=int, help="Starting position for pagination")
@click.option("--sort-by", "-s", help="Field to sort by")
@click.option(
    "--sort-order",
    type=click.Choice(["asc", "desc"]),
    default="asc",
    help="Sort order",
)
@click.option("--format", "-F", help="Format template for output")
@click.option(
    "--output-format",
    type=click.Choice(["json", "table", "csv", "text"]),
    default="table",
    help="Output format",
)
@click.option("--output", "-O", help="Output file path")
def query_entity(
    entity_name: str,
    profile: str | None,
    filter: list[str],
    output_field: list[str],
    limit: int | None,
    offset: int | None,
    sort_by: str | None,
    sort_order: str,
    format: str | None,
    output_format: str,
    output: str | None,
) -> None:
    """Query an entity.

    ENTITY_NAME: Name of the entity to query
    """
    try:
        # Create client
        client = ApiClient.from_profile(profile) if profile else ApiClient()

        # Create entity manager
        manager = EntityManager(client)

        # Get entity
        entity = manager.get_entity(entity_name)

        # Parse filters
        filters = {}
        for f in filter:
            if "=" in f:
                key, value = f.split("=", 1)
                filters[key] = value
            else:
                console.print(
                    f"[yellow]Warning: Ignoring invalid filter format: {f}[/yellow]",
                )

        # Query entity
        response = entity.list(
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
            fields=output_field if output_field else None,
        )

        if not response.success:
            console.print(f"[bold red]Error: {response.error}[/bold red]")
            if response.error_details:
                console.print(f"Details: {response.error_details}")
            sys.exit(1)

        data = response.data

        if not data:
            console.print("[yellow]No results found.[/yellow]")
            return

        # Determine fields to include in output
        fields = list(output_field) if output_field else list(data[0].keys())

        # Format output
        if output_format == "json":
            result = format_json(data, output_file=output)
            if not output:
                console.print(result)
        elif output_format == "csv":
            result = format_csv(data, fields=fields, output_file=output)
            if not output:
                console.print(result)
        elif output_format == "text":
            if not format:
                format = " ".join(f"{{{field}}}" for field in fields)
            result = format_text(data, format, output_file=output)
            if not output:
                console.print(result)
        else:  # table format
            result = format_table(
                data,
                fields=fields,
                title=f"{entity_name.title()} Query Results",
                output_file=output,
            )

        if output:
            console.print(f"[green]Output saved to {output}[/green]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e!s}")
        sys.exit(1)


@entity.command("get")
@click.argument("entity_name")
@click.argument("resource_id")
@click.option("--profile", "-p", help="Configuration profile to use")
@click.option("--output-field", "-o", multiple=True, help="Fields to include in output")
@click.option(
    "--output-format",
    type=click.Choice(["json", "table", "text"]),
    default="json",
    help="Output format",
)
@click.option("--output", "-O", help="Output file path")
def get_entity(
    entity_name: str,
    resource_id: str,
    profile: str | None,
    output_field: list[str],
    output_format: str,
    output: str | None,
) -> None:
    """Get a specific entity resource.

    ENTITY_NAME: Name of the entity
    RESOURCE_ID: ID of the resource to retrieve
    """
    try:
        # Create client
        client = ApiClient.from_profile(profile) if profile else ApiClient()

        # Create entity manager
        manager = EntityManager(client)

        # Get entity
        entity = manager.get_entity(entity_name)

        # Get resource
        response = entity.get(
            resource_id,
            fields=output_field if output_field else None,
        )

        if not response.success:
            console.print(f"[bold red]Error: {response.error}[/bold red]")
            if response.error_details:
                console.print(f"Details: {response.error_details}")
            sys.exit(1)

        data = response.data

        if not data:
            console.print(f"[yellow]Resource not found: {resource_id}[/yellow]")
            return

        # Format output
        if output_format == "json":
            result = format_json(data, output_file=output)
            if not output:
                console.print(result)
        elif output_format == "text":
            # Simple text format
            lines = []
            for key, value in data.items():
                if not output_field or key in output_field:
                    lines.append(f"{key}: {value}")
            result = "\n".join(lines)

            if output:
                with open(output, "w", encoding="utf-8") as f:
                    f.write(result)
            else:
                console.print(result)
        else:  # table format
            # Convert to list for table formatting
            item_list = [data]

            # Determine fields
            fields = list(output_field) if output_field else list(data.keys())

            result = format_table(
                item_list,
                fields=fields,
                title=f"{entity_name.title()} Resource: {resource_id}",
                output_file=output,
            )

        if output:
            console.print(f"[green]Output saved to {output}[/green]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e!s}")
        sys.exit(1)


# Schema commands
@main.group()
def schema() -> None:
    """Work with API schemas."""


@schema.command("extract")
@click.option("--profile", "-p", help="Configuration profile to use")
@click.option("--entity", "-e", multiple=True, help="Entity to extract schema for")
@click.option("--all", "-a", is_flag=True, help="Extract schemas for all entities")
@click.option("--output-dir", "-o", required=True, help="Output directory for schemas")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json"]),
    default="json",
    help="Output format",
)
def extract_schemas(
    profile: str | None,
    entity: list[str],
    all: bool,
    output_dir: str,
    format: str,
) -> None:
    """Extract entity schemas from the API.

    This command extracts entity schemas from the API and saves them to files.
    You can extract schemas for specific entities or for all available entities.
    """
    try:
        # Create client
        client = ApiClient.from_profile(profile) if profile else ApiClient()

        # Create schema extractor
        extractor = SchemaExtractor(client, cache_dir=output_dir)

        # Determine entities to extract
        entities_to_extract = list(entity)
        if all or not entities_to_extract:
            discovered_entities = extractor.discover_entities()
            entities_to_extract = discovered_entities

        if not entities_to_extract:
            console.print("[yellow]No entities to extract.[/yellow]")
            return

        # Extract schemas
        console.print(f"Extracting schemas for {len(entities_to_extract)} entities...")
        results = {}

        for entity_name in entities_to_extract:
            try:
                schema = extractor.extract_schema(entity_name)
                if schema:
                    # Save schema to file
                    file_path = schema.save(output_dir)
                    results[entity_name] = {"success": True, "file": file_path}
                    console.print(
                        f"[green]Extracted schema for {entity_name} to {file_path}[/green]",
                    )
                else:
                    results[entity_name] = {
                        "success": False,
                        "error": "Schema not found",
                    }
                    console.print(
                        f"[yellow]Failed to extract schema for {entity_name}[/yellow]",
                    )
            except Exception as e:
                results[entity_name] = {"success": False, "error": str(e)}
                console.print(
                    f"[red]Error extracting schema for {entity_name}: {e!s}[/red]",
                )

        # Output summary
        success_count = sum(1 for result in results.values() if result["success"])
        console.print(
            f"\n[bold]Schema extraction complete:[/bold] {success_count} of {len(entities_to_extract)} schemas extracted successfully.",
        )
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e!s}")
        sys.exit(1)


@schema.command("view")
@click.argument("entity_name")
@click.option("--schema-dir", "-d", help="Schema directory")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format",
)
def view_schema(
    entity_name: str,
    schema_dir: str | None,
    format: str,
) -> None:
    """View schema for an entity.

    ENTITY_NAME: Name of the entity
    """
    try:
        # Try to load schema from file
        schema_file = None
        if schema_dir:
            schema_file = Path(schema_dir) / f"{entity_name.lower()}.schema.json"
            if not schema_file.exists():
                console.print(f"[yellow]Schema file not found: {schema_file}[/yellow]")
                sys.exit(1)

        if schema_file:
            schema = SchemaDefinition.load(schema_file)
        else:
            console.print("[yellow]Schema directory not specified.[/yellow]")
            sys.exit(1)

        # Output schema
        if format == "json":
            console.print(json.dumps(schema.to_json_schema(), indent=2))
        else:  # table format
            # Create table of fields
            table = Table(title=f"Schema for {entity_name}")
            table.add_column("Field", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Required", style="yellow")
            table.add_column("Description", style="white")

            for field_name, field_schema in schema.fields.items():
                field_type = field_schema.get("type", "string")
                if field_schema.get("format"):
                    field_type = f"{field_type} ({field_schema['format']})"
                required = "✓" if field_name in schema.required_fields else ""
                description = field_schema.get("description", "")

                table.add_row(field_name, field_type, required, description)

            console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e!s}")
        sys.exit(1)


if __name__ == "__main__":
    main()

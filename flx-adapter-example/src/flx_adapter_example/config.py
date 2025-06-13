"""Configuration management for API client.

This module provides classes and functions for managing API client configuration
through environment variables, configuration files, and configuration profiles.
"""

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigProfile:
    """Configuration profile for API client.

    Profiles allow defining multiple configurations for different environments
    (e.g., development, staging, production).
    """

    def __init__(self, name: str, config: dict[str, Any]) -> None:
        """Initialize a configuration profile.

        Args:
            name: Profile name
            config: Configuration dictionary
        """
        self.name = name
        self.config = config

    @property
    def is_valid(self) -> bool:
        """Check if the profile contains the minimum required configuration."""
        return all(key in self.config for key in ["url", "username", "password"])

    def __repr__(self) -> str:
        """Return string representation of the profile."""
        # Hide password in representation
        config_repr = {
            k: "****" if k == "password" else v for k, v in self.config.items()
        }
        return f"ConfigProfile({self.name}, {config_repr})"


class Config(BaseSettings):
    """API client configuration.

    This class provides configuration management for the API client, including
    connection settings, authentication, and client behavior.

    Configuration can be loaded from environment variables, configuration files,
    or provided directly.
    """

    # Connection settings
    url: str = Field(..., description="API base URL")
    timeout: int = Field(60, description="Request timeout in seconds")
    verify_ssl: bool = Field(True, description="Verify SSL certificates")

    # Authentication
    username: str = Field(..., description="API username")
    password: SecretStr = Field(..., description="API password")

    # Client behavior
    max_retries: int = Field(3, description="Maximum number of retry attempts")
    retry_backoff: float = Field(
        0.5,
        description="Exponential backoff factor for retries",
    )
    debug: bool = Field(False, description="Enable debug mode")

    # Optional settings
    environment: str | None = Field(
        None,
        description="Environment name (e.g., development, production)",
    )

    model_config = SettingsConfigDict(
        env_prefix="API_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate and normalize URL."""
        if not v:
            msg = "URL cannot be empty"
            raise ValueError(msg)

        # Remove trailing slash
        v = v.removesuffix("/")

        # Ensure URL starts with http or https
        if not (v.startswith(("http://", "https://"))):
            msg = "URL must start with http:// or https://"
            raise ValueError(msg)

        return v

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        result = self.model_dump()
        # Convert SecretStr to plain string for easier serialization
        if "password" in result and isinstance(result["password"], SecretStr):
            result["password"] = result["password"].get_secret_value()
        return result

    def save(self, file_path: str | Path) -> None:
        """Save configuration to a file.

        Args:
            file_path: Path to save the configuration file
        """
        file_path = Path(file_path)

        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Determine file format based on extension
        if file_path.suffix.lower() == ".json":
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2)
        else:
            msg = f"Unsupported file format: {file_path.suffix}"
            raise ValueError(msg)

    @classmethod
    def from_file(cls, file_path: str | Path) -> "Config":
        """Load configuration from a file.

        Args:
            file_path: Path to the configuration file

        Returns:
            Config: Configuration object
        """
        file_path = Path(file_path)

        if not file_path.exists():
            msg = f"Configuration file not found: {file_path}"
            raise FileNotFoundError(msg)

        # Load based on file extension
        if file_path.suffix.lower() == ".json":
            with open(file_path, encoding="utf-8") as f:
                config_data = json.load(f)
        else:
            msg = f"Unsupported file format: {file_path.suffix}"
            raise ValueError(msg)

        return cls(**config_data)

    @classmethod
    def from_profile(cls, profile_name: str) -> "Config":
        """Load configuration from a profile.

        Args:
            profile_name: Name of the profile to load

        Returns:
            Config: Configuration object

        Raises:
            ValueError: If the profile doesn't exist or is invalid
        """
        # Load environment variables from profile-specific .env file
        env_file = f".env.{profile_name}"
        if not os.path.exists(env_file):
            msg = f"Profile environment file not found: {env_file}"
            raise ValueError(msg)

        load_dotenv(env_file)

        # Construct environment variable prefix for this profile
        env_prefix = f"API_{profile_name.upper()}_"

        # Extract configuration from environment variables
        config_data = {}
        for key in ["url", "username", "password", "timeout", "verify_ssl"]:
            env_var = f"{env_prefix}{key.upper()}"
            if env_var in os.environ:
                config_data[key] = os.environ[env_var]

        if not all(k in config_data for k in ["url", "username", "password"]):
            msg = f"Invalid profile configuration: {profile_name}"
            raise ValueError(msg)

        return cls(**config_data)


def load_config_from_env() -> Config:
    """Load configuration from environment variables.

    Returns:
        Config: Configuration object
    """
    return Config()


def list_available_profiles() -> list[str]:
    """List available configuration profiles.

    Profiles are identified by .env.{profile_name} files in the current directory.

    Returns:
        list[str]: list of available profile names
    """
    profiles = []

    # Search for .env.{profile} files
    for file in Path().glob(".env.*"):
        if file.name != ".env":
            profile_name = file.name.replace(".env.", "")
            profiles.append(profile_name)

    return profiles

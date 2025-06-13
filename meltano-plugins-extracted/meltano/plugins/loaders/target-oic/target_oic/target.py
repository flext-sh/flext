"""Oracle Integration Cloud target sink."""

import base64
import json
import logging
import time
from typing import Any

import requests
from requests.auth import HTTPBasicAuth
from singer_sdk.sinks import RecordSink
from singer_sdk.target_base import Target


class OICTarget(Target):
    """Target for Oracle Integration Cloud."""

    name = "target-oic"
    config_jsonschema = {
        "type": "object",
        "properties": {
            "oic_url": {
                "type": "string",
                "description": "OIC instance base URL",
            },
            "auth_method": {
                "type": "string",
                "enum": ["oauth2", "basic"],
                "default": "basic",
                "description": "Authentication method: oauth2 or basic",
            },
            "client_id": {
                "type": "string",
                "description": "OAuth2 client ID",
            },
            "client_secret": {
                "type": "string",
                "description": "OAuth2 client secret",
            },
            "idcs_url": {
                "type": "string",
                "description": "IDCS URL for OAuth2",
            },
            "resource_aud": {
                "type": "string",
                "description": "Resource audience for OAuth2",
            },
            "api_aud": {
                "type": "string",
                "description": "API audience for OAuth2",
            },
            "username": {
                "type": "string",
                "description": "Username for Basic Auth",
            },
            "password": {
                "type": "string",
                "description": "Password for Basic Auth",
            },
            "integrations": {
                "type": "object",
                "description": "Mapping from stream names to OIC integration endpoints",
                "additionalProperties": {
                    "type": "object",
                    "properties": {
                        "endpoint": {
                            "type": "string",
                            "description": "REST endpoint for the integration",
                        },
                        "method": {
                            "type": "string",
                            "enum": ["POST", "PUT", "PATCH"],
                            "default": "POST",
                            "description": "HTTP method to use",
                        },
                        "batch_size": {
                            "type": "integer",
                            "default": 1,
                            "description": "Number of records to send in each request",
                        },
                        "mapping_template": {
                            "type": "string",
                            "description": "JSON template for mapping Singer records to OIC format",
                        },
                    },
                    "required": ["endpoint"],
                },
            },
            "default_batch_size": {
                "type": "integer",
                "default": 1,
                "description": "Default batch size for all streams",
            },
            "retry_count": {
                "type": "integer",
                "default": 5,
                "description": "Number of retries on transient errors",
            },
            "retry_interval": {
                "type": "integer",
                "default": 5,
                "description": "Initial interval between retries (seconds)",
            },
            "retry_backoff": {
                "type": "number",
                "default": 2.0,
                "description": "Backoff multiplier for retries",
            },
            "request_timeout": {
                "type": "integer",
                "default": 300,
                "description": "HTTP request timeout in seconds",
            },
            "validate_records": {
                "type": "boolean",
                "default": True,
                "description": "Validate records against schema before sending",
            },
        },
        "required": ["oic_url", "integrations"],
        "anyOf": [
            {
                "required": [
                    "auth_method",
                    "client_id",
                    "client_secret",
                    "idcs_url",
                    "resource_aud",
                ],
                "properties": {"auth_method": {"enum": ["oauth2"]}},
            },
            {
                "required": ["username", "password"],
                "properties": {"auth_method": {"enum": ["basic"]}},
            },
        ],
    }

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        parse_env_config: bool = False,
    ) -> None:
        """Initialize the target."""
        super().__init__(config=config, parse_env_config=parse_env_config)
        self._auth_token = None
        self._token_expiry = 0
        self._session = requests.Session()
        self._logger = logging.getLogger("target-oic")
        self._setup_auth()

    def _setup_auth(self) -> None:
        """Set up authentication for OIC."""
        auth_method = self.config.get("auth_method", "basic")
        if auth_method == "oauth2":
            self._get_oauth_token()
        else:
            # For basic auth, we set the auth on each request
            self._session.auth = HTTPBasicAuth(
                self.config["username"],
                self.config["password"],
            )

    def _get_oauth_token(self) -> None:
        """Get OAuth2 token for OIC."""
        # Return if token is still valid
        if self._auth_token and time.time() < self._token_expiry - 60:
            return

        idcs_url = self.config["idcs_url"]
        client_id = self.config["client_id"]
        client_secret = self.config["client_secret"]
        resource_aud = self.config["resource_aud"]
        api_aud = self.config.get("api_aud", "")

        # Encode client credentials
        auth_string = f"{client_id}:{client_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()

        # Prepare headers and data
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded_auth}",
        }

        data = {
            "grant_type": "client_credentials",
            "scope": f"{resource_aud} {api_aud}".strip(),
        }

        # Send request
        url = f"https://{idcs_url}/oauth2/v1/token"
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()

        # Parse response
        token_data = response.json()
        self._auth_token = token_data["access_token"]
        self._token_expiry = time.time() + token_data["expires_in"]

        # Update session headers
        self._session.headers.update({"Authorization": f"Bearer {self._auth_token}"})

    def get_sink_class(self):
        """Return the sink class."""
        return OICSink

    def setup(self) -> None:
        """Set up the target."""
        # Test authentication
        self._logger.info("Testing connection to OIC...")
        self._test_connection()

    def _test_connection(self) -> None:
        """Test connection to OIC."""
        # Refresh token if using OAuth
        if self.config.get("auth_method") == "oauth2":
            self._get_oauth_token()

        # Try a simple request to verify connectivity
        url = f"{self.config['oic_url'].rstrip('/')}/ic/api/integration/v1/integrations"

        try:
            response = self._session.get(
                url,
                timeout=self.config.get("request_timeout", 300),
            )
            response.raise_for_status()
            self._logger.info("Successfully connected to OIC")
        except Exception as e:
            self._logger.exception(f"Failed to connect to OIC: {e!s}")
            msg = f"Connection test failed: {e!s}"
            raise RuntimeError(msg)


class OICSink(RecordSink):
    """OIC target sink class."""

    def __init__(
        self,
        target: Target,
        stream_name: str,
        schema: dict,
        key_properties: list[str] | None,
    ) -> None:
        """Initialize the sink."""
        super().__init__(
            target=target,
            stream_name=stream_name,
            schema=schema,
            key_properties=key_properties,
        )

        # Get stream-specific configuration
        self.integrations_config = target.config.get("integrations", {})
        self.stream_config = self.integrations_config.get(stream_name, {})

        if not self.stream_config:
            msg = f"No configuration found for stream '{stream_name}' in 'integrations' config"
            raise ValueError(
                msg,
            )

        # Set stream properties
        self.endpoint = self.stream_config["endpoint"]
        self.method = self.stream_config.get("method", "POST")
        self.batch_size = self.stream_config.get(
            "batch_size",
            target.config.get("default_batch_size", 1),
        )
        self.mapping_template = self.stream_config.get("mapping_template")

        # Retry configuration
        self.retry_count = target.config.get("retry_count", 5)
        self.retry_interval = target.config.get("retry_interval", 5)
        self.retry_backoff = target.config.get("retry_backoff", 2.0)
        self.request_timeout = target.config.get("request_timeout", 300)

        # Record batching
        self.records_buffer = []

        # Metrics
        self.records_processed = 0
        self.batch_count = 0
        self.error_count = 0

        self._logger = logging.getLogger(f"target-oic.{stream_name}")

    def process_record(self, record: dict, context: dict) -> None:
        """Process a single record."""
        self.records_buffer.append(record)

        # If we reached the batch size, send the batch
        if len(self.records_buffer) >= self.batch_size:
            self.process_batch()

    def process_batch(self) -> None:
        """Process the current batch of records."""
        if not self.records_buffer:
            return

        request_data = self._prepare_request_data(self.records_buffer)

        # If using OAuth2, refresh token if needed
        if self.target.config.get("auth_method") == "oauth2":
            self.target._get_oauth_token()

        # Construct the URL
        url = f"{self.target.config['oic_url'].rstrip('/')}/{self.endpoint.lstrip('/')}"

        # Set default headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Send the request with retries
        retries = 0
        retry_delay = self.retry_interval

        while True:
            try:
                response = self.target._session.request(
                    method=self.method,
                    url=url,
                    json=request_data,
                    headers=headers,
                    timeout=self.request_timeout,
                )

                response.raise_for_status()

                # Success! Record metrics and clear buffer
                self.records_processed += len(self.records_buffer)
                self.batch_count += 1
                self.records_buffer = []

                # Log success
                self._logger.info(
                    f"Successfully sent batch of {len(self.records_buffer)} records to {self.endpoint}",
                )

                break

            except requests.exceptions.RequestException as e:
                # Check if we should retry
                if retries >= self.retry_count:
                    self.error_count += 1
                    self._logger.exception(
                        f"Failed to send batch after {retries} retries: {e!s}",
                    )
                    msg = f"Failed to send batch to {self.endpoint}: {e!s}"
                    raise RuntimeError(
                        msg,
                    )

                # Check if error is retryable
                if (
                    isinstance(e, requests.exceptions.HTTPError)
                    and e.response.status_code >= 400
                    and e.response.status_code < 500
                ):
                    # Client errors are not retryable unless they're 429 (too many requests)
                    if e.response.status_code != 429:
                        self.error_count += 1
                        self._logger.exception(
                            f"Non-retryable client error: {e.response.status_code} {e.response.text}",
                        )
                        msg = f"Non-retryable client error: {e.response.status_code} {e.response.text}"
                        raise RuntimeError(
                            msg,
                        )

                # Log the error and retry
                self._logger.warning(
                    f"Retry {retries + 1}/{self.retry_count} - Error: {e!s}",
                )

                # Wait before retrying with exponential backoff
                time.sleep(retry_delay)
                retry_delay *= self.retry_backoff
                retries += 1

    def _prepare_request_data(self, records: list[dict]) -> dict | list:
        """Prepare the request payload based on mapping template."""
        # If mapping template is provided, use it to transform the records
        if self.mapping_template:
            return self._apply_mapping_template(records)

        # If batch size is 1 and we have a single record, return it directly
        if self.batch_size == 1 and len(records) == 1:
            return records[0]

        # Otherwise, return the list of records
        return records

    def _apply_mapping_template(self, records: list[dict]) -> dict | list:
        """Apply the mapping template to transform records."""
        try:
            # Parse the template as JSON
            template = json.loads(self.mapping_template)

            # If batch size is 1 and we have a single record, apply template to the single record
            if self.batch_size == 1 and len(records) == 1:
                return self._apply_template_to_record(template, records[0])

            # For multi-record batches, apply template to each record and return a list
            if "records" in template:
                # Template has a "records" key, so we'll put the transformed records there
                result = {}
                for key, value in template.items():
                    if key == "records":
                        result[key] = [
                            self._apply_template_to_record(value, record)
                            for record in records
                        ]
                    else:
                        # Static values in template
                        result[key] = value
                return result
            # No "records" key, so we'll apply the template to each record
            return [
                self._apply_template_to_record(template, record) for record in records
            ]

        except json.JSONDecodeError as e:
            msg = f"Invalid mapping template (not valid JSON): {e!s}"
            raise ValueError(msg)

    def _apply_template_to_record(self, template: dict, record: dict) -> dict:
        """Apply a template to a single record."""

        # Function to recursively process template values
        def process_value(value):
            if (
                isinstance(value, str)
                and value.startswith("${")
                and value.endswith("}")
            ):
                # It's a template variable
                field_name = value[2:-1].strip()
                if field_name in record:
                    return record[field_name]
                return None
            if isinstance(value, dict):
                return {k: process_value(v) for k, v in value.items()}
            if isinstance(value, list):
                return [process_value(item) for item in value]
            return value

        # Process the template
        return process_value(template)

    def clean_up(self) -> None:
        """Clean up resources and send any remaining records."""
        # Send any remaining records in the buffer
        if self.records_buffer:
            self.process_batch()

        # Log final metrics
        self._logger.info(
            f"Finished processing stream {self.stream_name}: "
            f"{self.records_processed} records in {self.batch_count} batches, "
            f"{self.error_count} errors",
        )

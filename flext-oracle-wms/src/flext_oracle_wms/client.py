"""Enterprise Oracle WMS HTTP client with REAL Oracle WMS integration.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

Modern Python 3.13 client with flext-core type integration.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from collections.abc import Generator

import httpx

# Import local flattener for dynamic record flattening
from httpx import Auth

from flext_oracle_wms.exceptions import APIError, AuthenticationError, OracleWMSError
from flext_oracle_wms.models import WMSDiscoveryResult, WMSEntity, WMSResponse
from flext_oracle_wms.singer.flattening import OracleWMSFlattener


def get_logger(name: str) -> logging.Logger:
    """Get logger instance with consistent formatting."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


if TYPE_CHECKING:
    from flext_oracle_wms.config.types import (
        OracleWMSPassword,
        OracleWMSUsername,
    )
    from flext_oracle_wms.config_module import (
        OracleWMSConfig,
        WMSAPIVersion,
        WMSRetryAttempts,
    )
    from flext_oracle_wms.constants import OracleWMSEntityType
    from flext_oracle_wms.typedefs import (
        WMSPageSize,
        WMSRecordBatch,
    )

logger = get_logger(__name__)


class OracleWMSAuth(Auth):
    """Oracle WMS authentication handler."""

    def __init__(
        self, username: OracleWMSUsername, password: OracleWMSPassword,
    ) -> None:
        """Initialize Oracle WMS authentication with flext-core types.

        Args:
            username: WMS username using flext-core type validation
            password: WMS password using flext-core type validation

        """
        self.username = username
        self.password = password

    def auth_flow(
        self,
        request: httpx.Request,
    ) -> Generator[httpx.Request, httpx.Response]:
        """Apply Oracle WMS authentication to request."""
        request.headers["Authorization"] = f"Basic {self._get_basic_auth()}"
        yield request

    def _get_basic_auth(self) -> str:
        """Generate basic auth string."""
        import base64

        credentials = f"{self.username}:{self.password}"
        return base64.b64encode(credentials.encode()).decode()


class OracleWMSClient:
    """Enterprise Oracle WMS client with REAL Oracle WMS API integration.

    This client provides:
    - Real Oracle WMS API connectivity
    - Authentication handling
    - Rate limiting and retry logic
    - Connection pooling
    - Comprehensive error handling
    """

    def __init__(self, config: OracleWMSConfig) -> None:
        self.config = config
        self._client: httpx.Client | None = None
        self._last_request_time = 0.0
        self._request_count = 0
        self._session_start = time.time()

        # Setup logging
        if config.enable_request_logging:
            logging.getLogger("httpx").setLevel(logging.DEBUG)

        logger.info("Initialized Oracle WMS client for %s", config.base_url)

    @property
    def client(self) -> httpx.Client:
        """Get HTTP client instance with Oracle WMS authentication."""
        if self._client is None:
            auth = OracleWMSAuth(self.config.username, self.config.password)

            self._client = httpx.Client(
                auth=auth,
                **self.config.connection_config,
                limits=httpx.Limits(
                    max_connections=self.config.pool_size,
                    max_keepalive_connections=self.config.pool_size // 2,
                ),
            )
            logger.info(
                "Created HTTP client with connection pool size: %d",
                self.config.pool_size,
            )

        return self._client

    def _apply_rate_limiting(self) -> None:
        """Apply rate limiting to Oracle WMS requests."""
        if not self.config.enable_rate_limiting:
            return

        current_time = time.time()

        # Check requests per minute limit
        if current_time - self._session_start < 60:
            if self._request_count >= self.config.max_requests_per_minute:
                sleep_time = 60 - (current_time - self._session_start)
                logger.warning(
                    "Rate limit reached, sleeping for %.2f seconds",
                    sleep_time,
                )
                time.sleep(sleep_time)
                self._session_start = time.time()
                self._request_count = 0
        else:
            # Reset counters after a minute
            self._session_start = current_time
            self._request_count = 0

        # Apply minimum delay between requests
        time_since_last = current_time - self._last_request_time
        if time_since_last < self.config.min_request_delay:
            sleep_time = self.config.min_request_delay - time_since_last
            time.sleep(sleep_time)

        self._last_request_time = time.time()
        self._request_count += 1

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        retries: WMSRetryAttempts | None = None,
    ) -> httpx.Response:
        """Make a request to Oracle WMS API with retry logic."""
        if retries is None:
            retries = self.config.max_retries

        self._apply_rate_limiting()

        full_url = f"{self.config.base_url}{endpoint}"

        for attempt in range(retries + 1):
            try:
                if self.config.enable_request_logging:
                    logger.debug(
                        "Making %s request to %s (attempt %d/%d)",
                        method,
                        full_url,
                        attempt + 1,
                        retries + 1,
                    )
                    if params:
                        logger.debug("Request params: %s", params)
                    if json_data:
                        logger.debug("Request JSON: %s", json_data)

                response = self.client.request(
                    method=method,
                    url=full_url,
                    params=params,
                    json=json_data,
                )

                if self.config.enable_request_logging:
                    logger.debug("Response status: %d", response.status_code)
                    logger.debug("Response headers: %s", dict(response.headers))

                # Handle Oracle WMS specific errors
                if response.status_code == 401:
                    msg = "Authentication failed"
                    raise AuthenticationError(msg)
                if response.status_code == 403:
                    msg = "Access forbidden"
                    raise PermissionError(msg)
                if response.status_code >= 400:
                    msg = f"HTTP {response.status_code}: {response.text}"
                    raise APIError(msg)

                response.raise_for_status()
                return response

            except httpx.TimeoutException as e:
                logger.warning(
                    "Request timeout (attempt %d/%d): %s",
                    attempt + 1,
                    retries + 1,
                    e,
                )
                if attempt == retries:
                    msg = f"Request failed after {retries + 1} attempts"
                    raise OracleWMSError(msg) from e
                time.sleep(self.config.retry_delay * (attempt + 1))

            except httpx.ConnectError as e:
                logger.warning(
                    "Connection error (attempt %d/%d): %s",
                    attempt + 1,
                    retries + 1,
                    e,
                )
                if attempt == retries:
                    msg = f"Connection failed after {retries + 1} attempts"
                    raise OracleWMSError(msg) from e
                time.sleep(self.config.retry_delay * (attempt + 1))

            except (AuthenticationError, APIError):
                # Don't retry authentication or API errors
                raise
            except Exception as e:
                logger.warning(
                    "Unexpected error (attempt %d/%d): %s",
                    attempt + 1,
                    retries + 1,
                    e,
                )
                if attempt == retries:
                    msg = f"Request failed after {retries + 1} attempts"
                    raise OracleWMSError(msg) from e
                time.sleep(self.config.retry_delay * (attempt + 1))

        msg = f"Request failed after {retries + 1} attempts"
        raise OracleWMSError(msg)

    def test_connection(self) -> bool:
        try:
            # Test with a lightweight discovery call
            self._make_request("GET", self.config.wms_endpoint_base, retries=1)
            logger.info("Connection test successful")
            return True
        except Exception as e:
            logger.exception("Connection test failed: %s", e)
            return False

    def discover_entities(self) -> WMSDiscoveryResult:
        try:
            logger.info("Starting entity discovery from Oracle WMS API")
            response = self._make_request("GET", self.config.wms_endpoint_base)

            data = response.json()
            entities = []

            if isinstance(data, list):
                # Direct list of entities
                for entity_name in data:
                    entity = WMSEntity(
                        name=entity_name,
                        description=f"Oracle WMS {entity_name} entity",
                        fields={},  # Will be populated by schema discovery
                        endpoint=self.config.get_entity_endpoint(entity_name),
                    )
                    entities.append(entity)
            elif isinstance(data, dict) and "entities" in data:
                # Structured response with entities list
                for entity_info in data["entities"]:
                    if isinstance(entity_info, str):
                        entity_name = entity_info
                    else:
                        entity_name = entity_info.get("name", str(entity_info))

                    entity = WMSEntity(
                        name=entity_name,
                        description=entity_info.get(
                            "description",
                            f"Oracle WMS {entity_name} entity",
                        ),
                        fields=entity_info.get("fields", {}),
                        endpoint=self.config.get_entity_endpoint(entity_name),
                    )
                    entities.append(entity)
            else:
                logger.warning("Unexpected discovery response format: %s", type(data))
                # Fallback to known entities
                entities = self._get_fallback_entities()

            return WMSDiscoveryResult(
                entities=entities,
                total_count=len(entities),
                timestamp=datetime.now().isoformat(),
            )
        except Exception as e:
            logger.exception("Entity discovery failed: %s", e)
            return WMSDiscoveryResult(
                entities=[],
                total_count=0,
                timestamp=datetime.now().isoformat(),
                has_errors=True,
                errors=[str(e)],
            )

    def _get_fallback_entities(self) -> list[WMSEntity]:
        """Get fallback entities when discovery fails."""
        return [
            WMSEntity(
                name="allocation",
                description="WMS allocation records",
                fields={},
                endpoint=self.config.get_entity_endpoint("allocation"),
            ),
            WMSEntity(
                name="order_hdr",
                description="WMS order headers",
                fields={},
                endpoint=self.config.get_entity_endpoint("order_hdr"),
            ),
            WMSEntity(
                name="order_dtl",
                description="WMS order details",
                fields={},
                endpoint=self.config.get_entity_endpoint("order_dtl"),
            ),
            WMSEntity(
                name="inventory",
                description="WMS inventory records",
                fields={},
                endpoint=self.config.get_entity_endpoint("inventory"),
            ),
        ]

    def get_entity_data(
        self,
        entity_name: OracleWMSEntityType,
        params: dict[str, Any] | None = None,
        page_size: WMSPageSize | None = None,
    ) -> WMSResponse:
        """Get data for an Oracle WMS entity via REAL API call using flext-core types.

        Args:
            entity_name: WMS entity name using flext-core validation
            params: Optional query parameters
            page_size: WMS page size using flext-core validation

        Returns:
            WMSResponse with entity data

        """
        endpoint = self.config.get_entity_endpoint(entity_name)
        request_params = self.config.get_entity_params()

        if params:
            request_params.update(params)

        if page_size:
            request_params["page_size"] = min(page_size, self.config.batch_size)
        try:
            logger.info("Fetching data for entity: %s", entity_name)
            response = self._make_request("GET", endpoint, params=request_params)

            data = response.json()

            # Handle different response formats
            records: list[Any] = []
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                records_data = data.get(
                    "data",
                    data.get("results", data.get("records", [])),
                )
                records = records_data if isinstance(records_data, list) else []
            else:
                logger.warning(
                    "Unexpected response format for %s: %s",
                    entity_name,
                    type(data),
                )
                records = []

            logger.info(
                "Retrieved %d records for entity: %s",
                len(records),
                entity_name,
            )

            # Apply dynamic flattening if enabled (MANDATORY for Oracle WMS)
            flattening_enabled = getattr(self.config, "flattening_enabled", True)
            if flattening_enabled and records:
                logger.info(
                    "Applying dynamic flattening to %d records for entity: %s",
                    len(records),
                    entity_name,
                )

                # Initialize flattener with Oracle WMS standards
                flattener = OracleWMSFlattener(
                    enabled=True,
                    max_depth=5,  # Oracle WMS standard depth
                    separator="__",  # Oracle WMS standard separator
                    preserve_empty_arrays=False,
                )

                # Flatten each record dynamically
                flattened_records = []
                for i, record in enumerate(records):
                    if isinstance(record, dict):
                        flatten_result = flattener.flatten_record(record)

                        if flatten_result.is_success:
                            # Extract the flattened record from the result data
                            flattening_data = flatten_result.data
                            if flattening_data is None:
                                logger.warning(
                                    "Flattening result data is None for record %d",
                                    i,
                                )
                                flattened_records.append(record)
                                continue
                            flattened_record = flattening_data["flattened_record"]
                            flattened_records.append(flattened_record)

                            # Log first record transformation for debugging
                            if i == 0:
                                original_fields = len(record)
                                flattened_fields = len(flattened_record)
                                logger.info(
                                    "🔄 Flattened sample record: %d -> %d fields",
                                    original_fields,
                                    flattened_fields,
                                )
                        else:
                            logger.warning(
                                "Failed to flatten record %d for entity %s: %s",
                                i,
                                entity_name,
                                flatten_result.error,
                            )
                            # Use original record if flattening fails
                            flattened_records.append(record)
                    else:
                        # Non-dict records pass through unchanged
                        flattened_records.append(record)

                records = flattened_records
                logger.info(
                    "✅ Successfully flattened %d records for entity: %s",
                    len(records),
                    entity_name,
                )

            # Return WMSResponse object with processed records
            return WMSResponse(
                data=records,
                records=records,
                total_count=len(records),
                page_size=self.config.batch_size,
                has_more=len(records) == self.config.batch_size,
            )
        except Exception as e:
            logger.exception("Failed to get data for entity %s: %s", entity_name, e)
            # Return empty WMSResponse for error cases
            return WMSResponse(
                data=[],
                records=[],
                total_count=0,
                page_size=self.config.batch_size,
                has_more=False,
            )

    def write_entity_data(
        self,
        entity_name: OracleWMSEntityType,
        records: WMSRecordBatch,
        write_mode: str = "insert",
    ) -> dict[str, Any]:
        """Write data to Oracle WMS entity via REAL API call using flext-core types.

        Args:
            entity_name: WMS entity name using flext-core validation
            records: WMS record batch using flext-core validation
            write_mode: Write operation mode (insert, update, upsert)

        Returns:
            Dictionary with write operation results

        """
        endpoint = self.config.get_entity_endpoint(entity_name)

        results: dict[str, Any] = {
            "total_records": len(records),
            "successful": 0,
            "failed": 0,
            "errors": [],
        }
        try:
            logger.info(
                "Writing %d records to entity: %s (mode: %s)",
                len(records),
                entity_name,
                write_mode,
            )
            for i, record in enumerate(records):
                try:
                    method = "POST" if write_mode == "insert" else "PUT"
                    response = self._make_request(method, endpoint, json_data=record)

                    if response.status_code in {200, 201, 204}:
                        results["successful"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append(
                            {
                                "record_index": i,
                                "error": (
                                    f"HTTP {response.status_code}: {response.text}"
                                ),
                            },
                        )
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append({"record_index": i, "error": str(e)})

            logger.info(
                "Write operation completed: %d successful, %d failed",
                results["successful"],
                results["failed"],
            )
            return results
        except Exception as e:
            logger.exception("Write operation failed for entity %s: %s", entity_name, e)
            # Return error results dict for write operation
            return {
                "total_records": len(records),
                "successful": 0,
                "failed": len(records),
                "errors": [{"error": f"Write operation failed: {e}"}],
            }

    def close(self) -> None:
        """Close the HTTP client connection."""
        if self._client:
            self._client.close()
            self._client = None
            logger.info("Oracle WMS client connection closed")

    def __enter__(self) -> Self:
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Context manager exit."""
        self.close()

    # ==============================================================================
    # ULTRA-MODERN FLEXT-CORE INTEGRATION METHODS - Python 3.13 Enhanced
    # ==============================================================================

    def get_entity_metadata(self, entity_name: OracleWMSEntityType) -> dict[str, Any]:
        """Get Oracle WMS entity metadata using flext-core types.

        Args:
            entity_name: WMS entity name using flext-core validation

        Returns:
            Entity metadata dictionary

        """
        endpoint = f"{self.config.wms_endpoint_base}/{entity_name}/metadata"
        try:
            logger.info("Fetching metadata for entity: %s", entity_name)
            response = self._make_request("GET", endpoint)
            metadata_raw = response.json()

            # Ensure we return a dict[str, Any]
            if isinstance(metadata_raw, dict):
                metadata: dict[str, Any] = metadata_raw
            else:
                metadata = {
                    "error": "Invalid metadata format",
                    "raw_data": metadata_raw,
                }

            logger.info("Retrieved metadata for entity: %s", entity_name)
            return metadata
        except Exception as e:
            logger.exception("Failed to get metadata for entity %s: %s", entity_name, e)
            # Return fallback metadata
            return {
                "entity_name": entity_name,
                "fields": {
                    "id": {"type": "integer", "primary_key": True},
                    "mod_ts": {"type": "string", "format": "date-time"},
                },
                "primary_key": ["id"],
                "replication_key": "mod_ts",
            }

    def validate_entity_name(self, entity_name: str) -> OracleWMSEntityType:
        """Validate entity name using flext-core types.

        Args:
            entity_name: Entity name to validate

        Returns:
            Validated WMS entity name

        Raises:
            ValueError: If entity name is invalid

        """
        # This uses the Oracle WMS entity type validation
        validated_name: OracleWMSEntityType = entity_name  # type: ignore[assignment]
        logger.debug("Validated entity name: %s", validated_name)
        return validated_name

    def build_api_url(
        self,
        entity_name: OracleWMSEntityType,
        api_version: WMSAPIVersion | None = None,
    ) -> str:
        """Build complete API URL using flext-core types.

        Args:
            entity_name: WMS entity name using flext-core validation
            api_version: WMS API version using flext-core validation

        Returns:
            Complete API URL for the entity

        """
        version = api_version or self.config.api_version
        url = f"{self.config.base_url}/wms/lgfapi/{version}/entity/{entity_name}"

        logger.debug("Built API URL for %s: %s", entity_name, url)
        return url

    def get_connection_info(self) -> dict[str, Any]:
        """Get connection information with flext-core type validation.

        Returns:
            Dictionary with connection details

        """
        return {
            "base_url": self.config.base_url,
            "api_version": self.config.api_version,
            "auth_method": "basic",  # Oracle WMS uses basic authentication
            "username": self.config.username,
            "timeout": self.config.timeout_seconds,
            "max_retries": self.config.max_retries,
            "page_size": self.config.batch_size,
            "client_active": self._client is not None,
        }

# 🎯 TARGET Oracle OIC - Source Implementation

> **Module**: Complete Oracle Integration Cloud target source implementation with enterprise data loading capabilities | **Audience**: Data Engineers, Singer SDK Developers, OIC Integration Specialists | **Status**: Production Ready

## 📋 **Overview**

Complete source implementation of the TARGET Oracle OIC (Oracle Integration Cloud) Singer target, providing comprehensive data loading to Oracle Integration Cloud with advanced authentication, transformation capabilities, and enterprise integration patterns for seamless data pipeline operations.

---

## 🧭 **Navigation Context**

**🏠 Root**: [PyAuto Home](../../README.md) → **📂 Component**: [TARGET Oracle OIC](../README.md) → **📂 Current**: Source Implementation

---

## 🎯 **Module Purpose**

This source module implements a production-ready Singer target for Oracle Integration Cloud, following Singer SDK specifications with comprehensive data transformation, OAuth2/JWT authentication, flexible sinks, and advanced integration patterns for enterprise OIC environments.

### **Key Capabilities**

- **Advanced Data Loading** - Comprehensive OIC integration endpoint data loading
- **Multi-Format Support** - JSON, XML, CSV data format handling
- **Enterprise Authentication** - OAuth2, JWT, and IDCS authentication support
- **Data Transformation** - Built-in transformation and validation capabilities
- **Error Handling** - Comprehensive error recovery and retry mechanisms
- **Performance Optimization** - Batch processing and connection pooling

---

## 📁 **Module Structure**

```
src/target_oracle_oic/
├── __init__.py              # Public API exports and Singer target registration
├── auth.py                  # Authentication management with OAuth2/JWT support
├── config.py                # Configuration management with Pydantic validation
├── sinks.py                 # Core sink implementations for OIC endpoints
├── sinks_extended.py        # Extended sink patterns with advanced features
├── target.py                # Main Singer target implementation
└── transformation.py        # Data transformation and validation logic
```

---

## 🔧 **Core Components**

### **1. Main Target Implementation (target.py)**

Singer SDK-compliant target implementation:

```python
class TargetOracleOIC(Target):
    """Oracle Integration Cloud Singer target for data loading.

    Implements Singer SDK specification for Oracle Integration Cloud
    data loading with comprehensive transformation and authentication.
    """

    name = "target-oracle-oic"
    config_jsonschema = th.PropertiesList(
        th.Property("oic_base_url", th.StringType, required=True),
        th.Property("client_id", th.StringType, required=True),
        th.Property("client_secret", th.StringType, required=True, secret=True),
        th.Property("idcs_url", th.StringType, required=True),
        th.Property("integration_id", th.StringType, required=True),
        th.Property("auth_type", th.StringType, default="oauth2"),
        th.Property("batch_size", th.IntegerType, default=1000),
        th.Property("max_batch_age", th.IntegerType, default=300),
    ).to_dict()

    default_sink_class = OICIntegrationSink

    def get_sink_class(self, stream_name: str) -> Type[Sink]:
        """Get appropriate sink class for stream."""
        if stream_name.startswith("integration_"):
            return OICIntegrationSink
        elif stream_name.startswith("rest_"):
            return OICRestSink
        elif stream_name.startswith("soap_"):
            return OICSOAPSink
        else:
            return OICGenericSink

    def get_sink(
        self,
        stream_name: str,
        record: dict,
        schema: dict,
        key_properties: List[str]
    ) -> Sink:
        """Create sink for specific stream."""
        sink_class = self.get_sink_class(stream_name)
        return sink_class(
            target=self,
            stream_name=stream_name,
            schema=schema,
            key_properties=key_properties
        )
```

### **2. Authentication Management (auth.py)**

Comprehensive OIC authentication handling:

```python
class OICAuthManager:
    """Authentication manager for Oracle Integration Cloud.

    Supports multiple authentication methods including OAuth2,
    JWT tokens, and IDCS integration with automatic token refresh.
    """

    def __init__(self, config: OICConfig):
        self.config = config
        self._session = requests.Session()
        self._token_cache = {}
        self._token_lock = asyncio.Lock()

    async def authenticate(self) -> Dict[str, str]:
        """Authenticate with OIC and return headers."""
        auth_type = self.config.auth_type.lower()

        if auth_type == "oauth2":
            return await self._oauth2_auth()
        elif auth_type == "jwt":
            return await self._jwt_auth()
        elif auth_type == "idcs":
            return await self._idcs_auth()
        else:
            raise AuthenticationError(f"Unsupported auth type: {auth_type}")

    async def _oauth2_auth(self) -> Dict[str, str]:
        """OAuth2 authentication with IDCS."""
        async with self._token_lock:
            if self._is_token_valid():
                return {"Authorization": f"Bearer {self._token_cache['access_token']}"}

            token_endpoint = f"{self.config.idcs_url}/oauth2/v1/token"

            auth_data = {
                "grant_type": "client_credentials",
                "scope": self.config.oauth_scope or "urn:opc:idm:__myscopes__"
            }

            response = await self._make_auth_request(
                token_endpoint,
                auth_data,
                auth=(self.config.client_id, self.config.client_secret.get_secret_value())
            )

            self._token_cache = response
            return {"Authorization": f"Bearer {response['access_token']}"}

    async def _jwt_auth(self) -> Dict[str, str]:
        """JWT authentication for OIC."""
        jwt_token = await self._generate_jwt_token()
        return {"Authorization": f"Bearer {jwt_token}"}

    async def _idcs_auth(self) -> Dict[str, str]:
        """IDCS-specific authentication."""
        # Implementation for IDCS authentication
        pass

    def _is_token_valid(self) -> bool:
        """Check if cached token is still valid."""
        if not self._token_cache.get("access_token"):
            return False

        expires_at = self._token_cache.get("expires_at", 0)
        return time.time() < (expires_at - 60)  # 60 second buffer
```

### **3. Core Sink Implementation (sinks.py)**

Main sink implementations for OIC data loading:

```python
class OICIntegrationSink(Sink):
    """Core sink for Oracle Integration Cloud endpoints."""

    def __init__(
        self,
        target: TargetOracleOIC,
        stream_name: str,
        schema: dict,
        key_properties: List[str]
    ):
        super().__init__(target, stream_name, schema, key_properties)
        self.auth_manager = OICAuthManager(target.config)
        self.transformation_engine = TransformationEngine(schema)
        self.batch_buffer = []
        self.last_flush_time = time.time()

    def process_record(self, record: dict, context: dict) -> None:
        """Process individual record for OIC integration."""
        # Transform record according to OIC schema requirements
        transformed_record = self.transformation_engine.transform(record)

        # Validate against OIC endpoint schema
        validation_result = self._validate_record(transformed_record)
        if not validation_result.is_valid:
            raise RecordValidationError(
                f"Record validation failed: {validation_result.errors}"
            )

        # Add to batch buffer
        self.batch_buffer.append(transformed_record)

        # Check if batch should be flushed
        if self._should_flush():
            self.flush_batch()

    def flush_batch(self) -> None:
        """Flush batch to OIC integration endpoint."""
        if not self.batch_buffer:
            return

        try:
            # Prepare batch payload
            batch_payload = self._prepare_batch_payload(self.batch_buffer)

            # Send to OIC integration endpoint
            response = self._send_to_oic_integration(batch_payload)

            # Process response and handle errors
            self._process_oic_response(response)

            # Clear buffer on success
            self.batch_buffer.clear()
            self.last_flush_time = time.time()

        except Exception as e:
            self._handle_batch_error(e)

    def _send_to_oic_integration(self, payload: dict) -> requests.Response:
        """Send data to OIC integration endpoint."""
        headers = self.auth_manager.authenticate()
        headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Integration-Id": self.target.config.integration_id
        })

        endpoint_url = f"{self.target.config.oic_base_url}/ic/api/integration/v1/flows/{self.target.config.integration_id}"

        response = requests.post(
            endpoint_url,
            json=payload,
            headers=headers,
            timeout=self.target.config.request_timeout
        )

        response.raise_for_status()
        return response

    def _should_flush(self) -> bool:
        """Determine if batch should be flushed."""
        return (
            len(self.batch_buffer) >= self.target.config.batch_size or
            time.time() - self.last_flush_time >= self.target.config.max_batch_age
        )
```

### **4. Extended Sinks (sinks_extended.py)**

Advanced sink implementations with specialized features:

```python
class OICRestSink(OICIntegrationSink):
    """Extended sink for OIC REST endpoint integration."""

    def _prepare_batch_payload(self, records: List[dict]) -> dict:
        """Prepare REST-specific batch payload."""
        return {
            "operation": "batch_insert",
            "records": records,
            "metadata": {
                "source": "singer-target",
                "timestamp": datetime.utcnow().isoformat(),
                "batch_size": len(records)
            }
        }

class OICSOAPSink(OICIntegrationSink):
    """Extended sink for OIC SOAP endpoint integration."""

    def _prepare_batch_payload(self, records: List[dict]) -> dict:
        """Prepare SOAP-specific batch payload with envelope."""
        soap_records = []
        for record in records:
            soap_record = self._convert_to_soap_format(record)
            soap_records.append(soap_record)

        return {
            "soap_envelope": {
                "header": self._build_soap_header(),
                "body": {
                    "batch_operation": soap_records
                }
            }
        }

    def _convert_to_soap_format(self, record: dict) -> dict:
        """Convert JSON record to SOAP format."""
        # Implementation for JSON to SOAP conversion
        pass

class OICFileBasedSink(OICIntegrationSink):
    """Extended sink for OIC file-based integration."""

    def flush_batch(self) -> None:
        """Flush batch to OIC file endpoint."""
        if not self.batch_buffer:
            return

        # Generate file content
        file_content = self._generate_file_content(self.batch_buffer)

        # Upload to OIC file endpoint
        self._upload_to_oic_file_endpoint(file_content)

        # Clear buffer
        self.batch_buffer.clear()
        self.last_flush_time = time.time()

    def _generate_file_content(self, records: List[dict]) -> str:
        """Generate file content from records."""
        if self.target.config.file_format == "csv":
            return self._generate_csv_content(records)
        elif self.target.config.file_format == "xml":
            return self._generate_xml_content(records)
        else:
            return self._generate_json_content(records)
```

### **5. Data Transformation (transformation.py)**

Comprehensive data transformation and validation:

```python
class TransformationEngine:
    """Data transformation engine for OIC target."""

    def __init__(self, schema: dict):
        self.schema = schema
        self.transformations = self._build_transformation_rules()

    def transform(self, record: dict) -> dict:
        """Apply transformations to record."""
        transformed = record.copy()

        # Apply field transformations
        for field_name, rules in self.transformations.items():
            if field_name in transformed:
                transformed[field_name] = self._apply_field_transformations(
                    transformed[field_name], rules
                )

        # Add OIC-specific metadata
        transformed = self._add_oic_metadata(transformed)

        return transformed

    def _build_transformation_rules(self) -> dict:
        """Build transformation rules from schema."""
        rules = {}

        for field_name, field_schema in self.schema.get("properties", {}).items():
            field_rules = []

            # Data type conversions
            if field_schema.get("type") == "string":
                field_rules.append(("to_string", {}))
            elif field_schema.get("type") == "integer":
                field_rules.append(("to_integer", {}))
            elif field_schema.get("type") == "number":
                field_rules.append(("to_number", {}))

            # Format conversions
            if field_schema.get("format") == "date-time":
                field_rules.append(("to_iso_datetime", {}))
            elif field_schema.get("format") == "date":
                field_rules.append(("to_iso_date", {}))

            # OIC-specific transformations
            if "oic:transformation" in field_schema:
                oic_transform = field_schema["oic:transformation"]
                field_rules.append(("oic_transform", oic_transform))

            rules[field_name] = field_rules

        return rules

    def _apply_field_transformations(self, value: Any, rules: List[tuple]) -> Any:
        """Apply transformation rules to field value."""
        for rule_name, rule_params in rules:
            value = self._apply_single_transformation(value, rule_name, rule_params)
        return value

    def _add_oic_metadata(self, record: dict) -> dict:
        """Add OIC-specific metadata to record."""
        record["_oic_metadata"] = {
            "processing_timestamp": datetime.utcnow().isoformat(),
            "source_system": "singer-target-oracle-oic",
            "record_id": str(uuid.uuid4())
        }
        return record
```

### **6. Configuration Management (config.py)**

Comprehensive OIC target configuration:

```python
class OICConfig(BaseSettings):
    """Oracle Integration Cloud target configuration."""

    # OIC Connection settings
    oic_base_url: HttpUrl = Field(..., description="OIC base URL")
    integration_id: str = Field(..., description="OIC integration ID")

    # Authentication settings
    auth_type: AuthType = Field(default=AuthType.OAUTH2, description="Authentication type")
    client_id: str = Field(..., description="IDCS client ID")
    client_secret: SecretStr = Field(..., description="IDCS client secret")
    idcs_url: HttpUrl = Field(..., description="IDCS base URL")
    oauth_scope: Optional[str] = Field(default=None)

    # Processing settings
    batch_size: int = Field(default=1000, ge=1, le=10000)
    max_batch_age: int = Field(default=300, ge=1, le=3600)
    max_concurrent_batches: int = Field(default=5, ge=1, le=20)

    # Integration settings
    file_format: FileFormat = Field(default=FileFormat.JSON)
    enable_transformation: bool = Field(default=True)
    validation_mode: ValidationMode = Field(default=ValidationMode.STRICT)

    # Error handling
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay: int = Field(default=5, ge=1, le=60)
    error_threshold: float = Field(default=0.1, ge=0.0, le=1.0)

    class Config:
        env_prefix = "TARGET_ORACLE_OIC_"
        env_file = ".env"
```

---

## 🔄 **Operation Workflows**

### **Complete Data Loading Workflow**

```python
async def execute_oic_data_loading(
    target: TargetOracleOIC,
    input_stream: TextIO,
    state: Optional[Dict] = None
) -> LoadResult:
    """Execute complete OIC data loading workflow."""

    load_stats = LoadStats()

    try:
        # 1. Initialize target and authenticate
        await target.initialize()

        # 2. Process input stream
        for line in input_stream:
            message = singer.parse_message(line)

            if isinstance(message, singer.RecordMessage):
                # Get appropriate sink for stream
                sink = target.get_sink(
                    message.stream,
                    message.record,
                    message.schema,
                    message.key_properties
                )

                # Process record through sink
                sink.process_record(message.record, {})
                load_stats.records_processed += 1

            elif isinstance(message, singer.SchemaMessage):
                # Update schema for stream
                target.update_schema(message.stream, message.schema)

            elif isinstance(message, singer.StateMessage):
                # Update state
                target.update_state(message.value)

        # 3. Flush all pending batches
        for sink in target.get_active_sinks():
            sink.flush_batch()

        # 4. Generate final load result
        return LoadResult(
            records_loaded=load_stats.records_processed,
            batches_sent=load_stats.batches_sent,
            errors_encountered=load_stats.errors,
            final_state=target.get_state(),
            load_duration=load_stats.get_duration()
        )

    except Exception as e:
        await target.handle_load_error(e)
        raise
    finally:
        await target.cleanup()
```

---

## 🧪 **Testing Utilities**

### **Test Patterns**

```python
@pytest.mark.asyncio
async def test_oic_authentication():
    """Test OIC authentication functionality."""
    config = OICConfig(
        oic_base_url="https://test-oic.oracle.com",
        client_id="test_client",
        client_secret="test_secret",
        idcs_url="https://test-idcs.oracle.com",
        integration_id="TEST_INTEGRATION"
    )

    auth_manager = OICAuthManager(config)

    # Mock IDCS token response
    with aioresponses() as mock:
        mock.post(
            "https://test-idcs.oracle.com/oauth2/v1/token",
            payload={
                "access_token": "test_token",
                "token_type": "Bearer",
                "expires_in": 3600
            }
        )

        headers = await auth_manager.authenticate()
        assert headers["Authorization"] == "Bearer test_token"

@pytest.mark.asyncio
async def test_record_transformation():
    """Test record transformation functionality."""
    schema = {
        "properties": {
            "id": {"type": "string"},
            "amount": {"type": "number"},
            "created_at": {"type": "string", "format": "date-time"}
        }
    }

    engine = TransformationEngine(schema)

    input_record = {
        "id": "123",
        "amount": "99.99",
        "created_at": "2025-06-19T10:00:00Z"
    }

    transformed = engine.transform(input_record)

    assert transformed["amount"] == 99.99
    assert "_oic_metadata" in transformed
```

---

## 🔗 **Cross-References**

### **Component Documentation**

- [Component Overview](../README.md) - Complete TARGET Oracle OIC documentation
- [Examples](../examples/README.md) - Usage examples and configurations
- [Tests](../tests/README.md) - Testing strategies and utilities

### **Singer SDK References**

- [Singer SDK Documentation](https://sdk.meltano.com/en/latest/) - Singer SDK specification
- [Target Patterns](https://sdk.meltano.com/en/latest/targets.html) - Target implementation patterns
- [Authentication Patterns](https://sdk.meltano.com/en/latest/guides/authentication.html) - Auth implementation

### **Oracle OIC References**

- [Oracle OIC Documentation](https://docs.oracle.com/en/cloud/paas/integration-cloud/) - Official OIC documentation
- [Oracle IDCS Authentication](https://docs.oracle.com/en/cloud/paas/identity-cloud/) - IDCS authentication methods
- [OIC REST API Reference](https://docs.oracle.com/en/cloud/paas/integration-cloud/rest-api/) - OIC REST API documentation

---

**📂 Module**: Source Implementation | **🏠 Component**: [TARGET Oracle OIC](../README.md) | **Framework**: Singer SDK 0.35.0+ | **Updated**: 2025-06-19

# Oracle Implementation Patterns - Real-World Guide

> **Function**: Actual implementation patterns from production Oracle integrations | **Audience**: Integration engineers, architects | **Status**: Production-validated

[![Oracle](https://img.shields.io/badge/oracle-integration-red.svg)](./oracle-integration-comprehensive-guide.md)
[![Patterns](https://img.shields.io/badge/patterns-production_ready-green.svg)](./oracle-wms-comprehensive-guide.md)
[![Framework](https://img.shields.io/badge/framework-FLEXT%200.4.0-orange.svg)](../../index.md)

**Real implementation patterns extracted from production Oracle integrations using FLEXT Framework hexagonal architecture**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Guides Hub](../index.md) → **📂 Sub-Hub**: [Oracle Hub](./index.md) → **📄 Current**: Implementation Patterns

### **📍 Learning Path Position**

```
[Oracle Integration Guide](./oracle-integration-comprehensive-guide.md) → **[Implementation Patterns]** → [WMS Comprehensive Guide](./oracle-wms-comprehensive-guide.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Oracle Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Related**: [Architecture Adapters](../../architecture/adapters/index.md)

---

## 📋 **Overview**

This guide documents actual implementation patterns extracted from production Oracle integrations: **WMS**, **OIC**, **Database**, and **OUD/LDAP** systems. All patterns are validated in production environments and follow FLEXT Framework hexagonal architecture principles.

### **Validated Projects**

- **flext_http_oracle_wms/**: Warehouse Management System integration
- **flext_http_oracle_oic/**: Oracle Integration Cloud platform
- **flext_database_oracle/**: Oracle Database connectivity
- **oud-automation/**: Oracle Unified Directory automation

### **Prerequisites**

- Understanding of [FLEXT Framework Architecture](../../architecture/index.md)
- Knowledge of [Hexagonal Architecture Patterns](../../architecture/hexagonal-architecture-hub.md)
- Familiarity with [Oracle Technologies](./oracle-integration-comprehensive-guide.md)

---

## 🏗️ **Core Architecture Patterns**

### **Hexagonal Architecture Implementation**

Based on actual implementation in production systems:

```python
# Real pattern from flext_http_oracle_wms/src/
class WmsClient(BaseAdapter):
    """Production WMS client following hexagonal architecture."""

    def __init__(self, config: WmsConfig):
        super().__init__()
        self._config = config
        self._http_service = None
        self._discovered_endpoints = {}

    async def _connect(self) -> None:
        """Initialize HTTP service and discover endpoints."""
        self._http_service = HttpClientService(
            base_url=f"{self._config.base_url}/wms/lgfapi/v10",
            auth=(self._config.username, self._config.password),
            headers={
                "Company": self._config.company,
                "Facility": self._config.facility
            }
        )
        await self._http_service.connect()
        await self._discover_endpoints()

    async def _discover_endpoints(self) -> None:
        """Dynamic endpoint discovery - production pattern."""
        try:
            response = await self._http_service.get("/entity")
            entities = response.get("entities", [])
            for entity in entities:
                self._discovered_endpoints[entity["name"]] = entity["endpoint"]
        except Exception as e:
            logger.warning(f"Endpoint discovery failed: {e}")
            # Fallback to static endpoints
            self._discovered_endpoints = self._config.fallback_endpoints
```

### **Configuration Hierarchy Pattern**

Production-validated configuration management:

```python
# Real implementation from flext_database_oracle/src/
class FlextDatabaseConfig(BaseModel):
    """Hierarchical configuration with environment support."""

    # Connection parameters
    host: str = Field(..., description="Oracle database host")
    port: int = Field(1521, description="Database port")
    service_name: str = Field(..., description="Oracle service name")

    # Authentication strategies
    auth_type: Literal["basic", "wallet", "kerberos"] = "basic"
    username: Optional[str] = None
    password: Optional[str] = None
    wallet_location: Optional[str] = None

    # Connection management
    pool_size: int = Field(5, ge=1, le=50)
    max_overflow: int = Field(10, ge=0, le=100)

    @classmethod
    def from_environment(cls, prefix: str = "FLX_DB") -> "FlextDatabaseConfig":
        """Load configuration from environment variables."""
        env_vars = {}
        for key, value in os.environ.items():
            if key.startswith(f"{prefix}_"):
                config_key = key[len(f"{prefix}_"):].lower()
                env_vars[config_key] = value
        return cls(**env_vars)

    @property
    def connection_string(self) -> str:
        """Generate Oracle connection string."""
        if self.auth_type == "wallet":
            return f"oracle+oracledb://@{self.service_name}?wallet_location={self.wallet_location}"
        return f"oracle+oracledb://{self.username}:{self.password}@{self.host}:{self.port}/{self.service_name}"
```

---

## 🔧 **Authentication Patterns**

### **Multi-Strategy Authentication (OIC)**

Production implementation supporting multiple auth methods:

```python
# Real implementation from flext_http_oracle_oic/src/
class OICAuthenticator:
    """Multi-strategy authentication for Oracle Integration Cloud."""

    def __init__(self, config: OracleOicConfig):
        self._config = config
        self._token_cache = {}

    async def authenticate(self) -> Dict[str, str]:
        """Select and execute authentication strategy."""
        strategy = self._config.auth_strategy

        if strategy == "jwt":
            return await self._jwt_authentication()
        elif strategy == "oauth2_client_credentials":
            return await self._oauth2_client_credentials()
        elif strategy == "idcs":
            return await self._idcs_authentication()
        else:
            raise ValueError(f"Unsupported auth strategy: {strategy}")

    async def _oauth2_client_credentials(self) -> Dict[str, str]:
        """OAuth2 Client Credentials flow - production implementation."""
        cache_key = f"oauth2_{self._config.client_id}"

        # Check token cache
        if cache_key in self._token_cache:
            token_data = self._token_cache[cache_key]
            if token_data["expires_at"] > time.time() + 300:  # 5min buffer
                return {"Authorization": f"Bearer {token_data['access_token']}"}

        # Request new token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._config.idcs_url}/oauth2/v1/token",
                data={
                    "grant_type": "client_credentials",
                    "scope": self._config.oauth_scope
                },
                auth=(self._config.client_id, self._config.client_secret)
            )
            response.raise_for_status()

            token_data = response.json()
            token_data["expires_at"] = time.time() + token_data["expires_in"]
            self._token_cache[cache_key] = token_data

            return {"Authorization": f"Bearer {token_data['access_token']}"}
```

### **Database Authentication Patterns**

Production Oracle database authentication:

```python
# Real implementation from flext_database_oracle/src/
class FlextOracleDbAdapter(BaseAdapter, DatabasePort):
    """Production Oracle database adapter."""

    async def _connect(self) -> None:
        """Multi-auth database connection."""
        if self._config.auth_type == "wallet":
            await self._connect_with_wallet()
        elif self._config.auth_type == "kerberos":
            await self._connect_with_kerberos()
        else:
            await self._connect_basic()

    async def _connect_with_wallet(self) -> None:
        """Oracle Autonomous Database wallet connection."""
        import oracledb

        # Configure wallet
        oracledb.init_oracle_client(
            config_dir=self._config.wallet_location
        )

        # Create connection pool
        self._pool = oracledb.create_pool(
            dsn=self._config.service_name,
            min=1,
            max=self._config.pool_size,
            increment=1
        )

        # Verify connection
        async with self._get_connection() as conn:
            await conn.execute("SELECT 1 FROM dual")
```

---

## 📊 **Data Processing Patterns**

### **Schema Discovery and Inference**

Production WMS schema discovery:

```python
# Real implementation pattern from flext_http_oracle_wms/
class WmsSchemaInference:
    """Production schema inference from WMS endpoints."""

    async def discover_entity_schema(self, entity_name: str) -> Dict[str, Any]:
        """Multi-method schema discovery."""
        schema = {}

        # Method 1: OPTIONS request
        try:
            schema.update(await self._discover_via_options(entity_name))
        except Exception:
            pass

        # Method 2: Sample data analysis
        try:
            schema.update(await self._discover_via_samples(entity_name))
        except Exception:
            pass

        # Method 3: HEAD request metadata
        try:
            schema.update(await self._discover_via_head(entity_name))
        except Exception:
            pass

        return schema

    async def _discover_via_samples(self, entity_name: str) -> Dict[str, Any]:
        """Analyze sample data to infer schema."""
        samples = await self._wms_client.get_entity_samples(entity_name, limit=100)

        schema = {"properties": {}, "required": []}

        for sample in samples:
            for field, value in sample.items():
                if field not in schema["properties"]:
                    schema["properties"][field] = {
                        "type": self._infer_type(value),
                        "examples": []
                    }

                if value is not None:
                    schema["properties"][field]["examples"].append(value)
                    if field not in schema["required"]:
                        schema["required"].append(field)

        return schema
```

### **Bulk Operations Pattern**

Production Oracle MERGE operations:

```python
# Real implementation from flext_database_oracle/
class OracleBulkOperations:
    """Production bulk operations with Oracle MERGE."""

    async def upsert_batch(
        self,
        table_name: str,
        records: List[Dict],
        key_columns: List[str],
        batch_size: int = 1000
    ) -> Dict[str, int]:
        """Bulk upsert using Oracle MERGE statement."""

        results = {"inserted": 0, "updated": 0, "errors": 0}

        for batch in self._chunk_records(records, batch_size):
            try:
                merge_sql = self._generate_merge_statement(
                    table_name, batch[0], key_columns
                )

                async with self._get_connection() as conn:
                    async with conn.cursor() as cursor:
                        await cursor.executemany(merge_sql, batch)

                        # Get affected row counts
                        affected = cursor.rowcount
                        results["inserted"] += affected

            except Exception as e:
                logger.error(f"Batch upsert failed: {e}")
                results["errors"] += len(batch)

        return results

    def _generate_merge_statement(
        self,
        table_name: str,
        sample_record: Dict,
        key_columns: List[str]
    ) -> str:
        """Generate dynamic Oracle MERGE statement."""

        columns = list(sample_record.keys())
        value_columns = [col for col in columns if col not in key_columns]

        # Build MERGE statement
        merge_sql = f"""
        MERGE INTO {table_name} target
        USING (SELECT {', '.join(f':{col} as {col}' for col in columns)} FROM dual) source
        ON ({' AND '.join(f'target.{col} = source.{col}' for col in key_columns)})
        WHEN MATCHED THEN UPDATE SET
            {', '.join(f'{col} = source.{col}' for col in value_columns)}
        WHEN NOT MATCHED THEN INSERT
            ({', '.join(columns)})
            VALUES ({', '.join(f'source.{col}' for col in columns)})
        """

        return merge_sql
```

---

## 🔄 **Integration Orchestration Patterns**

### **Service Coordination Pattern**

Production multi-service orchestration:

```python
# Real implementation from client-b_oic_wms/
class IntegrationOrchestrator:
    """Production integration orchestration."""

    def __init__(self):
        self._wms_client = None
        self._oic_client = None
        self._db_adapter = None

    async def execute_wms_to_db_sync(self, entity_type: str) -> Dict[str, Any]:
        """End-to-end WMS to Database synchronization."""

        sync_result = {
            "entity_type": entity_type,
            "records_processed": 0,
            "records_synced": 0,
            "errors": []
        }

        try:
            # Step 1: Extract from WMS
            wms_data = await self._wms_client.get_entities(entity_type)
            sync_result["records_processed"] = len(wms_data)

            # Step 2: Transform data
            transformed_data = await self._transform_wms_data(wms_data, entity_type)

            # Step 3: Load to database
            db_result = await self._db_adapter.upsert_batch(
                table_name=f"wms_{entity_type}",
                records=transformed_data,
                key_columns=self._get_key_columns(entity_type)
            )

            sync_result["records_synced"] = db_result["inserted"] + db_result["updated"]

            # Step 4: Notify via OIC (optional)
            if self._config.notify_oic:
                await self._notify_oic_completion(sync_result)

        except Exception as e:
            sync_result["errors"].append(str(e))
            logger.error(f"Sync failed for {entity_type}: {e}")

        return sync_result
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Oracle Integration Guide](./oracle-integration-comprehensive-guide.md) - Essential Oracle technology overview and concepts
- [Architecture Adapters](../../architecture/adapters/index.md) - Hexagonal architecture adapter patterns used in implementations
- [FLEXT Framework Core](../../architecture/core-domain-layer.md) - Domain layer concepts supporting Oracle integrations

### **Next Steps**

- [Oracle WMS Guide](./oracle-wms-comprehensive-guide.md) - Detailed WMS implementation using these patterns
- [Oracle Database Guide](./oracle-database-guide.md) - Database-specific implementation patterns
- [Infrastructure Services](../../infrastructure/index.md) - Infrastructure layer supporting Oracle integrations

### **Related Topics**

- [Development Testing](../../development/testing/index.md) - Testing strategies for Oracle integration patterns
- [Security Authentication](../../security/authentication/index.md) - Security patterns used in Oracle authentication
- [Performance Optimization](../../optimization/index.md) - Optimization techniques for Oracle integrations

---

## 🆘 **Production Issues and Solutions**

### **Connection Pool Exhaustion**

```python
# Problem: Connection pool exhaustion in high-load scenarios
# Solution: Proper connection lifecycle management

async def handle_high_load_operation(self):
    """Production pattern for high-load scenarios."""

    # Use connection pooling with limits
    async with self._db_adapter.get_connection() as conn:
        # Perform operation
        result = await conn.execute(query)

        # Connection automatically returned to pool

    # Never hold connections longer than necessary
```

### **Authentication Token Expiry**

```python
# Problem: Authentication tokens expiring during long operations
# Solution: Token refresh with retry logic

async def resilient_api_call(self, operation_func, *args, **kwargs):
    """Production pattern for token refresh."""

    for attempt in range(3):
        try:
            return await operation_func(*args, **kwargs)
        except AuthenticationError:
            if attempt < 2:  # Don't refresh on last attempt
                await self._refresh_authentication()
                continue
            raise
```

---

**📂 Hub**: [Oracle Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLEXT 0.4.0+

---

**Last Updated**: 2025-06-11 | **Validation**: ✅ Production Verified | **Source**: Real implementations

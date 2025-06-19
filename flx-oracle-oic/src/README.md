# ☁️ FLX Oracle OIC - Source Implementation

> **Module**: Oracle Integration Cloud (OIC) adapter source implementation with comprehensive API integration and artifact management | **Audience**: Integration Engineers, Oracle Cloud Architects, API Developers | **Status**: Production Ready

## 📋 **Overview**

Complete source implementation for Oracle Integration Cloud integration, providing comprehensive OIC API access, artifact management, authentication handling, and monitoring capabilities with multiple adapter patterns for different use cases.

---

## 🧭 **Navigation Context**

**🏠 Root**: [PyAuto Home](../../README.md) → **📂 Component**: [FLX Oracle OIC](../README.md) → **📂 Current**: Source Implementation

---

## 🎯 **Module Purpose**

This module implements comprehensive Oracle Integration Cloud integration patterns, providing multiple adapter implementations, robust authentication, artifact management, and monitoring capabilities for enterprise OIC environments.

### **Key Capabilities**

- **Multiple Adapter Patterns** - Legacy, modern, standalone, and dynamic adapters
- **Comprehensive Authentication** - OAuth2, IDCS, and basic authentication support
- **Artifact Management** - Complete OIC artifact lifecycle management
- **API Generation** - Dynamic API endpoint discovery and client generation
- **Monitoring & Progress** - Real-time operation monitoring and progress tracking
- **Configuration Management** - Flexible configuration with multiple patterns

---

## 📁 **Module Structure**

```
src/flx_oracle_oic/
├── __init__.py              # Public API exports
├── __main__.py              # CLI entry point
├── __version__.py           # Version information
├── adapter.py               # Legacy adapter implementation
├── adapter_modern.py        # Modern adapter with enhanced features
├── auth.py                  # Authentication management
├── cli.py                   # Command-line interface
├── client.py                # HTTP client implementation
├── client_modern.py         # Modern HTTP client
├── config.py                # Configuration management
├── config_modern.py         # Modern configuration patterns
├── constants.py             # OIC constants and endpoints
├── models.py                # Data models and schemas
├── monitoring.py            # Operation monitoring
├── progress.py              # Progress tracking utilities
├── api_declarative.py       # Declarative API definitions
├── api_generator.py         # Dynamic API client generation
├── dynamic_adapter.py       # Dynamic adapter implementation
├── simple_adapter.py        # Simplified adapter interface
├── standalone_adapter.py    # Standalone adapter (no FLX dependency)
├── standalone_client.py     # Standalone HTTP client
├── standalone_config.py     # Standalone configuration
└── dump_modules/            # OIC artifact dump utilities
    ├── __init__.py
    ├── artifacts.py         # Artifact management
    ├── base.py              # Base dump functionality
    ├── core_entities.py     # Core entity extraction
    └── system_REDACTED_LDAP_BIND_PASSWORD.py      # System REDACTED_LDAP_BIND_PASSWORDistration utilities
```

---

## 🔧 **Core Components**

### **1. Adapter Implementations**

#### **Legacy Adapter (adapter.py)**

Original adapter implementation:

```python
class FlxOracleOICAdapter:
    """Legacy Oracle OIC adapter implementation."""

    def __init__(self, config: OICConfig):
        self.config = config
        self.client = OICClient(config)

    async def get_integrations(self) -> List[Integration]:
        """Get all integrations from OIC."""

    async def get_integration_details(self, integration_id: str) -> IntegrationDetails:
        """Get detailed integration information."""

    async def activate_integration(self, integration_id: str) -> bool:
        """Activate integration in OIC."""

    async def deactivate_integration(self, integration_id: str) -> bool:
        """Deactivate integration in OIC."""
```

#### **Modern Adapter (adapter_modern.py)**

Enhanced adapter with advanced features:

```python
class ModernOICAdapter:
    """Modern OIC adapter with enhanced capabilities."""

    async def discover_endpoints(self) -> List[APIEndpoint]:
        """Discover all available API endpoints."""

    async def get_artifacts_by_type(self, artifact_type: ArtifactType) -> List[Artifact]:
        """Get artifacts filtered by type."""

    async def bulk_export_artifacts(
        self,
        artifact_ids: List[str],
        export_format: ExportFormat = ExportFormat.IAR
    ) -> ExportResult:
        """Bulk export artifacts in specified format."""

    async def monitor_integration_health(self, integration_id: str) -> HealthReport:
        """Monitor integration health and performance."""
```

#### **Standalone Adapter (standalone_adapter.py)**

Framework-independent adapter:

```python
class StandaloneOICAdapter:
    """Standalone OIC adapter without FLX dependencies."""

    def __init__(self, base_url: str, username: str, password: str):
        self.client = StandaloneOICClient(base_url, username, password)

    def get_integrations(self) -> List[Dict]:
        """Get integrations using synchronous calls."""

    def export_integration(self, integration_id: str, format: str = "IAR") -> bytes:
        """Export integration artifact."""

    def import_integration(self, iar_data: bytes) -> ImportResult:
        """Import integration from IAR data."""
```

### **2. Authentication Management (auth.py)**

Comprehensive authentication handling:

```python
class OICAuthManager:
    """OIC authentication management."""

    async def authenticate_oauth2(
        self,
        client_id: str,
        client_secret: str,
        scope: str
    ) -> OAuthToken:
        """Authenticate using OAuth2 flow."""

    async def authenticate_idcs(
        self,
        idcs_url: str,
        client_assertion: str
    ) -> IDCSToken:
        """Authenticate using IDCS (Identity Cloud Service)."""

    async def refresh_token(self, refresh_token: str) -> OAuthToken:
        """Refresh expired OAuth token."""

    async def validate_token(self, token: str) -> TokenValidation:
        """Validate token and get expiration info."""
```

### **3. HTTP Client Implementations**

#### **Modern Client (client_modern.py)**

Enhanced HTTP client with resilience:

```python
class ModernOICClient:
    """Modern HTTP client with circuit breaker and retry logic."""

    async def request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> ClientResponse:
        """Make HTTP request with comprehensive error handling."""

    async def get_paginated(
        self,
        endpoint: str,
        page_size: int = 100
    ) -> AsyncIterator[Dict]:
        """Get paginated results from OIC API."""

    async def upload_artifact(
        self,
        artifact_data: bytes,
        content_type: str
    ) -> UploadResult:
        """Upload artifact to OIC with progress tracking."""

    async def download_artifact(
        self,
        artifact_id: str,
        chunk_size: int = 8192
    ) -> AsyncIterator[bytes]:
        """Download artifact with streaming."""
```

### **4. Configuration Management**

#### **Modern Configuration (config_modern.py)**

Advanced configuration patterns:

```python
class ModernOICConfig(BaseSettings):
    """Modern OIC configuration with comprehensive validation."""

    # Connection settings
    base_url: HttpUrl
    username: str
    password: SecretStr

    # Authentication settings
    auth_type: AuthType = AuthType.BASIC
    oauth_client_id: Optional[str] = None
    oauth_client_secret: Optional[SecretStr] = None
    idcs_url: Optional[HttpUrl] = None

    # Performance settings
    request_timeout: int = Field(default=30, ge=1, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)
    circuit_breaker_threshold: int = Field(default=5, ge=1)

    # Monitoring settings
    enable_metrics: bool = True
    enable_tracing: bool = False
    log_level: str = "INFO"

    class Config:
        env_prefix = "OIC_"
        env_file = ".env"
```

### **5. API Generation (api_generator.py)**

Dynamic API client generation:

```python
class OICAPIGenerator:
    """Generate API clients from OIC OpenAPI specifications."""

    async def discover_api_specs(self) -> List[APISpec]:
        """Discover available API specifications."""

    async def generate_client_from_spec(
        self,
        spec: APISpec
    ) -> GeneratedClient:
        """Generate typed client from OpenAPI spec."""

    async def generate_models_from_spec(
        self,
        spec: APISpec
    ) -> List[GeneratedModel]:
        """Generate Pydantic models from API spec."""

    def save_generated_code(
        self,
        client: GeneratedClient,
        output_dir: Path
    ) -> None:
        """Save generated client code to files."""
```

### **6. Monitoring & Progress Tracking**

#### **Monitoring (monitoring.py)**

Comprehensive operation monitoring:

```python
class OICMonitor:
    """Monitor OIC operations and performance."""

    async def monitor_integration_performance(
        self,
        integration_id: str,
        duration: timedelta = timedelta(hours=1)
    ) -> PerformanceReport:
        """Monitor integration performance metrics."""

    async def monitor_api_health(self) -> APIHealthReport:
        """Monitor OIC API health and availability."""

    async def get_error_analytics(
        self,
        time_range: TimeRange
    ) -> ErrorAnalytics:
        """Analyze error patterns and trends."""

    async def track_resource_usage(self) -> ResourceUsage:
        """Track OIC resource utilization."""
```

#### **Progress Tracking (progress.py)**

Real-time progress tracking:

```python
class ProgressTracker:
    """Track progress of long-running operations."""

    def start_operation(self, operation_id: str, total_items: int) -> None:
        """Start tracking operation progress."""

    def update_progress(
        self,
        operation_id: str,
        completed_items: int,
        current_item: str = None
    ) -> None:
        """Update operation progress."""

    def complete_operation(
        self,
        operation_id: str,
        result: OperationResult
    ) -> None:
        """Mark operation as completed."""

    def get_progress_status(self, operation_id: str) -> ProgressStatus:
        """Get current progress status."""
```

---

## 🗂️ **Artifact Management (dump_modules/)**

### **Artifact Management (artifacts.py)**

Complete artifact lifecycle management:

```python
class ArtifactManager:
    """Manage OIC artifacts and their lifecycle."""

    async def export_artifact(
        self,
        artifact_id: str,
        format: ExportFormat
    ) -> ExportedArtifact:
        """Export single artifact."""

    async def import_artifact(
        self,
        artifact_data: bytes,
        options: ImportOptions
    ) -> ImportResult:
        """Import artifact into OIC."""

    async def bulk_export(
        self,
        filter_criteria: ArtifactFilter
    ) -> BulkExportResult:
        """Bulk export artifacts matching criteria."""

    async def compare_artifacts(
        self,
        source_id: str,
        target_id: str
    ) -> ArtifactComparison:
        """Compare two artifact versions."""
```

### **Core Entities (core_entities.py)**

Core OIC entity management:

```python
class CoreEntityManager:
    """Manage core OIC entities."""

    async def get_connections(self) -> List[Connection]:
        """Get all connection definitions."""

    async def get_integrations(self) -> List[Integration]:
        """Get all integration definitions."""

    async def get_packages(self) -> List[Package]:
        """Get all package definitions."""

    async def get_libraries(self) -> List[Library]:
        """Get all library definitions."""

    async def analyze_dependencies(
        self,
        artifact_id: str
    ) -> DependencyAnalysis:
        """Analyze artifact dependencies."""
```

### **System Administration (system_REDACTED_LDAP_BIND_PASSWORD.py)**

System REDACTED_LDAP_BIND_PASSWORDistration utilities:

```python
class SystemAdminTools:
    """System REDACTED_LDAP_BIND_PASSWORDistration tools for OIC."""

    async def get_system_health(self) -> SystemHealth:
        """Get overall system health status."""

    async def get_usage_metrics(
        self,
        time_range: TimeRange
    ) -> UsageMetrics:
        """Get system usage metrics."""

    async def manage_user_access(
        self,
        user_id: str,
        permissions: List[Permission]
    ) -> AccessResult:
        """Manage user access and permissions."""

    async def backup_configuration(self) -> BackupResult:
        """Backup OIC configuration."""
```

---

## 🔄 **Integration Workflows**

### **Complete Integration Export Workflow**

```python
async def export_integration_workflow(
    adapter: ModernOICAdapter,
    integration_id: str,
    include_dependencies: bool = True
) -> ExportResult:
    """Complete integration export workflow."""

    # 1. Get integration details
    integration = await adapter.get_integration_details(integration_id)

    # 2. Analyze dependencies if requested
    dependencies = []
    if include_dependencies:
        dep_analyzer = CoreEntityManager()
        dependency_analysis = await dep_analyzer.analyze_dependencies(integration_id)
        dependencies = dependency_analysis.required_artifacts

    # 3. Export main integration
    main_export = await adapter.export_artifact(
        integration_id,
        ExportFormat.IAR
    )

    # 4. Export dependencies
    dependency_exports = []
    for dep_id in dependencies:
        dep_export = await adapter.export_artifact(dep_id, ExportFormat.IAR)
        dependency_exports.append(dep_export)

    # 5. Package complete export
    return ExportResult(
        main_artifact=main_export,
        dependencies=dependency_exports,
        metadata=integration.metadata
    )
```

### **Monitoring Workflow**

```python
async def comprehensive_monitoring_workflow():
    """Comprehensive OIC monitoring workflow."""

    monitor = OICMonitor()

    while True:
        # 1. Check API health
        api_health = await monitor.monitor_api_health()

        # 2. Monitor active integrations
        active_integrations = await get_active_integrations()
        for integration in active_integrations:
            perf_report = await monitor.monitor_integration_performance(
                integration.id,
                duration=timedelta(minutes=15)
            )

            # Alert on performance issues
            if perf_report.error_rate > 0.05:  # 5% error rate threshold
                await send_alert(f"High error rate for {integration.name}")

        # 3. Analyze error patterns
        error_analytics = await monitor.get_error_analytics(
            TimeRange.last_hour()
        )

        # 4. Track resource usage
        resource_usage = await monitor.track_resource_usage()

        await asyncio.sleep(300)  # Monitor every 5 minutes
```

---

## 🧪 **Testing Strategies**

### **Adapter Testing**

```python
@pytest.mark.asyncio
async def test_modern_adapter_integration_retrieval():
    """Test modern adapter integration retrieval."""
    config = ModernOICConfig(
        base_url="https://test.oic.oraclecloud.com",
        username="test_user",
        password="test_password"
    )

    adapter = ModernOICAdapter(config)

    # Mock the HTTP response
    with aioresponses() as mock:
        mock.get(
            "https://test.oic.oraclecloud.com/ic/api/integration/v1/integrations",
            payload={"items": [{"id": "test-integration", "name": "Test Integration"}]}
        )

        integrations = await adapter.get_integrations()
        assert len(integrations) == 1
        assert integrations[0].id == "test-integration"
```

### **Authentication Testing**

```python
@pytest.mark.asyncio
async def test_oauth2_authentication():
    """Test OAuth2 authentication flow."""
    auth_manager = OICAuthManager()

    with aioresponses() as mock:
        mock.post(
            "https://idcs.oraclecloud.com/oauth2/v1/token",
            payload={
                "access_token": "test_token",
                "expires_in": 3600,
                "token_type": "Bearer"
            }
        )

        token = await auth_manager.authenticate_oauth2(
            client_id="test_client",
            client_secret="test_secret",
            scope="https://oic.oraclecloud.com/scope"
        )

        assert token.access_token == "test_token"
        assert token.expires_in == 3600
```

---

## 🔗 **Integration Patterns**

### **FLX Framework Integration**

```python
class OICPlugin:
    """FLX plugin for Oracle OIC integration."""

    def __init__(self, config: ModernOICConfig):
        self.config = config
        self.adapter = ModernOICAdapter(config)

    async def initialize(self) -> None:
        """Initialize OIC plugin."""
        await self.adapter.validate_connection()

    def get_integration_service(self) -> IntegrationService:
        """Get integration management service."""
        return IntegrationService(self.adapter)

    def get_monitoring_service(self) -> MonitoringService:
        """Get monitoring service."""
        return MonitoringService(self.adapter)
```

### **CLI Integration**

```bash
# Export integration
flx-oracle-oic export --integration-id INT_001 --format IAR --output integration.iar

# Import integration
flx-oracle-oic import --file integration.iar --environment PROD

# Monitor health
flx-oracle-oic monitor --integration-id INT_001 --duration 1h

# Generate API client
flx-oracle-oic generate-client --spec-url https://oic.com/api/spec --output-dir ./generated
```

---

## 🔗 **Cross-References**

### **Component Documentation**

- [Component Overview](../README.md) - Complete OIC component documentation
- [Configuration Guide](../docs/configuration.md) - OIC connection setup
- [API Reference](../docs/api/README.md) - Complete API documentation

### **Related Components**

- [TAP Oracle OIC](../../tap-oracle-oic/README.md) - OIC data extraction
- [Target Oracle OIC](../../target-oracle-oic/README.md) - OIC data loading
- [FLX HTTP Oracle OIC](../../flx-http-oracle-oic/README.md) - HTTP client

### **External References**

- [Oracle Integration Cloud Documentation](https://docs.oracle.com/en/cloud/paas/application-integration/) - OIC reference
- [OIC REST API Reference](https://docs.oracle.com/en/cloud/paas/integration-cloud/rest-api/) - API reference
- [Oracle Identity Cloud Service](https://docs.oracle.com/en/cloud/paas/identity-cloud/) - IDCS authentication

---

**📂 Module**: Source Implementation | **🏠 Component**: [FLX Oracle OIC](../README.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-19

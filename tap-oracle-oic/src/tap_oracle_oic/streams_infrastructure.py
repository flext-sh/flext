"""Oracle Integration Cloud - Infrastructure Streams.

Professional infrastructure streams providing comprehensive visibility into
OIC platform components, system health, adapters, and operational metadata.

Features:
- System health and status monitoring
- Adapter and agent management
- Platform configuration and capabilities
- Resource utilization and capacity
- Environment and deployment information
"""

from typing import Optional

from singer_sdk import typing as th

from .streams import OICBaseStream


class AdaptersStream(OICBaseStream):
    """OIC Adapters Stream.

    Provides comprehensive information about available adapters, their
    capabilities, versions, and configuration options.

    Features:
    - Complete adapter catalog
    - Capability and feature information
    - Version and compatibility data
    - Configuration schema and options
    - Usage statistics and adoption
    """

    name = "adapters"
    path = "/adapters"
    primary_keys = ["id"]
    replication_key = "lastUpdated"

    # Stream configuration
    api_category = "infrastructure"
    requires_design_api = True
    default_sort = "name:asc"

    schema = th.PropertiesList(
        # Core identification
        th.Property("id", th.StringType, description="Unique adapter identifier"),
        th.Property("name", th.StringType, description="Adapter name"),
        th.Property(
            "displayName", th.StringType, description="Human-readable display name"
        ),
        th.Property("description", th.StringType, description="Adapter description"),
        th.Property("vendor", th.StringType, description="Adapter vendor"),
        th.Property("category", th.StringType, description="Adapter category"),
        # Version and lifecycle
        th.Property("version", th.StringType, description="Current adapter version"),
        th.Property(
            "latestVersion", th.StringType, description="Latest available version"
        ),
        th.Property(
            "status",
            th.StringType,
            description="Adapter status (ACTIVE, DEPRECATED, PREVIEW)",
        ),
        th.Property("lifecycle", th.StringType, description="Lifecycle stage"),
        th.Property("supportLevel", th.StringType, description="Support level"),
        # Capabilities and features
        th.Property(
            "capabilities",
            th.ArrayType(th.StringType),
            description="Adapter capabilities (invoke, trigger, etc.)",
        ),
        th.Property(
            "features", th.ArrayType(th.StringType), description="Supported features"
        ),
        th.Property(
            "patterns",
            th.ArrayType(th.StringType),
            description="Supported integration patterns",
        ),
        th.Property(
            "protocols", th.ArrayType(th.StringType), description="Supported protocols"
        ),
        # Technical details
        th.Property("adapterType", th.StringType, description="Adapter type"),
        th.Property("runtime", th.StringType, description="Runtime environment"),
        th.Property("architecture", th.StringType, description="Architecture type"),
        th.Property("cloudNative", th.BooleanType, description="Cloud-native adapter"),
        # Agent and deployment
        th.Property(
            "agentRequired", th.BooleanType, description="Requires connectivity agent"
        ),
        th.Property(
            "agentSupported", th.BooleanType, description="Supports connectivity agent"
        ),
        th.Property(
            "cloudDeployment", th.BooleanType, description="Supports cloud deployment"
        ),
        th.Property(
            "onPremiseDeployment",
            th.BooleanType,
            description="Supports on-premise deployment",
        ),
        # Configuration and schema
        th.Property(
            "configurationProperties",
            th.ArrayType(
                th.ObjectType(
                    th.Property("name", th.StringType),
                    th.Property("type", th.StringType),
                    th.Property("required", th.BooleanType),
                    th.Property("description", th.StringType),
                    th.Property("defaultValue", th.StringType),
                )
            ),
            description="Configuration properties schema",
        ),
        th.Property(
            "securitySchemes",
            th.ArrayType(
                th.ObjectType(
                    th.Property("type", th.StringType),
                    th.Property("name", th.StringType),
                    th.Property("description", th.StringType),
                )
            ),
            description="Supported security schemes",
        ),
        # Usage and adoption
        th.Property(
            "connectionCount",
            th.IntegerType,
            description="Number of connections using this adapter",
        ),
        th.Property(
            "adoptionRate", th.NumberType, description="Adoption rate percentage"
        ),
        th.Property("popularityScore", th.NumberType, description="Popularity score"),
        # Documentation and resources
        th.Property("documentationUrl", th.StringType, description="Documentation URL"),
        th.Property("supportUrl", th.StringType, description="Support URL"),
        th.Property("iconUrl", th.StringType, description="Adapter icon URL"),
        th.Property("tags", th.ArrayType(th.StringType), description="Adapter tags"),
        # Metadata and timestamps
        th.Property("releaseDate", th.DateTimeType, description="Release date"),
        th.Property(
            "lastUpdated", th.DateTimeType, description="Last update timestamp"
        ),
        th.Property("endOfLife", th.DateTimeType, description="End of life date"),
        # Extraction metadata
        th.Property(
            "_tap_extracted_at", th.DateTimeType, description="Extraction timestamp"
        ),
        th.Property(
            "_tap_stream_name", th.StringType, description="Source stream name"
        ),
    ).to_dict()

    def additional_params(self, _context: Optional[dict[str, str]]) -> dict[str, str]:
        """Additional parameters for adapter queries."""
        params = {}

        # Include usage statistics
        if self.config.get("include_usage_stats", True):
            params["includeUsage"] = "true"

        # Filter by category
        category_filter = self.config.get("adapter_categories")
        if category_filter:
            params["category"] = ",".join(category_filter)

        # Filter by vendor
        vendor_filter = self.config.get("adapter_vendors")
        if vendor_filter:
            params["vendor"] = ",".join(vendor_filter)

        return params


class AgentGroupsStream(OICBaseStream):
    """Connectivity Agent Groups Stream.

    Provides information about connectivity agent groups, their configuration,
    status, and associated connections.

    Features:
    - Agent group configuration and status
    - Agent health and connectivity
    - Load balancing and high availability
    - Associated connections and usage
    """

    name = "agent_groups"
    path = "/agentGroups"
    primary_keys = ["id"]
    replication_key = "lastUpdated"

    # Stream configuration
    api_category = "infrastructure"
    requires_design_api = True
    default_sort = "name:asc"

    schema = th.PropertiesList(
        # Core identification
        th.Property("id", th.StringType, description="Unique agent group identifier"),
        th.Property("name", th.StringType, description="Agent group name"),
        th.Property(
            "description", th.StringType, description="Agent group description"
        ),
        th.Property("displayName", th.StringType, description="Display name"),
        # Status and health
        th.Property(
            "status",
            th.StringType,
            description="Agent group status (ACTIVE, INACTIVE, ERROR)",
        ),
        th.Property(
            "health",
            th.StringType,
            description="Health status (HEALTHY, DEGRADED, UNHEALTHY)",
        ),
        th.Property(
            "lastHealthCheck",
            th.DateTimeType,
            description="Last health check timestamp",
        ),
        th.Property("connected", th.BooleanType, description="Connected status"),
        # Configuration
        th.Property("type", th.StringType, description="Agent group type"),
        th.Property("version", th.StringType, description="Agent version"),
        th.Property(
            "environment",
            th.StringType,
            description="Environment (PRODUCTION, TEST, DEV)",
        ),
        th.Property("region", th.StringType, description="Geographic region"),
        # Agents in group
        th.Property(
            "agentCount", th.IntegerType, description="Number of agents in group"
        ),
        th.Property(
            "activeAgentCount", th.IntegerType, description="Number of active agents"
        ),
        th.Property(
            "agents",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.StringType),
                    th.Property("name", th.StringType),
                    th.Property("status", th.StringType),
                    th.Property("version", th.StringType),
                    th.Property("lastSeen", th.DateTimeType),
                )
            ),
            description="Individual agents in the group",
        ),
        # Load balancing and high availability
        th.Property(
            "loadBalancing", th.BooleanType, description="Load balancing enabled"
        ),
        th.Property(
            "highAvailability",
            th.BooleanType,
            description="High availability configured",
        ),
        th.Property("failoverEnabled", th.BooleanType, description="Failover enabled"),
        th.Property(
            "loadBalancingAlgorithm",
            th.StringType,
            description="Load balancing algorithm",
        ),
        # Usage and connections
        th.Property(
            "connectionCount",
            th.IntegerType,
            description="Number of associated connections",
        ),
        th.Property(
            "connections",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.StringType),
                    th.Property("name", th.StringType),
                    th.Property("adapterType", th.StringType),
                )
            ),
            description="Associated connections",
        ),
        # Security and access
        th.Property(
            "allowedIpRanges",
            th.ArrayType(th.StringType),
            description="Allowed IP ranges",
        ),
        th.Property("sslEnabled", th.BooleanType, description="SSL/TLS enabled"),
        th.Property(
            "certificateId", th.StringType, description="SSL certificate identifier"
        ),
        # Metadata and timestamps
        th.Property("created", th.DateTimeType, description="Creation timestamp"),
        th.Property(
            "lastUpdated", th.DateTimeType, description="Last update timestamp"
        ),
        th.Property("createdBy", th.StringType, description="Created by user"),
        th.Property("lastUpdatedBy", th.StringType, description="Last updated by user"),
        # Extraction metadata
        th.Property(
            "_tap_extracted_at", th.DateTimeType, description="Extraction timestamp"
        ),
        th.Property(
            "_tap_stream_name", th.StringType, description="Source stream name"
        ),
    ).to_dict()

    def additional_params(self, _context: Optional[dict[str, str]]) -> dict[str, str]:
        """Additional parameters for agent group queries."""
        params = {}

        # Include agent details
        if self.config.get("include_agent_details", True):
            params["includeAgents"] = "true"

        # Include connection information
        if self.config.get("include_connections", True):
            params["includeConnections"] = "true"

        # Filter by status
        status_filter = self.config.get("agent_status_filter")
        if status_filter:
            params["status"] = status_filter

        return params

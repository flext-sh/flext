"""Oracle Integration Cloud - Monitoring Streams.

Professional monitoring streams providing comprehensive visibility into
integration execution, performance metrics, errors, and operational health.

Features:
- Real-time execution monitoring
- Performance metrics and KPIs
- Error tracking and analysis
- Audit trail and compliance
- Resource utilization monitoring
"""

from typing import Any, Optional

from singer_sdk import typing as th

from .streams import OICBaseStream


class ExecutionsStream(OICBaseStream):
    """Integration Executions Stream.

    Provides comprehensive execution history with performance metrics,
    status tracking, and detailed runtime information.

    Features:
    - Complete execution history with filtering
    - Performance metrics and timing data
    - Error details and recovery information
    - Business data tracking and correlation
    - Incremental extraction based on execution time
    """

    name = "executions"
    path = "/monitoring/executions"
    primary_keys = ["executionId"]
    replication_key = "startTime"

    # Stream configuration
    api_category = "monitoring"
    requires_runtime_api = True
    default_sort = "startTime:desc"
    default_expand = "errorDetails,businessData"

    schema = th.PropertiesList(
        # Core identification
        th.Property(
            "executionId", th.StringType, description="Unique execution identifier"
        ),
        th.Property(
            "integrationId", th.StringType, description="Associated integration ID"
        ),
        th.Property("integrationName", th.StringType, description="Integration name"),
        th.Property(
            "integrationVersion", th.StringType, description="Integration version"
        ),
        th.Property("instanceId", th.StringType, description="Instance identifier"),
        th.Property("flowId", th.StringType, description="Flow identifier"),
        # Execution status
        th.Property(
            "status",
            th.StringType,
            description="Execution status (SUCCEEDED, FAILED, IN_PROGRESS, ABORTED)",
        ),
        th.Property("statusMessage", th.StringType, description="Status description"),
        th.Property(
            "percentComplete", th.IntegerType, description="Completion percentage"
        ),
        th.Property("state", th.StringType, description="Detailed execution state"),
        # Timing information
        th.Property(
            "startTime", th.DateTimeType, description="Execution start timestamp"
        ),
        th.Property("endTime", th.DateTimeType, description="Execution end timestamp"),
        th.Property("duration", th.IntegerType, description="Duration in milliseconds"),
        th.Property(
            "queueTime", th.IntegerType, description="Time spent in queue (ms)"
        ),
        th.Property(
            "processingTime", th.IntegerType, description="Processing time (ms)"
        ),
        # Business data and tracking
        th.Property(
            "businessIdentifier",
            th.StringType,
            description="Business tracking identifier",
        ),
        th.Property(
            "trackingVariables",
            th.ArrayType(
                th.ObjectType(
                    th.Property("name", th.StringType),
                    th.Property("value", th.StringType),
                    th.Property("type", th.StringType),
                )
            ),
            description="Business tracking variables",
        ),
        th.Property(
            "correlationId",
            th.StringType,
            description="Correlation identifier for related executions",
        ),
        th.Property(
            "parentExecutionId",
            th.StringType,
            description="Parent execution ID for sub-flows",
        ),
        # Error information
        th.Property("errorCode", th.StringType, description="Error code if failed"),
        th.Property("errorMessage", th.StringType, description="Error message"),
        th.Property(
            "errorDetails", th.ObjectType(), description="Detailed error information"
        ),
        th.Property("errorCategory", th.StringType, description="Error category"),
        th.Property(
            "retryCount", th.IntegerType, description="Number of retry attempts"
        ),
        th.Property(
            "recoverable", th.BooleanType, description="Whether error is recoverable"
        ),
        # Trigger and source information
        th.Property(
            "triggerType",
            th.StringType,
            description="Trigger type (SCHEDULED, REST, SOAP, EVENT)",
        ),
        th.Property("triggerName", th.StringType, description="Trigger endpoint name"),
        th.Property(
            "sourceApplication", th.StringType, description="Source application"
        ),
        th.Property("sourceIpAddress", th.StringType, description="Source IP address"),
        th.Property(
            "invokedBy", th.StringType, description="User or system that triggered"
        ),
        # Performance metrics
        th.Property(
            "messageCount", th.IntegerType, description="Number of messages processed"
        ),
        th.Property(
            "recordCount", th.IntegerType, description="Number of records processed"
        ),
        th.Property("bytesSent", th.IntegerType, description="Bytes sent"),
        th.Property("bytesReceived", th.IntegerType, description="Bytes received"),
        th.Property("cpuTime", th.IntegerType, description="CPU time consumed (ms)"),
        th.Property("memoryUsage", th.IntegerType, description="Memory usage (bytes)"),
        # Activities and milestones
        th.Property(
            "activities",
            th.ArrayType(
                th.ObjectType(
                    th.Property("activityId", th.StringType),
                    th.Property("name", th.StringType),
                    th.Property("type", th.StringType),
                    th.Property("status", th.StringType),
                    th.Property("startTime", th.DateTimeType),
                    th.Property("endTime", th.DateTimeType),
                    th.Property("duration", th.IntegerType),
                )
            ),
            description="Execution activities and milestones",
        ),
        # Instance and environment
        th.Property("instanceName", th.StringType, description="OIC instance name"),
        th.Property(
            "environment",
            th.StringType,
            description="Environment (PRODUCTION, TEST, DEV)",
        ),
        th.Property("region", th.StringType, description="Geographic region"),
        # Extraction metadata
        th.Property(
            "_tap_extracted_at", th.DateTimeType, description="Extraction timestamp"
        ),
        th.Property(
            "_tap_stream_name", th.StringType, description="Source stream name"
        ),
    ).to_dict()

    def additional_params(self, context: Optional[dict[str, Any]]) -> dict[str, Any]:
        """Additional parameters for execution queries."""
        params = {}

        # Time range filtering
        time_range = self.config.get("execution_time_range", "24h")
        params["timeRange"] = time_range

        # Status filtering
        status_filter = self.config.get("execution_status_filter")
        if status_filter:
            params["status"] = (
                ",".join(status_filter)
                if isinstance(status_filter, list)
                else status_filter
            )

        # Integration filtering
        integration_filter = self.config.get("integration_id_filter")
        if integration_filter:
            params["integrationId"] = integration_filter

        # Include sub-executions
        if self.config.get("include_sub_executions", True):
            params["includeSubExecutions"] = "true"

        # Include activity details
        if self.config.get("include_activity_details", False):
            params["includeActivities"] = "true"

        return params


class MetricsStream(OICBaseStream):
    """Integration Metrics Stream.

    Provides aggregated performance metrics, KPIs, and statistical data
    for integrations, including success rates, throughput, and latency.

    Features:
    - Real-time and historical metrics
    - Aggregated KPIs and statistics
    - Performance trending data
    - Resource utilization metrics
    - SLA compliance tracking
    """

    name = "metrics"
    path = "/monitoring/metrics"
    primary_keys = ["metricId", "timestamp"]
    replication_key = "timestamp"

    # Stream configuration
    api_category = "monitoring"
    requires_runtime_api = True
    default_sort = "timestamp:desc"

    schema = th.PropertiesList(
        # Metric identification
        th.Property("metricId", th.StringType, description="Unique metric identifier"),
        th.Property("metricName", th.StringType, description="Metric name"),
        th.Property(
            "metricType",
            th.StringType,
            description="Metric type (GAUGE, COUNTER, HISTOGRAM)",
        ),
        th.Property("category", th.StringType, description="Metric category"),
        # Resource information
        th.Property(
            "integrationId", th.StringType, description="Associated integration ID"
        ),
        th.Property("integrationName", th.StringType, description="Integration name"),
        th.Property(
            "resourceType", th.StringType, description="Resource type being measured"
        ),
        th.Property("resourceId", th.StringType, description="Resource identifier"),
        # Time information
        th.Property("timestamp", th.DateTimeType, description="Metric timestamp"),
        th.Property(
            "period", th.StringType, description="Aggregation period (1m, 5m, 1h, 1d)"
        ),
        th.Property("startTime", th.DateTimeType, description="Period start time"),
        th.Property("endTime", th.DateTimeType, description="Period end time"),
        # Metric values
        th.Property("value", th.NumberType, description="Metric value"),
        th.Property("count", th.IntegerType, description="Sample count"),
        th.Property("sum", th.NumberType, description="Sum of values"),
        th.Property("avg", th.NumberType, description="Average value"),
        th.Property("min", th.NumberType, description="Minimum value"),
        th.Property("max", th.NumberType, description="Maximum value"),
        th.Property("stdDev", th.NumberType, description="Standard deviation"),
        # Performance metrics
        th.Property(
            "successRate", th.NumberType, description="Success rate percentage"
        ),
        th.Property("errorRate", th.NumberType, description="Error rate percentage"),
        th.Property("throughput", th.NumberType, description="Messages per second"),
        th.Property(
            "avgResponseTime", th.NumberType, description="Average response time (ms)"
        ),
        th.Property(
            "p50ResponseTime",
            th.NumberType,
            description="50th percentile response time",
        ),
        th.Property(
            "p95ResponseTime",
            th.NumberType,
            description="95th percentile response time",
        ),
        th.Property(
            "p99ResponseTime",
            th.NumberType,
            description="99th percentile response time",
        ),
        # Resource utilization
        th.Property("cpuUsage", th.NumberType, description="CPU usage percentage"),
        th.Property(
            "memoryUsage", th.NumberType, description="Memory usage percentage"
        ),
        th.Property("diskUsage", th.NumberType, description="Disk usage percentage"),
        th.Property(
            "networkIn", th.NumberType, description="Network ingress (bytes/sec)"
        ),
        th.Property(
            "networkOut", th.NumberType, description="Network egress (bytes/sec)"
        ),
        # SLA and compliance
        th.Property("slaStatus", th.StringType, description="SLA compliance status"),
        th.Property("slaTarget", th.NumberType, description="SLA target value"),
        th.Property("slaActual", th.NumberType, description="Actual SLA value"),
        th.Property(
            "slaBreaches", th.IntegerType, description="Number of SLA breaches"
        ),
        # Metadata
        th.Property("tags", th.ArrayType(th.StringType), description="Metric tags"),
        th.Property("dimensions", th.ObjectType(), description="Additional dimensions"),
        th.Property("unit", th.StringType, description="Measurement unit"),
        # Extraction metadata
        th.Property(
            "_tap_extracted_at", th.DateTimeType, description="Extraction timestamp"
        ),
        th.Property(
            "_tap_stream_name", th.StringType, description="Source stream name"
        ),
    ).to_dict()

    def additional_params(self, context: Optional[dict[str, Any]]) -> dict[str, Any]:
        """Additional parameters for metrics queries."""
        params = {}

        # Time range
        time_range = self.config.get("metrics_time_range", "1h")
        params["timeRange"] = time_range

        # Aggregation period
        period = self.config.get("metrics_period", "5m")
        params["period"] = period

        # Metric types
        metric_types = self.config.get("metric_types")
        if metric_types:
            params["metricType"] = (
                ",".join(metric_types)
                if isinstance(metric_types, list)
                else metric_types
            )

        # Resource filtering
        resource_filter = self.config.get("resource_filter")
        if resource_filter:
            params["resourceId"] = resource_filter

        return params


class ErrorsStream(OICBaseStream):
    """Integration Errors Stream.

    Provides detailed error tracking, analysis, and recovery information
    for failed integrations and system errors.

    Features:
    - Comprehensive error details
    - Error categorization and analysis
    - Recovery and retry information
    - Root cause analysis data
    - Error trends and patterns
    """

    name = "errors"
    path = "/monitoring/errors"
    primary_keys = ["errorId"]
    replication_key = "timestamp"

    # Stream configuration
    api_category = "monitoring"
    requires_runtime_api = True
    default_sort = "timestamp:desc"

    schema = th.PropertiesList(
        # Error identification
        th.Property("errorId", th.StringType, description="Unique error identifier"),
        th.Property(
            "executionId", th.StringType, description="Associated execution ID"
        ),
        th.Property(
            "integrationId", th.StringType, description="Associated integration ID"
        ),
        th.Property("integrationName", th.StringType, description="Integration name"),
        th.Property(
            "activityId", th.StringType, description="Activity where error occurred"
        ),
        th.Property("activityName", th.StringType, description="Activity name"),
        # Error details
        th.Property("errorCode", th.StringType, description="Error code"),
        th.Property("errorMessage", th.StringType, description="Error message"),
        th.Property(
            "errorCategory",
            th.StringType,
            description="Error category (SYSTEM, BUSINESS, CONNECTIVITY)",
        ),
        th.Property("errorType", th.StringType, description="Error type"),
        th.Property(
            "severity",
            th.StringType,
            description="Error severity (CRITICAL, HIGH, MEDIUM, LOW)",
        ),
        # Timing and context
        th.Property(
            "timestamp", th.DateTimeType, description="Error occurrence timestamp"
        ),
        th.Property(
            "environment", th.StringType, description="Environment where error occurred"
        ),
        th.Property("region", th.StringType, description="Geographic region"),
        # Technical details
        th.Property("stackTrace", th.StringType, description="Full stack trace"),
        th.Property("rootCause", th.StringType, description="Root cause analysis"),
        th.Property("correlationId", th.StringType, description="Error correlation ID"),
        th.Property(
            "transactionId", th.StringType, description="Transaction identifier"
        ),
        # Recovery information
        th.Property(
            "recoverable", th.BooleanType, description="Whether error is recoverable"
        ),
        th.Property(
            "retryable", th.BooleanType, description="Whether operation can be retried"
        ),
        th.Property(
            "retryCount", th.IntegerType, description="Number of retry attempts"
        ),
        th.Property(
            "maxRetries", th.IntegerType, description="Maximum retry attempts allowed"
        ),
        th.Property(
            "nextRetryTime", th.DateTimeType, description="Next scheduled retry"
        ),
        th.Property(
            "recoveryAction", th.StringType, description="Recommended recovery action"
        ),
        # Impact and affected resources
        th.Property("impactLevel", th.StringType, description="Business impact level"),
        th.Property(
            "affectedRecords", th.IntegerType, description="Number of affected records"
        ),
        th.Property(
            "affectedSystems",
            th.ArrayType(th.StringType),
            description="List of affected systems",
        ),
        # Diagnostic information
        th.Property(
            "diagnosticData",
            th.ObjectType(),
            description="Additional diagnostic information",
        ),
        th.Property("contextData", th.ObjectType(), description="Error context data"),
        # Resolution
        th.Property("resolved", th.BooleanType, description="Resolution status"),
        th.Property("resolvedAt", th.DateTimeType, description="Resolution timestamp"),
        th.Property("resolvedBy", th.StringType, description="User who resolved"),
        th.Property("resolutionNotes", th.StringType, description="Resolution notes"),
        # Extraction metadata
        th.Property(
            "_tap_extracted_at", th.DateTimeType, description="Extraction timestamp"
        ),
        th.Property(
            "_tap_stream_name", th.StringType, description="Source stream name"
        ),
    ).to_dict()

    def additional_params(self, context: Optional[dict[str, Any]]) -> dict[str, Any]:
        """Additional parameters for error queries."""
        params = {}

        # Time range
        time_range = self.config.get("error_time_range", "24h")
        params["timeRange"] = time_range

        # Severity filtering
        severity_filter = self.config.get("error_severity_filter")
        if severity_filter:
            params["severity"] = (
                ",".join(severity_filter)
                if isinstance(severity_filter, list)
                else severity_filter
            )

        # Category filtering
        category_filter = self.config.get("error_category_filter")
        if category_filter:
            params["category"] = category_filter

        # Include resolved errors
        if self.config.get("include_resolved_errors", False):
            params["includeResolved"] = "true"

        return params


class AuditEventsStream(OICBaseStream):
    """Audit Events Stream.

    Provides comprehensive audit trail for compliance, security monitoring,
    and operational tracking.

    Features:
    - Complete audit trail
    - Security event tracking
    - Configuration change history
    - User activity monitoring
    - Compliance reporting data
    """

    name = "audit_events"
    path = "/monitoring/audit"
    primary_keys = ["auditId"]
    replication_key = "timestamp"

    # Stream configuration
    api_category = "monitoring"
    requires_runtime_api = True
    default_sort = "timestamp:desc"

    schema = th.PropertiesList(
        # Event identification
        th.Property(
            "auditId", th.StringType, description="Unique audit event identifier"
        ),
        th.Property("eventType", th.StringType, description="Audit event type"),
        th.Property(
            "eventCategory",
            th.StringType,
            description="Event category (SECURITY, CONFIGURATION, OPERATION)",
        ),
        th.Property("eventName", th.StringType, description="Event name"),
        # Timing and session
        th.Property("timestamp", th.DateTimeType, description="Event timestamp"),
        th.Property("sessionId", th.StringType, description="User session identifier"),
        th.Property("requestId", th.StringType, description="Request identifier"),
        # User and authentication
        th.Property("userId", th.StringType, description="User identifier"),
        th.Property("userName", th.StringType, description="User name"),
        th.Property("userEmail", th.StringType, description="User email"),
        th.Property("userRole", th.StringType, description="User role"),
        th.Property("authMethod", th.StringType, description="Authentication method"),
        th.Property("sourceIp", th.StringType, description="Source IP address"),
        th.Property("userAgent", th.StringType, description="User agent string"),
        # Resource information
        th.Property(
            "resourceType", th.StringType, description="Affected resource type"
        ),
        th.Property("resourceId", th.StringType, description="Affected resource ID"),
        th.Property(
            "resourceName", th.StringType, description="Affected resource name"
        ),
        th.Property(
            "action",
            th.StringType,
            description="Action performed (CREATE, UPDATE, DELETE, READ)",
        ),
        # Change details
        th.Property(
            "changes",
            th.ArrayType(
                th.ObjectType(
                    th.Property("field", th.StringType),
                    th.Property("oldValue", th.StringType),
                    th.Property("newValue", th.StringType),
                )
            ),
            description="List of changes made",
        ),
        th.Property(
            "changeDescription", th.StringType, description="Description of changes"
        ),
        # Status and outcome
        th.Property(
            "status", th.StringType, description="Event status (SUCCESS, FAILURE)"
        ),
        th.Property("statusCode", th.IntegerType, description="Status code"),
        th.Property(
            "errorMessage", th.StringType, description="Error message if failed"
        ),
        # Security and compliance
        th.Property(
            "riskLevel", th.StringType, description="Risk level (HIGH, MEDIUM, LOW)"
        ),
        th.Property(
            "complianceFlags",
            th.ArrayType(th.StringType),
            description="Compliance flags",
        ),
        th.Property(
            "securityContext",
            th.ObjectType(),
            description="Security context information",
        ),
        # Additional metadata
        th.Property("environment", th.StringType, description="Environment"),
        th.Property("region", th.StringType, description="Geographic region"),
        th.Property("tags", th.ArrayType(th.StringType), description="Event tags"),
        th.Property("metadata", th.ObjectType(), description="Additional metadata"),
        # Extraction metadata
        th.Property(
            "_tap_extracted_at", th.DateTimeType, description="Extraction timestamp"
        ),
        th.Property(
            "_tap_stream_name", th.StringType, description="Source stream name"
        ),
    ).to_dict()

    def additional_params(self, context: Optional[dict[str, Any]]) -> dict[str, Any]:
        """Additional parameters for audit queries."""
        params = {}

        # Time range
        time_range = self.config.get("audit_time_range", "7d")
        params["timeRange"] = time_range

        # Event type filtering
        event_types = self.config.get("audit_event_types")
        if event_types:
            params["eventType"] = (
                ",".join(event_types) if isinstance(event_types, list) else event_types
            )

        # User filtering
        user_filter = self.config.get("audit_user_filter")
        if user_filter:
            params["userId"] = user_filter

        # Resource filtering
        resource_filter = self.config.get("audit_resource_filter")
        if resource_filter:
            params["resourceId"] = resource_filter

        return params


class InstancesStream(OICBaseStream):
    """OIC Instances Stream.

    Provides information about OIC instances, their configuration,
    capacity, and operational status.

    Features:
    - Instance configuration and metadata
    - Capacity and resource limits
    - Feature availability
    - Health and status information
    """

    name = "instances"
    path = "/monitoring/instances"
    primary_keys = ["instanceId"]
    replication_key = "lastUpdated"

    # Stream configuration
    api_category = "monitoring"
    requires_runtime_api = True

    schema = th.PropertiesList(
        # Instance identification
        th.Property("instanceId", th.StringType, description="Instance identifier"),
        th.Property("instanceName", th.StringType, description="Instance name"),
        th.Property("displayName", th.StringType, description="Display name"),
        th.Property("description", th.StringType, description="Instance description"),
        # Configuration
        th.Property("version", th.StringType, description="OIC version"),
        th.Property(
            "edition", th.StringType, description="OIC edition (STANDARD, ENTERPRISE)"
        ),
        th.Property("environment", th.StringType, description="Environment type"),
        th.Property("region", th.StringType, description="Geographic region"),
        th.Property(
            "availabilityDomain", th.StringType, description="Availability domain"
        ),
        # Status and health
        th.Property("status", th.StringType, description="Instance status"),
        th.Property("lifecycleState", th.StringType, description="Lifecycle state"),
        th.Property("healthStatus", th.StringType, description="Health status"),
        th.Property(
            "lastHealthCheck", th.DateTimeType, description="Last health check"
        ),
        # Capacity and limits
        th.Property(
            "messagePacksPerHour",
            th.IntegerType,
            description="Message packs per hour limit",
        ),
        th.Property(
            "messagePacksUsed", th.IntegerType, description="Message packs used"
        ),
        th.Property("storageLimit", th.IntegerType, description="Storage limit (GB)"),
        th.Property("storageUsed", th.IntegerType, description="Storage used (GB)"),
        th.Property("connectionLimit", th.IntegerType, description="Connection limit"),
        th.Property("connectionsUsed", th.IntegerType, description="Connections used"),
        # Features and capabilities
        th.Property(
            "enabledFeatures",
            th.ArrayType(th.StringType),
            description="Enabled features",
        ),
        th.Property(
            "availableAdapters",
            th.ArrayType(th.StringType),
            description="Available adapters",
        ),
        th.Property(
            "fileServerEnabled", th.BooleanType, description="File server enabled"
        ),
        th.Property(
            "visualBuilderEnabled", th.BooleanType, description="Visual Builder enabled"
        ),
        th.Property(
            "processEnabled", th.BooleanType, description="Process automation enabled"
        ),
        # Network and security
        th.Property(
            "networkEndpointType", th.StringType, description="Network endpoint type"
        ),
        th.Property(
            "allowedIpRanges",
            th.ArrayType(th.StringType),
            description="Allowed IP ranges",
        ),
        th.Property("customEndpoint", th.StringType, description="Custom endpoint URL"),
        th.Property("idcsUrl", th.StringType, description="IDCS URL"),
        # Timestamps
        th.Property("created", th.DateTimeType, description="Creation timestamp"),
        th.Property(
            "lastUpdated", th.DateTimeType, description="Last update timestamp"
        ),
        th.Property(
            "lastActivity", th.DateTimeType, description="Last activity timestamp"
        ),
        # Extraction metadata
        th.Property(
            "_tap_extracted_at", th.DateTimeType, description="Extraction timestamp"
        ),
        th.Property(
            "_tap_stream_name", th.StringType, description="Source stream name"
        ),
    ).to_dict()

"""Oracle Integration Cloud - Extended Streams.

Professional extended streams providing comprehensive coverage of
additional OIC entities including projects, schedules, and business objects.

Features:
- Project and folder organization
- Schedule management and monitoring
- Business event tracking
- Import/export operations
- Advanced configuration management
"""

from typing import Any, Optional

from singer_sdk import typing as th

from .streams import OICBaseStream


class ProjectsStream(OICBaseStream):
    """Projects Stream.

    Provides comprehensive project management data including folder structure,
    permissions, and resource organization.

    Features:
    - Project hierarchy and organization
    - Folder structure and navigation
    - Access control and permissions
    - Resource grouping and tagging
    """

    name = "projects"
    path = "/projects"
    primary_keys = ["id"]
    replication_key = "lastUpdated"

    # Stream configuration
    api_category = "core"
    requires_design_api = True
    default_sort = "name:asc"
    default_expand = "folders,permissions"

    schema = th.PropertiesList(
        # Core identification
        th.Property("id", th.StringType, description="Project identifier"),
        th.Property("name", th.StringType, description="Project name"),
        th.Property("description", th.StringType, description="Project description"),
        th.Property("code", th.StringType, description="Project code"),
        # Organization
        th.Property("parentId", th.StringType, description="Parent project ID"),
        th.Property("path", th.StringType, description="Full project path"),
        th.Property("level", th.IntegerType, description="Hierarchy level"),
        th.Property("isDefault", th.BooleanType, description="Default project flag"),
        # Status and lifecycle
        th.Property("status", th.StringType, description="Project status"),
        th.Property("locked", th.BooleanType, description="Edit lock status"),
        th.Property("archived", th.BooleanType, description="Archive status"),
        # Folders and structure
        th.Property(
            "folders",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.StringType),
                    th.Property("name", th.StringType),
                    th.Property("type", th.StringType),
                    th.Property("itemCount", th.IntegerType),
                )
            ),
            description="Project folders",
        ),
        # Resource counts
        th.Property(
            "integrationCount", th.IntegerType, description="Number of integrations"
        ),
        th.Property(
            "connectionCount", th.IntegerType, description="Number of connections"
        ),
        th.Property("lookupCount", th.IntegerType, description="Number of lookups"),
        th.Property("libraryCount", th.IntegerType, description="Number of libraries"),
        # Permissions and access
        th.Property(
            "permissions",
            th.ArrayType(
                th.ObjectType(
                    th.Property("userId", th.StringType),
                    th.Property("role", th.StringType),
                    th.Property("permissions", th.ArrayType(th.StringType)),
                )
            ),
            description="Project permissions",
        ),
        th.Property("owner", th.StringType, description="Project owner"),
        th.Property("visibility", th.StringType, description="Visibility level"),
        # Metadata
        th.Property("tags", th.ArrayType(th.StringType), description="Project tags"),
        th.Property("properties", th.ObjectType(), description="Custom properties"),
        # Timestamps
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

    def additional_params(self, context: Optional[dict[str, Any]]) -> dict[str, Any]:
        """Additional parameters for project queries."""
        params = {}

        # Include folder details
        if self.config.get("include_folder_details", True):
            params["includeFolders"] = "true"

        # Include resource counts
        if self.config.get("include_resource_counts", True):
            params["includeResourceCounts"] = "true"

        return params


class SchedulesStream(OICBaseStream):
    """Schedules Stream.

    Provides comprehensive schedule management data for scheduled integrations,
    including execution windows, frequencies, and calendar configurations.

    Features:
    - Schedule configurations and patterns
    - Execution windows and blackouts
    - Calendar and timezone management
    - Next run calculations
    - Schedule monitoring and health
    """

    name = "schedules"
    path = "/schedules"
    primary_keys = ["id"]
    replication_key = "lastUpdated"

    # Stream configuration
    api_category = "core"
    requires_design_api = True
    default_sort = "nextRunTime:asc"

    schema = th.PropertiesList(
        # Core identification
        th.Property("id", th.StringType, description="Schedule identifier"),
        th.Property("name", th.StringType, description="Schedule name"),
        th.Property("description", th.StringType, description="Schedule description"),
        th.Property(
            "integrationId", th.StringType, description="Associated integration ID"
        ),
        th.Property("integrationName", th.StringType, description="Integration name"),
        # Schedule configuration
        th.Property(
            "scheduleType",
            th.StringType,
            description="Schedule type (SIMPLE, CRON, CALENDAR)",
        ),
        th.Property("frequency", th.StringType, description="Execution frequency"),
        th.Property("interval", th.IntegerType, description="Interval value"),
        th.Property(
            "intervalUnit",
            th.StringType,
            description="Interval unit (MINUTES, HOURS, DAYS)",
        ),
        th.Property("cronExpression", th.StringType, description="Cron expression"),
        # Timing configuration
        th.Property("startTime", th.DateTimeType, description="Schedule start time"),
        th.Property("endTime", th.DateTimeType, description="Schedule end time"),
        th.Property("timezone", th.StringType, description="Schedule timezone"),
        th.Property(
            "daylightSaving", th.BooleanType, description="Daylight saving adjustment"
        ),
        # Execution windows
        th.Property(
            "executionWindows",
            th.ArrayType(
                th.ObjectType(
                    th.Property("dayOfWeek", th.StringType),
                    th.Property("startHour", th.IntegerType),
                    th.Property("startMinute", th.IntegerType),
                    th.Property("endHour", th.IntegerType),
                    th.Property("endMinute", th.IntegerType),
                )
            ),
            description="Allowed execution windows",
        ),
        # Calendar configuration
        th.Property("calendarId", th.StringType, description="Associated calendar ID"),
        th.Property("includeHolidays", th.BooleanType, description="Include holidays"),
        th.Property("includeWeekends", th.BooleanType, description="Include weekends"),
        th.Property(
            "blackoutDates", th.ArrayType(th.DateType), description="Blackout dates"
        ),
        # Status and health
        th.Property(
            "status",
            th.StringType,
            description="Schedule status (ACTIVE, PAUSED, EXPIRED)",
        ),
        th.Property("enabled", th.BooleanType, description="Schedule enabled"),
        th.Property("lastRunTime", th.DateTimeType, description="Last execution time"),
        th.Property(
            "lastRunStatus", th.StringType, description="Last execution status"
        ),
        th.Property(
            "nextRunTime", th.DateTimeType, description="Next scheduled execution"
        ),
        # Execution statistics
        th.Property("executionCount", th.IntegerType, description="Total executions"),
        th.Property(
            "successCount", th.IntegerType, description="Successful executions"
        ),
        th.Property("failureCount", th.IntegerType, description="Failed executions"),
        th.Property("missedCount", th.IntegerType, description="Missed executions"),
        th.Property(
            "avgExecutionTime", th.NumberType, description="Average execution time (ms)"
        ),
        # Advanced configuration
        th.Property("priority", th.IntegerType, description="Execution priority"),
        th.Property(
            "maxConcurrentExecutions",
            th.IntegerType,
            description="Max concurrent executions",
        ),
        th.Property("retryOnFailure", th.BooleanType, description="Retry on failure"),
        th.Property("retryCount", th.IntegerType, description="Retry count"),
        th.Property(
            "retryInterval", th.IntegerType, description="Retry interval (minutes)"
        ),
        # Monitoring and alerts
        th.Property(
            "monitoringEnabled", th.BooleanType, description="Monitoring enabled"
        ),
        th.Property("alertOnFailure", th.BooleanType, description="Alert on failure"),
        th.Property(
            "alertOnMissed", th.BooleanType, description="Alert on missed execution"
        ),
        th.Property(
            "alertRecipients",
            th.ArrayType(th.StringType),
            description="Alert recipients",
        ),
        # Metadata
        th.Property("tags", th.ArrayType(th.StringType), description="Schedule tags"),
        th.Property("properties", th.ObjectType(), description="Custom properties"),
        # Timestamps
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

    def additional_params(self, context: Optional[dict[str, Any]]) -> dict[str, Any]:
        """Additional parameters for schedule queries."""
        params = {}

        # Include execution statistics
        if self.config.get("include_execution_stats", True):
            params["includeStats"] = "true"

        # Filter by status
        status_filter = self.config.get("schedule_status_filter")
        if status_filter:
            params["status"] = status_filter

        # Time range for next runs
        next_run_days = self.config.get("next_run_days", 7)
        params["nextRunDays"] = next_run_days

        return params


class BusinessEventsStream(OICBaseStream):
    """Business Events Stream.

    Provides tracking and monitoring of business events, custom events,
    and event-driven integration triggers.

    Features:
    - Business event definitions
    - Event subscriptions and routing
    - Event payload schemas
    - Event processing statistics
    - Event correlation and tracking
    """

    name = "business_events"
    path = "/events/business"
    primary_keys = ["eventId"]
    replication_key = "timestamp"

    # Stream configuration
    api_category = "core"
    requires_runtime_api = True
    default_sort = "timestamp:desc"

    schema = th.PropertiesList(
        # Event identification
        th.Property("eventId", th.StringType, description="Unique event identifier"),
        th.Property("eventType", th.StringType, description="Event type"),
        th.Property("eventName", th.StringType, description="Event name"),
        th.Property("eventVersion", th.StringType, description="Event version"),
        # Event source
        th.Property("sourceSystem", th.StringType, description="Source system"),
        th.Property(
            "sourceApplication", th.StringType, description="Source application"
        ),
        th.Property("sourceId", th.StringType, description="Source identifier"),
        th.Property("publisherId", th.StringType, description="Publisher ID"),
        # Timing
        th.Property("timestamp", th.DateTimeType, description="Event timestamp"),
        th.Property("receivedAt", th.DateTimeType, description="Received timestamp"),
        th.Property("processedAt", th.DateTimeType, description="Processed timestamp"),
        # Event data
        th.Property("payload", th.ObjectType(), description="Event payload"),
        th.Property("payloadSize", th.IntegerType, description="Payload size (bytes)"),
        th.Property("payloadFormat", th.StringType, description="Payload format"),
        th.Property("headers", th.ObjectType(), description="Event headers"),
        # Correlation and tracking
        th.Property(
            "correlationId", th.StringType, description="Correlation identifier"
        ),
        th.Property(
            "transactionId", th.StringType, description="Transaction identifier"
        ),
        th.Property("businessKey", th.StringType, description="Business key"),
        th.Property("sequenceNumber", th.IntegerType, description="Sequence number"),
        # Processing information
        th.Property("status", th.StringType, description="Processing status"),
        th.Property(
            "processingTime", th.IntegerType, description="Processing time (ms)"
        ),
        th.Property("retryCount", th.IntegerType, description="Retry attempts"),
        # Routing and subscribers
        th.Property(
            "subscribers",
            th.ArrayType(
                th.ObjectType(
                    th.Property("subscriberId", th.StringType),
                    th.Property("integrationId", th.StringType),
                    th.Property("status", th.StringType),
                    th.Property("deliveredAt", th.DateTimeType),
                )
            ),
            description="Event subscribers",
        ),
        th.Property("routingKey", th.StringType, description="Routing key"),
        # Error handling
        th.Property("errorCode", th.StringType, description="Error code if failed"),
        th.Property("errorMessage", th.StringType, description="Error message"),
        th.Property("dlqStatus", th.StringType, description="Dead letter queue status"),
        # Metadata
        th.Property("priority", th.IntegerType, description="Event priority"),
        th.Property("ttl", th.IntegerType, description="Time to live (seconds)"),
        th.Property("tags", th.ArrayType(th.StringType), description="Event tags"),
        th.Property("properties", th.ObjectType(), description="Custom properties"),
        # Extraction metadata
        th.Property(
            "_tap_extracted_at", th.DateTimeType, description="Extraction timestamp"
        ),
        th.Property(
            "_tap_stream_name", th.StringType, description="Source stream name"
        ),
    ).to_dict()

    def additional_params(self, context: Optional[dict[str, Any]]) -> dict[str, Any]:
        """Additional parameters for business event queries."""
        params = {}

        # Time range
        time_range = self.config.get("event_time_range", "24h")
        params["timeRange"] = time_range

        # Event type filtering
        event_types = self.config.get("business_event_types")
        if event_types:
            params["eventType"] = (
                ",".join(event_types) if isinstance(event_types, list) else event_types
            )

        # Status filtering
        status_filter = self.config.get("event_status_filter")
        if status_filter:
            params["status"] = status_filter

        return params


class ImportExportJobsStream(OICBaseStream):
    """Import/Export Jobs Stream.

    Tracks integration archive import and export operations, providing
    visibility into deployment and migration activities.

    Features:
    - Import/export job tracking
    - Job status and progress
    - Archive details and contents
    - Validation results
    - Deployment history
    """

    name = "import_export_jobs"
    path = "/jobs/importexport"
    primary_keys = ["jobId"]
    replication_key = "startTime"

    # Stream configuration
    api_category = "core"
    requires_design_api = True
    default_sort = "startTime:desc"

    schema = th.PropertiesList(
        # Job identification
        th.Property("jobId", th.StringType, description="Job identifier"),
        th.Property("jobName", th.StringType, description="Job name"),
        th.Property("jobType", th.StringType, description="Job type (IMPORT, EXPORT)"),
        th.Property("description", th.StringType, description="Job description"),
        # Job configuration
        th.Property("archiveFile", th.StringType, description="Archive file name"),
        th.Property("archiveSize", th.IntegerType, description="Archive size (bytes)"),
        th.Property("archiveFormat", th.StringType, description="Archive format"),
        th.Property(
            "sourceEnvironment", th.StringType, description="Source environment"
        ),
        th.Property(
            "targetEnvironment", th.StringType, description="Target environment"
        ),
        # Status and progress
        th.Property("status", th.StringType, description="Job status"),
        th.Property(
            "percentComplete", th.IntegerType, description="Completion percentage"
        ),
        th.Property(
            "currentStep", th.StringType, description="Current processing step"
        ),
        th.Property("totalSteps", th.IntegerType, description="Total steps"),
        # Timing
        th.Property("startTime", th.DateTimeType, description="Job start time"),
        th.Property("endTime", th.DateTimeType, description="Job end time"),
        th.Property("duration", th.IntegerType, description="Duration (seconds)"),
        th.Property(
            "estimatedCompletion", th.DateTimeType, description="Estimated completion"
        ),
        # Content details
        th.Property(
            "contents",
            th.ArrayType(
                th.ObjectType(
                    th.Property("resourceType", th.StringType),
                    th.Property("resourceId", th.StringType),
                    th.Property("resourceName", th.StringType),
                    th.Property("action", th.StringType),
                    th.Property("status", th.StringType),
                )
            ),
            description="Archive contents",
        ),
        th.Property(
            "integrationCount", th.IntegerType, description="Number of integrations"
        ),
        th.Property(
            "connectionCount", th.IntegerType, description="Number of connections"
        ),
        th.Property("lookupCount", th.IntegerType, description="Number of lookups"),
        # Validation and conflicts
        th.Property("validationStatus", th.StringType, description="Validation status"),
        th.Property(
            "validationErrors",
            th.ArrayType(
                th.ObjectType(
                    th.Property("resourceId", th.StringType),
                    th.Property("errorCode", th.StringType),
                    th.Property("errorMessage", th.StringType),
                )
            ),
            description="Validation errors",
        ),
        th.Property(
            "conflicts",
            th.ArrayType(
                th.ObjectType(
                    th.Property("resourceId", th.StringType),
                    th.Property("conflictType", th.StringType),
                    th.Property("resolution", th.StringType),
                )
            ),
            description="Resource conflicts",
        ),
        # Options and settings
        th.Property(
            "overwriteExisting",
            th.BooleanType,
            description="Overwrite existing resources",
        ),
        th.Property(
            "preserveCredentials", th.BooleanType, description="Preserve credentials"
        ),
        th.Property(
            "activateAfterImport", th.BooleanType, description="Activate after import"
        ),
        th.Property("options", th.ObjectType(), description="Additional options"),
        # Results
        th.Property(
            "successCount", th.IntegerType, description="Successful operations"
        ),
        th.Property("failureCount", th.IntegerType, description="Failed operations"),
        th.Property("warningCount", th.IntegerType, description="Warnings"),
        th.Property("resultSummary", th.StringType, description="Result summary"),
        # User information
        th.Property("initiatedBy", th.StringType, description="User who initiated"),
        th.Property("approvedBy", th.StringType, description="User who approved"),
        # Metadata
        th.Property("tags", th.ArrayType(th.StringType), description="Job tags"),
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
        """Additional parameters for job queries."""
        params = {}

        # Time range
        time_range = self.config.get("job_time_range", "7d")
        params["timeRange"] = time_range

        # Job type filtering
        job_type = self.config.get("job_type_filter")
        if job_type:
            params["jobType"] = job_type

        # Status filtering
        status_filter = self.config.get("job_status_filter")
        if status_filter:
            params["status"] = status_filter

        return params

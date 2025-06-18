"""Constants for Oracle Integration Cloud TAP."""

# Oracle OIC API Constants (from official documentation)
OIC_API_BASE_PATH = "/ic/api/integration/v1"
OIC_MONITORING_API_PATH = "/ic/api/monitoring/v1"
OIC_DESIGNTIME_API_PATH = "/ic/api/designtime/v1"
OIC_PROCESS_API_PATH = "/ic/api/process/v1"
OIC_B2B_API_PATH = "/ic/api/b2b/v1"
OIC_ENVIRONMENT_API_PATH = "/ic/api/environment/v1"

# Official OIC REST API Endpoints
OIC_ENDPOINTS = {
    # Core Integration APIs
    "integrations": "/integrations",
    "integrations_detail": "/integrations/{id}",
    "integrations_status": "/integrations/{id}/status",
    "integrations_archive": "/integrations/{id}/archive",
    # Connection APIs
    "connections": "/connections",
    "connections_detail": "/connections/{id}",
    "connections_test": "/connections/{id}/test",
    # Package APIs
    "packages": "/packages",
    "packages_detail": "/packages/{id}",
    "packages_export": "/packages/export",
    "packages_import": "/packages/import",
    # Monitoring APIs (v1) - correct paths according to Oracle docs
    "monitoring_instances": "/monitoring/instances",
    "monitoring_instances_detail": "/monitoring/instances/{id}",
    "monitoring_messages": "/monitoring/messages",
    "monitoring_errors": "/monitoring/errors",
    "monitoring_activity": "/monitoring/activity",
    "audit_records": "/audit/events",
    "usage_analytics": "/monitoring/usage",
    # Lookup APIs
    "lookups": "/lookups",
    "lookup_values": "/lookups/{name}/values",
    # Library APIs
    "libraries": "/libraries",
    "libraries_detail": "/libraries/{id}",
    # Agent Group APIs
    "agent_groups": "/agentGroups",
    "agent_groups_detail": "/agentGroups/{id}",
    # Certificate APIs
    "certificates": "/certificates",
    "certificates_detail": "/certificates/{alias}",
    # Adapter APIs
    "adapters": "/adapters",
    "adapters_detail": "/adapters/{id}",
    # Process Management APIs
    "process_definitions": "/process-definitions",
    "process_definitions_detail": "/process-definitions/{id}",
    "processes": "/processes",
    "processes_detail": "/processes/{id}",
    "process_instances": "/processes/{id}/instances",
    "tasks": "/tasks",
    "tasks_detail": "/tasks/{id}",
    "spaces": "/spaces",
    "spaces_detail": "/spaces/{id}",
    # B2B Trading Partner APIs
    "trading_partners": "/tpm/partners",
    "trading_partners_detail": "/tpm/partners/{id}",
    "document_types": "/tpm/documents",
    "document_types_detail": "/tpm/documents/{id}",
    "business_messages": "/monitoring/business-messages",
    "wire_messages": "/monitoring/wire-messages",
    # Environment APIs
    "cors_domains": "/cors-domains",
    # System APIs
    "health": "/health",
    "metadata": "/metadata",
    # Execution logs
    "execution_logs": "/monitoring/logs",
    "execution_logs_detail": "/monitoring/logs/{id}",
    # Lookup details
    "lookup_usage": "/lookups/{name}/usage",
}

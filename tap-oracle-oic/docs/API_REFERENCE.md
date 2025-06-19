# Oracle Integration Cloud REST API Reference

> **Version**: 1.0
> **Last Updated**: June 15, 2025
> **Base URL**: `https://{instance}.integration.ocp.oraclecloud.com`

## Table of Contents

1. [Authentication](#authentication)
2. [Integration APIs](#integration-apis)
3. [Connection APIs](#connection-apis)
4. [Project APIs](#project-apis)
5. [Monitoring APIs](#monitoring-apis)
6. [Lookup APIs](#lookup-apis)
7. [Schedule APIs](#schedule-apis)
8. [Error Handling](#error-handling)
9. [Rate Limits](#rate-limits)

## Authentication

### OAuth 2.0 (Recommended)

Oracle Integration Cloud Generation 3 uses OAuth 2.0 as the primary authentication method.

```http
Authorization: Bearer {access_token}
```

### Getting Access Token

```http
POST https://{idcs-domain}/oauth2/v1/token
Content-Type: application/x-www-form-urlencoded
Authorization: Basic {base64(client_id:client_secret)}

grant_type=client_credentials&
scope=https://{instance}.integration.ocp.oraclecloud.com:443
```

**Response**:

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "https://domain.integration.ocp.oraclecloud.com:443"
}
```

## Integration APIs

### Create Integration

Creates a new integration programmatically in Oracle Integration Cloud.

```http
POST /ic/api/integration/v1/integrations
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "name": "Customer Data Sync",
  "identifier": "CUSTOMER_DATA_SYNC",
  "version": "01.00.0000",
  "description": "Synchronizes customer data between systems",
  "pattern": "APP_DRIVEN_ORCHESTRATION",
  "style": "SCHEDULED",
  "projectId": "CUSTOMER_PROJECT",
  "packageName": "CustomerIntegrations",
  "sourceApplication": "SalesforceAdapter",
  "targetApplication": "OracleDBAdapter",
  "isPublishToOIC": false,
  "configuration": {
    "logLevel": "INFO",
    "enableTracing": true,
    "payloadTrace": false,
    "errorHandling": {
      "retryCount": 3,
      "retryInterval": 60
    },
    "schedule": {
      "frequency": "HOURLY",
      "startTime": "2025-06-15T00:00:00Z",
      "timeZone": "UTC"
    }
  },
  "connections": [
    {
      "role": "SOURCE",
      "connectionId": "SALESFORCE_CONN_01",
      "operations": [
        {
          "operationType": "QUERY",
          "objectName": "Account",
          "fields": ["Id", "Name", "Email", "LastModifiedDate"]
        }
      ]
    },
    {
      "role": "TARGET",
      "connectionId": "ORACLE_DB_CONN_01",
      "operations": [
        {
          "operationType": "INSERT",
          "objectName": "CUSTOMERS",
          "mappings": [
            {"source": "Id", "target": "CUSTOMER_ID"},
            {"source": "Name", "target": "CUSTOMER_NAME"},
            {"source": "Email", "target": "EMAIL_ADDRESS"}
          ]
        }
      ]
    }
  ],
  "transformations": [
    {
      "type": "FIELD_MAPPING",
      "mappings": [
        {
          "source": "Account.Id",
          "target": "CUSTOMERS.CUSTOMER_ID",
          "expression": "substring($source, 1, 20)"
        },
        {
          "source": "Account.Name",
          "target": "CUSTOMERS.CUSTOMER_NAME"
        }
      ]
    }
  ]
}
```

**Response (201 Created)**:

```json
{
  "id": "CUSTOMER_DATA_SYNC|01.00.0000",
  "name": "Customer Data Sync",
  "identifier": "CUSTOMER_DATA_SYNC",
  "version": "01.00.0000",
  "status": "CONFIGURED",
  "pattern": "APP_DRIVEN_ORCHESTRATION",
  "createdTime": "2025-06-15T10:00:00Z",
  "createdBy": "user@example.com",
  "modifiedTime": "2025-06-15T10:00:00Z",
  "projectId": "CUSTOMER_PROJECT",
  "links": [
    {
      "rel": "self",
      "href": "/ic/api/integration/v1/integrations/CUSTOMER_DATA_SYNC%7C01.00.0000"
    },
    {
      "rel": "activate",
      "href": "/ic/api/integration/v1/integrations/CUSTOMER_DATA_SYNC%7C01.00.0000/activate"
    },
    {
      "rel": "export",
      "href": "/ic/api/integration/v1/integrations/CUSTOMER_DATA_SYNC%7C01.00.0000/archive"
    }
  ]
}
```

### Import Integration Archive

Imports a pre-built integration archive (.iar file) into OIC.

```http
POST /ic/api/integration/v1/integrations/archive
Content-Type: multipart/form-data
Authorization: Basic {credentials}

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="CUSTOMER_ORDER_INT_01.00.0000.iar"
Content-Type: application/octet-stream

[Binary .iar file content]
------WebKitFormBoundary--
```

**Response (201 Created)**:

```json
{
  "id": "CUSTOMER_ORDER_INT|01.00.0000",
  "name": "Customer_Order_Integration",
  "identifier": "CUSTOMER_ORDER_INT",
  "version": "01.00.0000",
  "status": "CONFIGURED",
  "importedTime": "2025-06-15T10:00:00Z",
  "importedBy": "user@example.com",
  "links": [
    {
      "rel": "self",
      "href": "/ic/api/integration/v1/integrations/CUSTOMER_ORDER_INT%7C01.00.0000"
    },
    {
      "rel": "activate",
      "href": "/ic/api/integration/v1/integrations/CUSTOMER_ORDER_INT%7C01.00.0000/activate"
    }
  ]
}
```

**Note**: Integration archives (.iar files) can be created either through the Visual Designer export function or programmatically using the Create Integration API above.

### List Integrations

```http
GET /ic/api/integration/v1/integrations?limit=20&offset=0
```

**Query Parameters**:

- `limit` (optional): Number of results per page (default: 100, max: 500)
- `offset` (optional): Starting position (default: 0)
- `q` (optional): Search query
- `orderBy` (optional): Sort field (name, modifiedTime, status)
- `projectId` (optional): Filter by project

**Response**:

```json
{
  "items": [
    {
      "id": "CUSTOMER_ORDER_INT|01.00.0000",
      "name": "Customer_Order_Integration",
      "status": "ACTIVE",
      "pattern": "APP_DRIVEN_ORCHESTRATION",
      "modifiedTime": "2025-06-15T10:00:00Z"
    }
  ],
  "totalResults": 150,
  "hasMore": true,
  "limit": 20,
  "offset": 0
}
```

### Get Integration Details

```http
GET /ic/api/integration/v1/integrations/{id}
```

### Update Integration

```http
PUT /ic/api/integration/v1/integrations/{id}
Content-Type: application/json

{
  "description": "Updated description",
  "configuration": {
    "errorHandling": {
      "retryCount": 5
    }
  }
}
```

### Delete Integration

```http
DELETE /ic/api/integration/v1/integrations/{id}
```

### Clone Integration

Creates a copy of an existing integration with a new identifier.

```http
POST /ic/api/integration/v1/integrations/{id}/clone
Content-Type: application/json

{
  "name": "Customer_Order_Integration_v2",
  "identifier": "CUSTOMER_ORDER_INT_V2",
  "version": "02.00.0000",
  "projectId": "ORDER_PROCESSING"
}
```

**Note**: This creates a duplicate of an existing integration. New integrations can also be created from scratch using the Create Integration API above.

### Activate Integration

```http
POST /ic/api/integration/v1/integrations/{id}/activate
Content-Type: application/json

{
  "enablePayloadTracing": true,
  "payloadTracingLevel": "PRODUCTION"
}
```

### Deactivate Integration

```http
POST /ic/api/integration/v1/integrations/{id}/deactivate
```

### Export Integration (IAR)

```http
GET /ic/api/integration/v1/integrations/{id}/archive
```

**Response**: Binary IAR file

### Import Integration (IAR)

```http
POST /ic/api/integration/v1/integrations/archive
Content-Type: multipart/form-data

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="integration.iar"
Content-Type: application/octet-stream

[Binary IAR content]
------WebKitFormBoundary--
```

## Connection APIs

### Create Connection

Creates a new connection programmatically in Oracle Integration Cloud.

```http
POST /ic/api/integration/v1/connections
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "name": "Production Database Connection",
  "identifier": "PROD_DB_CONN_01",
  "description": "Oracle Database connection for production environment",
  "adapterType": "oracle-db-adapter",
  "version": "01.00.0000",
  "projectId": "CUSTOMER_PROJECT",
  "connectionProperties": {
    "host": "prod-db.example.com",
    "port": 1521,
    "serviceName": "PRODDB",
    "databaseSchema": "SALES",
    "connectionPooling": {
      "initialSize": 5,
      "maxSize": 20,
      "connectionTimeout": 30000
    },
    "security": {
      "authenticationType": "USERNAME_PASSWORD",
      "username": "${DB_USERNAME}",
      "password": "${DB_PASSWORD}",
      "useSSL": true,
      "trustStore": "SYSTEM_DEFAULT"
    },
    "advanced": {
      "queryTimeout": 300,
      "maxRowsPerRead": 10000,
      "enableXA": false,
      "customJDBCProperties": {
        "oracle.net.CONNECT_TIMEOUT": "60000",
        "oracle.jdbc.ReadTimeout": "120000"
      }
    }
  },
  "testConfiguration": {
    "enableTesting": true,
    "testQuery": "SELECT 1 FROM DUAL",
    "testTimeout": 30
  }
}
```

**Response (201 Created)**:

```json
{
  "id": "PROD_DB_CONN_01",
  "name": "Production Database Connection",
  "identifier": "PROD_DB_CONN_01",
  "status": "CONFIGURED",
  "adapterType": "oracle-db-adapter",
  "version": "01.00.0000",
  "createdTime": "2025-06-15T10:00:00Z",
  "createdBy": "user@example.com",
  "modifiedTime": "2025-06-15T10:00:00Z",
  "projectId": "CUSTOMER_PROJECT",
  "testStatus": "NOT_TESTED",
  "links": [
    {
      "rel": "self",
      "href": "/ic/api/integration/v1/connections/PROD_DB_CONN_01"
    },
    {
      "rel": "test",
      "href": "/ic/api/integration/v1/connections/PROD_DB_CONN_01/test"
    },
    {
      "rel": "metadata",
      "href": "/ic/api/integration/v1/connections/PROD_DB_CONN_01/metadata"
    }
  ]
}
```

### List Connections

```http
GET /ic/api/integration/v1/connections?adapterType=MYSQL
```

### Get Connection Details

```http
GET /ic/api/integration/v1/connections/{id}
```

### Update Connection

```http
PUT /ic/api/integration/v1/connections/{id}
Content-Type: application/json

{
  "connectionProperties": {
    "host": "mysql-new.prod.example.com",
    "connectionPooling": {
      "maxSize": 30
    }
  }
}
```

### Delete Connection

```http
DELETE /ic/api/integration/v1/connections/{id}
```

**Note**: Connections can only be deleted if they are not used by any integrations.

### Test Connection

```http
POST /ic/api/integration/v1/connections/{id}/test
```

**Response**:

```json
{
  "status": "SUCCESS",
  "message": "Connection test successful",
  "responseTime": 245,
  "timestamp": "2025-06-15T10:00:00Z",
  "details": {
    "serverVersion": "8.0.32",
    "characterSet": "utf8mb4",
    "maxConnections": 151
  }
}
```

### Get Connection Metadata

```http
GET /ic/api/integration/v1/connections/{id}/metadata
```

## Project APIs

### Create Project

Creates a new project in Oracle Integration Cloud.

```http
POST /ic/api/projects/v1/projects
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "name": "Customer Integration Project",
  "identifier": "CUSTOMER_PROJECT",
  "description": "Project for all customer-related integrations",
  "version": "1.0",
  "owner": "integration-team@example.com",
  "status": "ACTIVE",
  "configuration": {
    "enableVersionControl": true,
    "defaultEnvironment": "DEVELOPMENT",
    "deploymentStrategy": "ROLLING",
    "securityPolicy": "STANDARD"
  },
  "metadata": {
    "businessUnit": "Sales",
    "criticality": "HIGH",
    "tags": ["customer", "sales", "crm"]
  }
}
```

**Response (201 Created)**:

```json
{
  "id": "CUSTOMER_PROJECT",
  "name": "Customer Integration Project",
  "identifier": "CUSTOMER_PROJECT",
  "status": "ACTIVE",
  "version": "1.0",
  "createdTime": "2025-06-15T10:00:00Z",
  "createdBy": "user@example.com",
  "modifiedTime": "2025-06-15T10:00:00Z",
  "integrationCount": 0,
  "connectionCount": 0,
  "links": [
    {
      "rel": "self",
      "href": "/ic/api/projects/v1/projects/CUSTOMER_PROJECT"
    },
    {
      "rel": "integrations",
      "href": "/ic/api/integration/v1/integrations?projectId=CUSTOMER_PROJECT"
    },
    {
      "rel": "connections",
      "href": "/ic/api/integration/v1/connections?projectId=CUSTOMER_PROJECT"
    }
  ]
}
```

### List Projects

```http
GET /ic/api/projects/v1/projects
```

### Update Project

```http
PUT /ic/api/projects/v1/projects/{id}
```

### Delete Project

```http
DELETE /ic/api/projects/v1/projects/{id}
```

## Monitoring APIs

### Get Integration Metrics

```http
GET /ic/api/monitoring/v1/integrations/{id}/metrics?period=24h&interval=1h
```

**Query Parameters**:

- `period`: Time period (1h, 6h, 24h, 7d, 30d)
- `interval`: Data point interval
- `startTime`: ISO 8601 timestamp
- `endTime`: ISO 8601 timestamp

**Response**:

```json
{
  "integrationId": "CUSTOMER_ORDER_INT|01.00.0000",
  "period": "24h",
  "metrics": {
    "summary": {
      "totalExecutions": 1524,
      "successfulExecutions": 1498,
      "failedExecutions": 26,
      "averageExecutionTime": 1243,
      "errorRate": 0.017
    },
    "timeSeries": [
      {
        "timestamp": "2025-06-15T00:00:00Z",
        "executions": 63,
        "successful": 62,
        "failed": 1,
        "avgExecutionTime": 1180
      }
    ]
  }
}
```

### Get Execution History

```http
GET /ic/api/monitoring/v1/integrations/{id}/executions?limit=50&status=FAILED
```

**Query Parameters**:

- `status`: Filter by status (SUCCESS, FAILED, IN_PROGRESS)
- `startTime`: Start of time range
- `endTime`: End of time range
- `trackingField`: Filter by tracking field value

### Get Execution Details

```http
GET /ic/api/monitoring/v1/executions/{executionId}
```

### Get Execution Activity Stream

```http
GET /ic/api/monitoring/v1/executions/{executionId}/activities
```

### Get Error Details

```http
GET /ic/api/monitoring/v1/executions/{executionId}/errors
```

**Response**:

```json
{
  "errors": [
    {
      "timestamp": "2025-06-15T10:00:00Z",
      "activity": "InvokeRESTEndpoint",
      "errorCode": "HTTP-500",
      "errorMessage": "Internal Server Error",
      "errorDetails": "Connection timeout after 30000ms",
      "retryAttempt": 3,
      "stackTrace": "..."
    }
  ]
}
```

## Lookup APIs

### Create Lookup

```http
POST /ic/api/integration/v1/lookups
Content-Type: application/json

{
  "name": "CountryCodeMapping",
  "identifier": "COUNTRY_CODE_MAP",
  "description": "Maps country names to ISO codes",
  "columns": [
    {
      "name": "CountryName",
      "type": "STRING"
    },
    {
      "name": "ISOCode",
      "type": "STRING"
    }
  ],
  "data": [
    {
      "CountryName": "United States",
      "ISOCode": "US"
    },
    {
      "CountryName": "United Kingdom",
      "ISOCode": "GB"
    }
  ]
}
```

### Get Lookup Data

```http
GET /ic/api/integration/v1/lookups/{id}/data
```

## Schedule APIs

### Create Schedule

Creates a new schedule for an integration.

```http
POST /ic/api/integration/v1/integrations/{id}/schedule
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "name": "Hourly Customer Sync",
  "description": "Sync customers every hour",
  "frequency": "HOURLY",
  "startTime": "2025-06-15T00:00:00Z",
  "endTime": "2025-12-31T23:59:59Z",
  "timeZone": "America/New_York",
  "isActive": true,
  "runConcurrently": false,
  "parameters": [
    {
      "name": "batchSize",
      "value": "1000"
    },
    {
      "name": "includeDeleted",
      "value": "false"
    }
  ]
}
```

**Response (201 Created)**:

```json
{
  "id": "SCHEDULE_001",
  "integrationId": "CUSTOMER_ORDER_INT|01.00.0000",
  "name": "Hourly Customer Sync",
  "frequency": "HOURLY",
  "status": "ACTIVE",
  "nextRunTime": "2025-06-15T11:00:00Z",
  "createdTime": "2025-06-15T10:00:00Z",
  "links": [
    {
      "rel": "self",
      "href": "/ic/api/integration/v1/integrations/CUSTOMER_ORDER_INT%7C01.00.0000/schedule"
    },
    {
      "rel": "start",
      "href": "/ic/api/integration/v1/integrations/CUSTOMER_ORDER_INT%7C01.00.0000/schedule/start"
    },
    {
      "rel": "stop",
      "href": "/ic/api/integration/v1/integrations/CUSTOMER_ORDER_INT%7C01.00.0000/schedule/stop"
    }
  ]
}
```

### Update Schedule

```http
PUT /ic/api/integration/v1/schedules/{id}
```

### Delete Schedule

```http
DELETE /ic/api/integration/v1/schedules/{id}
```

## Error Handling

### Error Response Format

```json
{
  "type": "https://docs.oracle.com/error/OIC-123456",
  "title": "Integration Not Found",
  "status": 404,
  "detail": "Integration with ID 'INVALID_ID' was not found",
  "instance": "/ic/api/integration/v1/integrations/INVALID_ID",
  "o:errorCode": "OIC-123456",
  "o:errorPath": "/ic/api/integration/v1/integrations/INVALID_ID",
  "timestamp": "2025-06-15T10:00:00Z"
}
```

### Common Error Codes

| Code       | Status | Description                     |
| ---------- | ------ | ------------------------------- |
| OIC-400001 | 400    | Invalid request format          |
| OIC-401001 | 401    | Authentication failed           |
| OIC-403001 | 403    | Insufficient permissions        |
| OIC-404001 | 404    | Resource not found              |
| OIC-409001 | 409    | Resource already exists         |
| OIC-429001 | 429    | Rate limit exceeded             |
| OIC-500001 | 500    | Internal server error           |
| OIC-503001 | 503    | Service temporarily unavailable |

## Rate Limits

### Default Limits

| Resource                | Limit | Window | Scope       |
| ----------------------- | ----- | ------ | ----------- |
| API Requests            | 1000  | 1 hour | Per user    |
| Concurrent Integrations | 50    | -      | Per tenant  |
| Payload Size            | 10 MB | -      | Per request |
| Bulk Operations         | 100   | -      | Per request |

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 750
X-RateLimit-Reset: 1623456789
```

### Handling Rate Limits

When rate limit is exceeded:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 3600
Content-Type: application/json

{
  "type": "https://docs.oracle.com/error/OIC-429001",
  "title": "Rate Limit Exceeded",
  "status": 429,
  "detail": "API rate limit of 1000 requests per hour exceeded",
  "retryAfter": 3600
}
```

## Best Practices

1. **Use Pagination**: Always paginate when listing resources
2. **Handle Retries**: Implement exponential backoff for failed requests
3. **Cache Responses**: Cache metadata and configuration data
4. **Batch Operations**: Use bulk endpoints when available
5. **Monitor Rate Limits**: Track rate limit headers
6. **Use Projections**: Request only needed fields to reduce payload size
7. **Implement Timeouts**: Set appropriate timeouts for long-running operations

## References

- [Oracle Integration REST API Documentation](https://docs.oracle.com/en/cloud/paas/application-integration/rest-api/)
- [Oracle Cloud Infrastructure API Reference](https://docs.oracle.com/en-us/iaas/api/)
- [Oracle Integration Developer Guide](https://docs.oracle.com/en/cloud/paas/application-integration/)

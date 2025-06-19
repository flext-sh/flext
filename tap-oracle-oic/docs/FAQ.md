# Frequently Asked Questions (FAQ)

> **tap-oic Version**: 2.0
> **Last Updated**: June 15, 2025

## Table of Contents

1. [General Questions](#general-questions)
2. [Installation and Setup](#installation-and-setup)
3. [Integration Generation](#integration-generation)
4. [Data Extraction](#data-extraction)
5. [Performance and Optimization](#performance-and-optimization)
6. [Troubleshooting](#troubleshooting)
7. [Singer Ecosystem](#singer-ecosystem)
8. [Security](#security)

## General Questions

### Q: What is tap-oic?

**A:** tap-oic is a Singer tap for Oracle Integration Cloud (OIC) Generation 3. It provides two main capabilities:

1. **Data Extraction** - Extract integration metadata, monitoring data, and execution history from OIC
2. **Integration Generation** - Create integrations programmatically using OIC's REST APIs

### Q: What version of OIC is required?

**A:** tap-oic requires Oracle Integration Cloud Generation 3, which provides the REST API endpoints necessary for both extracting data and creating integrations programmatically.

### Q: Can OIC really create integrations via API?

**A:** Yes! Oracle Integration Cloud Generation 3 provides full REST API support for creating, updating, and managing integrations programmatically. You can:

- Create new integrations using `POST /ic/api/integration/v1/integrations`
- Create connections using `POST /ic/api/integration/v1/connections`
- Manage the complete integration lifecycle via API

### Q: What are the main use cases for tap-oic?

**A:** Common use cases include:

- Monitoring OIC integration performance
- Creating data pipelines from Singer tap/target configurations
- Automating integration deployment across environments
- Building multi-tenant integration solutions
- Implementing Infrastructure as Code for integrations

## Installation and Setup

### Q: How do I install tap-oic?

**A:** You can install tap-oic using pip:

```bash
pip install tap-oic
```

Or with Meltano:

```bash
meltano add extractor tap-oic
```

### Q: What authentication methods are supported?

**A:** tap-oic supports:

- Basic Authentication (username/password)
- OAuth 2.0
- API Key authentication
- Certificate-based authentication

### Q: How do I handle credentials securely?

**A:** Best practices for credential management:

1. Use environment variables: `${OIC_PASSWORD}`
2. Use a secrets manager (AWS Secrets Manager, HashiCorp Vault)
3. Never commit credentials to version control
4. Rotate credentials regularly

### Q: What Python version is required?

**A:** tap-oic requires Python 3.8 or higher. We recommend using Python 3.11+ for best performance.

## Integration Generation

### Q: Can I create integrations from Singer configurations?

**A:** Yes! tap-oic can automatically generate OIC integrations from Singer tap and target configurations:

```python
from tap_oic.generators import SingerIntegrationGenerator

generator = SingerIntegrationGenerator(oic_client)
integration = generator.create_from_configs(
    source=tap_config,
    destination=target_config,
    schedule="0 */2 * * *"
)
```

### Q: What integration patterns are supported?

**A:** OIC supports these patterns:

- `APP_DRIVEN_ORCHESTRATION` - REST/SOAP triggered
- `SCHEDULED_ORCHESTRATION` - Time-based execution
- `BASIC_ROUTING` - Simple message routing
- `PUBLISH_TO_OIC` - Event streaming
- `SUBSCRIBE_TO_OIC` - Event consumption

### Q: Can I create connections programmatically?

**A:** Yes, you can create connections for any supported adapter:

```python
connection = client.create_connection({
    "name": "MySQL_Production",
    "adapterType": "MYSQL",
    "connectionProperties": {
        "host": "mysql.example.com",
        "port": 3306,
        "database": "production"
    }
})
```

### Q: How do I deploy integrations across environments?

**A:** Use the multi-environment deployment pattern:

```python
environments = ["dev", "test", "prod"]

for env in environments:
    client = OICManagementClient(configs[env])
    integration = client.create_integration(template)
    client.activate_integration(integration['id'])
```

## Data Extraction

### Q: What data can I extract from OIC?

**A:** tap-oic can extract:

- Integration metadata and configurations
- Connection details
- Execution history
- Performance metrics
- Error logs
- Project information
- Lookup tables
- Schedule information

### Q: How do I filter the data being extracted?

**A:** You can filter data using:

1. Stream selection in the catalog
2. Date ranges with `start_date` configuration
3. Query parameters for specific endpoints
4. Custom filters in your configuration

### Q: Can I extract real-time data?

**A:** While tap-oic operates in batch mode, you can:

- Set frequent sync schedules (e.g., every 5 minutes)
- Use the monitoring APIs for near real-time metrics
- Implement webhook receivers for real-time events

### Q: How is incremental replication handled?

**A:** tap-oic uses bookmark fields (typically `modifiedTime`) to track progress:

```json
{
  "bookmarks": {
    "integrations": {
      "value": "2025-06-15T10:00:00Z"
    }
  }
}
```

## Performance and Optimization

### Q: How can I improve extraction performance?

**A:** Performance optimization strategies:

1. Adjust `page_size` (default: 100, max: 500)
2. Use connection pooling
3. Enable response compression
4. Select only needed streams
5. Use parallel processing for multiple streams

### Q: What are the API rate limits?

**A:** Default OIC rate limits:

- 1000 API calls per hour per user
- 50 concurrent integrations per tenant
- 10MB maximum payload size

Monitor rate limit headers:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 750
X-RateLimit-Reset: 1623456789
```

### Q: How do I handle large datasets?

**A:** For large datasets:

1. Use pagination with appropriate page sizes
2. Implement streaming to avoid memory issues
3. Use date-based partitioning
4. Consider parallel extraction for independent streams

### Q: Can I cache API responses?

**A:** Yes, implement caching for:

- Integration metadata (TTL: 5-15 minutes)
- Connection details (TTL: 30 minutes)
- Project information (TTL: 1 hour)

Don't cache:

- Execution data
- Real-time metrics
- Error logs

## Troubleshooting

### Q: Why am I getting authentication errors?

**A:** Common causes:

1. Incorrect username format (should be email)
2. Special characters in password not properly escaped
3. Account locked due to failed attempts
4. User lacks API access permissions
5. OAuth token expired

### Q: Why are my integrations not being created?

**A:** Check:

1. OIC Generation 3 is being used (not Gen 2)
2. User has Integration Developer role
3. Project exists and user has access
4. Integration identifier is unique
5. All required fields are provided

### Q: How do I debug API errors?

**A:** Enable debug logging:

```bash
export SINGER_LOG_LEVEL=DEBUG
tap-oic --config config.json --debug 2> debug.log
```

Check for:

- HTTP status codes
- Error response bodies
- Rate limit headers
- Network connectivity

### Q: Why is extraction slow?

**A:** Common performance issues:

1. Large page sizes causing timeouts
2. No connection pooling
3. Extracting all historical data
4. Network latency
5. Rate limiting

## Singer Ecosystem

### Q: How does tap-oic integrate with Meltano?

**A:** tap-oic is fully compatible with Meltano:

```yaml
extractors:
  - name: tap-oic
    pip_url: tap-oic
    config:
      instance_url: ${OIC_INSTANCE_URL}
      username: ${OIC_USERNAME}
      password: ${OIC_PASSWORD}
```

### Q: Can I use tap-oic with any Singer target?

**A:** Yes, tap-oic outputs standard Singer messages compatible with any target:

```bash
tap-oic | target-postgres
tap-oic | target-snowflake
tap-oic | target-s3
```

### Q: Can OIC act as a Singer target?

**A:** Yes, you can create an OIC integration that receives Singer messages:

```python
integration = create_singer_target_integration(
    stream_name="customers",
    target_connection="DATABASE_CONNECTION"
)
```

### Q: How do I handle Singer state management?

**A:** tap-oic supports multiple state backends:

- File-based (default)
- Redis
- S3
- Custom implementations

## Security

### Q: Is data encrypted in transit?

**A:** Yes, all communication uses HTTPS/TLS. You can also:

- Enforce TLS 1.2+
- Use certificate pinning
- Implement mutual TLS

### Q: How are credentials stored?

**A:** Best practices:

1. Never store plain text passwords
2. Use environment variables
3. Implement credential rotation
4. Use OAuth when possible
5. Leverage secrets management tools

### Q: What about data privacy?

**A:** tap-oic:

- Only accesses data you have permissions for
- Doesn't store data unless configured to
- Supports data masking/filtering
- Complies with OIC's security model

### Q: Can I audit API usage?

**A:** Yes, you can:

- Enable detailed logging
- Track API calls in OIC audit logs
- Monitor rate limit consumption
- Set up alerts for unusual activity

## Advanced Questions

### Q: Can I extend tap-oic functionality?

**A:** Yes, tap-oic is designed to be extensible:

```python
from tap_oic import BaseStream

class CustomStream(BaseStream):
    name = 'custom_data'
    endpoint = '/api/custom/endpoint'

    def transform_record(self, record):
        # Custom transformation logic
        return record
```

### Q: How do I contribute to tap-oic?

**A:** Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request
5. Ensure all tests pass

### Q: Where can I get help?

**A:** Resources for help:

1. GitHub Issues for bug reports
2. Singer Slack community
3. Oracle Support for OIC-specific issues
4. Documentation in this repository
5. Community forums

## Common Misconceptions Corrected

### Q: I heard OIC can't create integrations via API. Is this true?

**A:** This is **FALSE**. OIC Generation 3 has full REST API support for creating integrations, connections, and projects programmatically.

### Q: Can tap-oic only read data from OIC?

**A:** No! tap-oic v2.0 can both:

- Extract data from OIC (traditional Singer tap functionality)
- Generate integrations in OIC (new capability)

### Q: Is OIC just a monitoring platform?

**A:** No, OIC is a full integration platform that can:

- Create and manage integrations via API
- Connect to 100+ systems
- Transform data
- Orchestrate workflows
- Handle real-time and batch processing

## Summary

This FAQ covers the most common questions about tap-oic. For more detailed information, please refer to the specific documentation sections:

- [Installation Guide](INSTALLATION_AND_SETUP.md)
- [Implementation Guide](IMPLEMENTATION_GUIDE.md)
- [Integration Generation](INTEGRATION_GENERATION.md)
- [Examples](EXAMPLES.md)
- [API Reference](API_REFERENCE.md)

# transform-oic

This transformer plugin is responsible for configuration, management and monitoring of flows between Oracle WMS Cloud, Oracle Integration Cloud (OIC) and Oracle Autonomous Database.

## Features

- Integration Configuration in OIC for connection with WMS Cloud
- Webhook Configuration for real-time events
- Configuration and management of scheduled jobs for FTP file verification
- Monitoring and notifications
- Diagnostic and recovery tools

## Requirements

- Python 3.8 or higher
- Access to Oracle Integration Cloud (OIC v3)
- Access to Oracle WMS Cloud
- Properly configured integration credentials

## Architecture

This transformer manages the following flows:

### 1. Initial WMS Load to Oracle DB

```bash
# Execute initial load
meltano run wms_initial_load
```

This flow extracts historical data from WMS via CSV and loads it into Oracle DB. The scheduled job periodically checks the SFTP directory for new CSV files exported by WMS. When it finds files, it processes them and moves them to a processed files directory.

### 2. Real-time Events WMS → Oracle DB

```bash
# Configure webhook in WMS
meltano invoke transform-oic configure_webhook --stream orders
```

Configures WMS to send real-time events to OIC when new orders are created or updated. OIC processes and forwards this data to Oracle DB.

### 3. Integration Provisioning Oracle DB → WMS

```bash
# Configure integration for sending data to WMS
meltano invoke transform-oic setup_integration --type wms_inbound
```

Configures an integration in OIC that reads data from Oracle DB and sends it to WMS Cloud via REST API.

## Configuration

The transformer uses the following structure in the `meltano.yml` file:

```yaml
plugins:
  transformers:
    - name: transform-oic
      namespace: transform_oic
      pip_url: -e ./plugins/transformers/transform-oic
      config:
        oic_url: https://example.integration.ocp.oraclecloud.com
        oic_auth:
          type: oauth2
          client_id: $OIC_CLIENT_ID
          client_secret: $OIC_CLIENT_SECRET
          idcs_url: $OIC_IDCS_URL
          resource_aud: $OIC_RESOURCE_AUD
          api_aud: $OIC_API_AUD
        wms_config:
          url: https://example.wms.ocs.oraclecloud.com
          username: $WMS_USERNAME
          password: $WMS_PASSWORD
        sftp_config:
          host: sftp.example.com
          port: 22
          username: $SFTP_USERNAME
          password: $SFTP_PASSWORD
          input_directory: /input
          processed_directory: /processed
          error_directory: /error

schedules:
  - name: wms_initial_load
    extractor: tap-wms
    loader: target-oracle
    interval: "@hourly" # Check every hour for new files on SFTP
    job_id: initial_load
    start_date: 2023-01-01
    config:
      extraction_mode: "csv"
      # This configuration makes the job periodically check the SFTP directory
```

## Available Commands

The transformer offers the following commands:

```bash
# Configure webhooks in WMS
meltano invoke transform-oic configure_webhook --stream [orders|allocations]

# Configure integration in OIC
meltano invoke transform-oic setup_integration --type [wms_inbound|wms_outbound]

# Check integration status
meltano invoke transform-oic check_status

# Restart a failed integration
meltano invoke transform-oic restart_integration --integration_id INTEGRATION_ID

# Reprocess a file
meltano invoke transform-oic reprocess_file --file_path FILE_PATH
```

## Troubleshooting

### WMS Connection Failure

Check credentials and ensure the user has the necessary permissions to access WMS APIs. Required permissions include:

- `can_run_ws_stage_interface` for APIs
- Eligibility for specific companies/facilities

### SFTP File Processing Errors

1. Verify that the file format is as expected
2. Confirm that the file is in the correct directory
3. Check permissions and access to the SFTP server

### OIC Integration Execution Failure

Consult execution logs in the OIC console to identify the specific problem. Common issues include:

- Authentication failure
- Malformed payload
- Execution timeout exceeded

## Monitoring

The transformer collects metrics and logs that can be monitored via:

- OIC Console
- WMS Console
- Meltano Logs
- Alerts configured in OIC for integration failures

## Data Transformation Rules

### Order Header Transformation

```yaml
transformations:
  order_header:
    source_fields:
      - wms_order_id
      - order_date
      - customer_id
    target_fields:
      - order_number
      - created_date
      - customer_code
    mappings:
      order_number: "{{ wms_order_id }}"
      created_date: "{{ order_date | date_format }}"
      customer_code: "{{ customer_id | upper }}"
```

### Allocation Transformation

```yaml
transformations:
  allocation:
    source_fields:
      - alloc_id
      - item_id
      - qty_allocated
    target_fields:
      - allocation_number
      - product_id
      - quantity
    mappings:
      allocation_number: "{{ alloc_id }}"
      product_id: "{{ item_id }}"
      quantity: "{{ qty_allocated | int }}"
```

## Performance Optimization

- Configure appropriate batch sizes for data processing
- Use incremental processing when possible
- Monitor memory usage during large transformations
- Implement error handling and retry mechanisms

## Security Considerations

- Store credentials in environment variables or secure configuration
- Use OAuth2 authentication for OIC connections
- Validate data before transformation
- Implement audit logging for data changes

## License

This plugin is available under the Apache 2.0 license.

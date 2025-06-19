# Oracle WMS Operations Guide

A comprehensive guide to Oracle WMS operations available through the FLX HTTP Oracle WMS CLI.

## Overview

This CLI provides full access to Oracle WMS Cloud Integration API operations with enhanced features:

- **Dynamic Discovery**: Automatically discover available entities and endpoints
- **Type-Safe Operations**: Runtime validation using Pydantic models
- **High-Speed Extraction**: Paged extraction for large datasets
- **Multiple Formats**: Support for JSON, CSV, Excel, Parquet, YAML
- **Bulk Operations**: Process multiple operations in batches
- **Schema Management**: Validate and cache entity schemas

## Core WMS Operations

### 1. Entity Management

#### Object Inquiry

Query specific entities with full parameter support:

```bash
flx-http-oracle-wms entity-query [entity] [key] [company_code] [facility_code]
```

**Parameters:**

- `entity`: Entity name (items, orders, locations, etc.)
- `key`: Entity identifier/key
- `company_code`: Company code
- `facility_code`: Facility code
- `--minimize`: Minimize response data
- `--format-output`: Output format (table, json, yaml, csv)

**Example:**

```bash
flx-http-oracle-wms entity-query items ITEM001 001 DC1 --format-output table
```

#### Entity Status

Get status information for any entity:

```bash
flx-http-oracle-wms get-status [entity] [key] [company_code] [facility_code]
```

### 2. LPN Operations

#### Create LPN

Create License Plate Numbers with comprehensive parameters:

```bash
flx-http-oracle-wms create-lpn [lpn_nbr] [qty] [options...]
```

**Parameters:**

- `lpn_nbr`: LPN number (required)
- `qty`: Quantity (required)
- `--item-barcode`: Item barcode
- `--company-code`: Company code
- `--facility-code`: Facility code
- `--batch-number`: Batch number
- `--expiry-date`: Expiry date (YYYY-MM-DD)
- `--dest-facility-code`: Destination facility
- `--drop-locn-barcode`: Drop location barcode
- `--item-alternate-code`: Item alternate code
- `--lock-code`: Lock code
- `--lpn-weight`: LPN weight
- `--order-type`: Order type
- `--xdock-lpn-flg`: Cross-dock flag

**Example:**

```bash
flx-http-oracle-wms create-lpn LPN001 100 \
    --item-barcode ITEM001 \
    --company-code 001 \
    --facility-code DC1 \
    --batch-number BATCH001 \
    --expiry-date 2024-12-31
```

#### Receive LPN

Receive LPNs with tracking information:

```bash
flx-http-oracle-wms receive-lpn [lpn_nbr] [options...]
```

**Parameters:**

- `lpn_nbr`: LPN number (required)
- `--company-code`: Company code
- `--facility-code`: Facility code
- `--rcvd-trailer-nbr`: Received trailer number
- `--received-ts`: Received timestamp
- `--receiving-location`: Receiving location
- `--xdock-lpn-flg`: Cross-dock flag

**Example:**

```bash
flx-http-oracle-wms receive-lpn LPN001 \
    --company-code 001 \
    --facility-code DC1 \
    --rcvd-trailer-nbr TRAILER001 \
    --receiving-location DOCK01
```

### 3. Outbound Operations

#### Ship OBLPN

Ship outbound License Plate Numbers:

```bash
flx-http-oracle-wms ship-oblpn [oblpn_nbr] [company_code] [facility_code] [locn_barcode]
```

**Parameters:**

- `oblpn_nbr`: Outbound LPN number (required)
- `company_code`: Company code (required)
- `facility_code`: Facility code (required)
- `locn_barcode`: Location barcode (required)
- `--output-file-to-generate`: Output file to generate

**Example:**

```bash
flx-http-oracle-wms ship-oblpn OBLPN001 001 DC1 SHIP01 \
    --output-file-to-generate shipping_label.pdf
```

#### Assign OBLPN to Load

Assign outbound LPNs to loads:

```bash
flx-http-oracle-wms assign-oblpn-to-load [load_nbr] [oblpn_nbr] [options...]
```

**Parameters:**

- `load_nbr`: Load number (required)
- `oblpn_nbr`: OBLPN number (required)
- `--carrier-code`: Carrier code
- `--company-code`: Company code
- `--facility-code`: Facility code
- `--delimiter`: Delimiter
- `--reassign-load-flg`: Reassign load flag
- `--require-specific-oblpn-status`: Required OBLPN status
- `--trailer-nbr`: Trailer number

**Example:**

```bash
flx-http-oracle-wms assign-oblpn-to-load LOAD001 OBLPN001 \
    --carrier-code UPS \
    --company-code 001 \
    --facility-code DC1 \
    --trailer-nbr TRAILER001
```

### 4. Inventory Operations

#### Update Active Inventory

Update inventory with comprehensive parameters:

```bash
flx-http-oracle-wms update-inventory [location_barcode] [reason_code] [options...]
```

**Parameters:**

- `location_barcode`: Location barcode (required)
- `reason_code`: Reason code (required)
- `--actual-qty`: Actual quantity
- `--adjustment-qty`: Adjustment quantity
- `--item-barcode`: Item barcode
- `--company-code`: Company code
- `--facility-code`: Facility code
- `--batch-number`: Batch number
- `--expiry-date`: Expiry date
- `--item-code`: Item code
- `--item-alternate-code`: Item alternate code
- `--locn-capacity-check-flg`: Location capacity check flag

**Additional inventory attributes** (invn_attr_a through invn_attr_g) can be passed as additional parameters.

**Example:**

```bash
flx-http-oracle-wms update-inventory LOC001 ADJUST \
    --actual-qty 100 \
    --adjustment-qty 5 \
    --item-barcode ITEM001 \
    --company-code 001 \
    --facility-code DC1
```

### 5. Sequence Management

#### Get Next Numbers

Generate sequence numbers for various counters:

```bash
flx-http-oracle-wms get-next-numbers [counter_code] [options...]
```

**Parameters:**

- `counter_code`: Counter code (required)
- `--company-code`: Company code
- `--facility-code`: Facility code
- `--count`: Number of sequences to get (default: 1)

**Example:**

```bash
flx-http-oracle-wms get-next-numbers LPN_SEQ \
    --company-code 001 \
    --facility-code DC1 \
    --count 10
```

## Advanced Features

### High-Speed Data Extraction

Extract large datasets efficiently using paged queries:

```bash
flx-http-oracle-wms extract [entity_name] [output_file] [company_code] [facility_code] [options...]
```

**Parameters:**

- `entity_name`: Entity to extract (required)
- `output_file`: Output file path (required)
- `company_code`: Company code (required)
- `facility_code`: Facility code (required)
- `--format-export`: Export format (json, csv, parquet, xlsx)
- `--high-speed`: Enable high-speed paged extraction
- `--page-size`: Records per page (default: 1000)
- `--max-records`: Maximum records to extract

**Examples:**

```bash
# High-speed extraction to JSON
flx-http-oracle-wms extract items items_data.json 001 DC1 \
    --high-speed --page-size 5000 --format-export json

# Extract to CSV with limit
flx-http-oracle-wms extract orders orders.csv 001 DC1 \
    --format-export csv --max-records 10000

# Extract to Excel
flx-http-oracle-wms extract inventory inventory.xlsx 001 DC1 \
    --format-export xlsx

# Extract to Parquet for big data
flx-http-oracle-wms extract transactions data.parquet 001 DC1 \
    --format-export parquet --high-speed
```

### Bulk Operations

Process multiple operations from JSON files:

```bash
flx-http-oracle-wms bulk-operations [operation_file] [operation_type] [options...]
```

**Parameters:**

- `operation_file`: JSON file with operations (required)
- `operation_type`: Operation type (create_lpn, receive_lpn, etc.) (required)
- `--batch-size`: Operations per batch (default: 10)
- `--continue-on-error`: Continue on errors

**Example JSON file structure:**

```json
[
  {
    "lpn_nbr": "LPN001",
    "qty": 100,
    "item_barcode": "ITEM001",
    "company_code": "001",
    "facility_code": "DC1"
  },
  {
    "lpn_nbr": "LPN002",
    "qty": 200,
    "item_barcode": "ITEM002",
    "company_code": "001",
    "facility_code": "DC1"
  }
]
```

**Usage:**

```bash
flx-http-oracle-wms bulk-operations bulk_lpn_create.json create_lpn \
    --batch-size 50 --continue-on-error
```

### Schema Management

#### Get and Validate Schema

Retrieve entity schemas with validation:

```bash
flx-http-oracle-wms get-schema [entity_name] [options...]
```

**Parameters:**

- `entity_name`: Entity name (required)
- `--save-schema`: Save schema to schemas/entities directory
- `--validate`: Validate schema structure

**Example:**

```bash
flx-http-oracle-wms get-schema items --save-schema --validate
```

This creates: `schemas/entities/items.json`

## Output Formats

The CLI supports multiple output formats:

### Table Format (Default)

Rich formatted tables with colors and styling:

```bash
--format-output table
```

### JSON Format

Structured JSON output:

```bash
--format-output json
```

### YAML Format

Human-readable YAML:

```bash
--format-output yaml
```

### CSV Format

Comma-separated values:

```bash
--format-output csv
```

## Export Formats

For data extraction, additional formats are supported:

- **JSON**: Standard JSON format
- **CSV**: Comma-separated values
- **Excel**: .xlsx format
- **Parquet**: Columnar storage format for big data
- **YAML**: Human-readable format

## Error Handling

The CLI provides comprehensive error handling:

### Connection Errors

```bash
❌ Connection failed: Unable to connect to host your-wms-host.com
```

### Authentication Errors

```bash
❌ Discovery failed: Authentication failed - invalid credentials
```

### Validation Errors

```bash
❌ Schema missing fields: ['properties', 'type']
```

### API Errors

```bash
❌ Failed to create LPN: Invalid item barcode
```

## Performance Optimization

### High-Speed Extraction

- Use `--high-speed` for paged extraction
- Adjust `--page-size` based on memory and network
- Use Parquet format for large datasets

### Bulk Operations

- Process operations in batches
- Use `--continue-on-error` for resilient processing
- Monitor progress with verbose output

### Caching

- Schema validation caches schemas locally
- Use saved schemas for faster validation

## Integration Examples

### Data Pipeline

```bash
#!/bin/bash
# Extract all entity data for backup

entities=("items" "orders" "locations" "inventory")
for entity in "${entities[@]}"; do
    echo "Extracting ${entity}..."
    flx-http-oracle-wms extract "$entity" "backup/${entity}.parquet" 001 DC1 \
        --format-export parquet --high-speed
done
```

### Daily Operations

```bash
#!/bin/bash
# Daily WMS operations script

# 1. Check system status
flx-http-oracle-wms test-connection

# 2. Process inbound LPNs
flx-http-oracle-wms bulk-operations daily_receives.json receive_lpn

# 3. Generate shipping labels
flx-http-oracle-wms bulk-operations daily_ships.json ship_oblpn

# 4. Export daily reports
flx-http-oracle-wms extract orders "reports/daily_orders_$(date +%Y%m%d).xlsx" 001 DC1 \
    --format-export xlsx
```

## Troubleshooting

### Debug Mode

Enable detailed logging:

```bash
flx-http-oracle-wms --debug --verbose test-connection
```

### Configuration Validation

Test configuration and connection:

```bash
flx-http-oracle-wms show-config --validate-connection
```

### Schema Issues

Validate entity schemas:

```bash
flx-http-oracle-wms get-schema [entity] --validate
```

## Support

For additional support:

1. Use `--help` for command-specific help
2. Enable `--debug --verbose` for detailed logging
3. Validate configuration with `show-config --validate-connection`
4. Check schema validation for entity issues

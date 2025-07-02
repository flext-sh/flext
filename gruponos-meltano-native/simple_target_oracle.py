#!/usr/bin/env python3
"""
Simple Oracle target for testing real data extraction
Receives Singer messages and stores them in Oracle database
"""

import json
import sys
import oracledb
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Load .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"📋 Loaded environment from {env_path}", file=sys.stderr)

def get_oracle_connection():
    """Get Oracle database connection from environment variables"""
    try:
        # Connection details from .env
        host = os.getenv('DATABASE__HOST', '10.93.10.114')
        port = int(os.getenv('DATABASE__PORT', '1522'))
        service_name = os.getenv('DATABASE__SERVICE_NAME', 'gbe8f3f2dbbc562_dwpdb_low.adb.oraclecloud.com')
        username = os.getenv('DATABASE__USERNAME', 'oic')
        password = os.getenv('DATABASE__PASSWORD', '').strip('"')
        protocol = os.getenv('DATABASE__PROTOCOL', 'tcp').lower()
        
        print(f"🔗 Connecting to Oracle Autonomous Database", file=sys.stderr)
        print(f"   Protocol: {protocol}", file=sys.stderr)
        print(f"   Host: {host}:{port}", file=sys.stderr)
        print(f"   Service: {service_name}", file=sys.stderr)
        print(f"   User: {username}", file=sys.stderr)
        
        if protocol == 'tcps':
            # For Oracle Autonomous Database with TCPS
            # Build a proper DSN descriptor for secure connection
            dsn = (
                f"(DESCRIPTION="
                f"(RETRY_COUNT=20)(RETRY_DELAY=3)"
                f"(ADDRESS=(PROTOCOL=tcps)(HOST={host})(PORT={port}))"
                f"(CONNECT_DATA=(SERVICE_NAME={service_name}))"
                f"(SECURITY=(SSL_SERVER_DN_MATCH=no))"
                f")"
            )
            print(f"🔒 Using TCPS secure connection", file=sys.stderr)
        else:
            # Standard TCP connection
            dsn = f"{host}:{port}/{service_name}"
            print(f"📡 Using standard TCP connection", file=sys.stderr)
        
        # Connect to Oracle
        connection = oracledb.connect(
            user=username,
            password=password,
            dsn=dsn
        )
        
        print(f"✅ Connected to Oracle successfully", file=sys.stderr)
        
        # Test connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        result = cursor.fetchone()
        cursor.close()
        print(f"✅ Connection test passed: {result}", file=sys.stderr)
        
        return connection
        
    except Exception as e:
        print(f"❌ Oracle connection failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return None

def create_table_if_not_exists(connection, table_name: str, schema: Dict[str, Any]):
    """Create table if it doesn't exist based on Singer schema"""
    try:
        cursor = connection.cursor()
        
        # Simple column mapping
        columns = []
        for field_name, field_def in schema.get('properties', {}).items():
            # Skip Singer metadata columns - we'll add them separately
            if field_name.startswith('_'):
                continue
                
            field_type = field_def.get('type', 'string')
            
            # Check if it's a date-time field (handle anyOf structure)
            is_datetime = False
            if field_def.get('format') == 'date-time':
                is_datetime = True
            elif 'anyOf' in field_def:
                for option in field_def['anyOf']:
                    if option.get('format') == 'date-time':
                        is_datetime = True
                        break
            
            if is_datetime:
                sql_type = "TIMESTAMP"
            elif field_type == 'string' or (isinstance(field_type, list) and 'string' in field_type):
                max_length = field_def.get('maxLength', 4000)
                sql_type = f"VARCHAR2({min(max_length, 4000)})"
            elif field_type == 'number' or (isinstance(field_type, list) and 'number' in field_type):
                sql_type = "NUMBER"
            elif field_type == 'integer' or (isinstance(field_type, list) and 'integer' in field_type):
                sql_type = "NUMBER(38,0)"
            elif field_type == 'boolean' or (isinstance(field_type, list) and 'boolean' in field_type):
                sql_type = "VARCHAR2(5)"
            else:
                sql_type = "CLOB"
            
            columns.append(f'"{field_name.upper()}" {sql_type}')
        
        # Add Singer metadata columns
        columns.extend([
            '"_EXTRACTED_AT" TIMESTAMP',
            '"_ENTITY_NAME" VARCHAR2(100)',
            '"_LOADED_AT" TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        ])
        
        create_sql = f"""
        CREATE TABLE "{table_name.upper()}" (
            {', '.join(columns)}
        )
        """
        
        try:
            cursor.execute(create_sql)
            connection.commit()
            print(f"📊 Created table {table_name.upper()}", file=sys.stderr)
        except oracledb.DatabaseError as e:
            if "name is already used" in str(e) or "already exists" in str(e):
                print(f"📊 Table {table_name.upper()} already exists", file=sys.stderr)
            else:
                raise
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Error creating table {table_name}: {e}", file=sys.stderr)

def insert_record(connection, table_name: str, record: Dict[str, Any]):
    """Insert a record into the Oracle table"""
    try:
        cursor = connection.cursor()
        
        # Prepare data
        columns = []
        values = []
        placeholders = []
        
        for key, value in record.items():
            # Skip metadata fields - we'll handle them separately
            if key.startswith('_'):
                continue
                
            columns.append(f'"{key.upper()}"')
            
            # Convert values appropriately
            if value is None:
                values.append(None)
            elif isinstance(value, bool):
                values.append('TRUE' if value else 'FALSE')
            elif isinstance(value, (dict, list)):
                values.append(json.dumps(value)[:4000])  # Truncate if too long
            elif isinstance(value, str) and ('T' in value and (':' in value)):
                # Try to parse as timestamp
                try:
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    values.append(dt)
                except:
                    values.append(str(value)[:4000])
            else:
                values.append(str(value)[:4000] if isinstance(value, str) else value)
            
            placeholders.append(':' + str(len(placeholders) + 1))
        
        # Add Singer metadata columns if they exist in the record
        if '_extracted_at' in record:
            columns.append('"_EXTRACTED_AT"')
            # Convert ISO timestamp to Oracle format
            try:
                dt = datetime.fromisoformat(record['_extracted_at'].replace('Z', '+00:00'))
                values.append(dt)
            except:
                values.append(datetime.now())
            placeholders.append(':' + str(len(placeholders) + 1))
        
        if '_entity_name' in record:
            columns.append('"_ENTITY_NAME"')
            values.append(record['_entity_name'])
            placeholders.append(':' + str(len(placeholders) + 1))
        
        # Add standard metadata
        columns.append('"_LOADED_AT"')
        values.append(datetime.now())
        placeholders.append(':' + str(len(placeholders) + 1))
        
        insert_sql = f"""
        INSERT INTO "{table_name.upper()}" 
        ({', '.join(columns)}) 
        VALUES ({', '.join(placeholders)})
        """
        
        cursor.execute(insert_sql, values)
        connection.commit()
        cursor.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error inserting record into {table_name}: {e}", file=sys.stderr)
        print(f"❌ Record: {record}", file=sys.stderr)
        return False

def process_singer_messages():
    """Process Singer messages from stdin"""
    connection = get_oracle_connection()
    if not connection:
        print("❌ Failed to connect to Oracle database", file=sys.stderr)
        sys.exit(1)
    
    schemas = {}
    record_count = 0
    
    print("🎵 Processing Singer messages...", file=sys.stderr)
    
    for line in sys.stdin:
        try:
            message = json.loads(line.strip())
            
            if message.get('type') == 'SCHEMA':
                stream_name = message.get('stream')
                schema = message.get('schema')
                schemas[stream_name] = schema
                
                # Create table
                create_table_if_not_exists(connection, stream_name, schema)
                print(f"📝 Schema received for {stream_name}", file=sys.stderr)
                
            elif message.get('type') == 'RECORD':
                stream_name = message.get('stream')
                record = message.get('record')
                
                if stream_name in schemas:
                    if insert_record(connection, stream_name, record):
                        record_count += 1
                        if record_count % 100 == 0:
                            print(f"📊 Processed {record_count} records for {stream_name}", file=sys.stderr)
                
            elif message.get('type') == 'STATE':
                # Just acknowledge state messages
                print(f"💾 State received: {message.get('value', {})}", file=sys.stderr)
                
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON: {line.strip()}", file=sys.stderr)
        except Exception as e:
            print(f"❌ Error processing message: {e}", file=sys.stderr)
            print(f"❌ Message: {line.strip()}", file=sys.stderr)
    
    connection.close()
    print(f"✅ Finished processing. Total records: {record_count}", file=sys.stderr)

if __name__ == "__main__":
    process_singer_messages()
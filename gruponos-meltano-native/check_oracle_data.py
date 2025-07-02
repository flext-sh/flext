#!/usr/bin/env python3
"""
Check data in Oracle tables
"""

import oracledb
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

def get_connection():
    """Get Oracle connection"""
    host = os.getenv('DATABASE__HOST')
    port = int(os.getenv('DATABASE__PORT'))
    service_name = os.getenv('DATABASE__SERVICE_NAME')
    username = os.getenv('DATABASE__USERNAME')
    password = os.getenv('DATABASE__PASSWORD', '').strip('"')
    protocol = os.getenv('DATABASE__PROTOCOL', 'tcp').lower()
    
    if protocol == 'tcps':
        dsn = (
            f"(DESCRIPTION="
            f"(RETRY_COUNT=20)(RETRY_DELAY=3)"
            f"(ADDRESS=(PROTOCOL=tcps)(HOST={host})(PORT={port}))"
            f"(CONNECT_DATA=(SERVICE_NAME={service_name}))"
            f"(SECURITY=(SSL_SERVER_DN_MATCH=no))"
            f")"
        )
    else:
        dsn = f"{host}:{port}/{service_name}"
    
    return oracledb.connect(user=username, password=password, dsn=dsn)

def check_tables():
    """Check tables created by the target"""
    conn = get_connection()
    cursor = conn.cursor()
    
    print("📊 Tables created by simple_target_oracle:")
    print("-" * 50)
    
    # List tables
    cursor.execute("""
        SELECT table_name 
        FROM user_tables 
        WHERE table_name IN ('ALLOCATION', 'ORDER_HDR', 'ORDER_DTL', 'TEST', 'TEST_TABLE')
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    for table in tables:
        table_name = table[0]
        print(f"\n✅ Table: {table_name}")
        
        # Count records
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"   Records: {count}")
        
        # Show sample data for allocation
        if table_name == 'ALLOCATION' and count > 0:
            cursor.execute(f"""
                SELECT * FROM (
                    SELECT ALLOCATION_ID, ORDER_ID, STATUS, QUANTITY, 
                           TO_CHAR("_SDC_BATCHED_AT", 'YYYY-MM-DD HH24:MI:SS') as LOADED_AT
                    FROM {table_name}
                    ORDER BY "_SDC_BATCHED_AT" DESC
                ) WHERE ROWNUM <= 5
            """)
            
            print("\n   Sample records:")
            for row in cursor.fetchall():
                print(f"   - {row[0]} | {row[1]} | {row[2]} | Qty: {row[3]} | Loaded: {row[4]}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_tables()
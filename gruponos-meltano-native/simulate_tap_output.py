#!/usr/bin/env python3
"""
Simulate tap-oracle-wms output for testing the target
"""

import json
import sys
from datetime import datetime, timedelta
import random

def generate_allocation_record(i):
    """Generate a realistic allocation record"""
    now = datetime.utcnow()
    created = now - timedelta(hours=random.randint(1, 48))
    
    return {
        "allocation_id": f"ALLOC-{i:06d}",
        "order_id": f"ORD-{random.randint(1000, 9999):06d}",
        "item_id": f"ITEM-{random.randint(100, 999):04d}",
        "from_location": f"LOC-{random.randint(1, 100):03d}",
        "to_location": f"STAGE-{random.randint(1, 10):02d}",
        "quantity": random.randint(1, 100),
        "status": random.choice(["PENDING", "IN_PROGRESS", "COMPLETED"]),
        "priority": random.randint(1, 5),
        "created_date_utc": created.isoformat() + "Z",
        "last_update_date_utc": (created + timedelta(minutes=random.randint(0, 60))).isoformat() + "Z",
        "user_id": f"USER-{random.randint(1, 20):03d}",
        "warehouse_id": "WH-001"
    }

def main():
    # Send schema
    schema = {
        "type": "SCHEMA",
        "stream": "allocation",
        "schema": {
            "type": "object",
            "properties": {
                "allocation_id": {"type": "string"},
                "order_id": {"type": "string"},
                "item_id": {"type": "string"},
                "from_location": {"type": "string"},
                "to_location": {"type": "string"},
                "quantity": {"type": "integer"},
                "status": {"type": "string"},
                "priority": {"type": "integer"},
                "created_date_utc": {"type": "string", "format": "date-time"},
                "last_update_date_utc": {"type": "string", "format": "date-time"},
                "user_id": {"type": "string"},
                "warehouse_id": {"type": "string"}
            }
        },
        "key_properties": ["allocation_id"]
    }
    
    print(json.dumps(schema))
    sys.stdout.flush()
    
    # Send records
    num_records = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    for i in range(1, num_records + 1):
        record = {
            "type": "RECORD",
            "stream": "allocation",
            "record": generate_allocation_record(i)
        }
        print(json.dumps(record))
        sys.stdout.flush()
    
    # Send state
    state = {
        "type": "STATE",
        "value": {
            "bookmarks": {
                "allocation": {
                    "replication_key_value": datetime.utcnow().isoformat() + "Z",
                    "partitions": []
                }
            }
        }
    }
    print(json.dumps(state))
    sys.stdout.flush()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Test tap-oracle-wms directly without meltano
"""

import json
import os

# Load environment
from dotenv import load_dotenv

load_dotenv()

# Configuration
tap_config = {
    "base_url": os.getenv("WMS_BASE_URL"),
    "username": os.getenv("WMS_USERNAME"),
    "password": os.getenv("WMS_PASSWORD"),
    "api_key": os.getenv("WMS_API_KEY"),
    "timeout": 300,
    "page_size": 10,
    "start_date": "2025-06-01T00:00:00Z",
}

# Simple catalog for allocation
catalog = {
    "streams": [
        {
            "tap_stream_id": "allocation",
            "stream": "allocation",
            "schema": {"type": "object", "properties": {}},
            "metadata": [
                {
                    "breadcrumb": [],
                    "metadata": {
                        "inclusion": "selected",
                        "selected": True,
                        "table-key-properties": [],
                        "forced-replication-method": "incremental",
                        "replication-key": "last_update_date_utc",
                    },
                }
            ],
        }
    ]
}

# Write config files
with open("test_tap_config.json", "w") as f:
    json.dump(tap_config, f)

with open("test_catalog.json", "w") as f:
    json.dump(catalog, f)

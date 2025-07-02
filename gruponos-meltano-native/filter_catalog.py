#!/usr/bin/env python3
"""Filter catalog to only include required entities."""

import json
import sys

# Entities we want
REQUIRED_ENTITIES = ["allocation", "order_hdr", "order_dtl"]

# Read the full catalog
with open("catalog_clean.json", "r") as f:
    catalog = json.load(f)

# Filter streams
filtered_streams = []
for stream in catalog.get("streams", []):
    if stream.get("tap_stream_id") in REQUIRED_ENTITIES:
        # Enable selection
        stream["metadata"][0]["metadata"]["selected"] = True
        stream["metadata"][0]["metadata"]["replication-method"] = "INCREMENTAL"
        stream["metadata"][0]["metadata"]["replication-key"] = "mod_ts"
        filtered_streams.append(stream)
        print(f"✓ Found entity: {stream['tap_stream_id']}")

# Create filtered catalog
filtered_catalog = {
    "streams": filtered_streams
}

# Save filtered catalog
with open("catalog_filtered.json", "w") as f:
    json.dump(filtered_catalog, f, indent=2)

print(f"\n✅ Filtered catalog created with {len(filtered_streams)} entities")
print("📁 Saved to: catalog_filtered.json")
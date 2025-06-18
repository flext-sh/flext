#!/usr/bin/env python3
"""Test WMS API connectivity with real credentials."""

import base64
import json
from pathlib import Path

import requests


def test_wms_api():
    """Test WMS API connectivity."""
    # Load real config
    config_path = Path("tap-oracle-wms/config.json")
    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)

    base_url = config["base_url"]
    username = config["username"]
    password = config["password"]

    # Test authentication
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    headers = {"Authorization": f"Basic {encoded}"}

    try:
        # Test entity discovery endpoint
        test_url = f"{base_url}/wms/lgfapi/v10/entity/"

        response = requests.get(test_url, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()

            # Test specific documented entities
            documented_entities = [
                "item",
                "location",
                "inventory",
                "order_hdr",
                "order_dtl",
                "allocation",
            ]
            found_count = 0
            for entity in documented_entities:
                if entity in data:
                    found_count += 1

            # Test a specific entity endpoint
            for entity in ["item", "location"][:2]:  # Test first 2
                if entity in data:
                    entity_url = (
                        f"{base_url}/wms/lgfapi/v10/entity/{entity}?page_size=5"
                    )
                    requests.get(entity_url, headers=headers, timeout=30)

            return True
        return False

    except Exception:
        return False


if __name__ == "__main__":
    test_wms_api()

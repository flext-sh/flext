#!/usr/bin/env python3
"""
Test script for FLX REST API functionality.

This script demonstrates how the CLI commands are automatically exposed
via REST API endpoints, including plugin commands.
"""

import json
import time
from threading import Thread

import requests


def start_api_server():
    """Start the REST API server in background."""
    import uvicorn
    from flx.adapters.inbound.rest_api import create_rest_api

    from flx.adapters.inbound.fire_cli import create_cli

    cli = create_cli()
    app = create_rest_api(cli=cli)

    # Run server in thread
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")


def test_api_endpoints():
    """Test various API endpoints."""
    base_url = "http://127.0.0.1:8000"

    time.sleep(3)

    # Test cases
    test_cases = [
        {
            "name": "Health Check",
            "method": "GET",
            "url": f"{base_url}/health",
            "expected_status": 200,
        },
        {
            "name": "API Info",
            "method": "GET",
            "url": f"{base_url}/api/v1/info",
            "expected_status": 200,
        },
        {
            "name": "App Status",
            "method": "GET",
            "url": f"{base_url}/api/v1/app/status",
            "expected_status": 200,
        },
        {
            "name": "System Health",
            "method": "GET",
            "url": f"{base_url}/api/v1/system/health",
            "expected_status": 200,
        },
        {
            "name": "Database Status (Plugin)",
            "method": "GET",
            "url": f"{base_url}/api/v1/database/status",
            "expected_status": 200,
        },
        {
            "name": "Database Backup (Plugin)",
            "method": "POST",
            "url": f"{base_url}/api/v1/database/backup",
            "data": {"parameters": {"path": "/tmp/test-backup.sql", "compress": True}},
            "expected_status": 200,
        },
        {
            "name": "Monitoring Alerts (Plugin)",
            "method": "GET",
            "url": f"{base_url}/api/v1/monitoring/alerts?severity=critical",
            "expected_status": 200,
        },
        {
            "name": "System Report (Dynamic Command)",
            "method": "POST",
            "url": f"{base_url}/api/v1/system-report",
            "data": {"parameters": {"format": "json"}},
            "expected_status": 200,
        },
    ]

    results = []

    for test in test_cases:
        try:

            if test["method"] == "GET":
                response = requests.get(test["url"], timeout=10)
            elif test["method"] == "POST":
                headers = {"Content-Type": "application/json"}
                data = json.dumps(test.get("data", {}))
                response = requests.post(
                    test["url"], data=data, headers=headers, timeout=10
                )

            success = response.status_code == test["expected_status"]

            if success and response.headers.get("content-type", "").startswith(
                "application/json"
            ):
                try:
                    json_data = response.json()
                    if "success" in json_data:
                        # Plugin command response
                        json_data.get("execution_time_ms", 0)
                        if json_data["success"]:
                            pass
                    else:
                        # Direct response
                        pass
                except:
                    pass

            results.append(
                {
                    "test": test["name"],
                    "success": success,
                    "status_code": response.status_code,
                    "url": test["url"],
                }
            )

        except requests.exceptions.RequestException as e:
            results.append(
                {
                    "test": test["name"],
                    "success": False,
                    "error": str(e),
                    "url": test["url"],
                }
            )

    # Summary

    passed = sum(1 for r in results if r["success"])
    total = len(results)

    if passed == total:
        pass


if __name__ == "__main__":
    # Start API server in background thread
    server_thread = Thread(target=start_api_server, daemon=True)
    server_thread.start()

    # Run tests
    test_api_endpoints()

    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

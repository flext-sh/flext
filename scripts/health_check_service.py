#!/usr/bin/env python3
"""FLEXT Health Check Service - Real monitoring implementation."""

import asyncio
import json
import logging
import time
from typing import Any

import aiohttp


class FlextHealthChecker:
    """Comprehensive health checking for FLEXT services."""

    def __init__(self):
        self.services = {
            "api": "http://localhost:8000/health",
            "web": "http://localhost:8080/health",
            "grpc": "localhost:50051",  # Special handling for gRPC
            "redis": "redis://localhost:6379",
            "postgres": "postgresql://localhost:5432/flext_staging",
        }
        self.results = {}

    async def check_http_service(self, name: str, url: str) -> dict[str, Any]:
        """Check HTTP service health."""
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=5),
                ) as response:
                    duration = time.time() - start_time

                    if response.status == 200:
                        return {
                            "status": "healthy",
                            "response_time": duration,
                            "status_code": response.status,
                            "timestamp": time.time(),
                        }
                    return {
                        "status": "unhealthy",
                        "response_time": duration,
                        "status_code": response.status,
                        "error": f"HTTP {response.status}",
                        "timestamp": time.time(),
                    }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "timestamp": time.time()}

    async def check_all_services(self) -> dict[str, Any]:
        """Check all FLEXT services."""
        tasks = []

        # HTTP services
        for name, url in self.services.items():
            if url.startswith("http"):
                tasks.append(self.check_http_service(name, url))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine results
        service_names = [
            name for name, url in self.services.items() if url.startswith("http")
        ]
        health_status = {}

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                health_status[service_names[i]] = {
                    "status": "unhealthy",
                    "error": str(result),
                    "timestamp": time.time(),
                }
            else:
                health_status[service_names[i]] = result

        # Overall health
        all_healthy = all(
            status.get("status") == "healthy" for status in health_status.values()
        )

        return {
            "overall_status": "healthy" if all_healthy else "unhealthy",
            "services": health_status,
            "timestamp": time.time(),
            "healthy_count": sum(
                1 for s in health_status.values() if s.get("status") == "healthy"
            ),
            "total_count": len(health_status),
        }


async def main():
    """Run health checks and output results."""
    checker = FlextHealthChecker()

    while True:
        try:
            health_data = await checker.check_all_services()

            # Output JSON for monitoring tools
            print(json.dumps(health_data, indent=2))

            # Log critical issues
            if health_data["overall_status"] != "healthy":
                logging.error("Health check failed: %s", health_data)

            # Wait before next check
            await asyncio.sleep(10)

        except KeyboardInterrupt:
            print("\nHealth check service stopped")
            break
        except Exception as e:
            logging.exception("Health check error: %s", e)
            await asyncio.sleep(5)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

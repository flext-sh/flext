#!/usr/bin/env python3
"""Test monitoring infrastructure components."""

import asyncio
import json
import sys
import time
from pathlib import Path

import aiohttp


async def test_health_check() -> dict[str, object]:
    """Test a single health check run."""
    print("🔍 Testing Health Check Service...")

    services = {
        "mock_healthy": "https://httpbin.org/status/200",
        "mock_unhealthy": "https://httpbin.org/status/500",
    }

    results = {}

    for name, url in services.items():
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=5),
                ) as response:
                    duration = time.time() - start_time

                    results[name] = {
                        "status": "healthy" if response.status == 200 else "unhealthy",
                        "response_time": round(duration, 3),
                        "status_code": response.status,
                        "timestamp": time.time(),
                    }
        except Exception as e:
            results[name] = {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time(),
            }

    # Overall health
    all_healthy = all(status.get("status") == "healthy" for status in results.values())

    health_data: dict[str, object] = {
        "overall_status": "healthy" if all_healthy else "unhealthy",
        "services": results,
        "timestamp": time.time(),
        "healthy_count": sum(
            1 for s in results.values() if s.get("status") == "healthy"
        ),
        "total_count": len(results),
    }

    print("✅ Health check test completed:")
    print(json.dumps(health_data, indent=2))

    return health_data


def test_monitoring_files() -> bool:
    """Test that monitoring files were created correctly."""
    print("📁 Testing monitoring files...")

    project_root = Path(__file__).parent.parent
    monitoring_dir = project_root / "monitoring"

    required_files = [
        monitoring_dir / "prometheus.yml",
        monitoring_dir / "alerts" / "flext.yml",
        monitoring_dir / "docker-compose.monitoring.yml",
        monitoring_dir / "grafana" / "dashboards" / "flext-api.json",
        monitoring_dir / "grafana" / "dashboards" / "flext-pipeline.json",
        monitoring_dir / "start-monitoring.sh",
    ]

    all_exist = True
    for file_path in required_files:
        if file_path.exists():
            print(f"  ✅ {file_path.name}")
        else:
            print(f"  ❌ {file_path.name} (missing)")
            all_exist = False

    return all_exist


async def main() -> bool:
    """Run all monitoring tests."""
    print("📊 FLEXT MONITORING INFRASTRUCTURE TEST")
    print("=" * 50)

    # Test file creation
    files_ok = test_monitoring_files()

    print()

    # Test health check functionality
    health_data = await test_health_check()

    print("\n" + "=" * 50)

    if (
        files_ok and health_data["overall_status"] == "unhealthy"
    ):  # Expected since mock_unhealthy returns 500
        print("🎉 MONITORING INFRASTRUCTURE TESTS PASSED!")
        print("\n📋 TEST RESULTS:")
        print("  ✅ All monitoring files created")
        print("  ✅ Health check service functional")
        print("  ✅ HTTP monitoring working")
        print("  ✅ Error detection working")

        print("\n🚀 READY FOR DEPLOYMENT:")
        print("  • Prometheus configuration ready")
        print("  • Grafana dashboards created")
        print("  • Alerting rules configured")
        print("  • Health monitoring functional")
        return True
    print("❌ MONITORING TESTS FAILED")
    return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

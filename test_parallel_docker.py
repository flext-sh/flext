#!/usr/bin/env python3
"""Test parallel Docker container management across FLEXT projects.

This script tests the ParallelDockerManager by simulating concurrent
test execution from flext-ldap, flext-ldif, and client-a-oud-mig.
"""

import concurrent.futures
import sys
import time

sys.path.insert(0, "/home/marlonsc/flext/flext-core/src")

from flext_tests.parallel_docker import (
    ParallelDockerManager,
    get_client-a_oud_container,
    get_shared_openldap_container,
    release_client-a_oud_container,
    release_shared_openldap_container,
)


def simulate_flext_ldap_test(test_id: str) -> tuple[str, bool, str]:
    """Simulate flext-ldap test using shared OpenLDAP container."""
    try:
        container_result = get_shared_openldap_container()

        if container_result.is_failure:
            return (
                test_id,
                False,
                f"Failed to get container: {container_result.error}",
            )

        container_result.unwrap()

        # Simulate test execution
        time.sleep(2)

        release_result = release_shared_openldap_container()

        if release_result.is_failure:
            return (test_id, False, f"Failed to release: {release_result.error}")

        return (test_id, True, "LDAP test completed successfully")

    except Exception as e:
        return (test_id, False, f"Exception: {e}")


def simulate_flext_ldif_test(test_id: str) -> tuple[str, bool, str]:
    """Simulate flext-ldif test using shared OpenLDAP container."""
    try:
        container_result = get_shared_openldap_container()

        if container_result.is_failure:
            return (
                test_id,
                False,
                f"Failed to get container: {container_result.error}",
            )

        container_result.unwrap()

        # Simulate test execution
        time.sleep(3)

        release_result = release_shared_openldap_container()

        if release_result.is_failure:
            return (test_id, False, f"Failed to release: {release_result.error}")

        return (test_id, True, "LDIF test completed successfully")

    except Exception as e:
        return (test_id, False, f"Exception: {e}")


def simulate_client-a_oud_mig_test(test_id: str) -> tuple[str, bool, str]:
    """Simulate client-a-oud-mig test using client-a OUD container."""
    try:
        container_result = get_client-a_oud_container()

        if container_result.is_failure:
            return (
                test_id,
                False,
                f"Failed to get container: {container_result.error}",
            )

        container_result.unwrap()

        # Simulate test execution
        time.sleep(2)

        release_result = release_client-a_oud_container()

        if release_result.is_failure:
            return (test_id, False, f"Failed to release: {release_result.error}")

        return (test_id, True, "client-a test completed successfully")

    except Exception as e:
        return (test_id, False, f"Exception: {e}")


def main() -> None:
    """Test parallel container management."""
    # Check port conflicts first
    manager = ParallelDockerManager()
    port_check = manager.check_port_conflicts()

    if port_check.is_failure:
        return

    port_check.unwrap()

    # Create test scenarios simulating parallel execution
    test_scenarios = [
        ("ldap-1", simulate_flext_ldap_test),
        ("ldif-1", simulate_flext_ldif_test),
        ("client-a-1", simulate_client-a_oud_mig_test),
        ("ldap-2", simulate_flext_ldap_test),  # Second LDAP test (should share)
        ("ldif-2", simulate_flext_ldif_test),  # Second LDIF test (should share)
        ("client-a-2", simulate_client-a_oud_mig_test),  # Second client-a test (should share)
    ]

    # Execute tests in parallel
    results: list[tuple[str, bool, str]] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        # Submit all test scenarios
        futures = {
            executor.submit(test_func, test_id): test_id
            for test_id, test_func in test_scenarios
        }

        # Collect results
        for future in concurrent.futures.as_completed(futures):
            test_id = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append((test_id, False, f"Future exception: {e}"))

    # Display results
    successful = 0
    failed = 0

    for test_id, success, _message in sorted(results):
        if success:
            successful += 1
        else:
            failed += 1

    # Show container status
    manager.get_active_containers()

    # Summary

    if failed == 0:
        pass


if __name__ == "__main__":
    main()

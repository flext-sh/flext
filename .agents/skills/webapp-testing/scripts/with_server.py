#!/usr/bin/env python3
"""AI Hub governance hook projection: with_server.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

# Copyright (c) 2025 FLEXT Team. All rights reserved.
import shlex
import socket
import subprocess
import sys
import time

"""Start one or more servers, wait for them to be ready, run a command, then clean up.

Usage:
    # Single server
    python scripts/with_server.py --server "npm run dev" --port 5173 \
      -- python automation.py
    python scripts/with_server.py --server "npm start" --port 3000 \
      -- python test.py

    # Multiple servers
    python scripts/with_server.py \
      --server "cd backend && python server.py" --port 3000 \
      --server "cd frontend && npm run dev" --port 5173 \
      -- python test.py
"""


DEFAULT_SERVER_TIMEOUT = 30
SERVER_WAIT_SECONDS = 0.5
PROCESS_SHUTDOWN_LIMIT = 5
READY_POLL_INTERVAL = 1


def is_server_ready(port: int, timeout: int = DEFAULT_SERVER_TIMEOUT) -> bool:
    """Wait for server to be ready by polling the port.

    Args:
        port: Port the server should accept connections on.
        timeout: Maximum seconds to wait for readiness.

    Returns:
        True when the port accepts a connection within the timeout.

    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection(
                ("localhost", port),
                timeout=READY_POLL_INTERVAL,
            ):
                return True
        except (OSError, ConnectionRefusedError):
            time.sleep(SERVER_WAIT_SECONDS)
    return False


USAGE = """usage: with_server.py --server CMD --port PORT [--timeout N] [-- CMD ...]

Run one command once every server answers on its port, then clean the servers up."""


class UsageError(ValueError):
    """Invalid command-line usage reported to the caller."""


def _consume_option(
    argv: list[str],
    handled: int,
) -> tuple[str, object, int]:
    """Consume one option spell and its value from the argument list.

    Args:
        argv: Remaining command-line arguments.
        handled: Index of the option spell in argv.

    Returns:
        Tuple of option name, parsed value, and next index.

    Raises:
        UsageError: If the option is unknown or its value is missing.

    """
    spell = argv[handled]
    handled += 1
    if handled >= len(argv):
        msg = f"Missing value for {spell}"
        raise UsageError(msg)
    value: object = argv[handled]
    if spell in {"--port", "--timeout"}:
        value = int(str(value))
    elif spell != "--server":
        msg = f"Unknown option: {spell}"
        raise UsageError(msg)
    return spell, value, handled + 1


def parse_args(argv: list[str]) -> dict[str, object]:
    """Parse the with_server invocation without a CLI framework.

    Args:
        argv: Command-line arguments excluding the program name.

    Returns:
        Parsed servers, ports, timeout, and trailing command.

    Raises:
        UsageError: If the arguments are invalid.

    """
    if "--" in argv:
        separator = argv.index("--")
        trailing = argv[separator + 1 :]
        argv = argv[:separator]
    else:
        trailing = []

    if not trailing:
        msg = "a command must follow --"
        raise UsageError(msg)

    servers: list[str] = []
    ports: list[int] = []
    timeout: int = DEFAULT_SERVER_TIMEOUT
    handled = 0
    while handled < len(argv):
        spell, value, handled = _consume_option(argv, handled)
        if spell == "--server":
            servers.append(str(value))
        elif spell == "--port":
            ports.append(int(str(value)))
        else:
            timeout = int(str(value))

    if not servers or len(servers) != len(ports):
        msg_0 = "--port count must match --server count"
        raise UsageError(msg_0)

    return {"servers": servers, "ports": ports, "timeout": timeout, "command": trailing}


def _raise_not_started(port: int, timeout: int) -> None:
    sentinel = f"Server failed to start on port {port} within {timeout}s"
    raise RuntimeError(sentinel)


def main() -> None:
    """Start servers, run the trailing command, and clean the servers up."""
    try:
        args = parse_args(sys.argv[1:])
    except UsageError as e:
        sys.stderr.write(f"with_server.py: error: {e}\n{USAGE}\n")
        sys.exit(1)

    servers = [
        {"cmd": cmd, "port": port}
        for cmd, port in zip(args["servers"], args["ports"], strict=True)
    ]
    timeout: int = args["timeout"]
    command: list[str] = args["command"]

    server_processes = []
    try:
        for server in servers:
            server_argv = shlex.split(server["cmd"])
            process = subprocess.Popen(
                server_argv,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            server_processes.append(process)

            if not is_server_ready(server["port"], timeout=timeout):
                _raise_not_started(server["port"], timeout)

        runner = subprocess.run(command, check=False)
        sys.exit(runner.returncode)
    finally:
        for process in server_processes:
            try:
                process.terminate()
                process.wait(timeout=PROCESS_SHUTDOWN_LIMIT)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


if __name__ == "__main__":
    main()

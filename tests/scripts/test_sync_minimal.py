#!/usr/bin/env python3
"""Teste mínimo do sync_dependencies.py."""

import subprocess
import sys
import time


def run_with_timeout(cmd: list[str], timeout_sec: int = 10) -> None:
    """Executa comando com timeout e captura saída."""
    print(f"Executando: {' '.join(cmd)}")
    print(f"Timeout: {timeout_sec}s")
    print("-" * 60)

    start = time.time()

    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
        )

        output_lines = []

        while True:
            line = proc.stdout.readline() if proc.stdout else ""
            if not line and proc.poll() is not None:
                break

            if line:
                line = line.rstrip()
                print(line)
                output_lines.append(line)

            # Check timeout
            if time.time() - start > timeout_sec:
                print(f"\n⏰ TIMEOUT após {timeout_sec}s!")
                proc.terminate()
                proc.wait(timeout=5)
                break

        elapsed = time.time() - start
        print(f"\n⏱️ Tempo total: {elapsed:.1f}s")

        # Analisa onde parou
        if output_lines:
            print("\n📍 Última linha antes do timeout:")
            print(f"   {output_lines[-1]}")

            # Procura por menções a projetos
            for i, line in enumerate(output_lines[-10:]):
                if "flext-" in line:
                    print(f"\n🔍 Linha {i}: {line}")

    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    cmd = [
        sys.executable,
        "scripts/sync_dependencies.py",
        "--projects",
        "flext-web",
        "--discover-missing",
        "--dry-run",
    ]

    run_with_timeout(cmd, timeout_sec=15)

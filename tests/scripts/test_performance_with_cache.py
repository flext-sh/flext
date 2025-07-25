#!/usr/bin/env python3
"""Testa performance do sync_dependencies.py com e sem cache."""

import subprocess
import sys
import time


def measure_execution_time(cmd: list[str], description: str) -> tuple[float, bool]:
    """Mede tempo de execução de um comando."""
    print(f"\n🕐 {description}")
    print(f"📍 Comando: {' '.join(cmd)}")

    start_time = time.time()

    try:
        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutos máximo
        )

        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(f"✅ Sucesso em {elapsed:.2f} segundos")
        else:
            print(f"❌ Falhou em {elapsed:.2f} segundos")

        return elapsed, result.returncode == 0

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print(f"❌ Timeout após {elapsed:.2f} segundos")
        return elapsed, False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 0, False


def main() -> int:
    """Testa performance."""
    print("🔬 TESTE DE PERFORMANCE COM CACHE")
    print("=" * 60)

    base_cmd = [
        sys.executable,
        "/home/marlonsc/flext/scripts/sync_dependencies.py",
        "--projects",
        "flext-web",
        "--discover-missing",
        "--dry-run",
    ]

    # Teste 1: Limpa cache primeiro
    print("\n1️⃣ Limpando cache...")
    clear_cmd = [
        sys.executable,
        "/home/marlonsc/flext/scripts/sync_dependencies.py",
        "--clear-cache",
    ]
    subprocess.run(clear_cmd, check=False, capture_output=True)

    # Teste 2: Primeira execução (sem cache)
    time1, _success1 = measure_execution_time(base_cmd, "Primeira execução (SEM cache)")

    # Teste 3: Segunda execução (com cache)
    time2, _success2 = measure_execution_time(base_cmd, "Segunda execução (COM cache)")

    # Teste 4: Terceira execução (confirmação)
    time3, _success3 = measure_execution_time(base_cmd, "Terceira execução (COM cache)")

    # Análise
    print("\n📊 ANÁLISE DE PERFORMANCE:")
    print("=" * 60)

    if time1 > 0 and time2 > 0:
        speedup = time1 / time2
        improvement = (time1 - time2) / time1 * 100

        print(f"Tempo SEM cache: {time1:.2f}s")
        print(f"Tempo COM cache: {time2:.2f}s (média: {(time2 + time3) / 2:.2f}s)")
        print(f"Melhoria: {improvement:.1f}%")
        print(f"Speedup: {speedup:.1f}x mais rápido")

        if speedup > 2:
            print("🚀 Cache está fazendo GRANDE diferença!")
        elif speedup > 1.5:
            print("✅ Cache está melhorando performance significativamente")
        elif speedup > 1.1:
            print("📈 Cache está ajudando um pouco")
        else:
            print("⚠️ Cache não está fazendo muita diferença")

    # Teste com discover_missing_deps.py para comparação
    print("\n🔍 Comparação com discover_missing_deps.py:")
    alt_cmd = [
        sys.executable,
        "/home/marlonsc/flext/scripts/discover_missing_deps.py",
        "flext-web",
    ]

    time_alt, _ = measure_execution_time(
        alt_cmd, "discover_missing_deps.py (referência)",
    )

    if time_alt > 0 and time2 > 0:
        print(f"\nsync_dependencies.py (com cache): {time2:.2f}s")
        print(f"discover_missing_deps.py: {time_alt:.2f}s")

        if time2 < time_alt:
            print("✅ sync_dependencies.py com cache é mais rápido!")
        else:
            ratio = time2 / time_alt
            print(f"⚠️ sync_dependencies.py ainda é {ratio:.1f}x mais lento")

    # Mostra estatísticas do cache
    print("\n📦 ESTATÍSTICAS DO CACHE:")
    subprocess.run(
        [
            sys.executable,
            "-c",
            "from dependency_cache import cache_stats; cache_stats()",
        ],
        check=False,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())

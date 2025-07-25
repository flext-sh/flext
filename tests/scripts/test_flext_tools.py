#!/usr/bin/env python3
"""Script de teste para verificar funcionamento da biblioteca flext_tools.

Testa cada módulo e funcionalidade principal.
"""

import sys
import time
from pathlib import Path

# Adiciona scripts ao path para importar flext_tools
sys.path.insert(0, str(Path(__file__).parent))

from flext_tools import (
    CacheManager,
    Colors,
    ConflictAnalyzer,
    DependencyDiscovery,
    PoetryOperations,
    PoetryValidator,
    VersionAnalyzer,
    cached,
    get_stdlib_modules,
    print_colored,
    should_ignore_path,
)


def test_imports() -> bool:
    """Testa se todos os imports funcionam."""
    print_colored("1️⃣ Testando imports...", Colors.BLUE)

    # Lista de classes que devem estar disponíveis
    required_classes = [
        DependencyDiscovery,
        ConflictAnalyzer,
        PoetryValidator,
        PoetryOperations,
        VersionAnalyzer,
        CacheManager,
    ]

    for cls in required_classes:
        try:
            cls()
            print_colored(f"  ✅ {cls.__name__}: OK", Colors.GREEN)
        except Exception as e:
            print_colored(f"  ❌ {cls.__name__}: ERRO - {e}", Colors.RED)
            return False

    return True


def test_utils() -> bool:
    """Testa utilitários básicos."""
    print_colored("\n2️⃣ Testando utilitários...", Colors.BLUE)

    # Testa cores
    try:
        print_colored("  🎨 Teste de cores", Colors.CYAN)
        print_colored("  ✅ Cores funcionando", Colors.GREEN)
    except Exception as e:
        print_colored(f"  ❌ Erro nas cores: {e}", Colors.RED)
        return False

    # Testa stdlib modules
    try:
        stdlib = get_stdlib_modules()
        if len(stdlib) > 100:  # Deve ter muitos módulos
            print_colored(
                f"  ✅ Stdlib: {len(stdlib)} módulos detectados", Colors.GREEN,
            )
        else:
            print_colored(f"  ⚠️ Stdlib: apenas {len(stdlib)} módulos", Colors.YELLOW)
    except Exception as e:
        print_colored(f"  ❌ Erro na stdlib: {e}", Colors.RED)
        return False

    # Testa filtros de path
    try:
        test_paths = [
            Path("/normal/path/file.py"),
            Path("/archive/old/file.py"),
            Path("/node_modules/pkg/file.js"),
            Path("/.git/config"),
        ]

        filtered = [p for p in test_paths if should_ignore_path(p)]
        if len(filtered) == 3:  # Deve filtrar 3 dos 4
            print_colored("  ✅ Filtros de path funcionando", Colors.GREEN)
        else:
            print_colored(
                f"  ⚠️ Filtros: esperado 3, obtido {len(filtered)}", Colors.YELLOW,
            )
    except Exception as e:
        print_colored(f"  ❌ Erro nos filtros: {e}", Colors.RED)
        return False

    return True


def test_cache() -> bool:
    """Testa sistema de cache."""
    print_colored("\n3️⃣ Testando sistema de cache...", Colors.BLUE)

    try:
        # Testa cache manager direto
        cache = CacheManager()

        # Set/Get básico
        cache.set("test_key", "test_value", ttl=60)
        value = cache.get("test_key")

        if value == "test_value":
            print_colored("  ✅ Cache básico funcionando", Colors.GREEN)
        else:
            print_colored(f"  ❌ Cache retornou: {value}", Colors.RED)
            return False

        # Testa decorador cached
        @cached(namespace="test", ttl=60)
        def expensive_function(x):
            time.sleep(0.01)  # Simula operação custosa
            return x * 2

        # Primeira chamada (miss)
        result1 = expensive_function(5)

        # Segunda chamada (hit)
        result2 = expensive_function(5)

        if result1 == result2 == 10:
            print_colored("  ✅ Decorador @cached funcionando", Colors.GREEN)
        else:
            print_colored(f"  ❌ Decorador falhou: {result1}, {result2}", Colors.RED)
            return False

        # Testa estatísticas
        stats = expensive_function.cache_stats()
        if stats["hits"] >= 1:
            print_colored(
                f"  ✅ Stats: {stats['hits']} hits, {stats['misses']} misses",
                Colors.GREEN,
            )
        else:
            print_colored(f"  ⚠️ Stats inesperadas: {stats}", Colors.YELLOW)

    except Exception as e:
        print_colored(f"  ❌ Erro no cache: {e}", Colors.RED)
        return False

    return True


def test_discovery() -> bool:
    """Testa descoberta de dependências."""
    print_colored("\n4️⃣ Testando descoberta de dependências...", Colors.BLUE)

    try:
        discovery = DependencyDiscovery()

        # Testa em projeto real
        workspace_path = Path.cwd()

        # Procura por um projeto válido
        test_project = None
        for pyproject in workspace_path.rglob("pyproject.toml"):
            if not any(
                skip in str(pyproject) for skip in ["archive", "backup", "node_modules"]
            ):
                test_project = pyproject.parent
                break

        if test_project:
            result = discovery.discover_project_dependencies(test_project)

            if isinstance(result, dict) and "runtime" in result:
                print_colored(
                    f"  ✅ Descoberta OK em {test_project.name}", Colors.GREEN,
                )

                # Mostra sample dos resultados
                total = sum(len(deps) for deps in result.values())
                print_colored(f"    📊 {total} dependências descobertas", Colors.CYAN)
            else:
                print_colored(f"  ❌ Resultado inválido: {result}", Colors.RED)
                return False
        else:
            print_colored("  ⚠️ Nenhum projeto encontrado para teste", Colors.YELLOW)

    except Exception as e:
        print_colored(f"  ❌ Erro na descoberta: {e}", Colors.RED)
        return False

    return True


def test_version_analysis() -> bool:
    """Testa análise de versões."""
    print_colored("\n5️⃣ Testando análise de versões...", Colors.BLUE)

    try:
        analyzer = VersionAnalyzer()

        # Testa parsing de versões
        name, spec = analyzer.parse_version_spec("django>=3.2,<4.0")
        if name == "django" and spec == ">=3.2,<4.0":
            print_colored("  ✅ Parsing de versões OK", Colors.GREEN)
        else:
            print_colored(f"  ❌ Parsing falhou: {name}, {spec}", Colors.RED)
            return False

        # Testa normalização
        normalized = analyzer.normalize_constraint("^1.2.3")
        if ">=1.2.3" in normalized and "<2.0.0" in normalized:
            print_colored("  ✅ Normalização de constraints OK", Colors.GREEN)
        else:
            print_colored(f"  ⚠️ Normalização: {normalized}", Colors.YELLOW)

        # Testa compatibilidade
        compat = analyzer.check_version_compatibility([">=1.0", "<2.0"], "test")
        if isinstance(compat, dict) and "compatible" in compat:
            print_colored("  ✅ Análise de compatibilidade OK", Colors.GREEN)
        else:
            print_colored(f"  ❌ Compatibilidade falhou: {compat}", Colors.RED)
            return False

    except Exception as e:
        print_colored(f"  ❌ Erro na análise: {e}", Colors.RED)
        return False

    return True


def test_poetry_operations() -> bool:
    """Testa operações Poetry."""
    print_colored("\n6️⃣ Testando operações Poetry...", Colors.BLUE)

    try:
        # Sempre em modo dry-run para testes
        ops = PoetryOperations(dry_run=True)
        validator = PoetryValidator()

        # Testa validação
        workspace_path = Path.cwd()

        # Procura projeto para validar
        test_project = None
        for pyproject in workspace_path.rglob("pyproject.toml"):
            if not any(
                skip in str(pyproject) for skip in ["archive", "backup", "node_modules"]
            ):
                test_project = pyproject.parent
                break

        if test_project:
            validation = validator.validate_project(test_project)

            if isinstance(validation, dict) and "valid" in validation:
                status = "válido" if validation["valid"] else "inválido"
                print_colored(
                    f"  ✅ Validação OK: {test_project.name} é {status}", Colors.GREEN,
                )
            else:
                print_colored(f"  ❌ Validação falhou: {validation}", Colors.RED)
                return False
        else:
            print_colored("  ⚠️ Nenhum projeto encontrado para validação", Colors.YELLOW)

        # Testa operações (dry-run)
        test_deps = {"runtime": {"requests"}, "test": {"pytest"}}
        if test_project:
            result = ops.add_dependencies(test_project, test_deps, auto_confirm=True)

            if isinstance(result, dict):
                print_colored("  ✅ Operações Poetry OK (dry-run)", Colors.GREEN)
            else:
                print_colored(f"  ❌ Operações falharam: {result}", Colors.RED)
                return False

    except Exception as e:
        print_colored(f"  ❌ Erro nas operações Poetry: {e}", Colors.RED)
        return False

    return True


def run_performance_test() -> bool:
    """Testa performance com cache."""
    print_colored("\n🚀 Teste de Performance:", Colors.BLUE)

    try:

        @cached(namespace="perf", ttl=60)
        def slow_operation() -> str:
            time.sleep(0.1)  # Simula operação lenta
            return "resultado"

        # Primera execução (sem cache)
        start = time.time()
        slow_operation()
        time1 = time.time() - start

        # Segunda execução (com cache)
        start = time.time()
        slow_operation()
        time2 = time.time() - start

        # Cache deve ser muito mais rápido
        if time2 < time1 / 2:
            speedup = time1 / time2
            print_colored(f"  ✅ Cache {speedup:.1f}x mais rápido", Colors.GREEN)
        else:
            print_colored(
                f"  ⚠️ Cache não acelerou significativamente: {time1:.3f}s vs {time2:.3f}s",
                Colors.YELLOW,
            )

        # Mostra stats
        stats = slow_operation.cache_stats()
        print_colored(
            f"  📊 Stats: {stats['hits']} hits, {stats['misses']} misses", Colors.CYAN,
        )

    except Exception as e:
        print_colored(f"  ❌ Erro no teste de performance: {e}", Colors.RED)
        return False

    return True


def main():
    """Executa todos os testes."""
    print_colored("🧪 Teste da biblioteca flext_tools", Colors.BLUE)
    print_colored("=" * 50, Colors.BLUE)

    tests = [
        ("Imports", test_imports),
        ("Utilitários", test_utils),
        ("Cache", test_cache),
        ("Discovery", test_discovery),
        ("Version Analysis", test_version_analysis),
        ("Poetry Operations", test_poetry_operations),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print_colored(f"❌ {test_name} FALHOU", Colors.RED)
        except Exception as e:
            print_colored(f"❌ {test_name} ERRO: {e}", Colors.RED)

    # Teste de performance
    run_performance_test()

    # Resultado final
    print_colored("\n📊 RESULTADO DOS TESTES", Colors.BLUE)
    print_colored("=" * 50, Colors.BLUE)

    success_rate = (passed / total) * 100

    if passed == total:
        print_colored(f"🎉 TODOS OS TESTES PASSARAM! ({passed}/{total})", Colors.GREEN)
        status = 0
    else:
        print_colored(
            f"⚠️ {passed}/{total} testes passaram ({success_rate:.1f}%)", Colors.YELLOW,
        )
        status = 1

    print_colored(
        f"\n✨ Biblioteca flext_tools está {'funcionando!' if status == 0 else 'com problemas'}",
        Colors.GREEN if status == 0 else Colors.YELLOW,
    )

    return status


if __name__ == "__main__":
    sys.exit(main())

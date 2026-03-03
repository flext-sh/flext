"""FlextSettings — exercises ALL public API methods with golden file validation."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

from flext_core import FlextSettings, c
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Golden file checker infrastructure ---
_RESULTS: list[str] = []


def _check(label: str, value: object) -> None:
    _RESULTS.append(f"{label}: {_ser(value)}")


def _section(name: str) -> None:
    if _RESULTS:
        _RESULTS.append("")
    _RESULTS.append(f"[{name}]")


def _ser(v: object) -> str:
    if v is None:
        return "None"
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, str):
        return repr(v)
    if isinstance(v, list):
        return "[" + ", ".join(_ser(x) for x in v) + "]"
    if isinstance(v, dict):
        pairs = ", ".join(
            f"{_ser(k)}: {_ser(val)}"
            for k, val in sorted(v.items(), key=lambda kv: str(kv[0]))
        )
        return "{" + pairs + "}"
    if isinstance(v, type):
        return v.__name__
    return type(v).__name__


def _verify() -> None:
    actual = "\n".join(_RESULTS).strip() + "\n"
    me = Path(__file__)
    expected_path = me.with_suffix(".expected")
    n = sum(1 for line in _RESULTS if ": " in line and not line.startswith("["))
    if expected_path.exists():
        expected = expected_path.read_text(encoding="utf-8")
        if actual == expected:
            sys.stdout.write(f"PASS: {me.stem} ({n} checks)\n")
        else:
            actual_path = me.with_suffix(".actual")
            actual_path.write_text(actual, encoding="utf-8")
            sys.stdout.write(
                f"FAIL: {me.stem} — diff {expected_path.name} {actual_path.name}\n"
            )
            sys.exit(1)
    else:
        expected_path.write_text(actual, encoding="utf-8")
        sys.stdout.write(f"GENERATED: {expected_path.name} ({n} checks)\n")


# --- Env helpers ---


def _set_env(key: str, value: str | None) -> str | None:
    previous = os.environ.get(key)
    if value is None:
        _ = os.environ.pop(key, None)
    else:
        os.environ[key] = value
    return previous


def _restore_env(key: str, previous: str | None) -> None:
    if previous is None:
        _ = os.environ.pop(key, None)
    else:
        os.environ[key] = previous


# --- Demos ---


def demo_singleton_pattern() -> None:
    _section("singleton_pattern")
    FlextSettings.reset_global_instance()

    first = FlextSettings()
    second = FlextSettings()
    _check("singleton.identity", first is second)

    global_inst = FlextSettings.get_global_instance()
    _check("get_global_instance.identity", global_inst is first)

    FlextSettings._reset_instance()
    third = FlextSettings()
    _check("reset_instance.new_identity", third is not first)


def demo_materialize() -> None:
    _section("materialize")
    FlextSettings.reset_global_instance()

    global_inst = FlextSettings.get_global_instance()
    cloned = FlextSettings.materialize()
    _check(
        "materialize.clone.app_name_matches", cloned.app_name == global_inst.app_name
    )

    overridden = FlextSettings.materialize(
        config_overrides={"app_name": "flext-materialized", "timeout_seconds": 45.0}
    )
    _check("materialize.override.app_name", overridden.app_name)
    _check("materialize.override.timeout", overridden.timeout_seconds)

    explicit_none = FlextSettings.materialize(config_overrides=None)
    _check("materialize.none.app_name", explicit_none.app_name)


def demo_configuration_fields() -> None:
    _section("configuration_fields")
    FlextSettings.reset_global_instance()

    config = FlextSettings(
        app_name="flext-demo",
        version="1.2.3",
        debug=True,
        trace=False,
        log_level=c.Settings.LogLevel.INFO,
        async_logging=False,
        enable_caching=True,
        cache_ttl=120,
        database_url="sqlite:///tmp/flext.db",
        database_pool_size=4,
        circuit_breaker_threshold=5,
        rate_limit_max_requests=200,
        rate_limit_window_seconds=120,
        retry_delay=3,
        max_retry_attempts=9,
        enable_timeout_executor=True,
        dispatcher_enable_logging=True,
        dispatcher_auto_context=True,
        dispatcher_timeout_seconds=7.5,
        dispatcher_enable_metrics=True,
        executor_workers=6,
        timeout_seconds=25.0,
        max_workers=8,
        max_batch_size=200,
        api_key="example-key",
        exception_failure_level=c.Exceptions.FAILURE_LEVEL_DEFAULT,
    )

    _check("field.app_name", config.app_name)
    _check("field.version", config.version)
    _check("field.debug", config.debug)
    _check("field.api_key", config.api_key)
    _check("field.timeout_seconds", config.timeout_seconds)
    _check("field.max_workers", config.max_workers)
    _check("field.max_batch_size", config.max_batch_size)
    _check("field.dispatcher_timeout", config.dispatcher_timeout_seconds)

    validated = FlextSettings.model_validate(config.model_dump())
    _check("model_validate.app_name", validated.app_name)

    try:
        _ = FlextSettings(database_url="ftp://invalid")
        _check("invalid_db_scheme_raises", False)
    except ValueError:
        _check("invalid_db_scheme_raises", True)

    try:
        _ = FlextSettings(debug=False, trace=True)
        _check("trace_without_debug_raises", False)
    except ValueError:
        _check("trace_without_debug_raises", True)


def demo_effective_log_level() -> None:
    _section("effective_log_level")
    FlextSettings.reset_global_instance()

    base = FlextSettings(debug=False, trace=False, log_level=c.Settings.LogLevel.INFO)
    _check("effective.base", base.effective_log_level)

    debug_mode = FlextSettings.materialize(
        config_overrides={"debug": True, "trace": False}
    )
    _check("effective.debug", debug_mode.effective_log_level)

    trace_mode = FlextSettings.materialize(
        config_overrides={"debug": True, "trace": True}
    )
    _check("effective.trace", trace_mode.effective_log_level)


def demo_namespace_registry() -> None:
    _section("namespace_registry")
    FlextSettings.reset_global_instance()

    @FlextSettings.auto_register("decorated")
    class DecoratedNS(BaseSettings):
        model_config = SettingsConfigDict(
            env_prefix="FLEXT_DECORATED_",
            env_file=FlextSettings.resolve_env_file(),
            extra="ignore",
        )
        enabled: bool = True

    class ProgrammaticNS(BaseSettings):
        model_config = SettingsConfigDict(
            env_prefix="FLEXT_PROGRAMMATIC_",
            env_file=FlextSettings.resolve_env_file(),
            extra="ignore",
        )
        retries: int = 2

    FlextSettings.register_namespace("programmatic", ProgrammaticNS)

    _check(
        "get_ns_config.decorated",
        FlextSettings.get_namespace_config("decorated") is DecoratedNS,
    )
    _check(
        "get_ns_config.programmatic",
        FlextSettings.get_namespace_config("programmatic") is ProgrammaticNS,
    )
    _check("get_ns_config.missing", FlextSettings.get_namespace_config("missing"))

    base = FlextSettings()
    decorated_cfg = base.get_namespace("decorated", DecoratedNS)
    programmatic_cfg = base.get_namespace("programmatic", ProgrammaticNS)
    _check("get_namespace.decorated.enabled", decorated_cfg.enabled)
    _check("get_namespace.programmatic.retries", programmatic_cfg.retries)


def demo_context_overrides() -> None:
    _section("context_overrides")
    FlextSettings.reset_global_instance()

    FlextSettings.register_context_overrides(
        "ctx-worker", timeout_seconds=12.5, max_workers=3
    )

    with_ctx = FlextSettings.for_context(
        "ctx-worker", log_level=c.Settings.LogLevel.INFO
    )
    no_ctx = FlextSettings.for_context("ctx-missing")

    _check("for_context.registered.timeout", with_ctx.timeout_seconds)
    _check("for_context.registered.max_workers", with_ctx.max_workers)
    _check("for_context.registered.log_level", with_ctx.log_level)
    _check(
        "for_context.missing.is_global", no_ctx is FlextSettings.get_global_instance()
    )


def demo_override_methods() -> None:
    _section("override_methods")
    FlextSettings.reset_global_instance()

    config = FlextSettings()
    _check("validate_override.valid", config.validate_override("app_name", "x"))
    _check("validate_override.invalid", config.validate_override("nonexistent", "x"))

    config.apply_override("app_name", "override-name")
    _check("apply_override.app_name", config.app_name)

    before = config.max_workers
    config.apply_override("not_real_field", 999)
    _check("apply_override.invalid.unchanged", config.max_workers == before)


def demo_auto_config() -> None:
    _section("auto_config")
    FlextSettings.reset_global_instance()

    class LocalAutoConfig(BaseSettings):
        model_config = SettingsConfigDict(
            env_prefix="FLEXT_LOCAL_AUTO_",
            env_file=FlextSettings.resolve_env_file(),
            extra="ignore",
        )
        name: str = Field(default="auto")

    temp_path = Path(tempfile.gettempdir()) / "flext-example.env"
    _ = temp_path.write_text("DUMMY=1\n", encoding="utf-8")

    env_before = _set_env("FLEXT_ENV_FILE", str(temp_path))
    try:
        resolved = FlextSettings.resolve_env_file()
        _check("resolve_env_file.exists", resolved == str(temp_path.resolve()))

        auto = FlextSettings.AutoConfig(
            config_class=LocalAutoConfig,
            env_prefix="FLEXT_LOCAL_AUTO_",
            env_file=resolved,
        )
        created = auto.create_config()
        _check("auto_config.type", type(created).__name__)
        _check("auto_config.name", created.name)
    finally:
        _restore_env("FLEXT_ENV_FILE", env_before)
        if temp_path.exists():
            _ = temp_path.unlink()


def demo_di_config_provider() -> None:
    _section("di_config_provider")
    FlextSettings.reset_global_instance()

    config = FlextSettings()
    provider = config.get_di_config_provider()
    _check("get_di_config_provider.type", type(provider).__name__)


def main() -> None:
    demo_singleton_pattern()
    demo_materialize()
    demo_configuration_fields()
    demo_effective_log_level()
    demo_namespace_registry()
    demo_context_overrides()
    demo_override_methods()
    demo_auto_config()
    demo_di_config_provider()
    FlextSettings.reset_global_instance()
    _verify()


if __name__ == "__main__":
    main()

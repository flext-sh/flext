"""FlextLogger — exercises ALL public API methods with golden file validation."""

from __future__ import annotations

import sys
from pathlib import Path

from flext_core import FlextContainer, FlextLogger, c, r

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


def _ok(result: r[bool]) -> bool:
    return result.is_success


# --- Demos ---


def demo_factory_methods() -> None:
    _section("factory_methods")

    logger_default = FlextLogger.create_module_logger()
    _check("create_module_logger.type", type(logger_default).__name__)

    logger_named = FlextLogger.create_module_logger("examples.ex_03")
    _check("create_module_logger.named.type", type(logger_named).__name__)

    raw = FlextLogger.get_logger("examples.ex_03.raw")
    _check("get_logger.type", type(raw).__name__)

    bound = FlextLogger.create_bound_logger("examples.ex_03.bound", raw)
    _check("create_bound_logger.type", type(bound).__name__)

    manual = FlextLogger(
        "examples.ex_03.manual",
        config=None,
        _bound_logger=raw,
        _level="INFO",
        _service_name="examples",
        _service_version="0.1.0",
        _correlation_id="corr-ex-03",
        _force_new=True,
    )
    _check("constructor.type", type(manual).__name__)


def demo_log_levels() -> None:
    _section("log_levels")

    logger = FlextLogger.create_module_logger("examples.ex_03.levels")

    _check("debug.ok", _ok(logger.debug("debug msg", 123, stage="demo")))
    _check("info.ok", _ok(logger.info("info msg", "arg", state="ok")))
    _check("warning.ok", _ok(logger.warning("warn msg", "w", retriable=True)))
    _check("warn.ok", _ok(logger.warning("warn alias", code="W")))
    _check("error.ok", _ok(logger.error("error msg", errno=13)))
    _check("critical.ok", _ok(logger.critical("critical msg", sub="demo")))
    _check("trace.ok", _ok(logger.trace("trace msg", "t", span="abc")))
    _check("log.ok", _ok(logger.log("INFO", "generic", "a0", feat="all")))


def demo_binding() -> None:
    _section("binding")

    base = FlextLogger.create_module_logger("examples.ex_03.bind")

    bound = base.bind(component="binding", session="s-01")
    _check("bind.ok", _ok(bound.info("bound msg", action="bind")))

    renewed = bound.new(step="renewed")
    _check("new.ok", _ok(renewed.info("new msg", action="new")))

    unbound = renewed.unbind("step")
    _check("unbind.ok", _ok(unbound.info("unbind msg", action="unbind")))

    safe_unbound = unbound.try_unbind("missing-key", "session")
    _check("try_unbind.ok", _ok(safe_unbound.info("try_unbind msg")))


def demo_global_context() -> None:
    _section("global_context")

    logger = FlextLogger.create_module_logger("examples.ex_03.global")
    try:
        bind_r = FlextLogger.bind_global_context(
            app="flext", env="example", correlation_id="g-01"
        )
        _check("bind_global_context.ok", _ok(bind_r))
        _check("info_with_global.ok", _ok(logger.info("global active")))

        unbind_r = FlextLogger.unbind_global_context("env", "correlation_id")
        _check("unbind_global_context.ok", _ok(unbind_r))
    finally:
        clear_r = FlextLogger.clear_global_context()
        _check("clear_global_context.ok", _ok(clear_r))


def demo_scoped_context() -> None:
    _section("scoped_context")

    logger = FlextLogger.create_module_logger("examples.ex_03.scope")
    app_scope = c.Context.SCOPE_APPLICATION
    req_scope = c.Context.SCOPE_REQUEST
    op_scope = c.Context.SCOPE_OPERATION

    try:
        _check(
            "bind_context.app.ok",
            _ok(FlextLogger.bind_context(app_scope, app_id="demo")),
        )
        _check(
            "bind_context.req.ok",
            _ok(FlextLogger.bind_context(req_scope, request_id="req-42")),
        )
        _check(
            "bind_context.op.ok",
            _ok(FlextLogger.bind_context(op_scope, operation="write")),
        )
        _check("scoped_info.ok", _ok(logger.info("scoped bound")))

        with FlextLogger.scoped_context(req_scope, customer="acme", txn="tx-99"):
            _check("scoped_context.ok", _ok(logger.info("inside scoped")))
    finally:
        _check("clear_scope.app.ok", _ok(FlextLogger.clear_scope(app_scope)))
        _check("clear_scope.req.ok", _ok(FlextLogger.clear_scope(req_scope)))
        _check("clear_scope.op.ok", _ok(FlextLogger.clear_scope(op_scope)))


def demo_level_context() -> None:
    _section("level_context")

    logger = FlextLogger.create_module_logger("examples.ex_03.level")

    bind_r = FlextLogger.bind_context_for_level(
        "INFO", alert_channel="console", audience="ops"
    )
    _check("bind_context_for_level.ok", _ok(bind_r))
    _check("level_log.ok", _ok(logger.log("INFO", "level-bound")))

    unbind_r = FlextLogger.unbind_context_for_level("INFO", "audience", "alert_channel")
    _check("unbind_context_for_level.ok", _ok(unbind_r))


def demo_container_integration() -> None:
    _section("container_integration")

    container = FlextContainer()
    logger = FlextLogger.for_container(
        container, level="DEBUG", container_name="demo", zone="examples"
    )
    _check("for_container.ok", _ok(logger.debug("container active")))

    with FlextLogger.with_container_context(
        container, level="INFO", scope_name="scope", user="sample"
    ):
        _check("with_container_context.ok", _ok(logger.info("inside ctx")))


def demo_performance_tracker() -> None:
    _section("performance_tracker")

    logger = FlextLogger.create_module_logger("examples.ex_03.perf")
    with FlextLogger.PerformanceTracker(logger, "operation.demo"):
        _check("perf_tracker.ok", _ok(logger.info("inside tracker")))


def demo_result_adapter() -> None:
    _section("result_adapter")

    logger = FlextLogger.create_module_logger("examples.ex_03.result")
    adapter = logger.with_result()

    _check("adapter.debug.ok", _ok(adapter.debug("d", src="a")))
    _check("adapter.info.ok", _ok(adapter.info("i", src="a")))
    _check("adapter.warning.ok", _ok(adapter.warning("w", src="a")))
    _check("adapter.error.ok", _ok(adapter.error("e", src="a")))
    _check("adapter.critical.ok", _ok(adapter.critical("c", src="a")))
    _check("adapter.trace.ok", _ok(adapter.trace("t", src="a")))

    try:
        msg = "adapter exc"
        raise RuntimeError(msg)
    except RuntimeError as exc:
        _check(
            "adapter.exception.ok",
            _ok(adapter.exception("exc msg", exception=exc, exc_info=True)),
        )

    rebound = adapter.bind(ctx="bound")
    _check("adapter.bind.ok", _ok(rebound.info("rebound msg")))

    nested = adapter.with_result()
    _check("adapter.nested.ok", _ok(nested.info("nested msg")))


def demo_exception_logging() -> None:
    _section("exception_logging")

    logger = FlextLogger.create_module_logger("examples.ex_03.exc")

    try:
        msg = "example exc"
        raise ValueError(msg)
    except ValueError as exc:
        ctx = logger.build_exception_context(
            exception=exc,
            exc_info=True,
            context={"flow": "demo", "step": "build"},
        )
        _check("build_exception_context.type", type(ctx).__name__)
        _check(
            "exception.full.ok",
            _ok(logger.exception("logged", exception=exc, exc_info=True, context=ctx)),
        )
        _check(
            "exception.exc_info_only.ok",
            _ok(logger.exception("logged no exc", exc_info=True)),
        )


def main() -> None:
    demo_factory_methods()
    demo_log_levels()
    demo_binding()
    demo_global_context()
    demo_scoped_context()
    demo_level_context()
    demo_container_integration()
    demo_performance_tracker()
    demo_result_adapter()
    demo_exception_logging()
    _verify()


if __name__ == "__main__":
    main()

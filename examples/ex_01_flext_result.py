"""FlextResult (r) — exercises ALL public API methods with golden file validation."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from flext_core import FlextExceptions, FlextResult, r
from flext_core.result import is_failure_result, is_success_result
from pydantic import BaseModel
from returns.io import IOFailure, IOSuccess
from returns.maybe import Nothing, Some

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


# --- Pydantic models ---


class _UserModel(BaseModel):
    name: str
    age: int


@dataclass
class _Resource:
    value: int
    cleaned: bool = False


# --- Demos ---


def demo_factory_methods() -> None:
    _section("factory_methods")

    ok_result = r[int].ok(10)
    _check("ok.is_success", ok_result.is_success)
    _check("ok.value", ok_result.value)

    err = ValueError("bad input")
    fail_result = r[int].fail(
        error="boom",
        error_code="E_DEMO",
        error_data=None,
        expected_type=int,
        exception=err,
    )
    _check("fail.is_failure", fail_result.is_failure)
    _check("fail.error", fail_result.error)
    _check("fail.error_code", fail_result.error_code)
    _check("fail.error_data", fail_result.error_data)

    try:
        _ = r[str].ok(None)
        _check("ok_none_raises", False)
    except ValueError:
        _check("ok_none_raises", True)

    @FlextResult.safe
    def parse_int(value: str) -> int:
        return int(value)

    safe_ok = parse_int("42")
    safe_fail = parse_int("x")
    _check("safe.ok.is_success", safe_ok.is_success)
    _check("safe.ok.value", safe_ok.value)
    _check("safe.fail.is_failure", safe_fail.is_failure)

    def make_created() -> str:
        return "created"

    def fail_callable() -> str:
        msg = "intentional failure"
        raise RuntimeError(msg)

    callable_ok = FlextResult[str].create_from_callable(make_created)
    callable_fail = FlextResult[str].create_from_callable(
        fail_callable, error_code="E_CALL"
    )
    _check("create_from_callable.ok.value", callable_ok.unwrap_or("x"))
    _check("create_from_callable.fail.is_failure", callable_fail.is_failure)
    _check("create_from_callable.fail.error_code", callable_fail.error_code)


def demo_properties() -> None:
    _section("properties")

    success = r[str].ok("value")
    failure = r.fail("nope", error_code="E_PROP", error_data=None, expected_type=str)

    _check("success.is_success", success.is_success)
    _check("success.is_failure", success.is_failure)
    _check("failure.is_success", failure.is_success)
    _check("failure.is_failure", failure.is_failure)

    _check("success.value", success.value)
    _check("success.data", success.data)
    _check("success.result_is_self", success.result is success)
    _check("success.error", success.error)

    _check("failure.error", failure.error)
    _check("failure.error_code", failure.error_code)
    _check("failure.error_data", failure.error_data)

    success_returns = success.returns_result
    failure_returns = failure.returns_result
    _check("returns_result.success.value_or", success_returns.value_or("fallback"))
    _check("returns_result.failure.value_or", failure_returns.value_or("fallback"))


def demo_monadic_operations() -> None:
    _section("monadic_operations")

    side_effects: list[int] = []
    error_effects: list[str] = []

    base = r[int].ok(5)
    failed = r.fail("bad", expected_type=int)

    mapped = base.map(lambda n: n + 1)
    _check("map.value", mapped.value)

    flat_mapped = base.flat_map(lambda n: r[int].ok(n * 2))
    _check("flat_map.value", flat_mapped.value)

    and_then_mapped = base.and_then(lambda n: r[int].ok(n * 3))
    _check("and_then.value", and_then_mapped.value)

    tapped = base.tap(lambda n: side_effects.append(n))
    _check("tap.is_success", tapped.is_success)
    _check("tap.side_effects", side_effects)

    tapped_error = failed.tap_error(lambda e: error_effects.append(e))
    _check("tap_error.is_failure", tapped_error.is_failure)
    _check("tap_error.side_effects", error_effects)

    recovered = failed.recover(lambda e: len(e))
    _check("recover.is_success", recovered.is_success)
    _check("recover.value", recovered.value)

    alted = failed.alt(lambda e: f"ALT:{e}")
    _check("alt.error", alted.error)

    map_errored = failed.map_error(lambda e: f"MAPERR:{e}")
    _check("map_error.error", map_errored.error)

    lashed = failed.lash(lambda e: r[int].ok(len(e)))
    _check("lash.is_success", lashed.is_success)
    _check("lash.value", lashed.value)

    or_else_result = failed.or_else(lambda e: r[int].ok(len(e) + 1))
    _check("or_else.is_success", or_else_result.is_success)
    _check("or_else.value", or_else_result.value)

    filtered_ok = base.filter(lambda n: n > 0)
    filtered_fail = base.filter(lambda n: n < 0)
    _check("filter.pass.is_success", filtered_ok.is_success)
    _check("filter.fail.is_failure", filtered_fail.is_failure)

    folded_success = base.fold(lambda e: len(e), lambda n: n + 100)
    folded_failure = failed.fold(lambda e: len(e), lambda n: n + 100)
    _check("fold.success", folded_success)
    _check("fold.failure", folded_failure)


def demo_unwrap() -> None:
    _section("unwrap")

    success = r[int].ok(7)
    failure = r.fail("missing", expected_type=int)

    _check("unwrap_or.success", success.unwrap_or(0))
    _check("unwrap_or.failure", failure.unwrap_or(0))

    _check("get_or_else.success", success.get_or_else(9))
    _check("get_or_else.failure", failure.get_or_else(9))

    _check("map_or.default_only.success", success.map_or(99))
    _check("map_or.default_none.success", success.map_or(99, None))
    _check("map_or.default_only.failure", failure.map_or(99))
    _check("map_or.func.success", success.map_or("n/a", lambda n: f"v={n}"))
    _check("map_or.func.failure", failure.map_or("n/a", lambda n: f"v={n}"))


def demo_conversions() -> None:
    _section("conversions")

    success = r[int].ok(8)
    failure = r.fail("io-err", expected_type=int)

    maybe_success = success.to_maybe()
    maybe_failure = failure.to_maybe()
    _check("to_maybe.success.value", maybe_success.unwrap())
    _check("to_maybe.failure.value_or", maybe_failure.value_or(123))

    from_some = FlextResult.from_maybe(Some("x"), error_message="empty")
    from_nothing = FlextResult.from_maybe(Nothing, error_message="empty")
    _check("from_maybe.some.is_success", from_some.is_success)
    _check("from_maybe.some.value", from_some.value)
    _check("from_maybe.nothing.is_failure", from_nothing.is_failure)
    _check("from_maybe.nothing.error", from_nothing.error)

    io_value = success.to_io()
    _check("to_io.success.type", type(io_value).__name__)

    try:
        _ = failure.to_io()
        _check("to_io.failure_raises", False)
    except FlextExceptions.ValidationError:
        _check("to_io.failure_raises", True)

    io_result_success = success.to_io_result()
    io_result_failure = failure.to_io_result()
    _check("to_io_result.success.type", type(io_result_success).__name__)
    _check("to_io_result.failure.type", type(io_result_failure).__name__)

    from_io_ok = FlextResult.from_io_result(IOSuccess(11))
    from_io_fail = FlextResult.from_io_result(IOFailure("x"))
    _check("from_io_result.success.is_success", from_io_ok.is_success)
    _check("from_io_result.failure.is_failure", from_io_fail.is_failure)
    _check("from_io_result.failure.error", from_io_fail.error)


def demo_validation() -> None:
    _section("validation")

    valid_data = {"name": "Ada", "age": 30}
    invalid_data = {"name": "Ada", "age": "bad"}

    validated = r[_UserModel].from_validation(valid_data, _UserModel)
    validation_fail = r[_UserModel].from_validation(invalid_data, _UserModel)
    _check("from_validation.valid.is_success", validated.is_success)
    _check("from_validation.valid.name", validated.value.name)
    _check("from_validation.invalid.is_failure", validation_fail.is_failure)

    to_model_ok = r[dict[str, object]].ok(valid_data).to_model(_UserModel)
    to_model_fail = r.fail("not available", expected_type=str).to_model(_UserModel)
    _check("to_model.ok.is_success", to_model_ok.is_success)
    _check("to_model.ok.age", to_model_ok.value.age)
    _check("to_model.fail.is_failure", to_model_fail.is_failure)
    _check("to_model.fail.error", to_model_fail.error)


def demo_collections() -> None:
    _section("collections")

    def to_even(n: int) -> FlextResult[int]:
        if n % 2 == 0:
            return r[int].ok(n)
        return r.fail(f"odd:{n}", expected_type=int)

    traversed_ok = FlextResult.traverse([2, 4, 6], to_even)
    traversed_ff = FlextResult.traverse([2, 3, 4], to_even, fail_fast=True)
    traversed_col = FlextResult.traverse([1, 3, 5], to_even, fail_fast=False)
    _check("traverse.ok.is_success", traversed_ok.is_success)
    _check("traverse.ok.value", traversed_ok.value)
    _check("traverse.fail_fast.is_failure", traversed_ff.is_failure)
    _check("traverse.collect.is_failure", traversed_col.is_failure)

    acc_ok = FlextResult.accumulate_errors(r[int].ok(1), r[int].ok(2))
    acc_fail = FlextResult.accumulate_errors(
        r[int].ok(1),
        r.fail("e1", expected_type=int),
        r.fail("e2", expected_type=int),
    )
    _check("accumulate.ok.is_success", acc_ok.is_success)
    _check("accumulate.ok.value", acc_ok.value)
    _check("accumulate.fail.is_failure", acc_fail.is_failure)
    _check("accumulate.fail.has_e1", "e1" in (acc_fail.error or ""))
    _check("accumulate.fail.has_e2", "e2" in (acc_fail.error or ""))

    par_ok = FlextResult.parallel_map([2, 4], to_even)
    par_ff = FlextResult.parallel_map([2, 3], to_even, fail_fast=True)
    par_col = FlextResult.parallel_map([1, 3], to_even, fail_fast=False)
    _check("parallel_map.ok.is_success", par_ok.is_success)
    _check("parallel_map.ok.value", par_ok.value)
    _check("parallel_map.fail_fast.is_failure", par_ff.is_failure)
    _check("parallel_map.collect.is_failure", par_col.is_failure)


def demo_resource_management() -> None:
    _section("resource_management")

    cleaned: list[int] = []

    def factory() -> _Resource:
        return _Resource(value=21)

    def op(res: _Resource) -> FlextResult[int]:
        return r[int].ok(res.value * 2)

    def cleanup(res: _Resource) -> None:
        res.cleaned = True
        cleaned.append(res.value)

    with_cleanup = r[int].with_resource(factory, op, cleanup=cleanup)
    default_cleanup = r[int].with_resource(factory, op)
    _check("with_resource.cleanup.is_success", with_cleanup.is_success)
    _check("with_resource.cleanup.value", with_cleanup.value)
    _check("with_resource.cleanup.cleaned", cleaned)
    _check("with_resource.no_cleanup.is_success", default_cleanup.is_success)
    _check("with_resource.no_cleanup.value", default_cleanup.value)


def demo_module_helpers() -> None:
    _section("module_helpers")

    success = r[int].ok(1)
    failure = r.fail("x", expected_type=int)
    not_result = "plain"

    _check("is_success_result.success", is_success_result(success))
    _check("is_success_result.failure", is_success_result(failure))
    _check("is_success_result.non_result", is_success_result(not_result))
    _check("is_failure_result.failure", is_failure_result(failure))
    _check("is_failure_result.success", is_failure_result(success))
    _check("is_failure_result.non_result", is_failure_result(not_result))


def main() -> None:
    demo_factory_methods()
    demo_properties()
    demo_monadic_operations()
    demo_unwrap()
    demo_conversions()
    demo_validation()
    demo_collections()
    demo_resource_management()
    demo_module_helpers()
    _verify()


if __name__ == "__main__":
    main()

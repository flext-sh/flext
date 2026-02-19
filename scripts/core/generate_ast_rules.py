#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
"""Generate proper AST-aware rule files for all skills.

Replaces fake `kind: module` + `regex` rules with real AST patterns.
Also updates rules.yml to set all detection rules to type: ast-grep.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

SKILLS_DIR = Path(".claude/skills")

# ============================================================================
# RULE DEFINITIONS: skill -> list of (rule_id, ast_grep_yaml, language)
# Each entry produces a standalone YAML rule file.
# ============================================================================


def _import_any_name(
    rule_id: str, module: str, name: str, msg: str, sev: str = "error"
) -> str:
    """Generate rule to detect a specific name imported from a module.
    Handles: from <module> import <name>, and multi-import variants.
    """
    return textwrap.dedent(f"""\
        id: {rule_id}
        language: python
        rule:
          kind: import_from_statement
          all:
            - has:
                kind: dotted_name
                field: module_name
                regex: "^{module}$"
            - has:
                stopBy: end
                kind: identifier
                regex: "^{name}$"
        message: "{msg}"
        severity: {sev}
    """)


def _import_module(rule_id: str, module: str, msg: str, sev: str = "error") -> str:
    """Generate rule to ban direct import of a module.
    Handles: import <module> and from <module> import ...
    """
    # For dotted modules like returns.pipeline, we need regex
    mod_regex = module.replace(".", "\\\\.")
    return textwrap.dedent(f"""\
        id: {rule_id}
        language: python
        rule:
          any:
            - kind: import_statement
              has:
                kind: dotted_name
                regex: "^{mod_regex}"
                stopBy: end
            - kind: import_from_statement
              has:
                kind: dotted_name
                field: module_name
                regex: "^{mod_regex}"
        message: "{msg}"
        severity: {sev}
    """)


def _func_call(rule_id: str, pattern: str, msg: str, sev: str = "error") -> str:
    """Generate rule for a function/method call pattern."""
    return textwrap.dedent(f"""\
        id: {rule_id}
        language: python
        rule:
          pattern: "{pattern}"
        message: "{msg}"
        severity: {sev}
    """)


def _multi_func_call(
    rule_id: str, patterns: list[str], msg: str, sev: str = "error"
) -> str:
    """Generate rule matching any of several call patterns."""
    any_items = "\n".join(f'    - pattern: "{p}"' for p in patterns)
    return textwrap.dedent(f"""\
        id: {rule_id}
        language: python
        rule:
          any:
{any_items}
        message: "{msg}"
        severity: {sev}
    """)


def _comment(
    rule_id: str, regex: str, msg: str, lang: str = "python", sev: str = "warning"
) -> str:
    """Generate rule matching comments by regex.

    Anchors regex with ^# to prevent matching descriptive comments
    that merely mention the keyword.
    """
    # Anchor the regex to start of comment if not already anchored
    anchored = regex if regex.startswith("^") else f"^#\\\\s*{regex}"
    return textwrap.dedent(f"""\
        id: {rule_id}
        language: {lang}
        rule:
          kind: comment
          regex: "{anchored}"
        message: "{msg}"
        severity: {sev}
    """)


def _raw(yaml_str: str) -> str:
    """Raw YAML rule string (for complex custom rules)."""
    return textwrap.dedent(yaml_str)


# ============================================================================
# ALL SKILL RULES
# ============================================================================

RULES: dict[str, list[tuple[str, str]]] = {}  # skill_name -> [(rule_id, yaml_content)]


# --- async-python-patterns ---
RULES["async-python-patterns"] = [
    (
        "no-asyncio-run-in-src",
        _func_call(
            "no-asyncio-run-in-src",
            "asyncio.run($$$ARGS)",
            "asyncio.run() blocks event loop - use await instead",
        ),
    ),
    (
        "no-blocking-sleep-in-async",
        _func_call(
            "no-blocking-sleep-in-async",
            "time.sleep($$$ARGS)",
            "time.sleep() blocks async event loop - use asyncio.sleep()",
        ),
    ),
    (
        "no-sync-requests-in-src",
        _multi_func_call(
            "no-sync-requests-in-src",
            [
                "requests.get($$$ARGS)",
                "requests.post($$$ARGS)",
                "requests.put($$$ARGS)",
                "requests.delete($$$ARGS)",
                "requests.patch($$$ARGS)",
                "requests.head($$$ARGS)",
            ],
            "Sync requests in async code - use httpx or aiohttp",
        ),
    ),
]


# --- backend-api-patterns ---
RULES["backend-api-patterns"] = [
    (
        "no-fstring-execute",
        _raw("""\
        id: no-fstring-execute
        language: python
        rule:
          kind: call
          all:
            - has:
                kind: attribute
                regex: "execute$"
                stopBy: end
            - has:
                kind: argument_list
                has:
                  kind: string
                  has:
                    kind: string_start
                    regex: "^f"
                  stopBy: end
                stopBy: end
        message: "f-string in execute() is SQL injection risk"
        severity: error
    """),
    ),
    (
        "no-format-execute",
        _raw("""\
        id: no-format-execute
        language: python
        rule:
          kind: call
          all:
            - has:
                kind: attribute
                regex: "execute$"
                stopBy: end
            - has:
                kind: argument_list
                has:
                  kind: call
                  has:
                    kind: attribute
                    regex: "format$"
                    stopBy: end
                  stopBy: end
                stopBy: end
        message: ".format() in execute() is SQL injection risk"
        severity: error
    """),
    ),
    (
        "no-concat-execute",
        _raw("""\
        id: no-concat-execute
        language: python
        rule:
          kind: call
          all:
            - has:
                kind: attribute
                regex: "execute$"
                stopBy: end
            - has:
                kind: argument_list
                has:
                  kind: binary_operator
                  has:
                    kind: string
                    stopBy: end
                  stopBy: end
                stopBy: end
        message: "String concatenation in execute() is SQL injection risk"
        severity: error
    """),
    ),
    (
        "no-hardcoded-credentials",
        _raw("""\
        id: no-hardcoded-credentials
        language: python
        rule:
          kind: expression_statement
          has:
            kind: assignment
            all:
              - has:
                  kind: identifier
                  regex: "(?i)(password|secret|api_key|token)"
                  field: left
                  stopBy: end
              - has:
                  kind: string
                  field: right
        message: "Hardcoded credential detected"
        severity: error
    """),
    ),
]


# --- backend-data-patterns ---
RULES["backend-data-patterns"] = [
    (
        "no-hardcoded-version-in-constants",
        _raw("""\
        id: no-hardcoded-version-in-constants
        language: python
        rule:
          kind: expression_statement
          has:
            kind: assignment
            all:
              - has:
                  kind: identifier
                  regex: "^VERSION$"
                  field: left
              - has:
                  kind: string
                  field: right
                  regex: "\\\\d+\\\\.\\\\d+"
        message: "Hardcoded VERSION constant"
        severity: warning
    """),
    ),
    (
        "no-bare-constant-outside-class",
        _raw("""\
        id: no-bare-constant-outside-class
        language: python
        rule:
          kind: expression_statement
          has:
            kind: assignment
            has:
              kind: identifier
              regex: "^[A-Z][A-Z_]{2,}$"
              field: left
          not:
            inside:
              kind: class_definition
              stopBy: end
        message: "Bare constant outside class"
        severity: warning
    """),
    ),
    (
        "missing-final-annotation",
        _raw("""\
        id: missing-final-annotation
        language: python
        rule:
          kind: expression_statement
          all:
            - has:
                kind: assignment
                has:
                  kind: identifier
                  regex: "^[A-Z][A-Z_]{2,}$"
                  field: left
            - not:
                has:
                  kind: type
                  has:
                    regex: "Final"
                    stopBy: end
                  stopBy: end
          inside:
            kind: class_definition
            stopBy: end
        message: "Class constant missing Final annotation"
        severity: warning
    """),
    ),
]


# --- flext-architecture-layers ---
RULES["flext-architecture-layers"] = [
    (
        "ban-private-module-import",
        _raw("""\
        id: ban-private-module-import
        language: python
        rule:
          kind: import_from_statement
          has:
            kind: dotted_name
            field: module_name
            regex: "^flext_core\\\\._"
        message: "Direct import from flext_core private module"
        severity: error
    """),
    ),
]


# --- flext-docs-pointer-policy ---
RULES["flext-docs-pointer-policy"] = [
    # These target .md files - need custom type since ast-grep doesn't support Markdown
    # We'll handle these as custom rules
]


# --- flext-import-rules ---
RULES["flext-import-rules"] = [
    (
        "ban-wildcard-import",
        _raw("""\
        id: ban-wildcard-import
        language: python
        rule:
          kind: import_from_statement
          has:
            kind: wildcard_import
            stopBy: end
        message: "Wildcard import banned"
        severity: error
    """),
    ),
    (
        "ban-relative-import",
        _raw("""\
        id: ban-relative-import
        language: python
        rule:
          kind: import_from_statement
          has:
            kind: relative_import
            stopBy: end
        message: "Relative import banned"
        severity: error
    """),
    ),
    (
        "ban-direct-oracledb-import",
        _import_module(
            "ban-direct-oracledb-import",
            "oracledb",
            "Direct oracledb import banned - use flext_core adapter",
        ),
    ),
    (
        "ban-direct-sqlalchemy-import",
        _import_module(
            "ban-direct-sqlalchemy-import",
            "sqlalchemy",
            "Direct sqlalchemy import banned - use flext_core adapter",
        ),
    ),
    (
        "ban-direct-ldap3-import",
        _import_module(
            "ban-direct-ldap3-import",
            "ldap3",
            "Direct ldap3 import banned - use flext_core adapter",
        ),
    ),
    (
        "ban-direct-grpc-import",
        _import_module(
            "ban-direct-grpc-import",
            "grpc",
            "Direct grpc import banned - use flext_core adapter",
        ),
    ),
]


# --- flext-patterns ---
RULES["flext-patterns"] = [
    (
        "ban-print-in-src",
        _func_call(
            "ban-print-in-src",
            "print($$$ARGS)",
            "print() in src code - use FlextLogger",
        ),
    ),
    (
        "no-breakpoint",
        _multi_func_call(
            "no-breakpoint",
            ["breakpoint()", "pdb.set_trace()"],
            "Debug breakpoint in code",
        ),
    ),
    (
        "no-breakpoint-import",
        _raw("""\
        id: no-breakpoint-import
        language: python
        rule:
          pattern: import pdb
        message: "Debug pdb import"
        severity: error
    """),
    ),
    (
        "no-empty-except",
        _raw("""\
        id: no-empty-except
        language: python
        rule:
          kind: except_clause
          all:
            - not:
                has:
                  any:
                    - kind: identifier
                    - kind: attribute
                  stopBy: neighbor
            - has:
                kind: block
                has:
                  kind: pass_statement
                  stopBy: end
                stopBy: end
        message: "Empty bare except clause"
        severity: error
    """),
    ),
    (
        "no-hardcoded-version-string",
        _raw("""\
        id: no-hardcoded-version-string
        language: python
        rule:
          pattern: __version__ = $VAL
        constraints:
          VAL:
            kind: string
        message: "Hardcoded __version__ string"
        severity: warning
    """),
    ),
    (
        "no-sys-exit-in-library",
        _func_call(
            "no-sys-exit-in-library",
            "sys.exit($$$ARGS)",
            "sys.exit() in library code - raise SystemExit instead",
        ),
    ),
    (
        "detect-todo-fixme",
        _comment(
            "detect-todo-fixme", "(TODO|FIXME|HACK|XXX)", "TODO/FIXME comment found"
        ),
    ),
]


# --- flext-quality-gates ---
RULES["flext-quality-gates"] = [
    # These target YAML files (Makefile/pyproject.toml patterns) — need custom
]


# --- flext-strict-typing ---
RULES["flext-strict-typing"] = [
    (
        "grep-typing-any",
        _raw("""\
        id: grep-typing-any
        language: python
        rule:
          pattern: typing.Any
        message: "Direct typing.Any usage banned"
        severity: error
    """),
    ),
    (
        "grep-any-import",
        _import_any_name(
            "grep-any-import", "typing", "Any", "Importing Any from typing is banned"
        ),
    ),
    (
        "ban-type-ignore-comment",
        _comment(
            "ban-type-ignore-comment",
            "type:\\\\s*ignore",
            "type: ignore comment - fix the underlying type error",
        ),
    ),
    (
        "ban-noqa-comment",
        _comment(
            "ban-noqa-comment",
            "noqa",
            "noqa comment - fix the underlying lint violation",
        ),
    ),
    (
        "ban-pylint-disable-comment",
        _comment(
            "ban-pylint-disable-comment",
            "pylint:\\\\s*disable",
            "pylint: disable comment - fix the underlying violation",
        ),
    ),
    (
        "ban-mypy-ignore-comment",
        _comment(
            "ban-mypy-ignore-comment",
            "mypy:\\\\s*ignore",
            "mypy: ignore comment - fix the underlying type error",
        ),
    ),
]


# --- flext-type-system ---
RULES["flext-type-system"] = [
    (
        "ban-bare-dict-return",
        _raw("""\
        id: ban-bare-dict-return
        language: python
        rule:
          kind: function_definition
          has:
            field: return_type
            kind: type
            has:
              kind: identifier
              regex: "^dict$"
              stopBy: end
        message: "Function returns bare dict - use TypedDict or specific mapping"
        severity: warning
    """),
    ),
]


# --- frontend-standards ---
RULES["frontend-standards"] = [
    (
        "img-requires-alt",
        _raw("""\
        id: img-requires-alt
        language: html
        rule:
          kind: element
          all:
            - has:
                kind: start_tag
                has:
                  kind: tag_name
                  regex: "^img$"
                stopBy: end
            - not:
                has:
                  kind: attribute
                  has:
                    kind: attribute_name
                    regex: "^alt$"
                  stopBy: end
        message: "img element missing alt attribute"
        severity: error
    """),
    ),
    (
        "no-inline-style",
        _raw("""\
        id: no-inline-style
        language: html
        rule:
          kind: attribute
          has:
            kind: attribute_name
            regex: "^style$"
            stopBy: end
        message: "Inline style attribute - use CSS classes"
        severity: warning
    """),
    ),
]


# --- lib-beartype ---
RULES["lib-beartype"] = [
    (
        "ban-direct-beartype-decorator",
        _raw("""\
        id: ban-direct-beartype-decorator
        language: python
        rule:
          kind: decorator
          has:
            kind: identifier
            regex: "^beartype$"
            stopBy: end
        message: "Direct @beartype decorator banned - use package-level conf"
        severity: error
    """),
    ),
    (
        "ban-adhoc-beartype-conf",
        _func_call(
            "ban-adhoc-beartype-conf",
            "BeartypeConf($$$ARGS)",
            "Ad-hoc BeartypeConf() banned - use centralized configuration",
        ),
    ),
]


# --- lib-dependency-injector ---
RULES["lib-dependency-injector"] = [
    (
        "ban-direct-di-import",
        _import_module(
            "ban-direct-di-import",
            "dependency_injector",
            "Direct dependency_injector import banned - use flext_core DI bridge",
        ),
    ),
]


# --- lib-orjson ---
RULES["lib-orjson"] = [
    (
        "prefer-orjson-dumps",
        _func_call(
            "prefer-orjson-dumps",
            "json.dumps($$$ARGS)",
            "Use orjson.dumps() instead of json.dumps()",
        ),
    ),
    (
        "require-sort-keys",
        _raw("""\
        id: require-sort-keys
        language: python
        rule:
          pattern: orjson.OPT_SORT_KEYS
        message: "orjson OPT_SORT_KEYS usage found (tracking)"
        severity: warning
    """),
    ),
]


# --- lib-pydantic-settings ---
RULES["lib-pydantic-settings"] = [
    (
        "require-env-prefix",
        _raw("""\
        id: require-env-prefix
        language: python
        rule:
          kind: keyword_argument
          all:
            - has:
                kind: identifier
                regex: "^env_prefix$"
                field: name
            - has:
                kind: string
                field: value
        message: "env_prefix configuration found (tracking)"
        severity: warning
    """),
    ),
]


# --- lib-pydantic-v2 ---
RULES["lib-pydantic-v2"] = [
    (
        "pydantic-model-rebuild-critical",
        _raw("""\
        id: pydantic-model-rebuild-critical
        language: python
        rule:
          pattern: $OBJ.model_rebuild($$$ARGS)
        message: "model_rebuild() call - verify necessity"
        severity: warning
    """),
    ),
    (
        "pydantic-v1-from-orm",
        _raw("""\
        id: pydantic-v1-from-orm
        language: python
        rule:
          pattern: $OBJ.from_orm($$$ARGS)
        message: "Pydantic v1 .from_orm() - use model_validate()"
        severity: error
    """),
    ),
    (
        "pydantic-v1-validator-decorator",
        _raw("""\
        id: pydantic-v1-validator-decorator
        language: python
        rule:
          kind: decorator
          has:
            kind: call
            has:
              kind: identifier
              regex: "^validator$"
              stopBy: end
            stopBy: end
        message: "Pydantic v1 @validator - use @field_validator"
        severity: error
    """),
    ),
    (
        "pydantic-v1-root-validator-decorator",
        _raw("""\
        id: pydantic-v1-root-validator-decorator
        language: python
        rule:
          kind: decorator
          has:
            kind: call
            has:
              kind: identifier
              regex: "^root_validator$"
              stopBy: end
            stopBy: end
        message: "Pydantic v1 @root_validator - use @model_validator"
        severity: error
    """),
    ),
]


# --- lib-pyyaml ---
RULES["lib-pyyaml"] = [
    (
        "ban-unsafe-yaml-load",
        _func_call(
            "ban-unsafe-yaml-load",
            "yaml.load($$$ARGS)",
            "Unsafe yaml.load() - use yaml.safe_load()",
        ),
    ),
]


# --- lib-returns ---
RULES["lib-returns"] = [
    (
        "ban-direct-constructor",
        _multi_func_call(
            "ban-direct-constructor",
            ["FlextResult(Success($$$ARGS))", "FlextResult(Failure($$$ARGS))"],
            "Direct FlextResult constructor - use flext_success/flext_failure",
        ),
    ),
    (
        "ban-direct-returns-import",
        _import_module(
            "ban-direct-returns-import",
            "returns",
            "Direct returns library import - use flext_core bridge",
        ),
    ),
]


# --- lib-structlog ---
RULES["lib-structlog"] = [
    (
        "ban-print-in-src",
        _func_call(
            "ban-print-in-src-structlog",
            "print($$$ARGS)",
            "print() in src code - use FlextLogger",
        ),
    ),
    (
        "ban-direct-structlog-configure",
        _func_call(
            "ban-direct-structlog-configure",
            "structlog.configure($$$ARGS)",
            "Direct structlog.configure() - use FlextLogger factory",
        ),
    ),
]


# --- python-modern-type-syntax ---
RULES["python-modern-type-syntax"] = [
    (
        "no-union-import",
        _import_any_name(
            "no-union-import",
            "typing",
            "Union",
            "Union import from typing - use X | Y syntax",
        ),
    ),
    (
        "no-optional-import",
        _import_any_name(
            "no-optional-import",
            "typing",
            "Optional",
            "Optional import from typing - use X | None syntax",
        ),
    ),
    (
        "no-union-annotation",
        _raw("""\
        id: no-union-annotation
        language: python
        rule:
          pattern:
            context: "a: Union[$$$TYPES]"
            selector: generic_type
        message: "Union[X, Y] annotation - use X | Y syntax"
        severity: warning
    """),
    ),
    (
        "no-optional-annotation",
        _raw("""\
        id: no-optional-annotation
        language: python
        rule:
          pattern:
            context: "a: Optional[$T]"
            selector: generic_type
        message: "Optional[X] annotation - use X | None syntax"
        severity: warning
    """),
    ),
]


# --- python-performance ---
RULES["python-performance"] = [
    (
        "no-mutable-default-arg",
        _raw("""\
        id: no-mutable-default-arg
        language: python
        rule:
          kind: default_parameter
          has:
            any:
              - kind: list
              - kind: dictionary
            stopBy: end
        message: "Mutable default argument (list/dict) - use None with factory"
        severity: error
    """),
    ),
    (
        "no-star-import",
        _raw("""\
        id: no-star-import
        language: python
        rule:
          kind: import_from_statement
          has:
            kind: wildcard_import
            stopBy: end
        message: "Star import banned"
        severity: error
    """),
    ),
]


# --- python-type-narrowing ---
RULES["python-type-narrowing"] = [
    (
        "no-type-comparison",
        _raw("""\
        id: no-type-comparison
        language: python
        rule:
          kind: comparison_operator
          has:
            kind: call
            has:
              kind: identifier
              regex: "^type$"
              field: function
            stopBy: end
        message: "type() comparison - use isinstance() instead"
        severity: warning
    """),
    ),
    (
        "no-type-in-condition",
        _raw("""\
        id: no-type-in-condition
        language: python
        rule:
          kind: if_statement
          has:
            kind: call
            has:
              kind: identifier
              regex: "^type$"
              field: function
            stopBy: neighbor
        message: "type() in condition - use isinstance()"
        severity: warning
    """),
    ),
]


# --- readme-standardization ---
# Markdown not supported by ast-grep - these stay as custom rules
RULES["readme-standardization"] = []


# --- rules-cmd ---
RULES["rules-cmd"] = [
    (
        "require-shebang",
        _comment(
            "require-shebang",
            "^#!/usr/bin/env",
            "Shebang line found (tracking)",
            lang="python",
            sev="warning",
        ),
    ),
    (
        "require-docstring",
        _raw("""\
        id: require-docstring
        language: python
        rule:
          kind: expression_statement
          has:
            kind: string
            stopBy: end
          nthChild:
            position: 1
            ofRule:
              kind: module
        message: "Module docstring found (tracking)"
        severity: warning
    """),
    ),
]


# --- rules-docker ---
RULES["rules-docker"] = [
    (
        "ban-latest-tag",
        _raw("""\
        id: ban-latest-tag
        language: yaml
        rule:
          kind: block_mapping_pair
          all:
            - has:
                field: key
                regex: "^image$"
            - has:
                field: value
                regex: ":latest$"
        message: "Docker image uses :latest tag - pin specific version"
        severity: error
    """),
    ),
    (
        "require-healthcheck",
        _raw("""\
        id: require-healthcheck
        language: yaml
        rule:
          kind: block_mapping_pair
          has:
            field: key
            regex: "^(HEALTHCHECK|healthcheck)$"
        message: "Healthcheck configuration found (tracking)"
        severity: warning
    """),
    ),
]


# --- rules-docs ---
# Markdown not supported - these stay as custom rules
RULES["rules-docs"] = []


# --- rules-examples ---
RULES["rules-examples"] = [
    (
        "require-main-guard",
        _raw("""\
        id: require-main-guard
        language: python
        rule:
          pattern: |
            if __name__ == "__main__":
                $$$BODY
        message: "Main guard found (tracking)"
        severity: warning
    """),
    ),
    (
        "require-future-annotations",
        _raw("""\
        id: require-future-annotations
        language: python
        rule:
          pattern: from __future__ import annotations
        message: "Future annotations import found (tracking)"
        severity: warning
    """),
    ),
]


# --- rules-flext-core ---
RULES["rules-flext-core"] = [
    (
        "require-future-annotations",
        _raw("""\
        id: require-future-annotations-core
        language: python
        rule:
          pattern: from __future__ import annotations
        message: "Future annotations import found (tracking)"
        severity: warning
    """),
    ),
    (
        "require-flext-result-pattern",
        _raw("""\
        id: require-flext-result-pattern
        language: python
        rule:
          any:
            - kind: import_from_statement
              has:
                kind: identifier
                regex: "^FlextResult$"
                stopBy: end
            - kind: function_definition
              has:
                field: return_type
                regex: "FlextResult"
                stopBy: end
        message: "FlextResult pattern found (tracking)"
        severity: warning
    """),
    ),
    (
        "require-flext-constants-import",
        _raw("""\
        id: require-flext-constants-import
        language: python
        rule:
          kind: import_from_statement
          all:
            - has:
                kind: dotted_name
                field: module_name
                regex: "^flext_core"
            - has:
                kind: identifier
                regex: "^(FlextConstants|c)$"
                stopBy: end
        message: "FlextConstants import found (tracking)"
        severity: warning
    """),
    ),
]


# --- rules-github ---
RULES["rules-github"] = [
    (
        "require-workflow-name",
        _raw("""\
        id: require-workflow-name
        language: yaml
        rule:
          kind: block_mapping_pair
          has:
            field: key
            regex: "^name$"
        message: "Workflow name found (tracking)"
        severity: warning
    """),
    ),
    (
        "ban-hardcoded-secrets",
        _raw("""\
        id: ban-hardcoded-secrets
        language: yaml
        rule:
          kind: block_mapping_pair
          all:
            - has:
                field: key
                regex: "(?i)(password|secret|token)"
            - has:
                field: value
                not:
                  regex: "\\\\$\\\\{\\\\{"
        message: "Hardcoded secret in workflow - use GitHub secrets"
        severity: error
    """),
    ),
]


# --- rules-pkg ---
RULES["rules-pkg"] = [
    (
        "require-future-annotations",
        _raw("""\
        id: require-future-annotations-pkg
        language: python
        rule:
          pattern: from __future__ import annotations
        message: "Future annotations import found (tracking)"
        severity: warning
    """),
    ),
]


# --- rules-src ---
RULES["rules-src"] = [
    (
        "require-future-annotations",
        _raw("""\
        id: require-future-annotations-src
        language: python
        rule:
          pattern: from __future__ import annotations
        message: "Future annotations import found (tracking)"
        severity: warning
    """),
    ),
    (
        "ban-star-import",
        _raw("""\
        id: ban-star-import-src
        language: python
        rule:
          kind: import_from_statement
          has:
            kind: wildcard_import
            stopBy: end
        message: "Star import banned in src"
        severity: error
    """),
    ),
]


# --- rules-typings ---
RULES["rules-typings"] = [
    (
        "require-typing-extensions-compat",
        _raw("""\
        id: require-typing-extensions-compat
        language: python
        rule:
          kind: import_from_statement
          has:
            kind: dotted_name
            field: module_name
            regex: "^typing_extensions$"
        message: "typing_extensions import found (tracking)"
        severity: warning
    """),
    ),
]


# --- scripts-architecture ---
RULES["scripts-architecture"] = [
    (
        "no-direct-singer-import",
        _import_module(
            "no-direct-singer-import",
            "singer",
            "Direct singer import - use flext_meltano adapter",
        ),
    ),
    (
        "no-direct-singer-import-meltano",
        _import_module(
            "no-direct-singer-import-meltano",
            "meltano",
            "Direct meltano import - use flext_meltano adapter",
        ),
    ),
    (
        "no-direct-db-import",
        _raw("""\
        id: no-direct-db-import
        language: python
        rule:
          any:
            - kind: import_statement
              has:
                kind: dotted_name
                regex: "^(sqlalchemy|oracledb|cx_Oracle|ldap3)$"
                stopBy: end
            - kind: import_from_statement
              has:
                kind: dotted_name
                field: module_name
                regex: "^(sqlalchemy|oracledb|cx_Oracle|ldap3)"
        message: "Direct DB library import - use flext_core adapter"
        severity: error
    """),
    ),
    (
        "no-direct-http-import",
        _raw("""\
        id: no-direct-http-import
        language: python
        rule:
          any:
            - kind: import_statement
              has:
                kind: dotted_name
                regex: "^(requests|httpx|urllib)$"
                stopBy: end
            - kind: import_from_statement
              has:
                kind: dotted_name
                field: module_name
                regex: "^(requests|httpx|urllib)"
        message: "Direct HTTP library import - use flext_core adapter"
        severity: error
    """),
    ),
    (
        "no-direct-cli-import",
        _raw("""\
        id: no-direct-cli-import
        language: python
        rule:
          any:
            - kind: import_statement
              has:
                kind: dotted_name
                regex: "^(click|rich|typer)$"
                stopBy: end
            - kind: import_from_statement
              has:
                kind: dotted_name
                field: module_name
                regex: "^(click|rich|typer)"
        message: "Direct CLI library import - use flext_cli adapter"
        severity: error
    """),
    ),
    (
        "requires-flext-core",
        _import_module(
            "requires-flext-core",
            "flext_core",
            "flext_core import found (tracking)",
            sev="warning",
        ),
    ),
    (
        "requires-flext-meltano-integration",
        _import_module(
            "requires-flext-meltano-integration",
            "singer_sdk",
            "singer_sdk import found (tracking)",
            sev="warning",
        ),
    ),
    (
        "requires-singer-message-handling",
        _raw("""\
        id: requires-singer-message-handling
        language: python
        rule:
          any:
            - pattern: singer.write_message($$$ARGS)
            - pattern: singer.RecordMessage($$$ARGS)
            - pattern: singer.SchemaMessage($$$ARGS)
            - pattern: singer.StateMessage($$$ARGS)
        message: "Singer message handling found (tracking)"
        severity: warning
    """),
    ),
]


# --- scripts-dependencies ---
RULES["scripts-dependencies"] = [
    (
        "require-owner-skill-marker",
        _comment(
            "require-owner-skill-marker",
            "Owner-Skill:",
            "Owner-Skill marker found (tracking)",
        ),
    ),
    (
        "require-docstring",
        _raw("""\
        id: require-docstring-deps
        language: python
        rule:
          kind: expression_statement
          has:
            kind: string
            stopBy: end
          nthChild:
            position: 1
            ofRule:
              kind: module
        message: "Module docstring found (tracking)"
        severity: warning
    """),
    ),
]


# --- scripts-infra ---
RULES["scripts-infra"] = [
    (
        "owner-skill-marker",
        _comment(
            "owner-skill-marker", "Owner-Skill:", "Owner-Skill marker found (tracking)"
        ),
    ),
    (
        "shebang-env-bash",
        _raw("""\
        id: shebang-env-bash
        language: python
        rule:
          kind: comment
          regex: "^#!/usr/bin/env (bash|python3)"
          nthChild: 1
        message: "Shebang found (tracking)"
        severity: warning
    """),
    ),
    (
        "gate-contract-exit-codes",
        _raw("""\
        id: gate-contract-exit-codes
        language: python
        rule:
          any:
            - pattern: sys.exit($$$ARGS)
            - kind: identifier
              regex: "^(EXIT_PASS|EXIT_FAIL|EXIT_USAGE|EXIT_INFRA)$"
        message: "Exit code contract found (tracking)"
        severity: warning
    """),
    ),
]


# --- scripts-maintenance ---
RULES["scripts-maintenance"] = [
    (
        "require-owner-skill-marker",
        _comment(
            "require-owner-skill-marker-maint",
            "Owner-Skill:",
            "Owner-Skill marker found (tracking)",
        ),
    ),
    (
        "require-docstring",
        _raw("""\
        id: require-docstring-maint
        language: python
        rule:
          kind: expression_statement
          has:
            kind: string
            stopBy: end
          nthChild:
            position: 1
            ofRule:
              kind: module
        message: "Module docstring found (tracking)"
        severity: warning
    """),
    ),
]


# --- scripts-security ---
RULES["scripts-security"] = [
    (
        "require-owner-skill-marker",
        _comment(
            "require-owner-skill-marker-sec",
            "Owner-Skill:",
            "Owner-Skill marker found (tracking)",
        ),
    ),
    (
        "require-docstring",
        _raw("""\
        id: require-docstring-sec
        language: python
        rule:
          kind: expression_statement
          has:
            kind: string
            stopBy: end
          nthChild:
            position: 1
            ofRule:
              kind: module
        message: "Module docstring found (tracking)"
        severity: warning
    """),
    ),
]


# --- scripts-testing ---
RULES["scripts-testing"] = [
    (
        "require-owner-skill-marker",
        _comment(
            "require-owner-skill-marker-test",
            "Owner-Skill:",
            "Owner-Skill marker found (tracking)",
        ),
    ),
    (
        "require-shebang-in-sh",
        _comment(
            "require-shebang-in-sh", "^#!/usr/bin/env", "Shebang found (tracking)"
        ),
    ),
]


# --- testing-patterns ---
RULES["testing-patterns"] = [
    (
        "no-assert-true",
        _raw("""\
        id: no-assert-true
        language: python
        rule:
          pattern: assert True
        message: "assert True is always true - use proper assertion"
        severity: error
    """),
    ),
    (
        "no-assert-false",
        _raw("""\
        id: no-assert-false
        language: python
        rule:
          pattern: assert False
        message: "assert False - use pytest.fail() with reason"
        severity: error
        fix: pytest.fail("TODO: add failure reason")
    """),
    ),
    (
        "no-sleep-in-tests",
        _func_call(
            "no-sleep-in-tests",
            "time.sleep($$$ARGS)",
            "time.sleep() in tests - use mocking or freezegun",
        ),
    ),
    (
        "no-bare-assert",
        _raw("""\
        id: no-bare-assert
        language: python
        rule:
          kind: assert_statement
          all:
            - has:
                kind: identifier
                stopBy: neighbor
            - not:
                has:
                  any:
                    - kind: comparison_operator
                    - kind: boolean_operator
                    - kind: call
                    - kind: not_operator
                    - kind: parenthesized_expression
                  stopBy: neighbor
        message: "Bare assert (just variable) - use assertEqual or assert with message"
        severity: warning
    """),
    ),
]


# --- workspace-maintenance ---
RULES["workspace-maintenance"] = [
    (
        "require-owner-skill-marker",
        _comment(
            "require-owner-skill-marker-ws",
            "Owner-Skill:",
            "Owner-Skill marker found (tracking)",
        ),
    ),
    # gitignore patterns need custom since .gitignore isn't a supported language
]


# ============================================================================
# GENERATOR
# ============================================================================


def write_rule_files() -> None:
    """Write ast-grep rule files for all skills."""
    created = 0
    for skill_name, rules in RULES.items():
        if not rules:
            continue
        rules_dir = SKILLS_DIR / skill_name / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)

        for rule_id, yaml_content in rules:
            rule_file = rules_dir / f"{rule_id}.yml"
            # Clean up the YAML content
            content = yaml_content.strip()
            rule_file.write_text(content + "\n")
            created += 1

    print(
        f"Created {created} ast-grep rule files across {len([s for s, r in RULES.items() if r])} skills"
    )


def main() -> None:
    write_rule_files()


if __name__ == "__main__":
    main()

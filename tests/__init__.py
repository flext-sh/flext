# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if _t.TYPE_CHECKING:
    from flext import c, d, e, h, m, p, r, t, x
    from tests.infra.constants import TestsFlextRootConstants
    from tests.infra.models import TestsFlextRootModels
    from tests.infra.protocols import TestsFlextRootProtocols
    from tests.infra.typings import TestsFlextRootTypes
    from tests.infra.utilities import TestsFlextRootUtilities
    from tests.unit.docker_quality_mock_tests import TestDockerQualityDockerfiles
    from tests.unit.libs.versioning_tests import TestVersioning
    from tests.utilities import TestsFlextTestUtilities, u
_LAZY_IMPORTS = merge_lazy_imports(
    (".infra", ".unit"),
    build_lazy_import_map({
        ".infra.constants": ("TestsFlextRootConstants",),
        ".infra.models": ("TestsFlextRootModels",),
        ".infra.protocols": ("TestsFlextRootProtocols",),
        ".infra.typings": ("TestsFlextRootTypes",),
        ".infra.utilities": ("TestsFlextRootUtilities",),
        ".unit.docker_quality_mock_tests": ("TestDockerQualityDockerfiles",),
        ".unit.libs.versioning_tests": ("TestVersioning",),
        ".utilities": ("TestsFlextTestUtilities", "u"),
        "flext": ("c", "d", "e", "h", "m", "p", "r", "t", "x"),
    }),
    exclude_names=(
        "cleanup_submodule_namespace",
        "install_lazy_exports",
        "lazy_getattr",
        "logger",
        "merge_lazy_imports",
        "output",
        "output_reporting",
        "pytest_addoption",
        "pytest_collect_file",
        "pytest_collection_modifyitems",
        "pytest_configure",
        "pytest_runtest_setup",
        "pytest_runtest_teardown",
        "pytest_sessionfinish",
        "pytest_sessionstart",
        "pytest_terminal_summary",
        "pytest_warning_recorded",
    ),
    module_name=__name__,
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__: list[str] = [
    "TestDockerQualityDockerfiles",
    "TestVersioning",
    "TestsFlextRootConstants",
    "TestsFlextRootModels",
    "TestsFlextRootProtocols",
    "TestsFlextRootTypes",
    "TestsFlextRootUtilities",
    "TestsFlextTestUtilities",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "t",
    "u",
    "x",
]

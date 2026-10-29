# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests.unit package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType

from flext_core.lazy import install_lazy_exports
from tests.unit.docker_quality_mock_tests import TestsFlextRootDockerQualityDockerfiles
from tests.unit.examples_runtime_tests import TestsFlextRootExamplesRuntime
from tests.unit.infra_models_tests import TestsFlextRootInfraModels
from tests.unit.release_packaging_tests import TestsFlextRootReleasePackaging

__all__: tuple[str, ...] = (
    "TestsFlextRootDockerQualityDockerfiles",
    "TestsFlextRootExamplesRuntime",
    "TestsFlextRootInfraModels",
    "TestsFlextRootReleasePackaging",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "TestsFlextRootDockerQualityDockerfiles": ".docker_quality_mock_tests",
        "TestsFlextRootExamplesRuntime": ".examples_runtime_tests",
        "TestsFlextRootInfraModels": ".infra_models_tests",
        "TestsFlextRootReleasePackaging": ".release_packaging_tests",
    }),
    public_exports=__all__,
)

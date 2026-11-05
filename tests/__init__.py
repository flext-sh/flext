# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from examples import (
        ExamplesFlextRootConstants,
        FlextRootAclProcessingExample,
        FlextRootAdvancedProcessingExample,
        FlextRootCompleteWorkflowExample,
    )

    from flext import (
        FlextRootCli,
        FlextRootConfig,
        FlextRootConstants,
        FlextRootModels,
        FlextRootProtocols,
        FlextRootSettings,
        FlextRootTypes,
        FlextRootUtilities,
        c,
        config,
        d,
        h,
        m,
        main,
        p,
        r,
        settings,
        t,
        u,
        x,
    )
    from flext_oracle_wms import e
    from flext_tests import api, td, tf, tk, tm
    from tests.base import TestsFlextRootServiceBase, s
    from tests.infra import (
        TestsFlextRootConstants,
        TestsFlextRootModels,
        TestsFlextRootProtocols,
        TestsFlextRootResult,
        TestsFlextRootTypes,
        TestsFlextRootUtilities,
    )
    from tests.unit import (
        TestsFlextRootDockerQualityDockerfiles,
        TestsFlextRootExamplesRuntime,
        TestsFlextRootInfraModels,
        TestsFlextRootReleasePackaging,
    )


__all__: tuple[str, ...] = (
    "ExamplesFlextRootConstants",
    "FlextRootAclProcessingExample",
    "FlextRootAdvancedProcessingExample",
    "FlextRootCli",
    "FlextRootCompleteWorkflowExample",
    "FlextRootConfig",
    "FlextRootConstants",
    "FlextRootModels",
    "FlextRootProtocols",
    "FlextRootSettings",
    "FlextRootTypes",
    "FlextRootUtilities",
    "TestsFlextRootConstants",
    "TestsFlextRootDockerQualityDockerfiles",
    "TestsFlextRootExamplesRuntime",
    "TestsFlextRootInfraModels",
    "TestsFlextRootModels",
    "TestsFlextRootProtocols",
    "TestsFlextRootReleasePackaging",
    "TestsFlextRootResult",
    "TestsFlextRootServiceBase",
    "TestsFlextRootTypes",
    "TestsFlextRootUtilities",
    "api",
    "c",
    "config",
    "d",
    "e",
    "h",
    "m",
    "main",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "td",
    "tf",
    "tk",
    "tm",
    "u",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "ExamplesFlextRootConstants": "examples",
        "FlextRootAclProcessingExample": "examples",
        "FlextRootAdvancedProcessingExample": "examples",
        "FlextRootCli": "flext",
        "FlextRootCompleteWorkflowExample": "examples",
        "FlextRootConfig": "flext",
        "FlextRootConstants": "flext",
        "FlextRootModels": "flext",
        "FlextRootProtocols": "flext",
        "FlextRootSettings": "flext",
        "FlextRootTypes": "flext",
        "FlextRootUtilities": "flext",
        "TestsFlextRootConstants": ".infra",
        "TestsFlextRootDockerQualityDockerfiles": ".unit",
        "TestsFlextRootExamplesRuntime": ".unit",
        "TestsFlextRootInfraModels": ".unit",
        "TestsFlextRootModels": ".infra",
        "TestsFlextRootProtocols": ".infra",
        "TestsFlextRootReleasePackaging": ".unit",
        "TestsFlextRootResult": ".infra",
        "TestsFlextRootServiceBase": ".base",
        "TestsFlextRootTypes": ".infra",
        "TestsFlextRootUtilities": ".infra",
        "api": "flext_tests",
        "c": "flext",
        "config": "flext",
        "d": "flext",
        "e": "flext_oracle_wms",
        "h": "flext",
        "m": "flext",
        "main": "flext",
        "p": "flext",
        "r": "flext",
        "s": ".base",
        "settings": "flext",
        "t": "flext",
        "td": "flext_tests",
        "tf": "flext_tests",
        "tk": "flext_tests",
        "tm": "flext_tests",
        "u": "flext",
        "x": "flext",
    },
    public_exports=__all__,
)

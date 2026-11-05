# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from examples._constants import ExamplesFlextRootConstants
    from examples.acl_processing_example import FlextRootAclProcessingExample
    from examples.advanced_processing_example import FlextRootAdvancedProcessingExample
    from examples.complete_workflow_example import FlextRootCompleteWorkflowExample
    from flext import c, config, d, h, m, main, p, r, settings, t, u, x
    from flext_oracle_oic import s
    from flext_oracle_wms import e
    from flext_tests import api, td, tf, tk, tm


__all__: tuple[str, ...] = (
    "ExamplesFlextRootConstants",
    "FlextRootAclProcessingExample",
    "FlextRootAdvancedProcessingExample",
    "FlextRootCompleteWorkflowExample",
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
        "ExamplesFlextRootConstants": "._constants",
        "FlextRootAclProcessingExample": ".acl_processing_example",
        "FlextRootAdvancedProcessingExample": ".advanced_processing_example",
        "FlextRootCompleteWorkflowExample": ".complete_workflow_example",
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
        "s": "flext_oracle_oic",
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

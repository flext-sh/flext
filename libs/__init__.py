# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Libs package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import libs.versioning as _libs_versioning

    versioning = _libs_versioning
    from flext_core.constants import FlextConstants as c
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.models import FlextModels as m
    from flext_core.protocols import FlextProtocols as p
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from flext_core.typings import FlextTypes as t
    from flext_core.utilities import FlextUtilities as u
    from libs.versioning import (
        SEMVER_RE,
        bump_version,
        current_workspace_version,
        parse_semver,
        release_tag_from_branch,
        replace_project_version,
    )
_LAZY_IMPORTS = {
    "SEMVER_RE": ("libs.versioning", "SEMVER_RE"),
    "bump_version": ("libs.versioning", "bump_version"),
    "c": ("flext_core.constants", "FlextConstants"),
    "current_workspace_version": ("libs.versioning", "current_workspace_version"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("flext_core.models", "FlextModels"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "parse_semver": ("libs.versioning", "parse_semver"),
    "r": ("flext_core.result", "FlextResult"),
    "release_tag_from_branch": ("libs.versioning", "release_tag_from_branch"),
    "replace_project_version": ("libs.versioning", "replace_project_version"),
    "s": ("flext_core.service", "FlextService"),
    "t": ("flext_core.typings", "FlextTypes"),
    "u": ("flext_core.utilities", "FlextUtilities"),
    "versioning": "libs.versioning",
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__: list[str] = [
    "SEMVER_RE",
    "bump_version",
    "c",
    "current_workspace_version",
    "d",
    "e",
    "h",
    "m",
    "p",
    "parse_semver",
    "r",
    "release_tag_from_branch",
    "replace_project_version",
    "s",
    "t",
    "u",
    "versioning",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext.cli import FlextRootCli, main
    from flext.config import FlextRootConfig, config
    from flext.constants import FlextRootConstants, c
    from flext.models import FlextRootModels, m
    from flext.protocols import FlextRootProtocols, p
    from flext.settings import FlextRootSettings, settings
    from flext.typings import FlextRootTypes, t
    from flext.utilities import FlextRootUtilities, u
    from flext_db_oracle import (
        build_lazy_import_map,
        cleanup_submodule_namespace,
        core,
        db_oracle,
        install_lazy_exports,
        lazy,
        lazy_getattr,
        lazy_member,
        merge_lazy_imports,
        normalize_lazy_imports,
        resolve_lazy_members,
    )
    from flext_grpc import grpc
    from flext_infra import infra
    from flext_ldap import ldap, ldif
    from flext_meltano import meltano
    from flext_observability import observability
    from flext_oracle_oic import auth, d, h, oracle_oic, r, s, web, x
    from flext_oracle_wms import cli, e, oracle_wms
    from flext_plugin import plugin
    from flext_quality import quality
    from flext_tests import api, install_local_packages, td, tf, tk, tm


__all__: tuple[str, ...] = (
    "FlextRootCli",
    "FlextRootConfig",
    "FlextRootConstants",
    "FlextRootModels",
    "FlextRootProtocols",
    "FlextRootSettings",
    "FlextRootTypes",
    "FlextRootUtilities",
    "api",
    "auth",
    "build_lazy_import_map",
    "c",
    "cleanup_submodule_namespace",
    "cli",
    "config",
    "core",
    "d",
    "db_oracle",
    "e",
    "grpc",
    "h",
    "infra",
    "install_lazy_exports",
    "install_local_packages",
    "lazy",
    "lazy_getattr",
    "lazy_member",
    "ldap",
    "ldif",
    "m",
    "main",
    "meltano",
    "merge_lazy_imports",
    "normalize_lazy_imports",
    "observability",
    "oracle_oic",
    "oracle_wms",
    "p",
    "plugin",
    "quality",
    "r",
    "resolve_lazy_members",
    "s",
    "settings",
    "t",
    "td",
    "tf",
    "tk",
    "tm",
    "u",
    "web",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextRootCli": ".cli",
        "FlextRootConfig": ".config",
        "FlextRootConstants": ".constants",
        "FlextRootModels": ".models",
        "FlextRootProtocols": ".protocols",
        "FlextRootSettings": ".settings",
        "FlextRootTypes": ".typings",
        "FlextRootUtilities": ".utilities",
        "api": "flext_tests",
        "auth": "flext_oracle_oic",
        "build_lazy_import_map": "flext_db_oracle",
        "c": ".constants",
        "cleanup_submodule_namespace": "flext_db_oracle",
        "cli": "flext_oracle_wms",
        "config": ".config",
        "core": "flext_db_oracle",
        "d": "flext_oracle_oic",
        "db_oracle": "flext_db_oracle",
        "e": "flext_oracle_wms",
        "grpc": "flext_grpc",
        "h": "flext_oracle_oic",
        "infra": "flext_infra",
        "install_lazy_exports": "flext_db_oracle",
        "install_local_packages": "flext_tests",
        "lazy": "flext_db_oracle",
        "lazy_getattr": "flext_db_oracle",
        "lazy_member": "flext_db_oracle",
        "ldap": "flext_ldap",
        "ldif": "flext_ldap",
        "m": ".models",
        "main": ".cli",
        "meltano": "flext_meltano",
        "merge_lazy_imports": "flext_db_oracle",
        "normalize_lazy_imports": "flext_db_oracle",
        "observability": "flext_observability",
        "oracle_oic": "flext_oracle_oic",
        "oracle_wms": "flext_oracle_wms",
        "p": ".protocols",
        "plugin": "flext_plugin",
        "quality": "flext_quality",
        "r": "flext_oracle_oic",
        "resolve_lazy_members": "flext_db_oracle",
        "s": "flext_oracle_oic",
        "settings": ".settings",
        "t": ".typings",
        "td": "flext_tests",
        "tf": "flext_tests",
        "tk": "flext_tests",
        "tm": "flext_tests",
        "u": ".utilities",
        "web": "flext_oracle_oic",
        "x": "flext_oracle_oic",
    }),
    public_exports=__all__,
)

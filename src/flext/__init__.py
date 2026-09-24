# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_auth import auth
    from flext_cli import cli
    from flext_core import core, d, e, h, lazy_attribute, r, x
    from flext_db_oracle import db_oracle
    from flext_dbt_ldap import dbt_ldap
    from flext_dbt_ldif import dbt_ldif
    from flext_dbt_oracle_wms import dbt_oracle_wms
    from flext_grpc import grpc
    from flext_infra import docs_main, infra
    from flext_ldap import ldap
    from flext_ldif import ldif
    from flext_meltano import meltano
    from flext_observability import observability
    from flext_oracle_oic import oracle_oic
    from flext_oracle_wms import oracle_wms
    from flext_plugin import plugin
    from flext_quality import quality
    from flext_tap_ldap import tap_ldap
    from flext_tap_ldif import tap_ldif
    from flext_tap_oracle import tap_oracle
    from flext_tap_oracle_oic import tap_oracle_oic
    from flext_tap_oracle_wms import tap_oracle_wms
    from flext_target_ldap import target_ldap
    from flext_target_ldif import target_ldif
    from flext_target_oracle import target_oracle
    from flext_target_oracle_oic import target_oracle_oic
    from flext_target_oracle_wms import target_oracle_wms
    from flext_tests import (
        active_rules,
        discover_repository_root,
        install_local_packages,
        load_infra_report,
        split_csv,
        td,
        tf,
        tk,
        tm,
        tv,
    )
    from flext_web import web

    from . import services
    from .api import FlextRoot, api, flext
    from .base import FlextRootServiceBase, s
    from .cli import FlextRootCli, main
    from .config import FlextRootConfig, config
    from .constants import FlextRootConstants, c
    from .models import FlextRootModels, m
    from .protocols import FlextRootProtocols, p
    from .settings import FlextRootSettings, FlextRootSettings as settings
    from .typings import FlextRootTypes, t
    from .utilities import FlextRootUtilities, u


__all__: tuple[str, ...] = (
    "FlextRoot",
    "FlextRootCli",
    "FlextRootConfig",
    "FlextRootConstants",
    "FlextRootModels",
    "FlextRootProtocols",
    "FlextRootServiceBase",
    "FlextRootSettings",
    "FlextRootTypes",
    "FlextRootUtilities",
    "active_rules",
    "api",
    "auth",
    "c",
    "cli",
    "config",
    "core",
    "d",
    "db_oracle",
    "dbt_ldap",
    "dbt_ldif",
    "dbt_oracle_wms",
    "discover_repository_root",
    "docs_main",
    "e",
    "flext",
    "grpc",
    "h",
    "infra",
    "install_local_packages",
    "lazy_attribute",
    "ldap",
    "ldif",
    "load_infra_report",
    "m",
    "main",
    "meltano",
    "observability",
    "oracle_oic",
    "oracle_wms",
    "p",
    "plugin",
    "quality",
    "r",
    "s",
    "services",
    "settings",
    "split_csv",
    "t",
    "tap_ldap",
    "tap_ldif",
    "tap_oracle",
    "tap_oracle_oic",
    "tap_oracle_wms",
    "target_ldap",
    "target_ldif",
    "target_oracle",
    "target_oracle_oic",
    "target_oracle_wms",
    "td",
    "tf",
    "tk",
    "tm",
    "tv",
    "u",
    "web",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".api": ("FlextRoot", "api", "flext"),
            ".base": ("FlextRootServiceBase", "s"),
            ".cli": ("FlextRootCli", "main"),
            ".config": ("FlextRootConfig", "config"),
            ".constants": ("FlextRootConstants", "c"),
            ".models": ("FlextRootModels", "m"),
            ".protocols": ("FlextRootProtocols", "p"),
            ".services": ("services",),
            ".settings": ("FlextRootSettings", "settings"),
            ".typings": ("FlextRootTypes", "t"),
            ".utilities": ("FlextRootUtilities", "u"),
            "flext_auth": ("auth",),
            "flext_cli": ("cli",),
            "flext_core": ("core", "d", "e", "h", "lazy_attribute", "r", "x"),
            "flext_db_oracle": ("db_oracle",),
            "flext_dbt_ldap": ("dbt_ldap",),
            "flext_dbt_ldif": ("dbt_ldif",),
            "flext_dbt_oracle_wms": ("dbt_oracle_wms",),
            "flext_grpc": ("grpc",),
            "flext_infra": ("docs_main", "infra"),
            "flext_ldap": ("ldap",),
            "flext_ldif": ("ldif",),
            "flext_meltano": ("meltano",),
            "flext_observability": ("observability",),
            "flext_oracle_oic": ("oracle_oic",),
            "flext_oracle_wms": ("oracle_wms",),
            "flext_plugin": ("plugin",),
            "flext_quality": ("quality",),
            "flext_tap_ldap": ("tap_ldap",),
            "flext_tap_ldif": ("tap_ldif",),
            "flext_tap_oracle": ("tap_oracle",),
            "flext_tap_oracle_oic": ("tap_oracle_oic",),
            "flext_tap_oracle_wms": ("tap_oracle_wms",),
            "flext_target_ldap": ("target_ldap",),
            "flext_target_ldif": ("target_ldif",),
            "flext_target_oracle": ("target_oracle",),
            "flext_target_oracle_oic": ("target_oracle_oic",),
            "flext_target_oracle_wms": ("target_oracle_wms",),
            "flext_tests": (
                "active_rules",
                "discover_repository_root",
                "install_local_packages",
                "load_infra_report",
                "split_csv",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
            ),
            "flext_web": ("web",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)

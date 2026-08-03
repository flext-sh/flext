"""FLEXT infra test helpers for utilities."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from flext_tests import FlextTestsUtilities
from tests.infra.typings import t


class TestsFlextRootUtilities(FlextTestsUtilities):
    class Workspace:
        """Workspace-level test utilities."""

        class Tests:
            """Test infrastructure utility functions."""

            @staticmethod
            def resolve_module_path(*, anchor_file: Path, relative_path: str) -> Path:
                for parent in anchor_file.resolve().parents:
                    candidate = parent / relative_path
                    if candidate.exists():
                        return candidate
                msg = f"Could not resolve module path: {relative_path}"
                raise FileNotFoundError(msg)

            @staticmethod
            def load_module(
                module_name: str, relative_path: str, *, anchor_file: Path
            ) -> t.Workspace.Tests.LoadedModule:
                module_path = (
                    TestsFlextRootUtilities.Workspace.Tests.resolve_module_path(
                        anchor_file=anchor_file, relative_path=relative_path
                    )
                )
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is None or spec.loader is None:
                    msg = f"Invalid module spec for {module_name}"
                    raise RuntimeError(msg)
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)
                return module


u = TestsFlextRootUtilities

__all__: list[str] = ["TestsFlextRootUtilities", "u"]

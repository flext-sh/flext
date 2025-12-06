"""Tests for flext workspace package components.

This module provides tests for the centralized components in the flext package.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import FlextCliConstants, FlextCliModels, FlextCliUtilities

from flext import (
    FlextConstants,
    FlextModels,
    FlextProtocols,
    FlextServiceBase,
    FlextTypes,
    FlextUtilities,
    c,
    m,
    p,
    s,
    t,
    u,
)


class TestFlextWorkspace:
    """Test suite for flext workspace components."""

    def test_constants_inheritance(self) -> None:
        """Test that FlextConstants inherits correctly."""
        assert issubclass(FlextConstants, FlextCliConstants)
        assert hasattr(FlextConstants, "Workspace")
        assert FlextConstants.Workspace.NAME == "flext"
        assert c is FlextConstants

    def test_models_inheritance(self) -> None:
        """Test that FlextModels inherits correctly."""
        assert issubclass(FlextModels, FlextCliModels)
        assert m is FlextModels

    def test_utilities_inheritance(self) -> None:
        """Test that FlextUtilities inherits correctly."""
        assert issubclass(FlextUtilities, FlextCliUtilities)
        assert u is FlextUtilities
        # Check nested class aliases
        assert u.Constants is FlextConstants
        assert u.Models is FlextModels
        assert u.Types is FlextTypes

    def test_service_base_inheritance(self) -> None:
        """Test that FlextServiceBase inherits correctly."""
        assert issubclass(FlextServiceBase, FlextServiceBase.__base__)
        assert s is FlextServiceBase
        # Check nested class aliases
        assert s.Constants is FlextConstants
        assert s.Models is FlextModels
        assert s.Types is FlextTypes
        assert s.Utilities is FlextUtilities

    def test_protocols_existence(self) -> None:
        """Test that FlextProtocols exists."""
        assert p is FlextProtocols

    def test_types_existence(self) -> None:
        """Test that FlextTypes exists."""
        assert t is FlextTypes

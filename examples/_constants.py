"""Shared constants for FLEXT runnable examples.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, MutableSequence, Sequence
from enum import StrEnum, unique
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from examples import t


class FlextRootExamplesConstants:
    """Examples constants facade — access via FlextRootExamplesConstants.*."""

    MIN_OID_ACL_ATTRIBUTES: int = 2
    EXPECTED_OID_ACL_COUNT: int = 2

    class Stage(StrEnum):
        """Processing stage enumeration used across pipeline examples."""

        VALIDATE = "validate"
        PROCESS = "process"
        ANALYZE = "analyze"

    @unique
    class WorkflowStage(StrEnum):
        """Processing stage enumeration used across complete-workflow examples."""

        VALIDATION = "validation"
        PROCESSING = "processing"
        ANALYSIS = "analysis"
        AGGREGATION = "aggregation"

    @unique
    class ErrorMessages(StrEnum):
        """Runtime error message constants for example execution."""

        LDIF_NO_ENTRIES = "LDIF parser produced no entries"
        ACL_PERMISSION_NOT_GRANTED = (
            "LDIF ACL example did not grant the declared permission"
        )
        OID_INSUFFICIENT_ATTRIBUTES = (
            "OID server declared fewer than two ACL attributes"
        )
        OID_ACL_ATTRIBUTE_LOST = "OID ACL example lost a declared attribute"
        ADVANCED_NO_ANALYSIS = "advanced example produced no analysis"
        COMPLETE_NO_CONTENT = "complete workflow produced no content"

    class JsonMappingOrNoneHelper:
        """Helper to extract JsonMapping from JsonValue."""

        @staticmethod
        def extract(value: t.JsonValue) -> t.JsonMapping | None:
            if not isinstance(value, Mapping):
                return None
            return dict(value.items())

    class JsonMappingSequenceHelper:
        """Helper to extract sequence of JsonMapping from JsonValue."""

        @staticmethod
        def extract(value: t.JsonValue) -> t.SequenceOf[t.JsonMapping]:
            if not isinstance(value, Sequence) or isinstance(
                value,
                (str, bytes, bytearray),
            ):
                return ()
            mappings: MutableSequence[t.JsonMapping] = []
            for item in value:
                mapping_item = (
                    FlextRootExamplesConstants.JsonMappingOrNoneHelper.extract(item)
                )
                if mapping_item is not None:
                    mappings.append(mapping_item)
            return tuple(mappings)

    class StringSequenceHelper:
        """Helper to extract string sequence from JsonValue."""

        @staticmethod
        def extract(value: t.JsonValue) -> t.StrSequence:
            if not isinstance(value, Sequence) or isinstance(
                value,
                (str, bytes, bytearray),
            ):
                return ()
            strings: MutableSequence[str] = []
            for item in value:
                if isinstance(item, str):
                    strings.append(item)
            return tuple(strings)


Stage = FlextRootExamplesConstants.Stage

__all__: list[str] = ["FlextRootExamplesConstants"]

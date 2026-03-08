"""Auto-generated centralized models."""

from __future__ import annotations

from flext_core import t
from pydantic import BaseModel, ConfigDict

EntryDict = dict[str, t.Scalar | list[str] | dict[str, t.Scalar | list[str]]]


class ValidationRules(BaseModel):
    model_config = ConfigDict(extra="forbid")
    required_permissions: list[str]
    forbidden_combinations: list[tuple[str, str]]


class EntryWithServer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entry: EntryDict
    server_type: str

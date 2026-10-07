"""Public validation and serialization of workspace test models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from json import dumps
from pathlib import Path

import pytest
from flext_tests import tm

from flext import c, m, t
from tests.infra import TestsFlextRootModels


class TestsFlextRootInfraModels:
    """Exercise the exported model without replacing its declaration owner."""

    class Tests:
        """Public Pydantic contracts for module references."""

        @staticmethod
        def test_module_ref_json_contract(tmp_path: Path) -> None:
            """Preserve supplied values, schema metadata and validation failures."""
            model = TestsFlextRootModels.TestsFlextRoot.ModuleRef
            anchor_file = tmp_path / "module.py"
            module_name = __name__
            relative_path = "module.py"
            value = model(
                anchor_file=anchor_file,
                module_name=module_name,
                relative_path=relative_path,
            )
            restored = model.model_validate_json(value.model_dump_json())
            for current in (value, restored):
                tm.that(current.anchor_file, eq=anchor_file)
                tm.that(current.module_name, eq=module_name)
                tm.that(current.relative_path, eq=relative_path)
            tm.that(restored.model_dump(), eq=value.model_dump())
            tm.that(m.Value in type(restored).__mro__, eq=True)
            tm.that(type(restored) is model, eq=True)

            schema = model.model_json_schema()
            required = {
                name
                for name, field in model.model_fields.items()
                if field.is_required()
            }
            tm.that(set(schema["required"]), eq=required)
            for name in ("anchor_file", "module_name", "relative_path"):
                tm.that(
                    schema["properties"][name]["description"],
                    eq=model.model_fields[name].description,
                )
                with pytest.raises(c.ValidationError) as captured:
                    model.model_validate_json(value.model_dump_json(exclude={name}))
                tm.that(
                    any(
                        error["loc"] == (name,) and error["type"] == "missing"
                        for error in captured.value.errors()
                    ),
                    eq=True,
                )

            invalid_paths: t.VariadicTuple[t.JsonValue] = (None, {}, [])
            for invalid_path in invalid_paths:
                payload = value.model_dump(mode="json")
                payload["anchor_file"] = invalid_path
                with pytest.raises(c.ValidationError):
                    model.model_validate_json(dumps(payload))
            with pytest.raises(c.ValidationError):
                model.model_validate_json("{")

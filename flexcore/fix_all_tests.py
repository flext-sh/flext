#!/usr/bin/env python3
import re

"""Fix_All_Tests module.

This module provides fix_all_tests functionality.
"""

def fix_pipeline_test_complete(content):
    # Fix all PipelineStep literals - add missing fields
    content = re.sub(
        r"(entities\.PipelineStep\{[^}]+),\s*\}",
        r"\1,\n\t\tIsEnabled: true,\n\t}",
        content,
    )

    # Fix err variable references that should be res
    lines = content.split("\n")
    fixed_lines = []
    last_var = None

    for line in lines:
        # Track variable assignments
        if "err := pipeline." in line:
            last_var = "err"
            line = line.replace("err :=", "res :=")
        elif "res := pipeline." in line:
            last_var = "res"

        # Fix assertions based on last variable
        if last_var == "res" and "err)" in line and "assert." in line:
            line = line.replace("err)", "res)")
            line = line.replace(
                "assert.Error(t, res)", "assert.True(t, res.IsFailure())"
            )
            line = line.replace(
                "require.NoError(t, res)", "require.True(t, res.IsSuccess())"
            )
            line = line.replace("err.Error()", "res.Error().Error()")

        # Fix Validate calls
        if "err := tt.pipeline.Validate()" in line:
            line = line.replace("err :=", "res :=")
            last_var = "res"
        elif "err := pipeline.Validate()" in line:
            line = line.replace("err :=", "res :=")
            last_var = "res"

        # Fix BenchmarkPipelineValidate
        if "_ = pipeline.Validate()" in line:
            line = "\t\t_ = pipeline.Validate()"

        # Remove Description field references
        if "Description:" in line and "pipeline.Steps[0].Description" not in line:
            continue

        # Fix Description assertions
        if (
            'assert.Equal(t, "Updated description", pipeline.Steps[0].Description)'
            in line
        ):
            line = "\t// Description field removed"

        fixed_lines.append(line)

    content = "\n".join(fixed_lines)

    # Fix specific benchmark issues
    content = re.sub(
        r'pipeline := entities\.NewPipeline\("benchmark", "description", "owner"\)\n\tpipeline\.AddStep',
        'result := entities.NewPipeline("benchmark", "description", "owner")\n\trequire.True(b, result.IsSuccess())\n\tpipeline := result.Value()\n\tpipeline.AddStep',
        content,
    )

    # Fix Order field in validation test
    return content.replace(
        '{ID: "1", Name: "Step1", Type: "extractor", Order: 1}',
        '{ID: "1", Name: "Step1", Type: "extractor", IsEnabled: true}',
    )


with open("/home/marlonsc/flext/flexcore/domain/entities/pipeline_test.go") as f:
    content = f.read()

fixed = fix_pipeline_test_complete(content)

with open("/home/marlonsc/flext/flexcore/domain/entities/pipeline_test.go", "w") as f:
    f.write(fixed)

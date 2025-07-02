#!/usr/bin/env python3
import re

"""Fix_Tests module.

This module provides fix_tests functionality.
"""

def fix_pipeline_tests(content):
    # Fix all err := pipeline.AddStep to res := pipeline.AddStep
    content = re.sub(
        r"err := pipeline\.AddStep\(([^)]+)\)\n\s+require\.NoError\(t, err\)",
        r"res := pipeline.AddStep(\1)\n\trequire.True(t, res.IsSuccess())",
        content,
    )

    # Fix all err := pipeline.UpdateStep
    content = re.sub(
        r"err := pipeline\.UpdateStep\(([^)]+)\)\n\s+require\.NoError\(t, err\)",
        r"res := pipeline.UpdateStep(\1)\n\trequire.True(t, res.IsSuccess())",
        content,
    )

    # Fix all err := pipeline.RemoveStep
    content = re.sub(
        r"err := pipeline\.RemoveStep\(([^)]+)\)\n\s+require\.NoError\(t, err\)",
        r"res := pipeline.RemoveStep(\1)\n\trequire.True(t, res.IsSuccess())",
        content,
    )

    # Fix assert.Error calls
    content = re.sub(
        r"err := pipeline\.(AddStep|UpdateStep|RemoveStep)\(([^)]+)\)\n\s+assert\.Error\(t, err\)",
        r"res := pipeline.\1(\2)\n\tassert.True(t, res.IsFailure())",
        content,
    )

    # Fix assert.Contains for error messages
    content = re.sub(
        r'assert\.Contains\(t, err\.Error\(\), "([^"]+)"\)',
        r'assert.Contains(t, res.Error().Error(), "\1")',
        content,
    )

    # Remove Description and Order fields from PipelineStep
    content = re.sub(r'\s+Description: "[^"]+",?\n', "", content)
    content = re.sub(r"\s+Order:\s+\d+,?\n", "", content)

    # Fix step creation with proper fields
    content = re.sub(
        r'step2 := entities\.PipelineStep\{\n\s+ID:\s+uuid\.New\(\)\.String\(\),\n\s+Name:\s+"Transform",\n\s+Type:\s+"transformer",\n\s+Config:\s+map\[string\]interface\{\}\{"operation": "clean"\},\n\s+\}',
        'step2 := entities.PipelineStep{\n\t\tID:          uuid.New().String(),\n\t\tName:        "Transform",\n\t\tType:        "transformer",\n\t\tConfig:      map[string]interface{}{"operation": "clean"},\n\t\tIsEnabled:   true,\n\t}',
        content,
    )

    # Fix other step creations
    content = re.sub(
        r'entities\.PipelineStep\{ID: ([^,]+), Name: "([^"]+)", Order: \d+\}',
        r'entities.PipelineStep{ID: \1, Name: "\2", Type: "generic", IsEnabled: true}',
        content,
    )

    # Fix Start, Complete, Fail method calls
    content = re.sub(
        r"err := pipeline\.(Start|Complete|Fail)\((.*?)\)\n\s+require\.NoError\(t, err\)",
        r"res := pipeline.\1(\2)\n\trequire.True(t, res.IsSuccess())",
        content,
    )

    content = re.sub(
        r"err := pipeline\.(Start|Complete|Fail)\((.*?)\)\n\s+assert\.Error\(t, err\)",
        r"res := pipeline.\1(\2)\n\tassert.True(t, res.IsFailure())",
        content,
    )

    # Fix Validate method
    content = re.sub(
        r"err := ([^.]+)\.Validate\(\)\n(\s+)if tt\.expectError \{",
        r"res := \1.Validate()\n\2if tt.expectError {",
        content,
    )

    content = re.sub(
        r"assert\.Error\(t, err\)\n(\s+)assert\.Contains\(t, err\.Error\(\), tt\.errorMsg\)",
        r"assert.True(t, res.IsFailure())\n\1assert.Contains(t, res.Error().Error(), tt.errorMsg)",
        content,
    )

    return re.sub(
        r"assert\.NoError\(t, err\)", r"assert.True(t, res.IsSuccess())", content
    )


if __name__ == "__main__":
    filename = "/home/marlonsc/flext/flexcore/domain/entities/pipeline_test.go"

    with open(filename) as f:
        content = f.read()

    fixed_content = fix_pipeline_tests(content)

    with open(filename, "w") as f:
        f.write(fixed_content)

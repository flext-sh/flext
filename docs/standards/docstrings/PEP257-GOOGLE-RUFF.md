# FLEXT Docstring Standards — PEP 257 + Google Style + Ruff Compliant

**Compliance**:

- PEP 257 (Python Docstring Conventions)
- Google Style (Google Python Style Guide)
- Ruff strict mode (`select = ["ALL"]`, `preview = true`)
- Target: Python 3.13+

**Key ruff rules enforced**:

- `D1xx` - Missing docstrings
- `D2xx` - Whitespace in docstrings
- `D4xx` - Docstring content
- `DOC501/502` - Undocumented parameters/raises

**Ignored by design** (per `pyproject.toml`):

- `D203` - blank line before class docstring ✗ (not used)
- `D213` - multi-line summary on line 2 ✗ (keep on line 1)

**Not enforced by the current Ruff policy:**

- `D401` - imperative mood (ignored as `non-imperative-mood`)
- `D417` - undocumented params (ignored as `undocumented-param`)

---

## Module Level Docstring

### Format

```python
"""Brief one-line module summary.

More detailed explanation of what this module does, key classes,
and responsibilities. Can span multiple lines, organized logically.

Key exports:
    ClassName: What it does.
    FunctionName: What it does.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

# Rest of file follows
```

### Rules

- `"""` on first line (not line 2)
- One-line summary ends with period
- Blank line before extended description
- **Copyright INSIDE docstring** (not comment)
- Copyright format: exactly `Copyright (c) 2025 FLEXT Team. All rights reserved.`
- SPDX on separate line

### Real Example from Project

```python
"""DDD base models with Pydantic v2 validation and dispatcher-first CQRS.

Expose ``FlextModels`` as the façade for entities, value objects, aggregates,
commands, queries, and domain events that integrate directly with the
dispatcher-driven CQRS layer. Concrete implementations live in the
``models`` subpackage and are organized for clear validation, serialization,
and event collection.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""
```

---

## Class Docstring

### Format

```python
class MyClass(BaseClass):
    """Brief one-line class summary.

    Extended description explaining:
    - Domain role (what it represents)
    - Key responsibilities
    - Notable constraints or lifecycle

    Attributes:
        attr_name (type): Description of what it stores.
        another_attr (type): Another attribute.

    Raises:
        ValueError: When attribute validation fails.

    Example:
        >>> obj = MyClass(name="test")
        >>> obj.process()
    """
```

### Rules

- Summary on first line, ends with period
- No blank line after `"""` opening
- Extended description starts on next line
- Blank line before `Attributes:` section
- Attributes format: `name (type): description.`
- Raises section if class **init** can raise exceptions
- Example section for complex public APIs

### Real Example from Project

```python
class Ex00UserProfile(m.Entity):
    """User profile transport model."""

    name: str = u.Field(min_length=1)
    email: str = u.Field(min_length=1)
    status: c.Status = c.Status.ACTIVE

    def activate(self) -> p.Result[None]:
        """Activate user once."""
        if self.status == c.Status.ACTIVE:
            return r[None].fail("Already active")
        return r.ok(None)
```

---

## Function / Method Docstring

### Format

```python
def process_data(
    input_path: Path, *, validate: bool = True, timeout: int | None = None
) -> t.MappingKV[str, Any]:
    """Process data from input file and return structured result.

    Longer description explaining what this function does,
    key assumptions, and how it differs from similar functions.

    Args:
        input_path: Path to input file to process.
        validate: Whether to validate data before processing.
            Defaults to True.
        timeout: Maximum seconds to wait. None means no timeout.

    Returns:
        Dictionary with keys 'data' (list) and 'errors' (list).
        Empty errors list indicates entirely successful processing.

    Raises:
        FileNotFoundError: If input_path does not exist.
        ValueError: If data validation fails with validate=True.
        TimeoutError: If operation exceeds timeout seconds.

    Example:
        >>> result = process_data(Path("data.json"))
        >>> if result["errors"]:
        ...     u.Cli.print(f"Found {len(result['errors'])} errors")
    """
```

### Rules

- Summary on first line, ends with period
- Blank line before extended description
- **Args section**: Required if function takes parameters
  - Format: `name: Brief description.`
  - Multiple lines use hanging indent
  - Document defaults here, not in description
- **Returns section**: Required if returns non-None value
  - Format: `type: Description of what's returned.`
  - If complex, describe each field
- **Raises section**: Required if function can raise exceptions
  - Format: `ExceptionType: When it's raised.`
  - Each exception on separate line
- **Example section**: Optional but recommended for public APIs

### Real Example from Project

```python
@staticmethod
def iter_directory_python_files(
    directory: Path, *, pattern: str | None = None, skip_pycache: bool = True
) -> t.SequenceOf[Path]:
    """Iterate Python files in a single directory tree.

    Scoped to one directory (project src, subdirectory, etc.) — unlike
    ``iter_python_files`` which discovers across the whole workspace.

    Args:
        directory: Root directory to scan.
        pattern: Glob pattern (defaults to ``c.Infra.Extensions.PYTHON_GLOB``).
        skip_pycache: Exclude ``__pycache__`` paths (default True).

    Returns:
        Sorted list of matching file paths. Empty list if directory
        does not exist.
    """
    if not directory.is_dir():
        return []
    effective_pattern = pattern or c.Infra.Extensions.PYTHON_GLOB
    files = sorted(directory.rglob(effective_pattern))
    if skip_pycache:
        return [f for f in files if "__pycache__" not in f.parts]
    return files
```

---

## Private Function (`_func`)

### When to Document

- Skip detailed docstring if name + signature is self-explanatory
- Add one-liner if purpose is non-obvious

### Examples

```python
def _parse_value(text: str) -> int:
    """Parse integer from text string."""
    return int(text.strip())


def _looks_like_project(path: Path) -> bool:
    # Skip docstring HERE—obvious from name
    return (path / "Makefile").exists() or (path / "pyproject.toml").exists()
```

---

## Property

### Format

```python
@property
def computed_value(self) -> float:
    """Return the computed value for this instance."""
    return self.value * self._factor
```

### Rules

- One-line summary, ends with period (usually)
- No Args/Returns sections (obvious from decorator)
- If side effects or expensive computation, explain

---

## Magic Methods (`__init__`, `__str__`, etc.)

### `__init__`

```python
def __init__(self, name: str, timeout: int = 30):
    """Initialize processor with name and timeout.

    Args:
        name: Human-readable identifier for this processor.
        timeout: Seconds to wait before raising TimeoutError.

    Raises:
        ValueError: If timeout is negative.
    """
```

### `__str__` / `__repr__`

```python
def __str__(self) -> str:
    """Return '{ClassName}(field1=value, field2=value)' representation."""
    return f"{self.__class__.__name__}(name={self.name!r}, count={self.count})"
```

### Others

- Document if behavior is non-obvious
- Skip if trivial (e.g., `__eq__` comparing fields)

---

## Exception Class

### Format

```python
class DataProcessingError(Exception):
    """Raised when data processing encounters unrecoverable error.

    Attributes:
        message: Human-readable error description.
        code: Error code for categorization (e.g., "PARSE_ERROR").
        data: Original data that caused the error.
    """

    def __init__(self, message: str, code: str = "UNKNOWN", data: Any = None) -> None:
        """Initialize error with message and optional code.

        Args:
            message: Error description.
            code: Error category (defaults to "UNKNOWN").
            data: Original problematic data (for debugging).
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data
```

---

## Async Function

### Format

```python
async def fetch_data(url: str, timeout: int = 30) -> bytes:
    """Fetch data from URL asynchronously.

    Args:
        url: Full URL to fetch (must use HTTPS).
        timeout: Seconds before canceling request.

    Returns:
        Raw response bytes.

    Raises:
        ConnectionError: If network request fails.
        TimeoutError: If operation exceeds timeout.
    """
```

---

## Multi-line Parameter Description

### Format

```python
def configure(
    mode: str, options: t.MappingKV[str, Any] | None = None, verbosity: int = 1
) -> None:
    """Settingsure processor behavior.

    Args:
        mode: Processing mode ("strict", "lenient", or "auto").
            Strict mode raises on first error. Lenient collects all errors.
        options: Configuration options passed to underlying library.
            Reserved keys: \"_timeout\", \"_retries\".
        verbosity: Output verbosity level (0=silent, 1=normal, 2=verbose).
    """
```

---

## Ruff-Compliant Checklist

Before committing code, verify:

- [ ] All files have module docstring (ruff: D100)
- [ ] All public functions have docstring (ruff: D102)
- [ ] All public classes have docstring (ruff: D101)
- [ ] All functions with Args include `Args:` section (ruff: DOC402, but ignored)
- [ ] All functions with Returns include `Returns:` section (ruff: DOC501, but ignored)
- [ ] All functions with Raises include `Raises:` section (ruff: DOC502, but ignored)
- [ ] No blank line after opening `"""` (ruff: D202)
- [ ] Docstring ends with `"""` on separate line for multi-line (ruff: D209)
- [ ] No double blank lines in docstring (ruff: D205)
- [ ] Module copyright is INSIDE docstring, not comment
- [ ] Copyright format: `Copyright (c) 2025 FLEXT Team. All rights reserved.`
- [ ] SPDX identifier present: `SPDX-License-Identifier: MIT`

Run validation:

```bash
ruff check --select=D --preview src/
ruff check --select=D,DOC --preview src/
```

---

## Private vs Public

### Skip docstring (private)

```python
def _internal_helper(x: int) -> int:
    # Skip if obvious from name + type
    return x * 2


def _validate_email(addr: str) -> bool:
    # Skip if implementation self-documenting
    return "@" in addr and "." in addr.split("@")[1]
```

### Document (public)

```python
def search(query: str, limit: int = 10) -> t.SequenceOf[Result]:
    """Search index with query, return up to limit results."""


def validate_settings(cfg: dict) -> bool:
    """Validate configuration against schema."""
```

---

## Document When

✅ **MUST document**:

- Non-obvious return value semantics (True/False/None meaning)
- Functions that modify state or have side effects
- Multiple similar methods (contrast them)
- Complex algorithms or constraints
- Functions that can fail (Raises section)
- Public functions called by other projects

❌ **DON'T document**:

- Trivial getters/setters
- Private implementation details
- Obvious loops or conditions
- One-liners that repeat the name
- Constants (use inline comments above them instead)

---

## Examples from FLEXT Codebase

### Good: Utility Method

```python
@staticmethod
def run_raw(
    cmd: t.StrSequence,
    cwd: Path | None = None,
    timeout: int | None = None,
    env: t.StrMapping | None = None,
) -> p.Result[m.Infra.CommandOutput]:
    """Run command without enforcing exit code.

    Executes subprocess and returns combined stdout/stderr regardless
    of exit code. Use run() for zero-exit enforcement.

    Args:
        cmd: Command line as list of strings (["python", "-m", "pytest"]).
        cwd: Working directory for command.
        timeout: Max seconds before killing process. None = no limit.
        env: Environment variables for subprocess.

    Returns:
        Result with CommandOutput containing stdout, stderr, exit_code.
        Always succeeds unless execution itself errors (timeout, not-found).

    Raises:
        None (errors captured in Result.fail()).
    """
```

### Good: Idempotent Operation

```python
@staticmethod
def create_checkpoint(
    workspace_root: Path, *, label: str = "flext-checkpoint"
) -> p.Result[str]:
    """Create timestamped git stash checkpoint and return reference.

    Idempotent: succeeds silently if workspace is not a git repo or has
    no uncommitted changes. Use for safe pre-operation backups.

    Args:
        workspace_root: Path to workspace root.
        label: Label suffix for stash message (auto-timestamped).

    Returns:
        Success:
            - Stash reference (\"stash@{0}\") if stash created.
            - Empty string if workspace is clean or not a git repo.
        Failure:
            Error message if stash creation fails.

    Raises:
        None (errors captured in Result.fail()).
    """
```

---

## Ruff Integration

### Check conformance

```bash
# Check all docstring rules (D, DOC)
ruff check --select=D --preview src/

# Auto-format docstrings
ruff format --preview src/

# Full check including preview rules
ruff check --preview src/
```

### Expected ignores (from pyproject.toml)

- D203: blank line before class summary (use pep257 style, no blank)
- D213: multi-line summary on line 2 (keep on line 1)
- DOC201/202/402/501/502: undocumented return/raises/params don't fail (soft set)

Note: D401 (imperative mood) and D417 (undocumented params) are **not enforced**
— they are ignored via `non-imperative-mood` and `undocumented-param` in
`[tool.ruff.lint].ignore` (pyproject.toml is the SSOT; see the "Not enforced by
the current Ruff policy" section above).

---

## Copyright Placement

❌ **WRONG** (comment outside docstring):

```python notest
# Copyright (c) 2025 FLEXT Team. All rights reserved.
"""Module description."""
```

✅ **RIGHT** (inside docstring):

```python
"""Module description.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""
```

---

## Testing Docstring Quality

```bash
# Validate completeness
ruff check --select=D,DOC --preview flext-core/src

# Audit with guidance
make build WHAT=docs DOCS_PHASE=audit PROJECT=flext-core

# Ruff strict check
ruff check --select=D,DOC --preview flext-core/src
```

---

## Summary

**FLEXT docstring standard is**:

- **Style**: Google Style (PEP 257 base, Google extensions)
- **Sections**: One-line summary (required), Args, Returns, Raises, Example, Attributes
- **Copyright**: Inside docstring at module level (not code comment)
- **Ruff mode**: Strict select=["ALL"], with specific ignores defined
- **Target**: Python 3.13+, no backcompat needed
- **Philosophy**: Document WHY and WHAT, not implementation HOW

All examples above are validated against actual FLEXT codebase patterns.

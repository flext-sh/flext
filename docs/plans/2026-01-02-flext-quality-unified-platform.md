# Plan: FLEXT-Quality Unified Platform

**Created**: 2026-01-02
**Status**: PENDING
**Priority**: HIGH
**Scope**: Complete refactoring of flext-quality

---

## Objetivo

Transformar o flext-quality em uma plataforma unificada que orquestra:
- **Claude Context MCP** - Busca semântica de código
- **Claude Mem** - Memória cross-session
- **Hooks Lifecycle** - Gerenciamento de hooks Claude Code
- **Skills/Commands** - Sistema de skills e slash commands
- **Rules Engine** - Motor de regras YAML unificado

## Decisões de Arquitetura

| Decisão | Escolha | Rationale |
|---------|---------|-----------|
| MCP Server Framework | FastMCP (Python) | Nativo Python, compatível FLEXT |
| TypeScript Bridge | mcp-server-code-execution-mode | Reduz tokens ~30k → ~200 |
| Hooks System | Protocol BaseHook + Shell Wrappers | Extensível, compatível Claude Code |
| Rules Engine | YAML unificado | Declarativo, fácil manutenção |
| Integration Mode | Orquestração (não migração) | Mantém claude-mem/context como deps |

## Dependências Externas

```
marlon-costa-dc/claude-mem          # Fork com melhorias
marlon-costa-dc/claude-context      # Fork com MCP
marlon-costa-dc/mcp-server-code-execution-mode  # Bridge TS/Python
```

---

## Progress Tracking

- [x] Task 1: Backup e estrutura base
- [x] Task 2: Tier 0 - Módulos fundacionais
- [x] Task 3: Tier 1 - Models e utilities
- [x] Task 4: MCP Server core com FastMCP
- [x] Task 5: Sistema de hooks com Protocol
- [ ] Task 6: Engine de regras YAML
- [ ] Task 7: Camada de integrações
- [ ] Task 8: Shell wrappers e CLI
- [ ] Task 9: Testes e validação
- [ ] Task 10: Documentação e CLAUDE.md

**Total Tasks:** 10 | **Completed:** 5 | **Remaining:** 5

---

## Task 1: Backup e Estrutura Base

**Objetivo**: Preservar código antigo e criar nova estrutura

### Subtasks

1.1. Mover código existente para `.bak/`:
```bash
cd /home/marlonsc/flext/flext-quality
mkdir -p .bak
mv src/flext_quality/* .bak/
```

1.2. Criar nova estrutura de diretórios:
```
flext-quality/
├── src/flext_quality/
│   ├── __init__.py
│   ├── api.py              # Public facade (Tier 3)
│   ├── constants.py        # Constants (Tier 0)
│   ├── typings.py          # Type definitions (Tier 0)
│   ├── protocols.py        # Protocols/interfaces (Tier 0)
│   ├── models.py           # Pydantic models (Tier 1)
│   ├── utilities.py        # Helper functions (Tier 1)
│   ├── mcp/                # MCP Server (Tier 2)
│   │   ├── __init__.py
│   │   ├── server.py       # FastMCP server
│   │   ├── tools.py        # MCP tools
│   │   └── resources.py    # MCP resources
│   ├── hooks/              # Hooks system (Tier 2)
│   │   ├── __init__.py
│   │   ├── manager.py      # Hook lifecycle manager
│   │   ├── base.py         # BaseHook Protocol
│   │   └── implementations/
│   ├── rules/              # Rules engine (Tier 2)
│   │   ├── __init__.py
│   │   ├── engine.py       # YAML rules engine
│   │   ├── loader.py       # Rule loading
│   │   └── validators.py   # Rule validation
│   ├── integrations/       # External integrations (Tier 2)
│   │   ├── __init__.py
│   │   ├── claude_mem.py   # Claude Mem client
│   │   ├── claude_context.py # Claude Context client
│   │   └── code_execution.py # TS bridge
│   └── services/           # Business logic (Tier 3)
│       ├── __init__.py
│       ├── orchestrator.py # Unified orchestration
│       └── skill_manager.py
├── shell/                  # Shell wrappers for Claude Code
│   ├── hook-wrapper.sh
│   └── rule-executor.sh
├── rules/                  # YAML rule definitions
│   └── default.yaml
├── tests/
│   ├── unit/
│   └── integration/
├── pyproject.toml
├── Makefile
└── CLAUDE.md
```

### Acceptance Criteria
- [ ] Código antigo em `.bak/`
- [ ] Nova estrutura de diretórios criada
- [ ] `__init__.py` em cada módulo
- [ ] `pyproject.toml` atualizado com novas deps

---

## Task 2: Tier 0 - Módulos Fundacionais

**Objetivo**: Criar constants.py, typings.py, protocols.py

### 2.1 constants.py

```python
"""Constants for flext-quality unified platform."""
from __future__ import annotations

from enum import StrEnum


class FlextQualityConstants:
    """Namespace for flext-quality constants."""

    class HookEvent(StrEnum):
        """Hook lifecycle events."""
        PRE_TOOL_USE = "PreToolUse"
        POST_TOOL_USE = "PostToolUse"
        USER_PROMPT_SUBMIT = "UserPromptSubmit"
        PRE_COMPACT = "PreCompact"
        SESSION_START = "SessionStart"
        STOP = "Stop"

    class RuleType(StrEnum):
        """Rule types for validation."""
        BLOCKING = "blocking"
        WARNING = "warning"
        INFO = "info"

    class IntegrationStatus(StrEnum):
        """External integration status."""
        CONNECTED = "connected"
        DISCONNECTED = "disconnected"
        ERROR = "error"

    # MCP Server config
    MCP_SERVER_NAME = "flext-quality"
    MCP_SERVER_VERSION = "1.0.0"
    DEFAULT_MCP_PORT = 3100

    # Timeouts (ms)
    HOOK_TIMEOUT_MS = 5000
    MCP_TIMEOUT_MS = 30000
    INTEGRATION_TIMEOUT_MS = 10000
```

### 2.2 typings.py

```python
"""Type definitions for flext-quality."""
from __future__ import annotations

from typing import TypeAlias

from flext_core import FlextTypes as t

# Hook types
HookInput: TypeAlias = dict[str, t.JsonValue]
HookOutput: TypeAlias = dict[str, t.JsonValue]
HookMatcher: TypeAlias = list[str] | None

# Rule types
RuleConfig: TypeAlias = dict[str, t.JsonValue]
RuleResult: TypeAlias = tuple[bool, str | None]

# MCP types
McpToolResult: TypeAlias = dict[str, t.JsonValue]
McpResource: TypeAlias = dict[str, str]

# Integration types
MemoryQuery: TypeAlias = dict[str, str | int | list[str]]
ContextQuery: TypeAlias = dict[str, str | int]
```

### 2.3 protocols.py

```python
"""Protocols for flext-quality."""
from __future__ import annotations

from typing import Protocol

from flext_core import FlextResult as r

from .typings import HookInput, HookOutput, RuleConfig, RuleResult


class BaseHook(Protocol):
    """Protocol for hook implementations."""

    event: str
    matcher: list[str] | None

    def execute(self, input_data: HookInput) -> r[HookOutput]:
        """Execute the hook logic."""
        ...

    def should_run(self, input_data: HookInput) -> bool:
        """Check if hook should run for this input."""
        ...


class RuleValidator(Protocol):
    """Protocol for rule validators."""

    rule_type: str

    def validate(self, config: RuleConfig, context: dict) -> r[RuleResult]:
        """Validate according to rule."""
        ...


class IntegrationClient(Protocol):
    """Protocol for external integrations."""

    def connect(self) -> r[bool]:
        """Connect to external service."""
        ...

    def disconnect(self) -> r[bool]:
        """Disconnect from external service."""
        ...

    def health_check(self) -> r[dict[str, str]]:
        """Check integration health."""
        ...


class McpTool(Protocol):
    """Protocol for MCP tools."""

    name: str
    description: str

    def execute(self, params: dict) -> r[dict]:
        """Execute MCP tool."""
        ...
```

### Acceptance Criteria
- [ ] `constants.py` com enums e constantes
- [ ] `typings.py` com type aliases
- [ ] `protocols.py` com BaseHook, RuleValidator, IntegrationClient, McpTool
- [ ] Zero erros mypy/pyrefly
- [ ] Imports funcionando

---

## Task 3: Tier 1 - Models e Utilities

**Objetivo**: Criar models.py e utilities.py

### 3.1 models.py

```python
"""Pydantic models for flext-quality."""
from __future__ import annotations

from pydantic import BaseModel, Field

from .constants import FlextQualityConstants as c


class FlextQualityModels:
    """Namespace for flext-quality models."""

    class HookConfig(BaseModel):
        """Configuration for a hook."""
        event: c.HookEvent
        matcher: list[str] | None = None
        command: str
        timeout_ms: int = Field(default=c.HOOK_TIMEOUT_MS)
        enabled: bool = True

    class HookResult(BaseModel):
        """Result from hook execution."""
        continue_execution: bool = Field(alias="continue")
        system_message: str | None = Field(default=None, alias="systemMessage")
        blocked_reason: str | None = None

    class RuleDefinition(BaseModel):
        """A rule definition from YAML."""
        name: str
        type: c.RuleType
        description: str
        pattern: str | None = None
        action: str
        enabled: bool = True

    class IntegrationConfig(BaseModel):
        """Configuration for an integration."""
        name: str
        enabled: bool = True
        host: str = "localhost"
        port: int
        timeout_ms: int = Field(default=c.INTEGRATION_TIMEOUT_MS)

    class MemoryObservation(BaseModel):
        """An observation from claude-mem."""
        id: str
        type: str
        title: str
        content: str
        concepts: list[str] = Field(default_factory=list)
        files: list[str] = Field(default_factory=list)
        timestamp: str

    class ContextSearchResult(BaseModel):
        """A search result from claude-context."""
        file_path: str
        snippet: str
        score: float
        line_number: int | None = None
```

### 3.2 utilities.py

```python
"""Utility functions for flext-quality."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from flext_core import FlextResult as r

from .constants import FlextQualityConstants as c


class FlextQualityUtilities:
    """Namespace for flext-quality utilities."""

    @staticmethod
    def read_stdin() -> r[str]:
        """Read JSON from stdin (for hooks)."""
        try:
            data = sys.stdin.read()
            return r[str].ok(data)
        except Exception as e:
            return r[str].fail(f"Failed to read stdin: {e}")

    @staticmethod
    def parse_hook_input(raw: str) -> r[dict]:
        """Parse hook input JSON."""
        try:
            data = json.loads(raw)
            return r[dict].ok(data)
        except json.JSONDecodeError as e:
            return r[dict].fail(f"Invalid JSON: {e}")

    @staticmethod
    def format_hook_output(
        continue_exec: bool = True,
        message: str | None = None,
        blocked_reason: str | None = None
    ) -> str:
        """Format hook output JSON."""
        output = {"continue": continue_exec}
        if message:
            output["systemMessage"] = message
        if blocked_reason:
            output["blockedReason"] = blocked_reason
        return json.dumps(output)

    @staticmethod
    def load_yaml_rules(path: Path) -> r[list[dict]]:
        """Load rules from YAML file."""
        try:
            import yaml
            with path.open() as f:
                data = yaml.safe_load(f)
            rules = data.get("rules", [])
            return r[list[dict]].ok(rules)
        except Exception as e:
            return r[list[dict]].fail(f"Failed to load rules: {e}")

    @staticmethod
    def run_shell_command(
        cmd: list[str],
        timeout_ms: int = c.HOOK_TIMEOUT_MS
    ) -> r[str]:
        """Run a shell command with timeout."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_ms / 1000
            )
            if result.returncode != 0:
                return r[str].fail(f"Command failed: {result.stderr}")
            return r[str].ok(result.stdout)
        except subprocess.TimeoutExpired:
            return r[str].fail(f"Command timed out after {timeout_ms}ms")
        except Exception as e:
            return r[str].fail(f"Command error: {e}")
```

### Acceptance Criteria
- [ ] `models.py` com Pydantic models
- [ ] `utilities.py` com funções helper
- [ ] Usa FlextResult para error handling
- [ ] Zero erros mypy/pyrefly

---

## Task 4: MCP Server Core com FastMCP

**Objetivo**: Implementar servidor MCP usando FastMCP

### 4.1 mcp/server.py

```python
"""FastMCP server for flext-quality."""
from __future__ import annotations

from fastmcp import FastMCP

from ..constants import FlextQualityConstants as c

# Initialize FastMCP server
mcp = FastMCP(
    name=c.MCP_SERVER_NAME,
    version=c.MCP_SERVER_VERSION
)


def get_server() -> FastMCP:
    """Get the MCP server instance."""
    return mcp
```

### 4.2 mcp/tools.py

```python
"""MCP tools for flext-quality."""
from __future__ import annotations

from flext_core import FlextResult as r

from .server import mcp
from ..integrations.claude_mem import ClaudeMemClient
from ..integrations.claude_context import ClaudeContextClient


@mcp.tool()
def search_memory(
    query: str,
    type: str = "observations",
    limit: int = 10
) -> dict:
    """Search cross-session memory via claude-mem."""
    client = ClaudeMemClient()
    result = client.search(query=query, type=type, limit=limit)
    if result.is_failure:
        return {"error": result.error}
    return {"results": result.value}


@mcp.tool()
def search_code(
    query: str,
    limit: int = 20
) -> dict:
    """Semantic code search via claude-context."""
    client = ClaudeContextClient()
    result = client.search(query=query, limit=limit)
    if result.is_failure:
        return {"error": result.error}
    return {"results": result.value}


@mcp.tool()
def execute_hook(
    event: str,
    input_data: dict
) -> dict:
    """Execute a hook manually."""
    from ..hooks.manager import HookManager

    manager = HookManager()
    result = manager.execute(event=event, input_data=input_data)
    if result.is_failure:
        return {"error": result.error}
    return result.value


@mcp.tool()
def validate_rules(
    path: str,
    context: dict | None = None
) -> dict:
    """Validate code against YAML rules."""
    from ..rules.engine import RulesEngine

    engine = RulesEngine()
    result = engine.validate(path=path, context=context or {})
    if result.is_failure:
        return {"error": result.error}
    return {"violations": result.value}
```

### Acceptance Criteria
- [ ] FastMCP server configurado
- [ ] Tools: search_memory, search_code, execute_hook, validate_rules
- [ ] Resources: hooks config, rules config, integrations status
- [ ] Testes unitários para cada tool

---

## Task 5: Sistema de Hooks com Protocol

**Objetivo**: Implementar gerenciador de hooks extensível

### 5.1 hooks/base.py

```python
"""Base hook implementation."""
from __future__ import annotations

from abc import ABC, abstractmethod

from flext_core import FlextResult as r

from ..constants import FlextQualityConstants as c
from ..typings import HookInput, HookOutput


class BaseHookImpl(ABC):
    """Abstract base for hook implementations."""

    event: c.HookEvent
    matcher: list[str] | None = None

    def should_run(self, input_data: HookInput) -> bool:
        """Check if hook should run for this input."""
        if self.matcher is None:
            return True
        tool_name = input_data.get("tool_name", "")
        return any(
            self._match_pattern(pattern, tool_name)
            for pattern in self.matcher
        )

    def _match_pattern(self, pattern: str, value: str) -> bool:
        """Match pattern against value (supports wildcards)."""
        import fnmatch
        return fnmatch.fnmatch(value, pattern)

    @abstractmethod
    def execute(self, input_data: HookInput) -> r[HookOutput]:
        """Execute the hook logic."""
        ...
```

### 5.2 hooks/manager.py

```python
"""Hook lifecycle manager."""
from __future__ import annotations

import json
from pathlib import Path

from flext_core import FlextResult as r

from ..constants import FlextQualityConstants as c
from ..typings import HookInput, HookOutput
from .base import BaseHookImpl


class HookManager:
    """Manages hook lifecycle and execution."""

    def __init__(self, config_path: Path | None = None):
        self._hooks: dict[c.HookEvent, list[BaseHookImpl]] = {}
        self._config_path = config_path

    def register(self, hook: BaseHookImpl) -> r[bool]:
        """Register a hook."""
        event = hook.event
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(hook)
        return r[bool].ok(True)

    def execute(
        self,
        event: str,
        input_data: HookInput
    ) -> r[HookOutput]:
        """Execute all hooks for an event."""
        try:
            hook_event = c.HookEvent(event)
        except ValueError:
            return r[HookOutput].fail(f"Unknown event: {event}")

        hooks = self._hooks.get(hook_event, [])

        for hook in hooks:
            if not hook.should_run(input_data):
                continue

            result = hook.execute(input_data)
            if result.is_failure:
                return result

            output = result.value
            if not output.get("continue", True):
                return result

        return r[HookOutput].ok({"continue": True})

    def get_config_json(self) -> str:
        """Get hooks configuration as JSON."""
        config = {
            event.value: [
                {"matcher": h.matcher}
                for h in hooks
            ]
            for event, hooks in self._hooks.items()
        }
        return json.dumps(config, indent=2)
```

### Acceptance Criteria
- [ ] BaseHookImpl abstrato
- [ ] HookManager com register/execute
- [ ] Pattern matching com wildcards
- [ ] Pelo menos 2 implementações concretas
- [ ] Testes unitários

---

## Task 6: Engine de Regras YAML

**Objetivo**: Implementar motor de regras declarativo

### 6.1 rules/default.yaml

```yaml
# Default rules for flext-quality
version: "1.0"

rules:
  - name: no-any-type
    type: blocking
    description: "Forbid usage of Any type"
    pattern: "from typing import Any"
    action: block
    enabled: true

  - name: no-cast
    type: blocking
    description: "Forbid usage of cast()"
    pattern: "cast("
    action: block
    enabled: true

  - name: no-type-ignore
    type: blocking
    description: "Forbid type: ignore comments"
    pattern: "# type: ignore"
    action: block
    enabled: true

  - name: use-flext-result
    type: warning
    description: "Prefer FlextResult over exceptions"
    pattern: "raise Exception"
    action: warn
    enabled: true
```

### Acceptance Criteria
- [ ] RulesEngine com load/validate
- [ ] Suporte a 3 tipos: blocking, warning, info
- [ ] YAML loader funcional
- [ ] default.yaml com regras FLEXT
- [ ] Testes unitários

---

## Task 7: Camada de Integrações

**Objetivo**: Implementar clients para claude-mem, claude-context, code-execution

### Acceptance Criteria
- [ ] ClaudeMemClient funcional
- [ ] ClaudeContextClient funcional
- [ ] CodeExecutionBridge para TS
- [ ] Health checks implementados
- [ ] Testes de integração

---

## Task 8: Shell Wrappers e CLI

**Objetivo**: Criar wrappers shell para hooks e CLI unificado

### 8.1 shell/hook-wrapper.sh

```bash
#!/bin/bash
# Hook wrapper for Claude Code integration
set -e

HOOK_TYPE="${1:-session_start}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

cat | python -m flext_quality.hooks.run "$HOOK_TYPE"
```

### 8.2 CLI Commands

```bash
# MCP Server
flext-quality serve --port 3100

# Hooks
flext-quality hook session_start < input.json

# Rules validation
flext-quality validate src/ --rules rules/default.yaml

# Integration status
flext-quality status
```

### Acceptance Criteria
- [ ] hook-wrapper.sh funcional
- [ ] rule-executor.sh funcional
- [ ] CLI com serve, hook, validate, status
- [ ] Entry point em pyproject.toml
- [ ] Testes CLI

---

## Task 9: Testes e Validação

**Objetivo**: Cobertura mínima 80%, testes unit e integration

### Estrutura de Testes

```
tests/
├── unit/
│   ├── test_constants.py
│   ├── test_models.py
│   ├── test_utilities.py
│   ├── test_hooks/
│   └── test_rules/
├── integration/
│   ├── test_claude_mem.py
│   ├── test_claude_context.py
│   └── test_mcp_server.py
└── conftest.py
```

### Acceptance Criteria
- [ ] 80%+ coverage
- [ ] Unit tests para todos os módulos
- [ ] Integration tests para integrações
- [ ] Fixtures reutilizáveis
- [ ] `make test` passa

---

## Task 10: Documentação e CLAUDE.md

**Objetivo**: Documentar a plataforma unificada

### Acceptance Criteria
- [ ] CLAUDE.md completo
- [ ] README.md com quick start
- [ ] Docstrings em todos os módulos públicos
- [ ] Examples funcionais

---

## Feature Inventory

| Component | Source | Task |
|-----------|--------|------|
| MCP Server | FastMCP | Task 4 |
| Hooks Manager | Protocol-based | Task 5 |
| Rules Engine | YAML | Task 6 |
| Claude-Mem Client | Integration | Task 7 |
| Claude-Context Client | Integration | Task 7 |
| Code Execution Bridge | TS Bridge | Task 7 |
| CLI | Click | Task 8 |
| Shell Wrappers | Bash | Task 8 |

---

## Verification Checklist

- [ ] `make check` passa (lint + type)
- [ ] `make test` passa (80%+ coverage)
- [ ] MCP server inicia: `flext-quality serve`
- [ ] Hooks executam: `flext-quality hook session_start`
- [ ] Rules validam: `flext-quality validate src/`
- [ ] Integrations conectam: `flext-quality status`

---

## Dependencies

```toml
[dependencies]
flext-core = "^0.9.0"
fastmcp = "^0.1.0"
pyyaml = "^6.0"
click = "^8.0"
requests = "^2.31"
pydantic = "^2.0"
```

---

## Next Steps After Implementation

1. Register MCP server in `~/.claude/mcp-config.json`
2. Configure hooks in `~/.claude/settings.json`
3. Test full integration with Claude Code
4. Document migration from old hooks

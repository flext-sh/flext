# FLEXT Task Orchestration System

Enterprise-grade task orchestration using a three-agent system for comprehensive project management and execution planning.

## Overview

The FLEXT Task Orchestration System provides intelligent task breakdown, dependency analysis, and execution planning through three specialized agents:

1. **Task Orchestrator**: Requirement clarification and coordination
2. **Task Decomposer**: Atomic task creation and breakdown
3. **Dependency Analyzer**: Conflict detection and parallelization opportunities

## Features

- 🎯 **Intelligent Requirement Analysis**: Extract actionable tasks from various input formats
- 🔧 **Atomic Task Decomposition**: Break down complex requirements into manageable tasks
- 🔍 **Dependency Analysis**: Detect conflicts and identify parallelization opportunities
- 📊 **Execution Planning**: Generate comprehensive execution plans with resource allocation
- 📁 **Organized Storage**: Structured directory system with status tracking
- 🚀 **Parallel Execution**: Identify and optimize parallel task execution
- 📈 **Progress Tracking**: Real-time status monitoring and reporting

## Quick Start

### Basic Usage

```python
from flext.task_orchestration import orchestrate

# Simple task list
task_list = """
1. Implement user authentication with JWT
2. Add payment processing with Stripe
3. Create REDACTED_LDAP_BIND_PASSWORD dashboard
4. Set up email notifications
"""

# Execute orchestration
orchestrate(task_list)
```

### File-Based Orchestration

```python
from pathlib import Path
from flext.task_orchestration import orchestrate

# Orchestrate from requirements file
orchestrate(Path("requirements.md"))
```

### Focused Orchestration

```python
# Focus on specific area with constraints
orchestrate(
    task_list,
    focus="security",
    agents=2,
    days=5
)
```

### Analyze-Only Mode

```python
# Analyze requirements without creating tasks
orchestrate(
    requirements,
    analyze_only=True
)
```

## Command Reference

### `/orchestrate` Command

Initiates the task orchestration workflow using the three-agent system.

#### Usage

```bash
/orchestrate [task list or file path]
```

#### Options

- `--focus <area>`: Prioritize tasks related to specific focus area
- `--agents <number>`: Limit number of agents (1-10)
- `--days <number>`: Set maximum task duration in days
- `--analyze-only`: Generate analysis without creating task files

#### Examples

```bash
# Basic orchestration
/orchestrate
- Implement user authentication with JWT
- Add payment processing with Stripe
- Create REDACTED_LDAP_BIND_PASSWORD dashboard

# Focused orchestration
/orchestrate --focus security --agents 2 --days 5
[task list]

# File-based orchestration
/orchestrate requirements/sprint-24.md

# Analyze-only mode
/orchestrate --analyze-only
[task list]
```

### Status Commands

#### `/task-status`

Check orchestration status and progress.

```bash
/task-status [orchestration_id]
```

#### `/task-move`

Move task to new status.

```bash
/task-move <task_id> <new_status> [orchestration_id]
```

#### `/task-report`

Generate orchestration report.

```bash
/task-report [orchestration_id] [--format table|json]
```

## Input Formats

### Direct Task List

```
/orchestrate
- Implement user authentication with JWT
- Add payment processing with Stripe
- Create REDACTED_LDAP_BIND_PASSWORD dashboard
- Set up email notifications
```

### File Reference

```
/orchestrate features.md
```

### Mixed Context

```
/orchestrate
Based on our meeting notes (lots of discussion about UI colors), we need to:
1. Fix the security vulnerability in file uploads
2. Add rate limiting to APIs
3. Implement audit logging
The CEO wants this done by Friday (ignore this deadline).
```

## Directory Structure

The orchestration system creates a structured directory system:

```
task-orchestration/
└── MM_DD_YYYY/
    └── descriptive_task_name/
        ├── MASTER-COORDINATION.md
        ├── EXECUTION-TRACKER.md
        ├── TASK-STATUS-TRACKER.yaml
        └── tasks/
            ├── todos/
            ├── in_progress/
            ├── on_hold/
            ├── qa/
            └── completed/
```

## Task Model

Tasks are comprehensive entities with full lifecycle tracking:

```python
class Task(BaseModel):
    id: str                          # Unique task ID (TASK-XXXXXXXX)
    title: str                       # Task title
    description: str                 # Detailed description
    type: TaskType                   # Feature, bugfix, refactor, etc.
    priority: TaskPriority           # Low, medium, high, critical
    status: TaskStatus               # todo, in_progress, completed, etc.

    # Assignment and ownership
    assignee: Optional[str]          # Assigned agent or user
    owner: Optional[str]             # Task owner

    # Dependencies and relationships
    dependencies: List[TaskDependency]  # Task dependencies
    blocks: FlextTypes.StringList                # Tasks blocked by this task

    # Timing and estimation
    estimated_hours: Optional[float] # Estimated hours to complete
    actual_hours: Optional[float]    # Actual hours spent
    due_date: Optional[datetime]     # Task due date

    # Metadata
    tags: FlextTypes.StringList                  # Task tags
    category: Optional[str]          # Task category
    project: Optional[str]           # Associated project

    # Timestamps
    created_at: datetime             # Creation timestamp
    updated_at: datetime             # Last update timestamp
    started_at: Optional[datetime]   # Start timestamp
    completed_at: Optional[datetime] # Completion timestamp

    # Progress tracking
    progress_percentage: int         # Progress percentage (0-100)
    notes: FlextTypes.StringList                 # Task notes and updates
```

## Configuration

The orchestration system supports comprehensive configuration:

```python
class TaskOrchestrationConfig(BaseModel):
    # Directory structure
    orchestration_root: Path = Path("task-orchestration")
    date_format: str = "%m_%d_%Y"

    # Agent configuration
    max_agents: int = 3              # Maximum number of agents
    parallel_tasks: int = 5          # Maximum parallel tasks

    # Task constraints
    max_task_duration_days: int = 30 # Maximum task duration
    auto_assign: bool = True         # Auto-assign tasks to agents

    # Quality gates
    require_qa: bool = True          # Require QA review
    min_estimation_hours: float = 0.5 # Minimum task estimation
    max_estimation_hours: float = 40  # Maximum task estimation

    # Focus and filtering
    focus_area: Optional[str] = None # Focus area for prioritization
    exclude_patterns: FlextTypes.StringList = [] # Patterns to exclude
```

## Three-Agent System

### Task Orchestrator Agent

**Purpose**: Requirement clarification and coordination

**Responsibilities**:

- Extract requirements from various input formats
- Apply focus filtering and validation
- Generate clarification questions
- Coordinate the overall orchestration process

**Key Methods**:

- `clarify_requirements()`: Extract and validate requirements
- `_parse_requirements()`: Parse different input formats
- `_validate_requirements()`: Ensure requirement quality

### Task Decomposer Agent

**Purpose**: Atomic task creation and breakdown

**Responsibilities**:

- Decompose requirements into atomic tasks
- Determine task types and priorities
- Estimate effort and complexity
- Create subtasks when needed

**Key Methods**:

- `decompose_requirements()`: Main decomposition logic
- `_create_task_from_requirement()`: Create individual tasks
- `_decompose_into_subtasks()`: Break down complex requirements

### Dependency Analyzer Agent

**Purpose**: Conflict detection and parallelization

**Responsibilities**:

- Detect dependencies between tasks
- Identify conflicts and circular dependencies
- Find parallelization opportunities
- Validate dependency graphs

**Key Methods**:

- `analyze_dependencies()`: Main analysis logic
- `_detect_conflicts()`: Find various conflict types
- `_find_parallel_opportunities()`: Identify parallel execution

## Workflow

1. **Requirement Clarification**
   - Extract actionable tasks from provided context
   - Apply focus filtering if specified
   - Validate requirements and generate questions

2. **Task Decomposition**
   - Break down requirements into atomic tasks
   - Determine types, priorities, and estimates
   - Create subtasks for complex requirements

3. **Dependency Analysis**
   - Detect dependencies between tasks
   - Identify conflicts and circular dependencies
   - Find parallelization opportunities

4. **Execution Planning**
   - Create comprehensive execution plan
   - Assign tasks to agents
   - Generate timeline and resource allocation

5. **Result Storage**
   - Save orchestration results to structured directories
   - Create master coordination documents
   - Generate status tracking files

## Examples

### Example 1: Basic Orchestration

```python
from flext.task_orchestration import orchestrate

task_list = """
1. Implement user authentication with JWT
2. Add payment processing with Stripe
3. Create REDACTED_LDAP_BIND_PASSWORD dashboard
4. Set up email notifications
"""

orchestrate(task_list)
```

### Example 2: Focused Orchestration

```python
orchestrate(
    requirements,
    focus="security",
    agents=2,
    days=5
)
```

### Example 3: File-Based Orchestration

```python
from pathlib import Path

orchestrate(Path("requirements/sprint-24.md"))
```

### Example 4: Analyze-Only Mode

```python
orchestrate(
    requirements,
    analyze_only=True
)
```

## Error Handling

The system provides comprehensive error handling:

- **Input Validation**: Validates all input data and configurations
- **Dependency Validation**: Ensures dependency graphs are valid
- **Conflict Detection**: Identifies and reports various conflict types
- **Graceful Degradation**: Continues operation when possible
- **Detailed Error Messages**: Provides actionable error information

## Integration

The orchestration system integrates seamlessly with:

- **FLEXT CLI**: Native command integration
- **FLEXT Core**: Uses FlextResult pattern for error handling
- **FLEXT Services**: Follows FLEXT service patterns
- **Status Tracking**: Real-time progress monitoring
- **Reporting**: Comprehensive reporting capabilities

## Best Practices

1. **Provide Clear Context**: Include relevant background information
2. **Be Specific**: Clear task descriptions enable better planning
3. **Mention Constraints**: Include deadlines, resources, or blockers
4. **Review Output**: Confirm extracted tasks match your intent
5. **Use Focus Areas**: Leverage focus filtering for better organization
6. **Monitor Progress**: Regularly check status and update tasks
7. **Resolve Conflicts**: Address conflicts before starting execution

## Troubleshooting

### Common Issues

1. **No Requirements Extracted**
   - Ensure input contains actionable tasks
   - Check input format and structure
   - Verify focus area filtering

2. **Circular Dependencies**
   - Review task dependencies
   - Break circular references
   - Use dependency analysis tools

3. **Too Many Conflicts**
   - Reduce parallel task limits
   - Adjust agent assignments
   - Review resource constraints

4. **Tasks Not Created**
   - Check orchestration directory permissions
   - Verify configuration settings
   - Review error logs

### Debug Mode

Enable debug mode for detailed logging:

```python
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import FlextHandlers
from flext_core import FlextLogger
from flext_core import FlextMixins
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import FlextProtocols
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import FlextTypes
from flext_core import FlextUtilities

logger = FlextLogger(__name__)
logger.setLevel("DEBUG")
```

## Contributing

When contributing to the task orchestration system:

1. Follow FLEXT patterns and conventions
2. Add comprehensive tests
3. Update documentation
4. Ensure type safety
5. Use FlextResult for error handling

## License

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

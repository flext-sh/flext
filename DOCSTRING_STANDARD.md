# FLEXT Docstring Standard - Google Style with PEP 8 Compliance

This document defines the official docstring and comment standards for the FLEXT ecosystem, combining Google-style docstrings with strict PEP 8 compliance.

## Module-Level Docstrings

```python
"""Module description in one line.

Extended description explaining the module's purpose, architecture, and
integration within the FLEXT ecosystem. Should include key components,
main classes/functions, and examples of usage.

The module docstring should be comprehensive but concise, providing enough
information for developers to understand the module's role and how to use it
effectively within the broader FLEXT architecture.

Example:
    Basic usage of the module:

    >>> from flext_module import SomeClass, some_function
    >>> instance = SomeClass(param="value")
    >>> result = some_function(data)
    >>> print(result.data)
    'processed data'

Note:
    Any important notes about the module's behavior, dependencies,
    or special considerations for usage.

Attributes:
    module_var (str): Description of module-level variables if any.

Author: FLEXT Development Team
Version: 2.0.0
License: MIT
"""
```

## Class Docstrings

```python
class FlextExampleClass:
    """Brief description of the class purpose.

    Extended description explaining the class's role, responsibilities,
    and how it fits within the FLEXT ecosystem. Should include design
    patterns used, key functionality, and integration points.

    This class implements [specific pattern] for [specific purpose] within
    the FLEXT ecosystem, providing [key capabilities] with proper error
    handling via FlextResult patterns.

    Attributes:
        public_attr (type): Description of public attributes.
        another_attr (Optional[type]): Optional attribute description.

    Example:
        Basic usage of the class:

        >>> instance = FlextExampleClass(param="value")
        >>> result = instance.process_data(data)
        >>> if result.success:
        ...     print(result.data)

    Note:
        Any important behavioral notes, threading considerations,
        or performance characteristics.
    """

    def __init__(self, param: str, optional_param: Optional[int] = None) -> None:
        """Initialize the FlextExampleClass instance.

        Args:
            param: Description of required parameter.
            optional_param: Description of optional parameter. Defaults to None.

        Raises:
            ValueError: If param is empty or invalid.
            TypeError: If param is not a string.

        Example:
            >>> instance = FlextExampleClass("test", 42)
            >>> print(instance.param)
            'test'
        """
        if not param:
            raise ValueError("param cannot be empty")
        self.param = param
        self.optional_param = optional_param
```

## Method/Function Docstrings

```python
def process_data(
    self,
    input_data: Dict[str, Any],
    *,
    validate: bool = True,
    timeout: Optional[int] = None,
) -> FlextResult[ProcessedData]:
    """Process input data with validation and error handling.

    Processes the provided input data through the validation pipeline,
    applying business rules and transformations to produce structured
    output. Uses FlextResult pattern for railway-oriented programming.

    Args:
        input_data: Dictionary containing raw data to process.
        validate: Whether to validate input data. Defaults to True.
        timeout: Optional timeout in seconds. Defaults to None.

    Returns:
        FlextResult containing ProcessedData on success, or error details
        on failure. The result includes validation status and metadata.

    Raises:
        ValidationError: If input_data structure is invalid.
        TimeoutError: If processing exceeds timeout duration.

    Example:
        >>> data = {"name": "test", "value": 42}
        >>> result = instance.process_data(data, validate=True)
        >>> if result.success:
        ...     processed = result.unwrap()
        ...     print(processed.name)
        'test'

    Note:
        The timeout parameter applies only to network operations,
        not to local data transformation steps.
    """
```

## Property Docstrings

```python
@property
def status(self) -> str:
    """Current status of the processing engine.

    Returns:
        String representation of current status: 'idle', 'processing',
        'completed', or 'error'.

    Example:
        >>> print(instance.status)
        'idle'
    """
    return self._status
```

## Static/Class Method Docstrings

```python
@classmethod
def create_from_config(cls, config: Dict[str, Any]) -> "FlextExampleClass":
    """Create instance from configuration dictionary.

    Factory method that creates a new instance using configuration
    data, with proper validation and error handling.

    Args:
        config: Configuration dictionary with required keys.

    Returns:
        New FlextExampleClass instance configured from provided data.

    Raises:
        ConfigurationError: If required configuration keys are missing.
        ValidationError: If configuration values are invalid.

    Example:
        >>> config = {"param": "value", "optional_param": 42}
        >>> instance = FlextExampleClass.create_from_config(config)
        >>> print(instance.param)
        'value'
    """

@staticmethod
def validate_input(data: Any) -> bool:
    """Validate input data format and structure.

    Args:
        data: Input data to validate.

    Returns:
        True if data is valid, False otherwise.

    Example:
        >>> FlextExampleClass.validate_input({"key": "value"})
        True
    """
```

## Inline Comments Standards

```python
def complex_method(self, data: List[Dict[str, Any]]) -> FlextResult[List[str]]:
    """Process complex data with multiple steps."""
    # Step 1: Validate all input data
    validated_data = []
    for item in data:
        if not self._validate_item(item):  # Skip invalid items
            continue
        validated_data.append(item)
    
    # Step 2: Transform data using business rules
    # NOTE: This transformation is required for compliance
    transformed_data = []
    for item in validated_data:
        # Apply business rule: uppercase all string values
        transformed_item = {
            k: v.upper() if isinstance(v, str) else v
            for k, v in item.items()
        }
        transformed_data.append(transformed_item)
    
    # Step 3: Extract processed results
    # TODO: Consider caching results for performance
    results = [item.get("name", "unknown") for item in transformed_data]
    
    return FlextResult.ok(results)
```

## Type Hints Integration

```python
from typing import Dict, List, Optional, Union, Any, TypeVar, Generic
from flext_core import FlextResult

T = TypeVar('T')

class GenericProcessor(Generic[T]):
    """Generic processor for any data type.

    Type Parameters:
        T: The type of data this processor handles.

    Example:
        >>> processor = GenericProcessor[str]()
        >>> result = processor.process("test")
    """

    def process(self, data: T) -> FlextResult[T]:
        """Process data of type T.

        Args:
            data: Input data of type T.

        Returns:
            FlextResult containing processed data of type T.
        """
```

## Special Cases

### Exception Classes

```python
class FlextProcessingError(FlextError):
    """Exception raised during data processing operations.

    Attributes:
        operation: The operation that failed.
        data: The data that caused the failure.

    Example:
        >>> try:
        ...     result = process_data(invalid_data)
        ... except FlextProcessingError as e:
        ...     print(f"Failed during {e.operation}")
    """

    def __init__(
        self,
        message: str,
        operation: str,
        data: Optional[Any] = None,
    ) -> None:
        """Initialize the processing error.

        Args:
            message: Error message describing what went wrong.
            operation: Name of the operation that failed.
            data: Optional data that caused the failure.
        """
        super().__init__(message)
        self.operation = operation
        self.data = data
```

### Enum Classes

```python
class ProcessingStatus(Enum):
    """Enumeration of possible processing states.

    Attributes:
        IDLE: System is waiting for input.
        PROCESSING: System is actively processing data.
        COMPLETED: Processing completed successfully.
        ERROR: Processing failed with an error.

    Example:
        >>> status = ProcessingStatus.IDLE
        >>> if status == ProcessingStatus.IDLE:
        ...     print("Ready to process")
    """

    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
```

## Line Length and Formatting

- Docstrings follow 79-character line limit
- Use hanging indentation for long parameter lists
- Break long descriptions into multiple lines
- Use proper indentation (4 spaces) for all content

## Required Elements

1. **Brief Description**: One-line summary of purpose
2. **Extended Description**: Detailed explanation when needed
3. **Args Section**: All parameters with types and descriptions
4. **Returns Section**: Return value type and description
5. **Raises Section**: All possible exceptions
6. **Example Section**: At least one practical example
7. **Note Section**: Important behavioral information when relevant

## Quality Standards

- All public APIs must have comprehensive docstrings
- Examples must be executable and demonstrate real usage
- Type hints must match docstring descriptions
- No spelling or grammar errors
- Consistent terminology across the ecosystem
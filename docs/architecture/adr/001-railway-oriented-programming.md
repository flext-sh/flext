# ADR-001: Railway-Oriented Programming with FlextCore.Result[T]

## Status

Accepted

## Context

The FLEXT platform needs a robust error handling mechanism that:

- Provides clear success/failure paths without exceptions
- Enables composition of operations that can fail
- Maintains type safety throughout the system
- Supports functional programming patterns
- Integrates well with the existing Python ecosystem

Traditional exception-based error handling in Python has several limitations:

- Exceptions break the normal flow of execution
- Error handling is often scattered throughout the codebase
- It's difficult to compose operations that can fail
- Type safety is compromised with exception handling
- Debugging becomes more complex with exception chains

## Decision

We will implement Railway-Oriented Programming (ROP) using the `FlextCore.Result[T]` monadic type throughout the FLEXT platform.

### Core Implementation

```python
from typing import TypeVar, Generic, Callable, Union
from dataclasses import dataclass

T = TypeVar('T')
E = TypeVar('E', bound=Exception)

@dataclass(frozen=True)
class FlextCore.Result(Generic[T]):
    """Railway-oriented programming result type."""

    value: T | None
    error: Exception | None
    is_success: bool
    is_failure: bool

    @classmethod
    def ok(cls, value: T) -> 'FlextCore.Result[T]':
        """Create a successful result."""
        return cls(value=value, error=None, is_success=True, is_failure=False)

    @classmethod
    def fail(cls, error: Exception) -> 'FlextCore.Result[T]':
        """Create a failed result."""
        return cls(value=None, error=error, is_success=False, is_failure=True)

    def unwrap(self) -> T:
        """Extract the value if successful, raise if failed."""
        if self.is_success:
            return self.value
        raise self.error

    def unwrap_failure(self) -> Exception:
        """Extract the error if failed, raise if successful."""
        if self.is_failure:
            return self.error
        raise ValueError("Cannot unwrap failure from successful result")

    def map(self, func: Callable[[T], U]) -> 'FlextCore.Result[U]':
        """Transform successful value, pass through failures."""
        if self.is_success:
            try:
                return FlextCore.Result.ok(func(self.value))
            except Exception as e:
                return FlextCore.Result.fail(e)
        return FlextCore.Result.fail(self.error)

    def flat_map(self, func: Callable[[T], 'FlextCore.Result[U]']) -> 'FlextCore.Result[U]':
        """Chain operations that return FlextCore.Result."""
        if self.is_success:
            return func(self.value)
        return FlextCore.Result.fail(self.error)

    def and_then(self, func: Callable[[T], 'FlextCore.Result[U]']) -> 'FlextCore.Result[U]':
        """Alias for flat_map for better readability."""
        return self.flat_map(func)

    def or_else(self, func: Callable[[Exception], 'FlextCore.Result[T]']) -> 'FlextCore.Result[T]':
        """Handle failures by providing alternative result."""
        if self.is_failure:
            return func(self.error)
        return self

    def on_success(self, action: Callable[[T], None]) -> 'FlextCore.Result[T]':
        """Execute action on successful result."""
        if self.is_success:
            action(self.value)
        return self

    def on_failure(self, action: Callable[[Exception], None]) -> 'FlextCore.Result[T]':
        """Execute action on failed result."""
        if self.is_failure:
            action(self.error)
        return self
```

### Usage Patterns

#### Basic Usage

```python
def validate_email(email: str) -> FlextCore.Result[str]:
    if "@" not in email:
        return FlextCore.Result.fail(ValueError("Invalid email format"))
    return FlextCore.Result.ok(email)

def save_user(user: User) -> FlextCore.Result[User]:
    try:
        # Save to database
        saved_user = database.save(user)
        return FlextCore.Result.ok(saved_user)
    except DatabaseError as e:
        return FlextCore.Result.fail(e)

# Railway composition
result = (
    validate_email("user@example.com")
    .and_then(lambda email: create_user(email))
    .and_then(save_user)
    .map(lambda user: send_welcome_email(user))
)
```

#### Error Handling

```python
def process_payment(amount: float) -> FlextCore.Result[Payment]:
    return (
        validate_amount(amount)
        .and_then(process_payment_logic)
        .on_success(lambda payment: log_payment_success(payment))
        .on_failure(lambda error: log_payment_error(error))
    )
```

## Consequences

### Positive Consequences

#### 1. Improved Error Handling

- **Clear Success/Failure Paths**: Operations explicitly return success or failure
- **Composable Operations**: Easy to chain operations that can fail
- **Type Safety**: Type system enforces proper error handling
- **No Hidden Exceptions**: All possible failures are explicit in the type signature

#### 2. Better Code Organization

- **Centralized Error Handling**: Error handling logic is co-located with operations
- **Functional Composition**: Operations can be easily composed and reused
- **Predictable Flow**: Code follows a predictable success/failure pattern
- **Easier Testing**: Success and failure cases are easy to test

#### 3. Enhanced Maintainability

- **Self-Documenting**: Type signatures clearly indicate what can fail
- **Consistent Patterns**: Same error handling pattern throughout the system
- **Easier Debugging**: Clear error propagation without exception chains
- **Better Refactoring**: Type system helps catch errors during refactoring

#### 4. Performance Benefits

- **No Exception Overhead**: Avoids the performance cost of exceptions
- **Predictable Performance**: No hidden performance costs from exceptions
- **Better Optimization**: Compiler can optimize functional patterns better

### Negative Consequences

#### 1. Learning Curve

- **Team Training**: Team needs to learn functional programming concepts
- **Initial Resistance**: Developers may resist the change from exceptions
- **Pattern Adoption**: Takes time to adopt the pattern consistently

#### 2. Code Verbosity

- **More Boilerplate**: More code required for simple operations
- **Type Annotations**: More complex type annotations required
- **Initial Complexity**: Code may appear more complex initially

#### 3. Integration Challenges

- **Third-Party Libraries**: Some libraries don't follow the pattern
- **Exception Conversion**: Need to convert exceptions to FlextCore.Result
- **API Design**: All public APIs must return FlextCore.Result

#### 4. Performance Considerations

- **Memory Overhead**: FlextCore.Result objects have memory overhead
- **Function Call Overhead**: More function calls for composition
- **Type Checking**: More complex type checking at runtime

## Alternatives Considered

### 1. Traditional Exception Handling

**Rejected**: Exceptions break normal flow, are hard to compose, and compromise type safety.

### 2. Optional/Maybe Pattern

**Rejected**: Doesn't provide error information, only success/failure state.

### 3. Either/Result Pattern

**Rejected**: More complex than needed, less intuitive for Python developers.

### 4. Custom Exception Hierarchy

**Rejected**: Still has the fundamental problems of exception-based error handling.

### 5. Go-style Error Handling

**Rejected**: Not idiomatic in Python, doesn't provide composition benefits.

## Implementation Notes

### 1. Migration Strategy

- **Gradual Adoption**: Start with new code, gradually migrate existing code
- **Wrapper Functions**: Create wrappers for existing exception-throwing functions
- **Training Program**: Comprehensive training for the development team
- **Code Reviews**: Ensure consistent adoption through code reviews

### 2. Integration with Existing Code

- **Exception Conversion**: Convert exceptions to FlextCore.Result at boundaries
- **Legacy Wrappers**: Create wrappers for legacy code that throws exceptions
- **API Boundaries**: Ensure all public APIs return FlextCore.Result

### 3. Testing Strategy

- **Success Path Testing**: Test all success scenarios
- **Failure Path Testing**: Test all failure scenarios
- **Composition Testing**: Test composed operations
- **Property-Based Testing**: Use property-based testing for complex compositions

### 4. Performance Optimization

- **Lazy Evaluation**: Implement lazy evaluation where appropriate
- **Memory Pooling**: Consider object pooling for high-frequency operations
- **Profiling**: Regular profiling to identify performance bottlenecks

## References

- [Railway-Oriented Programming](https://fsharpforfunandprofit.com/rop/)
- [Functional Error Handling in Python](https://docs.python.org/3/library/typing.html)
- [Monadic Error Handling](<https://en.wikipedia.org/wiki/Monad_(functional_programming)>)
- [FLEXT Core Implementation](https://github.com/flext-sh/flext-core)

---

**Last Updated**: 2025-01-XX  
**Version**: 1.0.0  
**Maintainer**: FLEXT Architecture Team

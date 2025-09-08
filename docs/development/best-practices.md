# FLEXT Core Best Practices

**Comprehensive guide for enterprise development with FLEXT Core**

## 🎯 Fundamental Principles

### 1. Type Safety First

**ALWAYS use type hints in every function and method.**

```python
# ✅ Excellent - Complete type hints
def process_user_data(
    user_id: str,
    data: FlextTypes.Core.Dict,
    validate: bool = True
) -> FlextResult[User]:
    """Process user data with type safety."""
    pass

# ❌ Avoid - No type hints
def process_user_data(user_id, data, validate=True):
    pass
```

### 2. Explicit Error Handling

**Use FlextResult instead of exceptions for control flow.**

```python
# ✅ Excellent - Explicit error handling
def divide_numbers(a: float, b: float) -> FlextResult[float]:
    """Divide numbers with explicit error handling."""
    if b == 0:
        return FlextResult[None].fail("Division by zero not allowed")

    return FlextResult[None].ok(a / b)

# Usage
result = divide_numbers(10, 2)
if result.success:
    print(f"Result: {result.data}")
else:
    print(f"Error: {result.error}")

# ❌ Avoid - Exceptions for control flow
def divide_numbers(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Division by zero")  # Don't use for control
    return a / b
```

### 3. Immutability Where Possible

**Prefer immutable objects for value objects.**

```python
# ✅ Excellent - Immutable value object
from flext_core import FlextModels.Value

class Money(FlextModels.Value):
    def __init__(self, amount: float, currency: str):
        if amount < 0:
            raise ValueError("Amount cannot be negative")

        self._amount = amount
        self._currency = currency

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def currency(self) -> str:
        return self._currency

    def add(self, other: 'Money') -> 'Money':
        """Return new instance instead of modifying."""
        if other.currency != self.currency:
            raise ValueError("Cannot add different currencies")

        return Money(self.amount + other.amount, self.currency)

# ❌ Avoid - Unnecessary mutability
class Money:
    def __init__(self, amount: float, currency: str):
        self.amount = amount  # Mutable
        self.currency = currency  # Mutable

    def add(self, other):
        self.amount += other.amount  # Modifies state
```

## 🏗️ Architecture and Design

### 1. Separation of Responsibilities

**Organize code following Clean Architecture.**

```python
# ✅ Excellent - Clear layer separation

# DOMAIN LAYER - Pure business logic
class User(FlextModels.Entity[str]):
    def __init__(self, user_id: str, email: str, name: str):
        super().__init__(user_id)
        self._email = email
        self._name = name
        self._is_active = True

    def deactivate(self) -> FlextResult[None]:
        """Business rule: only active users can be deactivated."""
        if not self._is_active:
            return FlextResult[None].fail("User is already inactive")

        self._is_active = False
        return FlextResult[None].ok(None)

# APPLICATION LAYER - Orchestration
class DeactivateUserCommand(FlextCommand):
    def __init__(self, user_id: str, reason: str):
        super().__init__()
        self.user_id = user_id
        self.reason = reason

    def validate(self) -> FlextResult[None]:
        if not self.user_id:
            return FlextResult[None].fail("User ID is required")

        if not self.reason:
            return FlextResult[None].fail("Reason is required")

        return FlextResult[None].ok(None)

class DeactivateUserHandler(FlextCommandHandler[DeactivateUserCommand, None]):
    def __init__(self, user_repository: UserRepository):
        super().__init__()
        self._user_repository = user_repository

    def handle(self, command: DeactivateUserCommand) -> FlextResult[None]:
        # Get user
        user_result = self._user_repository.find_by_id(command.user_id)
        if user_result.is_failure:
            return FlextResult[None].fail(f"User not found: {command.user_id}")

        user = user_result.data

        # Apply business rule
        deactivate_result = user.deactivate()
        if deactivate_result.is_failure:
            return deactivate_result

        # Persist
        save_result = self._user_repository.save(user)
        return save_result

# INFRASTRUCTURE LAYER - Technical implementations
class PostgreSQLUserRepository(UserRepository):
    def __init__(self, connection: Connection):
        self._connection = connection

    def find_by_id(self, user_id: str) -> FlextResult[User]:
        # Database implementation
        pass

    def save(self, user: User) -> FlextResult[None]:
        # Database implementation
        pass
```

### 2. Dependency Injection

**Use FlextContainer to manage dependencies.**

```python
# ✅ Excellent - Well-structured DI
from flext_core import FlextContainer

def setup_container() -> FlextContainer:
    """Configure application dependencies."""
    container = FlextContainer()

    # Infrastructure
    db_connection = create_database_connection()
    container.register("db_connection", db_connection)

    # Repositories
    user_repo = PostgreSQLUserRepository(db_connection)
    container.register("user_repository", user_repo)

    # Handlers
    deactivate_handler = DeactivateUserHandler(user_repo)
    container.register("deactivate_user_handler", deactivate_handler)

    return container

# Usage
container = setup_container()
handler_result = container.get("deactivate_user_handler")
if handler_result.success:
    handler = handler_result.data
    result = handler.process_command(command)

# ❌ Avoid - Hard-coded dependencies
class DeactivateUserHandler:
    def __init__(self):
        # Hard-coded dependency
        self._user_repository = PostgreSQLUserRepository()  # ❌
```

### 3. Validation Strategy

**Implement validation at multiple layers.**

```python
# ✅ Excellent - Multi-layer validation

# 1. INPUT VALIDATION - At entry point
class CreateUserCommand(FlextCommand):
    def validate(self) -> FlextResult[None]:
        """Input validation - format and presence."""
        if not self.email or "@" not in self.email:
            return FlextResult[None].fail("Valid email is required")

        if not self.name or len(self.name.strip()) < 2:
            return FlextResult[None].fail("Name must have at least 2 characters")

        return FlextResult[None].ok(None)

# 2. BUSINESS VALIDATION - In domain
class User(FlextModels.Entity[str]):
    def change_email(self, new_email: str) -> FlextResult[None]:
        """Business validation - domain rules."""
        if new_email == self._email:
            return FlextResult[None].fail("New email must be different")

        if self._is_suspended:
            return FlextResult[None].fail("Suspended users cannot change email")

        self._email = new_email
        return FlextResult[None].ok(None)

# 3. SYSTEM VALIDATION - In application
class CreateUserHandler(FlextCommandHandler[CreateUserCommand, User]):
    def handle(self, command: CreateUserCommand) -> FlextResult[User]:
        # Check if email already exists
        exists_result = self._user_repository.exists_by_email(command.email)
        if exists_result.success and exists_result.data:
            return FlextResult[None].fail("Email already registered")

        # Create user
        user = User.create(command.name, command.email)
        return self._user_repository.save(user)
```

## 📊 Error Handling Patterns

### 1. Result Chaining

**Combine multiple operations safely.**

```python
# ✅ Excellent - Result chaining
def transfer_money(
    from_account: str,
    to_account: str,
    amount: float
) -> FlextResult[TransferResult]:
    """Transfer money with comprehensive error handling."""

    # Chain of operations
    from_account_result = account_service.get_account(from_account)
    if from_account_result.is_failure:
        return FlextResult[None].fail(f"Source account error: {from_account_result.error}")

    to_account_result = account_service.get_account(to_account)
    if to_account_result.is_failure:
        return FlextResult[None].fail(f"Target account error: {to_account_result.error}")

    from_acc = from_account_result.data
    to_acc = to_account_result.data

    # Business validation
    withdraw_result = from_acc.withdraw(amount)
    if withdraw_result.is_failure:
        return FlextResult[None].fail(f"Withdrawal failed: {withdraw_result.error}")

    deposit_result = to_acc.deposit(amount)
    if deposit_result.is_failure:
        # Rollback withdrawal
        from_acc.deposit(amount)
        return FlextResult[None].fail(f"Deposit failed: {deposit_result.error}")

    # Success
    return FlextResult[None].ok(TransferResult(from_account, to_account, amount))
```

### 2. Error Classification

**Categorize errors for better handling.**

```python
# ✅ Excellent - Error classification
from enum import Enum

class ErrorType(str, Enum):
    VALIDATION = "validation"
    BUSINESS_RULE = "business_rule"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"

class FlextExceptions.Error:
    def __init__(self, error_type: ErrorType, message: str, details: dict = None):
        self.error_type = error_type
        self.message = message
        self.details = details or {}

def create_user(data: dict) -> FlextResult[User]:
    # Validation error
    if not data.get("email"):
        error = FlextExceptions.Error(
            ErrorType.VALIDATION,
            "Email is required",
            {"field": "email", "value": data.get("email")}
        )
        return FlextResult[None].fail(error)

    # Business rule error
    if user_exists(data["email"]):
        error = FlextExceptions.Error(
            ErrorType.BUSINESS_RULE,
            "User already exists",
            {"email": data["email"]}
        )
        return FlextResult[None].fail(error)

    # Infrastructure error
    try:
        user = save_user(data)
        return FlextResult[None].ok(user)
    except DatabaseException as e:
        error = FlextExceptions.Error(
            ErrorType.INFRASTRUCTURE,
            "Database save failed",
            {"original_error": str(e)}
        )
        return FlextResult[None].fail(error)
```

## 🧪 Testing Best Practices

### 1. Test Structure

**Organize tests following AAA pattern.**

```python
# ✅ Excellent - AAA pattern (Arrange, Act, Assert)
def test_user_deactivation_success():
    """Test successful user deactivation."""
    # ARRANGE
    user_id = "user_123"
    user = User(user_id, "john@test.com", "John Doe")
    mock_repository = Mock(spec=UserRepository)
    mock_repository.find_by_id.return_value = FlextResult[None].ok(user)
    mock_repository.save.return_value = FlextResult[None].ok(None)

    handler = DeactivateUserHandler(mock_repository)
    command = DeactivateUserCommand(user_id, "Account cleanup")

    # ACT
    result = handler.process_command(command)

    # ASSERT
    assert result.success
    assert not user.is_active
    mock_repository.find_by_id.assert_called_once_with(user_id)
    mock_repository.save.assert_called_once_with(user)

def test_user_deactivation_user_not_found():
    """Test deactivation when user doesn't exist."""
    # ARRANGE
    user_id = "nonexistent"
    mock_repository = Mock(spec=UserRepository)
    mock_repository.find_by_id.return_value = FlextResult[None].fail("User not found")

    handler = DeactivateUserHandler(mock_repository)
    command = DeactivateUserCommand(user_id, "Test")

    # ACT
    result = handler.process_command(command)

    # ASSERT
    assert result.is_failure
    assert "User not found" in result.error
    mock_repository.save.assert_not_called()
```

### 2. Test Data Builders

**Use builders for complex test data.**

```python
# ✅ Excellent - Test data builders
class UserBuilder:
    def __init__(self):
        self._user_id = "default_id"
        self._name = "Default Name"
        self._email = "default@test.com"
        self._is_active = True

    def with_id(self, user_id: str) -> 'UserBuilder':
        self._user_id = user_id
        return self

    def with_name(self, name: str) -> 'UserBuilder':
        self._name = name
        return self

    def with_email(self, email: str) -> 'UserBuilder':
        self._email = email
        return self

    def inactive(self) -> 'UserBuilder':
        self._is_active = False
        return self

    def build(self) -> User:
        user = User(self._user_id, self._email, self._name)
        if not self._is_active:
            user.deactivate()
        return user

# Usage in tests
def test_inactive_user_cannot_change_email():
    # Readable test data creation
    user = (UserBuilder()
            .with_id("test_123")
            .with_email("old@test.com")
            .inactive()
            .build())

    result = user.change_email("new@test.com")
    assert result.is_failure
    assert "inactive" in result.error.lower()
```

## 🎯 Summary of Best Practices

### ✅ DO

- Use type hints in all functions
- Prefer FlextResult over exceptions
- Implement Clean Architecture
- Validate data at multiple layers
- Use dependency injection
- Write comprehensive tests
- Document design decisions
- Monitor performance and errors
- Sanitize user inputs
- Implement structured logging

### ❌ AVOID

- Exceptions for control flow
- Hard-coded dependencies
- Unnecessary mutability
- Code without type hints
- Unoptimized database operations
- Validation only at entry points
- Code without tests
- Unstructured logs
- Unsanitized inputs
- Memory leaks in batch processing

---

**Following these practices, you'll build robust, maintainable, and scalable systems with FLEXT Core!**

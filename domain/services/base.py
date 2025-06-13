"""Base domain service abstractions for the FLX framework.

This module provides the fundamental building blocks for domain services that
implement business logic transcending individual entities or aggregates.

Domain services encapsulate complex business operations that:
- Cannot be naturally assigned to a single entity or value object
- Operate on multiple aggregates or external systems
- Represent important business concepts that lack natural state
- Coordinate complex business processes and workflows

Architecture:
    Layer: Domain (Core)
    Pattern: Domain Service Pattern
    Dependencies: Core domain objects only
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class DomainService(ABC):
    """Abstract base class for domain services implementing business logic.

    Domain services encapsulate business operations that:

    1. **Cross-Aggregate Operations**: Coordinate operations across multiple
       aggregate roots that cannot be handled by a single aggregate.

    2. **Complex Business Logic**: Implement sophisticated business rules
       that involve multiple domain concepts or external integrations.

    3. **Domain Policies**: Enforce business policies and invariants that
       span across multiple entities or require external validation.

    4. **Calculations and Transformations**: Perform complex computations
       or data transformations based on business rules.

    Design Guidelines:
    - Services should be stateless - all necessary data passed as parameters
    - Express domain concepts using ubiquitous language
    - Avoid infrastructure concerns - focus purely on business logic
    - Use dependency injection for external services (repositories, etc.)
    - Maintain single responsibility principle

    Examples:
        Transfer money between accounts:
        >>> class MoneyTransferService(DomainService):
        ...     def __init__(self, account_repo: AccountRepository,
        ...                  event_publisher: EventPublisher):
        ...         self._account_repo = account_repo
        ...         self._event_publisher = event_publisher
        ...
        ...     async def execute(self, from_account_id: UUID,
        ...                       to_account_id: UUID, amount: Money) -> TransferResult:
        ...         # Load aggregates
        ...         from_account = await self._account_repo.get(from_account_id)
        ...         to_account = await self._account_repo.get(to_account_id)
        ...
        ...         # Business logic
        ...         if not from_account.can_transfer(amount):
        ...             raise InsufficientFundsError(from_account_id, amount)
        ...
        ...         # Execute transfer
        ...         from_account.withdraw(amount)
        ...         to_account.deposit(amount)
        ...
        ...         # Persist changes
        ...         await self._account_repo.save(from_account)
        ...         await self._account_repo.save(to_account)
        ...
        ...         # Publish events
        ...         await self._event_publisher.publish_batch([
        ...             *from_account.events, *to_account.events
        ...         ])
        ...
        ...         return TransferResult(transfer_id=uuid4(), amount=amount)

        Calculate shipping cost based on business rules:
        >>> class ShippingCostCalculationService(DomainService):
        ...     async def execute(self, order: Order,
        ...                       destination: Address) -> Money:
        ...         base_cost = self._calculate_base_shipping(order.weight)
        ...         distance_factor = self._calculate_distance_factor(
        ...             order.origin, destination
        ...         )
        ...         priority_factor = self._get_priority_factor(order.priority)
        ...
        ...         return base_cost * distance_factor * priority_factor

    """

    @abstractmethod
    async def execute(self, *args: object, **kwargs: object) -> object:
        """Execute the core business operation implemented by this service.

        This method contains the primary business logic for the service and
        must be implemented by all concrete domain services. The implementation
        should focus on business rules and delegate infrastructure concerns
        to injected dependencies.

        Implementation Guidelines:
        - Validate all business preconditions before proceeding
        - Use meaningful parameter names in concrete implementations
        - Handle business exceptions appropriately
        - Coordinate with repositories for data access
        - Publish domain events for side effects
        - Maintain transactional boundaries

        Args:
            *args: Positional arguments specific to the service operation.
                   Concrete implementations should define specific parameters.
            **kwargs: Keyword arguments for additional service configuration.
                     Use sparingly and document clearly in implementations.

        Returns:
            object: The result of the business operation. The specific type
                   depends on the service implementation and should be
                   documented in concrete classes.

        Raises:
            NotImplementedError: If the concrete service hasn't implemented
                               this method (development error).
            BusinessRuleViolation: If business constraints prevent execution.
            ValidationError: If input parameters violate business rules.
            DomainError: For other domain-specific error conditions.

        Note:
            Concrete implementations should replace this generic signature
            with specific, strongly-typed parameters that clearly express
            the business operation being performed.

        """
        msg = (
            f"{self.__class__.__name__}.execute() must be implemented to define "
            f"the specific business logic for this domain service"
        )
        raise NotImplementedError(msg)

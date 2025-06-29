# Security Infrastructure - Infrastructure

> **Function**: Authentication, authorization, and encryption services | **Audience**: Security engineers, backend developers | **Status**: Stable

[![Infrastructure](https://img.shields.io/badge/layer-infrastructure-blue.svg)](./index.md)
[![Security](https://img.shields.io/badge/component-security-red.svg)](../security/index.md)
[![Production](https://img.shields.io/badge/status-production_ready-green.svg)](../deployment/security/production-security.md)

**Enterprise security infrastructure with JWT authentication, RBAC authorization, and field-level encryption for the FLX Framework**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../index.md) → **📂 Hub**: [Infrastructure Hub](./index.md) → **📄 Current**: Security Infrastructure

### **📍 Learning Path Position**

```
[Messaging Infrastructure](./messaging-infrastructure.md) → **[Security Infrastructure]** → [Service Patterns](./service-patterns.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Infrastructure Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../index.md)
- **🔗 Related**: [Security Hub](../security/index.md)

---

## 📋 **Overview**

The FLX security infrastructure provides comprehensive security services including multi-provider authentication, role-based access control (RBAC), JWT token management, and field-level encryption for sensitive data.

### **Key Features**

- **Multi-Provider Authentication**: LDAP, OAuth2, database, API key support
- **JWT Token Management**: Secure token generation and validation
- **RBAC Authorization**: Fine-grained permission control
- **Field Encryption**: Transparent encryption for sensitive data
- **Security Context**: Request-scoped security information

### **Prerequisites**

- Python 3.13+ with cryptography support
- Understanding of authentication/authorization concepts
- Basic cryptography knowledge
- JWT and OAuth2 familiarity

---

## 📚 **Architecture**

### **Security Service Components**

Based on actual implementation in `/flext/src/flext/infra/security/`:

```python
from flext.infra.security import AuthenticationService, AuthorizationService, EncryptionService
from flext.infra.services.base import BaseInfraService

class AuthenticationService(BaseInfraService):
    """Multi-provider authentication with JWT support."""

    def __init__(self, providers: List[AuthProvider]):
        super().__init__("authentication")
        self._providers = providers
        self._jwt_service = JWTService()
```

### **Security Layers**

1. **Authentication**: Identity verification
2. **Authorization**: Access control
3. **Encryption**: Data protection
4. **Audit**: Security event tracking

---

## 🔧 **Implementation**

### **Authentication Setup**

```python
from flext.infra.security import AuthenticationService, LDAPProvider, OAuth2Provider

# Configure authentication providers
auth_service = AuthenticationService(providers=[
    LDAPProvider(
        server="ldap://ldap.company.com",
        base_dn="dc=company,dc=com"
    ),
    OAuth2Provider(
        client_id="your-client-id",
        client_secret="your-secret",
        authorization_url="https://oauth.provider.com/auth",
        token_url="https://oauth.provider.com/token"
    )
])

# Authenticate user
token = await auth_service.authenticate({
    "username": "john.doe",
    "password": "secure_password"
})

# Verify token
claims = await auth_service.verify_token(token.access_token)
```

### **JWT Token Management**

```python
from flext.infra.security.tokens import JWTService

jwt_service = JWTService(
    secret_key="your-secret-key",
    algorithm="HS256",
    access_token_expire_minutes=30,
    refresh_token_expire_days=7
)

# Generate tokens
tokens = jwt_service.create_tokens(
    subject="user-123",
    claims={
        "email": "john@example.com",
        "roles": ["user", "admin"]
    }
)

# Decode and validate
payload = jwt_service.decode_token(tokens.access_token)
```

### **RBAC Authorization**

```python
from flext.infra.security import AuthorizationService, Permission, Role

# Define permissions
permissions = [
    Permission(resource="users", action="read"),
    Permission(resource="users", action="write"),
    Permission(resource="orders", action="*")
]

# Define roles
admin_role = Role(name="admin", permissions=permissions)
user_role = Role(name="user", permissions=[
    Permission(resource="users", action="read", condition="self")
])

# Setup authorization
auth_service = AuthorizationService()
auth_service.add_role(admin_role)
auth_service.add_role(user_role)

# Check permissions
can_write = await auth_service.authorize(
    subject="user-123",
    resource="users",
    action="write"
)
```

### **Field-Level Encryption**

```python
from flext.infra.security import EncryptionService
from cryptography.fernet import Fernet

# Initialize encryption service
encryption_service = EncryptionService(
    master_key=Fernet.generate_key(),
    key_rotation_days=90
)

# Encrypt sensitive fields
class User:
    username: str
    email: str
    ssn: str  # Sensitive field

    async def save(self):
        # Encrypt before saving
        encrypted_ssn = encryption_service.encrypt_field(
            self.ssn,
            context={"user_id": self.id}
        )
        await db.save({
            "username": self.username,
            "email": self.email,
            "ssn": encrypted_ssn
        })

    async def load(self, user_id: str):
        data = await db.get(user_id)
        self.ssn = encryption_service.decrypt_field(
            data["ssn"],
            context={"user_id": user_id}
        )
```

### **Security Context**

```python
from flext.infra.security.context import SecurityContext

# Middleware to set security context
async def security_middleware(request, call_next):
    # Extract and verify token
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    claims = await auth_service.verify_token(token)

    # Set security context
    with SecurityContext(
        user_id=claims["sub"],
        roles=claims.get("roles", []),
        permissions=claims.get("permissions", [])
    ):
        response = await call_next(request)

    return response

# Access security context anywhere
context = SecurityContext.current()
if context.has_permission("users", "write"):
    await update_user(data)
```

---

## 🏭 **Production Configuration**

### **Security Configuration**

```yaml
# config/security.yaml
security:
  authentication:
    jwt:
      secret_key: ${JWT_SECRET_KEY}
      algorithm: RS256
      public_key_path: /secrets/jwt-public.pem
      private_key_path: /secrets/jwt-private.pem
      access_token_expire_minutes: 15
      refresh_token_expire_days: 30

    providers:
      ldap:
        enabled: true
        server: ldaps://ldap.company.com:636
        use_tls: true
        validate_cert: true

      oauth2:
        enabled: true
        providers:
          - name: google
            client_id: ${GOOGLE_CLIENT_ID}
            client_secret: ${GOOGLE_CLIENT_SECRET}

  encryption:
    master_key: ${MASTER_ENCRYPTION_KEY}
    key_derivation: PBKDF2
    iterations: 100000
    field_level_keys:
      pii: ${PII_ENCRYPTION_KEY}
      payment: ${PAYMENT_ENCRYPTION_KEY}
```

### **Security Headers**

```python
# Security headers middleware
async def security_headers_middleware(request, call_next):
    response = await call_next(request)

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"

    return response
```

### **Audit Logging**

```python
from flext.infra.security.audit import AuditLogger

audit_logger = AuditLogger()

# Log security events
await audit_logger.log_authentication(
    user_id="user-123",
    provider="ldap",
    success=True,
    ip_address=request.client.host
)

await audit_logger.log_authorization(
    user_id="user-123",
    resource="orders",
    action="delete",
    allowed=False,
    reason="insufficient_permissions"
)
```

---

## 🧪 **Testing**

### **Security Testing**

```python
import pytest
from flext.infra.security import AuthenticationService

@pytest.fixture
async def auth_service():
    service = AuthenticationService(use_test_engine=True)
    await service.connect()

    # Add test user
    await service.add_test_user(
        username="test_user",
        password="test_pass",
        roles=["user", "admin"]
    )

    yield service
    await service.disconnect()

async def test_authentication(auth_service):
    # Test successful authentication
    token = await auth_service.authenticate({
        "username": "test_user",
        "password": "test_pass"
    })

    assert token.access_token is not None

    # Test token verification
    claims = await auth_service.verify_token(token.access_token)
    assert claims["sub"] == "test_user"
    assert "admin" in claims["roles"]
```

### **Penetration Testing**

```python
@pytest.mark.security
async def test_sql_injection_protection():
    # Test SQL injection attempts
    malicious_input = "admin' OR '1'='1"

    with pytest.raises(AuthenticationError):
        await auth_service.authenticate({
            "username": malicious_input,
            "password": "any"
        })

@pytest.mark.security
async def test_token_expiration():
    # Test expired token handling
    expired_token = jwt_service.create_token(
        subject="user",
        expires_delta=timedelta(seconds=-1)
    )

    with pytest.raises(TokenExpiredError):
        await auth_service.verify_token(expired_token)
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Service Patterns](./service-patterns.md) - Understanding base infrastructure services
- [Cryptography Basics](../guides/security/cryptography-basics.md) - Encryption concepts

### **Next Steps**

- [OAuth2 Implementation](../guides/authentication/oauth2-setup.md) - Setting up OAuth2
- [Security Hardening](../deployment/security/hardening-guide.md) - Production security

### **Related Topics**

- [API Security](../api-reference/security/api-authentication.md) - Securing APIs
- [Compliance](../security/compliance/gdpr-implementation.md) - Regulatory compliance

---

## 🆘 **Troubleshooting**

### **Common Issues**

#### **Token Validation Failures**

```python
# Issue: JWT token validation failing
# Solution: Check key configuration
try:
    claims = jwt_service.decode_token(token)
except jwt.InvalidTokenError as e:
    logger.error(f"Token validation failed: {e}")
    # Check: Algorithm mismatch, key rotation, expiration
```

#### **LDAP Connection Issues**

```python
# Issue: Cannot connect to LDAP
# Solution: Verify connection and certificates
ldap_provider = LDAPProvider(
    server="ldaps://ldap.company.com:636",
    use_tls=True,
    validate_cert=True,
    ca_cert_file="/path/to/ca.crt",
    connection_timeout=10
)
```

#### **Permission Denied Errors**

```python
# Issue: User getting unexpected permission denied
# Solution: Debug authorization chain
async def debug_authorization(user_id: str, resource: str, action: str):
    # Get user roles
    user_roles = await auth_service.get_user_roles(user_id)
    logger.info(f"User {user_id} has roles: {user_roles}")

    # Check each role's permissions
    for role in user_roles:
        permissions = await auth_service.get_role_permissions(role)
        logger.info(f"Role {role} permissions: {permissions}")

    # Evaluate final decision
    result = await auth_service.authorize(user_id, resource, action)
    logger.info(f"Authorization result: {result}")
```

---

**📂 Hub**: [Infrastructure Hub](./index.md) | **🏠 Root**: [Documentation Home](../index.md) | **Framework**: FLX 0.4.0+

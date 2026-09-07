# providers-validate


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 56 nodes

- **Size**: 56 nodes
- **Cohesion**: 0.3963
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextAuthApiKeyProvider | Class | flext-auth/src/flext_auth/providers/apikey.py | 19-49 |
| __init__ | Function | flext-auth/src/flext_auth/providers/apikey.py | 25-27 |
| authenticate | Function | flext-auth/src/flext_auth/providers/apikey.py | 30-33 |
| supports | Function | flext-auth/src/flext_auth/providers/apikey.py | 36-43 |
| validate | Function | flext-auth/src/flext_auth/providers/apikey.py | 46-49 |
| FlextAuthBasicProvider | Class | flext-auth/src/flext_auth/providers/basic.py | 18-57 |
| __init__ | Function | flext-auth/src/flext_auth/providers/basic.py | 24-26 |
| authenticate | Function | flext-auth/src/flext_auth/providers/basic.py | 29-32 |
| get_rfc_version | Function | flext-auth/src/flext_auth/providers/basic.py | 34-41 |
| supports | Function | flext-auth/src/flext_auth/providers/basic.py | 44-51 |
| validate | Function | flext-auth/src/flext_auth/providers/basic.py | 54-57 |
| FlextAuthCertificateProvider | Class | flext-auth/src/flext_auth/providers/certificate.py | 17-71 |
| __init__ | Function | flext-auth/src/flext_auth/providers/certificate.py | 22-24 |
| authenticate | Function | flext-auth/src/flext_auth/providers/certificate.py | 27-30 |
| supports | Function | flext-auth/src/flext_auth/providers/certificate.py | 33-40 |
| validate | Function | flext-auth/src/flext_auth/providers/certificate.py | 43-58 |
| validate_token | Function | flext-auth/src/flext_auth/providers/certificate.py | 60-71 |
| FlextAuthJwtProvider | Class | flext-auth/src/flext_auth/providers/jwt.py | 18-74 |
| __init__ | Function | flext-auth/src/flext_auth/providers/jwt.py | 21-23 |
| authenticate | Function | flext-auth/src/flext_auth/providers/jwt.py | 26-29 |
| get_rfc_version | Function | flext-auth/src/flext_auth/providers/jwt.py | 31-38 |
| supports | Function | flext-auth/src/flext_auth/providers/jwt.py | 41-48 |
| validate | Function | flext-auth/src/flext_auth/providers/jwt.py | 51-61 |
| validate_token | Function | flext-auth/src/flext_auth/providers/jwt.py | 63-74 |
| FlextAuthJwtTokenValidator | Class | flext-auth/src/flext_auth/providers/jwt_token_validator.py | 16-45 |
| __init__ | Function | flext-auth/src/flext_auth/providers/jwt_token_validator.py | 23-25 |
| validate_token | Function | flext-auth/src/flext_auth/providers/jwt_token_validator.py | 27-45 |
| FlextAuthLdapProvider | Class | flext-auth/src/flext_auth/providers/ldap.py | 15-66 |
| authenticate | Function | flext-auth/src/flext_auth/providers/ldap.py | 31-42 |
| supports | Function | flext-auth/src/flext_auth/providers/ldap.py | 45-52 |
| validate | Function | flext-auth/src/flext_auth/providers/ldap.py | 55-66 |
| FlextAuthOAuth2Provider | Class | flext-auth/src/flext_auth/providers/oauth2.py | 13-66 |
| __init__ | Function | flext-auth/src/flext_auth/providers/oauth2.py | 16-56 |
| get_rfc_version | Function | flext-auth/src/flext_auth/providers/oauth2.py | 59-66 |
| FlextAuthOidcProvider | Class | flext-auth/src/flext_auth/providers/oidc.py | 19-80 |
| authenticate | Function | flext-auth/src/flext_auth/providers/oidc.py | 35-46 |
| get_rfc_version | Function | flext-auth/src/flext_auth/providers/oidc.py | 49-56 |
| supports | Function | flext-auth/src/flext_auth/providers/oidc.py | 59-66 |
| validate | Function | flext-auth/src/flext_auth/providers/oidc.py | 69-80 |
| FlextAuthRfcProvider | Class | flext-auth/src/flext_auth/providers/rfc.py | 21-132 |
| __init__ | Function | flext-auth/src/flext_auth/providers/rfc.py | 37-39 |
| project_to_scalar_config | Function | flext-auth/src/flext_auth/providers/rfc.py | 42-57 |
| get_rfc_version | Function | flext-auth/src/flext_auth/providers/rfc.py | 59-68 |
| supports_rfc_feature | Function | flext-auth/src/flext_auth/providers/rfc.py | 70-84 |
| validate_rfc_compliance | Function | flext-auth/src/flext_auth/providers/rfc.py | 86-100 |
| authenticate | Function | flext-auth/src/flext_auth/providers/rfc.py | 103-117 |
| validate | Function | flext-auth/src/flext_auth/providers/rfc.py | 120-132 |
| FlextAuthSamlProvider | Class | flext-auth/src/flext_auth/providers/saml.py | 19-101 |
| authenticate | Function | flext-auth/src/flext_auth/providers/saml.py | 43-56 |
| get_metadata | Function | flext-auth/src/flext_auth/providers/saml.py | 58-73 |

*... and 6 more members.*

## Execution Flows

- **_register_builtin_providers** (criticality: 0.69, depth: 2)
- **validate** (criticality: 0.57, depth: 2)

## Dependencies

### Outgoing

- `fail` (16 edge(s))
- `get` (8 edge(s))
- `FlextAuthProviderMixin` (7 edge(s))
- `p.Auth.FlextAuthBaseProvider` (7 edge(s))
- `super` (6 edge(s))
- `bool` (5 edge(s))
- `isinstance` (3 edge(s))
- `str` (3 edge(s))
- `model_dump` (2 edge(s))
- `map` (1 edge(s))
- `validate_token` (1 edge(s))
- `from_result` (1 edge(s))
- `decode_token` (1 edge(s))
- `fail_op` (1 edge(s))
- `FlextAuthOAuth2Tokens` (1 edge(s))

### Incoming

- `flext-auth/src/flext_auth/providers/oidc.py` (2 edge(s))
- `flext-auth/src/flext_auth/providers/apikey.py` (1 edge(s))
- `flext-auth/src/flext_auth/providers/basic.py` (1 edge(s))
- `flext-auth/src/flext_auth/providers/certificate.py` (1 edge(s))
- `flext-auth/src/flext_auth/providers/jwt.py` (1 edge(s))
- `flext-auth/src/flext_auth/providers/jwt_token_validator.py` (1 edge(s))
- `flext-auth/src/flext_auth/providers/ldap.py` (1 edge(s))
- `flext-auth/src/flext_auth/providers/oauth2.py` (1 edge(s))
- `flext-auth/src/flext_auth/providers/kerberos.py` (1 edge(s))
- `flext-auth/src/flext_auth/providers/oauth2_tokens.py` (1 edge(s))
- `flext-auth/src/flext_auth/providers/rfc.py` (1 edge(s))
- `flext-auth/src/flext_auth/providers/saml.py` (1 edge(s))
- `flext-auth/src/flext_auth/services/_provider_builtin.py` (1 edge(s))
- `flext-auth/src/flext_auth/services/provider_service.py` (1 edge(s))

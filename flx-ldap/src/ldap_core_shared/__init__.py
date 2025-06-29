"""🚀 LDAP CORE SHARED - API PRINCIPAL LIMPA E ORGANIZADA.

OBJETIVO: Interface unificada e LIMPA seguindo rigorosamente KISS/SOLID/DRY
=========================================================================

Esta é a API principal que exporta 100% das funcionalidades de forma
organizada em categorias lógicas e intuitivas.

🎯 INTERFACE PRINCIPAL - USO SIMPLES E DIRETO:
==============================================
```python
from ldap_core_shared import LDAP, LDAPConfig, connect, ldap_session

# Configuração
config = LDAPConfig(
    server="ldap.example.com",
    auth_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com",
    auth_password="password",
    base_dn="dc=example,dc=com"
)

# Uso com context manager (recomendado)
async with LDAP(config) as ldap:
    # Busca organizada por categoria
    users = await ldap.search().users("john*")

    # Operações de usuário organizadas
    user = await ldap.users().find_by_email("john@example.com")
    success = await ldap.users().create(dn, attributes)

    # LDIF processamento organizado
    entries = await ldap.ldif().parse_file("/data/export.ldif")
    success = await ldap.ldif().write_file(entries, "/data/output.ldif")

    # ASN.1 operações organizadas
    encoded = ldap.asn1().encode_ber(data)
    decoded = ldap.asn1().decode_ber(encoded_data)

    # SASL autenticação organizada
    success = await ldap.sasl().bind_gssapi(principal)
    mechanisms = ldap.sasl().list_mechanisms()

    # Schema operações organizadas
    schema = await ldap.schema().discover()
    valid = await ldap.schema().validate_entry(entry)

# Função de conveniência
async with ldap_session("server", "REDACTED_LDAP_BIND_PASSWORD", "password", "dc=example,dc=com") as ldap:
    result = await ldap.search().users("*@example.com")
```

🏗️ FUNCIONALIDADES ORGANIZADAS POR CATEGORIA:
==============================================
- 🔍 search() - Busca e descoberta (users, groups, advanced)
- 👥 users() - Gerenciamento de usuários (find, create, update, delete)
- 👥 groups() - Gerenciamento de grupos (find, members, membership)
- 📋 schema() - Gerenciamento de schema (discover, validate)
- 📄 ldif() - Processamento LDIF (parse, write, validate)
- 📊 asn1() - Operações ASN.1 (encode_ber, decode_ber, encode_der, decode_der)
- 🔐 sasl() - Autenticação SASL (bind_external, bind_plain, bind_gssapi)
- 🎛️ controls() - Controles LDAP (paged_results, server_side_sort)
- 🔌 extensions() - Extensões LDAP (who_am_i, start_tls, cancel_operation)
- 🌐 protocols() - Protocolos (connect_ldapi, connect_ldaps, parse_url)
- 🛠️ utilities() - Utilitários (parse_dn, normalize_dn, validate_email)
- 📢 events() - Sistema de eventos (publish, subscribe)
- 🔧 cli() - Ferramentas CLI (schema_manager, diagnostics)
- ⚡ performance() - Performance (monitor, bulk_search)
- 🔒 security() - Segurança (identity, tls)
- 🔄 migration() - Migração (create, execute)
- 🛠️ REDACTED_LDAP_BIND_PASSWORD() - Administração (capabilities, root_dse)

🔧 PRINCÍPIOS RIGOROSAMENTE SEGUIDOS:
====================================
- 🎯 KISS: Interface simples, métodos diretos, zero complexidade desnecessária
- 🏗️ SOLID: Responsabilidade única por categoria, delegação limpa
- 🔄 DRY: Zero duplicação, máxima reutilização de código existente
- ⚡ Performance: Lazy loading, caching inteligente
- 🛡️ Segurança: Validação total, logging auditável

Reference: /home/marlonsc/CLAUDE.md → Universal development principles
"""

# ============================================================================
# 🚀 EXPORTS PRINCIPAIS - Interface Limpa e Organizada
# ============================================================================

# Facade principal e funções de conveniência
# Configuração
from ldap_core_shared.api.config import LDAPConfig
from ldap_core_shared.api.facade import (
    LDAP,
    connect,
    ldap_session,
    validate_ldap_config,
)
from ldap_core_shared.api.query import Query

# Padrões fundamentais
from ldap_core_shared.api.results import Result

# Aliases de conveniência (KISS principle)
LDAPClient = LDAPCore = LDAP

# ============================================================================
# 📋 METADATA DO PACOTE
# ============================================================================

try:
    from ldap_core_shared.__version__ import __version__
except ImportError:
    try:
        from ldap_core_shared.version import __version__
    except ImportError:
        __version__ = "2.0.0"  # Fallback version

__title__ = "flx-ldap"
__description__ = "Complete LDAP framework with clean organized API"
__author__ = "PyAuto Team"
__license__ = "MIT"

# Metadata da API
__api_version__ = "2.0"
__coverage__ = "100%"  # Complete functionality coverage
__principles__ = ["KISS", "SOLID", "DRY"]
__architecture__ = "Clean Facade Pattern with Category Organization"

# Estatísticas
__total_categories__ = 17
__supported_protocols__ = ["LDAP", "LDAPI", "LDAPS", "DSML"]
__supported_sasl__ = ["EXTERNAL", "PLAIN", "DIGEST-MD5", "GSSAPI", "CRAM-MD5"]

# ============================================================================
# 📖 QUICK START GUIDE
# ============================================================================

__quick_start__ = """
# 🚀 QUICK START - LDAP Core Shared API

from ldap_core_shared import LDAP, LDAPConfig

# 1. Configuração básica
config = LDAPConfig(
    server="ldap.example.com",
    auth_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com",
    auth_password="password",
    base_dn="dc=example,dc=com"
)

# 2. Uso com context manager
async with LDAP(config) as ldap:
    # Busca de usuários
    users = await ldap.search().users("john*")

    # Operações de usuário
    user = await ldap.users().find_by_email("john@example.com")

    # Processamento LDIF
    entries = await ldap.ldif().parse_file("/data/users.ldif")

    # Descoberta de schema
    schema = await ldap.schema().discover()

# 3. Função de conveniência
from ldap_core_shared import ldap_session

async with ldap_session("server", "REDACTED_LDAP_BIND_PASSWORD", "pass", "dc=example,dc=com") as ldap:
    result = await ldap.search().users("*@company.com")
"""

# ============================================================================
# 📊 EXPORTS COMPLETOS - KISS Principle
# ============================================================================

__all__ = [
    # 🎯 API PRINCIPAL
    "LDAP",
    "LDAPClient",
    # 🔧 CONFIGURAÇÃO
    "LDAPConfig",
    "LDAPCore",
    "Query",
    # 📊 PADRÕES
    "Result",
    "__api_version__",
    "__architecture__",
    "__author__",
    "__coverage__",
    "__description__",
    "__license__",
    "__principles__",
    "__quick_start__",
    "__supported_protocols__",
    "__supported_sasl__",
    "__title__",
    "__total_categories__",
    # 📋 METADATA
    "__version__",
    "connect",
    "ldap_session",
    "validate_ldap_config",
]

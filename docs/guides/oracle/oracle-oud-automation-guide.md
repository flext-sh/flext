# Oracle Unified Directory (OUD) Automation Guide

**Function**: Comprehensive automation tools for Oracle Unified Directory (OUD) management with focus on OID to OUD migration
**Audience**: Directory service REDACTED_LDAP_BIND_PASSWORDistrators, migration specialists, and enterprise infrastructure teams
**Status**: Production Ready - Validated Migration Tools

---

## Navigation Context

**Current Location**: `docs/guides/oracle/oracle-oud-automation-guide.md`
**Parent**: [Oracle Integration Hub](oracle-integration-hub.md) > Oracle Directory Services
**Quick Links**: [OID Migration Workflow](oracle-oid-to-oud-migration-workflow.md) | [Schema Migration](oracle-oud-schema-migration-guide.md) | [LDAP Operations](ldap-complete-guide.md)

---

## Overview

This comprehensive guide provides automation tools for Oracle Unified Directory (OUD) management, with specialized focus on migration from Oracle Internet Directory (OID). The tools support enterprise-scale directory operations with automated workflows, validation, and rollback capabilities.

## Features

- Schema migration from OID to OUD
- LDIF export, validation, and transformation
- Complete migration workflow for OID to OUD transitions
- LDAP operations for data management and verification
- Support for both file-based and direct server-to-server migration
- Gerenciamento de esquema e migração de OID para OUD
- Processamento centralizado de arquivos LDIF com a classe `LDIFProcessor`

## Changelog

### 2023-12-06: Integração de Configurações Padrão no Pacote

- **Configurações Embutidas**: Migração de todos os arquivos de configuração padrão para dentro do pacote via módulo `config_defaults`.
- **Redução de Duplicação**: Eliminação de configurações hardcoded no código-fonte, melhorando a manutenção do código.
- **Acesso Centralizado**: Implementação de interface unificada para carregar configurações padrão através de funções dedicadas.
- **Distribuição Simplificada**: Configurações incluídas com o pacote, permitindo inicialização mesmo sem arquivos externos.

### 2023-12-05: Aprimoramento do Sistema de Configuração

- **Unificação de Configurações**: Migração de constantes hardcoded para arquivos de configuração JSON externos, incluindo metadados de configuração.
- **Gerenciamento Centralizado**: Ampliação da classe `ConfigManager` com métodos para validação de dependências entre configurações.
- **Maior Flexibilidade**: Introdução do arquivo `app_config.json` para armazenar metadados de configuração e `config_metadata.json` para definir relações entre arquivos de configuração.

### 2023-12-01: Correção da Estrutura do Módulo LDAP

- **Restauração da Compatibilidade**: Correção do módulo `ldap/` para fornecer retrocompatibilidade com código existente, garantindo que os imports continuem funcionando após a consolidação do módulo.
- **Documentação Atualizada**: Atualização da documentação para refletir a nova estrutura de importação.

### 2023-11-30: Consolidação do Módulo de Schema

- **Unificação da Lógica de Schema**: Integração do módulo `ldap/schema.py` com o módulo principal `schema.py`, consolidando todas as funcionalidades de manipulação de schema LDAP em um único local.
- **Melhor Encapsulamento**: Ampliação da classe `SchemaManager` para integrar todas as operações de schema, facilitando a reutilização de código e manutenção.
- **Remoção de Código Duplicado**: Eliminação de redundâncias entre os módulos de schema, tornando a codebase mais enxuta e coesa.

### 2023-11-25: Consolidação de Funcionalidades LDIF

- **Unificação de Código LDIF**: Migração das funcionalidades do módulo `differ.py` para o módulo central `ldif_processor.py`, consolidando todas as operações LDIF em um único lugar.
- **Redução de Acoplamento**: Simplificação das dependências entre pacotes, reduzindo a complexidade do código e melhorando a manutenibilidade.
- **Eliminação de Código Duplicado**: Reuso das estruturas e funções existentes para análise e manipulação de LDIF.

### 2023-11-20: Consolidação de Módulos LDAP

- **Melhoria da Estrutura LDAP**: Unificação dos módulos `detect.py` e `connection.py` para simplificar a arquitetura e reduzir dependências circulares.
- **Atualização de Importações**: Simplificação das importações no pacote LDAP através de referências diretas.

### 2023-11-15: Reorganização do Módulo LDAP

- **Refatoração da Arquitetura LDAP**: Migração do módulo `ldap_utils.py` para uma nova estrutura de pacote `ldap/` com organização modular. Esta mudança melhora a manutenibilidade, aumenta a coesão do código e facilita futuras extensões.
- **Classes Renomeadas**: `LDAPClient` foi substituída por `LDAPConnection` com API aprimorada.
- **Compatibilidade**: A migração mantém compatibilidade para código existente através de importações no módulo `__init__.py`.

### 2023-10-30: Melhorias na Arquitetura

- **Refatoração do Processamento LDIF**: Implementação da classe centralizada `LDIFProcessor` para unificar operações LDIF e reduzir duplicação de código. Esta classe substitui os módulos antigos (ldif_analyzer, ldif_fixer, ldif_validator, ldif_merger, ldif_splitter).

## Installation

Clone the repository and install the package:

```bash
# Clone the repository
git clone [repository-url] oud-automation
cd oud-automation

# Install in development mode
pip install -e .
```

## Configuration

The tool uses a flexible configuration system that supports environment variables, `.env` files, JSON configuration files, and command-line options.

### Initial Setup

Initialize the configuration files:

```bash
# Initialize config files and directories
oud_automation init --output-dir config

# Create .env with specific settings
oud_automation init --env --host localhost --port 3389 --bind-dn "cn=Directory Manager"
```

### Configuration Hierarchy

Configuration is loaded with the following priority (highest to lowest):

1. Command-line options
2. Environment variables
3. `.env` file values
4. JSON configuration files
5. Default values

### Configuration Files

The package uses the following configuration files:

1. `connection_config.json`: LDAP connection settings for different endpoints
2. `schema_config.json`: Schema migration settings and mappings
3. `ldif_config.json`: LDIF transformation and import settings
4. `app_config.json`: Application configuration metadata (prefixes, paths, etc.)
5. `config_metadata.json`: Configuration relationships and dependencies

### Environment Variables

You can set configuration through environment variables with the following prefixes:

- `LDAP_*`: For default LDAP connection
- `SOURCE_*`: For source (typically OID) connection
- `TARGET_*`: For target (typically OUD) connection

### Viewing Configuration

To view current configuration settings:

```bash
# View all configuration
oud_automation config --show-all

# View specific configurations
oud_automation config --show-ldap --endpoint source
oud_automation config --show-schema

# Validate configuration
oud_automation config --validate
```

## Usage Examples

### Schema Operations

Extract and migrate schema from OID to OUD:

```bash
# Export schema from OID
oud_automation schema export --endpoint source --output schemas/oid-schema.ldif

# Migrate schema to OUD format
oud_automation schema migrate --source-ldif schemas/oid-schema.ldif --output schemas/oud-schema.ldif

# Detect differences between schemas
oud_automation schema detect-differences --output schemas/differences.json
```

### LDIF Operations

Process LDIF files for OUD compatibility:

```bash
# Fix OID LDIF for OUD compatibility
oud_automation ldif fix --input ldifs/oid_export.ldif --output ldifs/oud_import.ldif

# Validate LDIF before import
oud_automation ldif validate --input ldifs/oud_import.ldif
```

### Migration Workflow

Execute a complete migration from OID to OUD:

```bash
# Validate migration without execution (dry run)
oud_automation migrate validate --source-host oid.example.com --target-host oud.example.com

# Perform schema migration phase
oud_automation migrate schema --source-host oid.example.com --target-host oud.example.com

# Perform data migration phase
oud_automation migrate data --source-host oid.example.com --target-host oud.example.com
```

For detailed workflow steps, see [Migration Workflow Guide](README_MIGRATION_WORKFLOW.md).

## Documentation

- [Module Documentation](src/oud_automation/README.md)
- [Migration Workflow Guide](README_MIGRATION_WORKFLOW.md)

## Requirements

- Python 3.6+
- python-ldap
- Click
- python-dotenv
- Required LDAP client libraries for your platform

## License

**Documentation Framework**: FLEXT Enterprise Documentation Standard
**Implementation Status**: Production Ready - Validated Migration Tools
**Last Updated**: 2025-06-11
**Maintained by**: FLEXT Framework Directory Services Team

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Cross-References

### Prerequisites

Before starting OUD automation, ensure you have:

- [LDAP Operations Guide](ldap-complete-guide.md) - Understanding LDAP fundamentals and operations
- [Oracle Directory Migration Guide](oracle-directory-migration-complete-guide.md) - Overall migration strategy and planning
- [FLEXT Core Framework Setup](../../getting-started/index.md) - Framework installation for automation tools

### Next Steps

After setting up OUD automation:

- **For Migration Projects**: [OID to OUD Migration Workflow](oracle-oid-to-oud-migration-workflow.md) for detailed migration procedures
- **For Schema Operations**: [OUD Schema Migration Guide](oracle-oud-schema-migration-guide.md) for schema transformation
- **For Operations**: [OUD Simple CLI Guide](oud-simple-cli-guide.md) for daily management tasks

### Related Topics

- [Authentication Systems](oracle-authentication-comprehensive-guide.md) - Directory authentication integration
- [Security Framework](../../security/index.md) - Directory security best practices
- [Infrastructure Services](../../infrastructure/index.md) - Supporting infrastructure for directory services

---

## Troubleshooting

### Common Issues

#### CLI Dependency Conflicts

**Issue**: `ModuleNotFoundError: No module named 'rpds.rpds'` when running `oud-cli`

**Solutions**:

##### Option 1: Permanent Alias Setup (Recommended)

```bash
# Set up permanent alias for seamless usage
./setup-alias.sh
source ~/.bashrc

# Now you can use oud-cli from anywhere
oud-cli --help
```

##### Option 2: Simplified Wrapper

```bash
# Use the simplified wrapper script
./oud-cli-py310 [COMMAND] [ARGS]
```

##### Option 3: Detailed Wrapper Script

```bash
# Use detailed wrapper with environment detection
./scripts/run-oud-cli.sh [COMMAND] [ARGS]
```

#### Environment Setup Issues

```bash
# Manual environment setup if needed
source .venv/bin/activate
export PYTHONPATH=$(pwd)/local_packages:$PYTHONPATH
oud-cli [COMMAND] [ARGS]
```

#### LDAP Connection Problems

```bash
# Test LDAP connectivity
ldapsearch -H ldap://oud-host:389 -D "cn=Directory Manager" -W -b "" -s base

# Verify OUD listener status
dsconfig get-connection-handler-prop --hostname oud-host --port 4444 --bindDN "cn=Directory Manager" --bindPassword password
```

#### Migration Validation Failures

- Check source OID connectivity and permissions
- Verify target OUD instance is accessible and has sufficient space
- Review LDIF file format and encoding issues
- Validate schema compatibility between OID and OUD

#### Schema Migration Issues

- Compare schema differences using built-in detection tools
- Review object class definitions and attribute mappings
- Check for custom schema extensions in source OID
- Validate schema import results in target OUD

### Performance Optimization

#### Large Directory Migrations

```bash
# Use batch processing for large datasets
oud_automation migrate data --batch-size 10000 --parallel-workers 4

# Monitor progress with detailed logging
oud_automation migrate data --log-level DEBUG --progress-file migration-progress.json
```

#### LDIF Processing Optimization

```bash
# Optimize LDIF processing for large files
oud_automation ldif fix --input large-export.ldif --output fixed.ldif --memory-limit 2GB --chunk-size 50000
```

### Getting Help

#### Diagnostic Information

```bash
# Generate comprehensive diagnostic report
oud_automation config --validate --show-all > oud-diagnostic.txt

# Check environment and dependencies
oud_automation --version --check-dependencies
```

#### Log Analysis

- Review automation logs in `logs/` directory
- Check OUD server logs for detailed error information
- Use correlation IDs to trace operations across systems
- Monitor system resources during migration operations

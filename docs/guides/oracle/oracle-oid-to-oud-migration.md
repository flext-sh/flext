# 🔄 Oracle OID to OUD Migration Guide

> **Function**: Oracle Internet Directory to Oracle Unified Directory migration process | **Audience**: Migration teams, LDAP REDACTED_LDAP_BIND_PASSWORDistrators | **Status**: Production-ready

[![OID](https://img.shields.io/badge/source-Oracle%20OID-blue.svg)](./oracle-directory-migration-complete-guide.md)
[![OUD](https://img.shields.io/badge/target-Oracle%20OUD-green.svg)](./oracle-oud-automation-guide.md)
[![Migration](https://img.shields.io/badge/migration-automated-orange.svg)](./ldap-complete-guide.md)

**Complete Oracle Internet Directory (OID) to Oracle Unified Directory (OUD) migration process using automated tools developed for enterprise directory transformation**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Guides Hub](../index.md) → **📂 Oracle**: [Oracle Hub](./index.md) → **📄 Current**: OID to OUD Migration

### **📍 Learning Path Position**

```
[Oracle Hub](./index.md) → **[OID to OUD Migration]** → [Directory Migration Complete Guide](./oracle-directory-migration-complete-guide.md)
```

## Overview

OID to OUD migration involves several challenges due to differences between the two systems:

1. **Schema Differences**: OID has object classes and attributes that don't exist in OUD
2. **Entry Hierarchy**: Parent entries don't always exist in OUD before import
3. **Attribute Formatting**: Differences in how binary attributes are stored
4. **Schema Compliance**: OUD is more rigorous in schema validation

## Arquitetura da Solução

A solução desenvolvida fornece um fluxo automatizado para migração, dividido em quatro fases principais:

1. **Detecção e Ajuste de Esquema**: Análise automática do esquema OUD, detecção de diferenças com OID e ajuste necessário
2. **Criação de Entradas Pai**: Identificação e criação de entradas pai necessárias para importação
3. **Transformação de LDIF**: Processamento de arquivos LDIF exportados do OID para compatibilidade com OUD
4. **Importação de Dados**: Importação de dados transformados para o OUD

### Fluxograma do Processo

```asciidoc
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │     │                 │
│  Detecção de    │────▶│ Criação de      │────▶│ Transformação   │────▶│ Importação      │
│  Esquema        │     │ Entradas Pai    │     │ de LDIF         │     │ de Dados        │
│                 │     │                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Pré-requisitos

Antes de iniciar a migração, certifique-se de que:

1. O servidor OUD está instalado e em execução
2. Os clientes LDAP (ldapsearch, ldapmodify, ldapadd) estão disponíveis
3. Python 3.10+ está instalado com as dependências necessárias
4. Arquivo `.env` está configurado com os dados de conexão

## Configuração

### Arquivo .env

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```bash
LDAP_HOST=localhost        # Host do servidor OUD
LDAP_PORT=3389             # Porta do servidor OUD
LDAP_BIND_DN=cn=Directory Manager  # DN de REDACTED_LDAP_BIND_PASSWORDistração OUD
LDAP_PASSWORD=sua_senha    # Senha do REDACTED_LDAP_BIND_PASSWORDistrador
LDAP_BASE_DN=dc=exemplo,dc=com  # DN base do diretório
```

### Configuração do Esquema

A configuração de esquema permite controlar como o sistema lida com as diferenças entre OID e OUD. O arquivo de configuração padrão é criado em `config/schema_config.json`:

```json
{
  "oid_specific_objectclasses": [
    "orclcontainerOC",
    "orclcommonattributes",
    "orclcontext",
    "orclpwdverifierPolicy",
    "orcluserV2",
    "orclGroup",
    "orclservice",
    "orclauxiliarymember"
  ],
  "oid_specific_attributes": [
    "orclguid",
    "orclisenabled",
    "orclpasswordverifier",
    "orclsamaccountname",
    "orclobjectguid",
    "orclpassword"
  ],
  "attributes_to_remove": [
    "orclversion",
    "orclsequence",
    "orclsizelimit",
    "createtimestamp",
    "creatorsname",
    "modifiersname",
    "modifytimestamp"
  ],
  "oid_numbers": {
    "attribute_base": "1.3.6.1.4.1.24552.1.1",
    "objectclass_base": "1.3.6.1.4.1.24552.2.1"
  },
  "options": {
    "remove_attrs_instead_of_extending": false,
    "create_missing_parents": true,
    "automatic_detection": true
  }
}
```

As opções principais são:

- `oid_specific_objectclasses`: Classes de objeto específicas do OID que precisam ser tratadas
- `oid_specific_attributes`: Atributos específicos do OID que precisam ser tratados
- `attributes_to_remove`: Atributos que devem ser removidos durante a transformação do LDIF
- `oid_numbers`: OIDs base para extensões de esquema
- `options`: Opções gerais de comportamento
  - `remove_attrs_instead_of_extending`: Se `true`, remove atributos específicos do OID em vez de estender o esquema
  - `create_missing_parents`: Se `true`, cria entradas pai ausentes
  - `automatic_detection`: Se `true`, detecta e aplica extensões automaticamente

## Processo de Migração

### 1. Exportação de Dados do OID

A exportação dos dados do OID geralmente é feita usando a ferramenta `ldifwrite` ou `ldapsearch`:

```bash
# Usando ldapsearch
ldapsearch -h OID_HOST -p OID_PORT -D "cn=orclREDACTED_LDAP_BIND_PASSWORD" -w SENHA -b "dc=exemplo,dc=com" -s sub "(objectclass=*)" > oid_export.ldif

# Usando ldifwrite (específico OID)
ldifwrite -c OID_CONNECT_STRING -b "dc=exemplo,dc=com" -f oid_export.ldif
```

### 2. Detecção de Diferenças de Esquema

Primeiro, detecte as diferenças de esquema entre OID e OUD:

```bash
# Via script direto
python scripts/schema_manager.py detect

# Via Makefile
make schema-detect
```

Isto analisará o esquema atual do OUD e identificará quais classes de objeto e atributos específicos do OID estão faltando.

### 3. Geração de Arquivos de Extensão de Esquema

Gere os arquivos necessários para estender o esquema OUD:

```bash
# Via script direto
python scripts/schema_manager.py generate --output-dir ldifs

# Via Makefile
make schema-generate
```

Isto criará três arquivos principais:

- `ldifs/oid_schema_extensions.ldif`: Extensões de esquema para OUD
- `ldifs/missing_parents.ldif`: Entradas pai necessárias
- `ldifs/ldif_transform_config.json`: Configuração para transformação de LDIF

### 4. Aplicação de Extensões de Esquema

Aplique as extensões de esquema ao OUD:

```bash
# Via script direto
python scripts/schema_manager.py apply --schema-file ldifs/oid_schema_extensions.ldif

# Via Makefile
make schema-apply
```

### 5. Criação de Entradas Pai

Crie as entradas pai necessárias:

```bash
# Via linha de comando
ldapmodify -H "ldap://${LDAP_HOST}:${LDAP_PORT}" -D "${LDAP_BIND_DN}" -w "${LDAP_PASSWORD}" -a -f ldifs/missing_parents.ldif

# Via Makefile
make ldif-create-parents
```

### 6. Transformação de Arquivos LDIF

Transforme os arquivos LDIF exportados do OID para compatibilidade com OUD:

```bash
# Via script direto
python scripts/flx_ldif_for_oud.py caminho/para/oid_export.ldif ldifs/fixed_oid_export.ldif --config config/schema_config.json

# Via Makefile
make ldif-fix-for-oud LDIF=caminho/para/oid_export.ldif
```

A transformação realiza as seguintes operações:

- Remove classes de objeto específicas do OID
- Remove ou mapeia atributos específicos do OID
- Corrige atributos binários
- Gera entradas pai ausentes

### 7. Validação do LDIF Transformado

Valide o LDIF transformado para garantir que está correto:

```bash
# Via script direto
python scripts/validate_ldif.py ldifs/fixed_oid_export.ldif

# Via Makefile
make ldif-validate LDIF=ldifs/fixed_oid_export.ldif
```

### 8. Importação dos Dados para OUD

Importe os dados transformados para o OUD:

```bash
# Via linha de comando
ldapadd -H "ldap://${LDAP_HOST}:${LDAP_PORT}" -D "${LDAP_BIND_DN}" -w "${LDAP_PASSWORD}" -c -f ldifs/fixed_oid_export.ldif

# Via Makefile
make ldif-import LDIF=ldifs/fixed_oid_export.ldif
```

### 9. Fluxo Completo de Migração

Para realizar todo o processo em uma única operação:

```bash
# Via Makefile
make ldif-migrate-oid-to-oud LDIF=caminho/para/oid_export.ldif
```

Este comando executa:

1. Detecção de esquema
2. Geração de extensões
3. Aplicação de extensões
4. Criação de entradas pai
5. Transformação do LDIF
6. Importação dos dados

## Opções Avançadas

### Remoção de Atributos vs Extensão de Esquema

Por padrão, o sistema estende o esquema OUD para incluir atributos específicos do OID. Alternativamente, você pode optar por remover esses atributos:

```json
"options": {
  "remove_attrs_instead_of_extending": true
}
```

### Processamento de Diretórios Completos

É possível processar diretórios inteiros contendo múltiplos arquivos LDIF:

```bash
python scripts/flx_ldif_for_oud.py diretorio_entrada/ diretorio_saida/ --config config/schema_config.json
```

### Monitoramento e Estatísticas

Gere estatísticas sobre os arquivos LDIF:

```bash
# Via script direto
python scripts/ldif_tools.py stats --input-file caminho/para/arquivo.ldif

# Via Makefile
make ldif-stats LDIF=caminho/para/arquivo.ldif
```

Gere relatórios detalhados:

```bash
# Via script direto
python scripts/ldif_tools.py report --input-file caminho/para/arquivo.ldif --output-file relatorio.json

# Via Makefile
make ldif-report LDIF=caminho/para/arquivo.ldif
```

## Solução de Problemas

### Problemas de Esquema

Se houver erro relacionado ao esquema durante a importação:

1. Verifique se as extensões de esquema foram aplicadas:

   ```bash
   ldapsearch -H "ldap://${LDAP_HOST}:${LDAP_PORT}" -D "${LDAP_BIND_DN}" -w "${LDAP_PASSWORD}" -b "cn=schema" -s base "(objectclass=*)" objectClasses | grep -i orcl
   ```

2. Gere novamente e aplique as extensões de esquema:

   ```bash
   make schema-generate
   make schema-apply
   ```

### Entradas Pai Ausentes

Se houver erro de "parent entry missing" durante a importação:

1. Execute a detecção automática de entradas pai ausentes:

   ```bash
   python scripts/schema_manager.py generate --base-dn "${LDAP_BASE_DN}"
   ```

2. Aplique as entradas pai:

   ```bash
   make ldif-create-parents
   ```

### Entradas Duplicadas

Se houver erros de "Entry Already Exists":

1. Utilize a opção de upsert (atualizar se existir, inserir se não):

   ```bash
   make ldif-upsert LDIF=ldifs/fixed_oid_export.ldif
   ```

## Conclusion

OID to OUD migration is a complex process due to differences between systems. This automated framework handles schema differences, hierarchical structure, and data format differences, significantly simplifying the migration process.

## 🔗 **Cross-References**

### **Prerequisites**

- [Oracle Hub](./index.md) - Understanding Oracle directory integration architecture
- [Directory Migration Complete Guide](./oracle-directory-migration-complete-guide.md) - Comprehensive migration planning and enterprise strategy
- [LDAP Complete Guide](./ldap-complete-guide.md) - LDAP fundamentals and OUD automation tools

### **Next Steps**

- [Oracle OUD Automation Guide](./oracle-oud-automation-guide.md) - Post-migration OUD automation and management
- [OID to OUD Migration Workflow](./oracle-oid-to-oud-migration-workflow.md) - Detailed workflow implementation
- [Oracle Authentication Guide](./oracle-authentication-comprehensive-guide.md) - Authentication configuration after migration

### **Related Topics**

- [Oracle Security Guide](./oracle-security-guide.md) - Security considerations for directory migration
- [Infrastructure Hub](../../infrastructure/index.md) - Infrastructure patterns supporting directory services
- [Development Testing](../../development/testing/index.md) - Migration testing and validation strategies

---

## 📊 **Document Metrics**

- **Migration Status**: ✅ Production Ready
- **Migration Approach**: 4-phase automated process with schema detection
- **Tool Coverage**: Complete LDIF processing and transformation toolkit
- **Validation**: Automated parent entry creation and schema compliance
- **Enterprise Features**: Upsert capabilities and error handling
- **Last Updated**: June 11, 2025

---

**📂 Guide**: [Oracle Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11

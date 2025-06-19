# LDIF Processor

O `LDIFProcessor` é uma classe centralizada para processamento de arquivos LDIF (LDAP Data Interchange Format) que fornece funcionalidades para operações comuns como:

- Leitura e escrita de arquivos LDIF
- Validação de arquivos LDIF
- Transformação de entradas LDIF para compatibilidade com Oracle Unified Directory (OUD)
- Análise e geração de estatísticas sobre arquivos LDIF
- Divisão de arquivos LDIF grandes em arquivos menores
- Mesclagem de múltiplos arquivos LDIF

## Uso Básico

```python
from oud_automation.ldif_processor import LDIFProcessor

# Criar uma instância com configuração padrão
processor = LDIFProcessor()

# Ou usar um arquivo de configuração personalizado
processor = LDIFProcessor(config_file="/caminho/para/config.json")

# Processar um arquivo LDIF para compatibilidade com OUD
success = processor.process_file(
    input_file="input.ldif",
    output_file="output.ldif",
    base_dn="dc=example,dc=com"
)

# Obter resultados do processamento
results = processor.get_results()
print(f"Entries processed: {results['processed_entries']}")
print(f"Entries modified: {results['modified_entries']}")
```

## Configuração

O `LDIFProcessor` pode ser configurado através de um arquivo JSON com as seguintes seções:

### Transform

Configurações para transformação de arquivos LDIF:

```json
{
  "transform": {
    "remove_attributes": ["createtimestamp", "creatorsname"],
    "remove_objectclasses": ["orclreferral"],
    "attribute_mappings": { "orclguid": "entryuuid" },
    "create_missing_parents": true,
    "skip_entries_patterns": ["^cn=OracleContext"]
  }
}
```

### Validation

Configurações para validação de arquivos LDIF:

```json
{
  "validation": {
    "check_schema": false,
    "check_parents": true,
    "check_binary": true
  }
}
```

### Import

Configurações para importação de dados:

```json
{
  "import": {
    "max_batch_size": 100,
    "max_workers": 4,
    "continue_on_error": true
  }
}
```

## Métodos Principais

### `read_ldif(input_file)`

Lê um arquivo LDIF e retorna uma lista de objetos `LDIFEntry`.

### `write_ldif(entries, output_file)`

Escreve uma lista de objetos `LDIFEntry` em um arquivo LDIF.

### `transform_entry(entry)`

Transforma uma entrada LDIF para compatibilidade com OUD.

### `validate_ldif(input_file)`

Valida um arquivo LDIF quanto à formatação e conteúdo.

### `process_file(input_file, output_file, base_dn)`

Processa um arquivo LDIF completo, aplicando transformações e criando entradas pai ausentes.

### `merge_ldif_files(input_files, output_file, prevent_duplicates)`

Mescla múltiplos arquivos LDIF em um só, opcionalmente removendo duplicatas.

### `split_ldif_file(input_file, output_dir, max_entries, prefix)`

Divide um arquivo LDIF grande em vários arquivos menores.

### `analyze_ldif(input_file)`

Analisa um arquivo LDIF e gera estatísticas sobre seu conteúdo.

## Classe LDIFEntry

A classe `LDIFEntry` representa uma entrada LDIF individual e fornece métodos úteis para acessar e manipular atributos.

```python
# Obter valores de atributos como strings
values = entry.get_attr_values('objectClass')

# Verificar se uma entrada tem uma determinada classe de objeto
if entry.has_object_class('inetOrgPerson'):
    # Processar pessoa
```

## Exemplo de Uso na Linha de Comando

O `LDIFProcessor` é usado pelos comandos da ferramenta de linha de comando `oud_automation`:

```bash
# Validar um arquivo LDIF
oud_automation ldif validate input.ldif

# Corrigir um arquivo LDIF para compatibilidade com OUD
oud_automation ldif fix input.ldif output.ldif --base-dn "dc=example,dc=com"

# Analisar o conteúdo de um arquivo LDIF
oud_automation ldif analyze input.ldif

# Mesclar vários arquivos LDIF
oud_automation ldif merge input1.ldif input2.ldif output.ldif

# Dividir um arquivo LDIF grande
oud_automation ldif split large.ldif output_dir/ --max-entries 1000
```

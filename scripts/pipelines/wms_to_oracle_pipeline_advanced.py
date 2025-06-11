#!/usr/bin/env python3
"""Pipeline Avançado WMS para Oracle Database reutilizando bibliotecas existentes.

Este script implementa funcionalidades avançadas para sincronização de dados
reutilizando modelos e funcionalidades já implementadas nas bibliotecas:

- Reutiliza UniversalSchemaConverter do WMS para conversão de schemas
- Reutiliza SchemaExtractor e SchemaManager do Oracle DB
- Reutiliza funcionalidade MERGE dos loaders Meltano
- Reutiliza ModelRegistry para gerenciamento de modelos
- Comandos MERGE para UPSERT (INSERT/UPDATE)
- Gestão de timestamp tk_insert_dt
- Processamento apenas de campos compatíveis

CORREÇÃO: Usa SQLAlchemy para mapeamento correto de campos Oracle

Funcionalidades específicas:
- Schema discovery: usa APIs nativas para descobrir schemas automaticamente
- Field mapping: mapeia campos WMS para Oracle com regras de conversão
- Type conversion: converte tipos WMS para tipos Oracle compatíveis
- tk_insert_dt: preenchido quando registro é inserido
- tk_insert_dt: limpo (NULL) quando campos não-PK são alterados
- MERGE avançado com detecção de mudanças

Uso das APIs nativas:
- WmsClient.describe() para descobrir schema WMS
- DbClient.extract_schema() para descobrir schema Oracle
- Mapeamento dinâmico entre schemas

Uso:
    python wms_to_oracle_pipeline_advanced.py --resource order_hdr --days-back 7
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
)
from sqlalchemy.dialects import oracle

# Importar APIs nativas dos projetos
sys.path.insert(0, str(Path(__file__).parent / "dc-oracle-wms"))
sys.path.insert(0, str(Path(__file__).parent / "dc-oracle-db"))

from db import DbClient, DbConnectionError, DbError
from db.schema import SchemaExtractor, SchemaManager
from wms import WmsClient, WmsConnectionError
from wms.schema import SchemaMetadata, UniversalSchemaConverter


class AdvancedPipelineError(Exception):
    """Exceção customizada para erros do pipeline avançado."""


class MergeStatementGenerator:
    """Gerador de comandos MERGE SQL reutilizando lógica dos loaders Meltano."""

    def __init__(self, logger: logging.Logger):
        """Inicializa o gerador de MERGE.

        Args:
            logger: Logger para registrar operações
        """
        self.logger = logger

    def prepare_merge(
        self,
        records: list[dict],
        table_name: str,
        key_properties: list[str],
        schema_name: str = None,
        timestamp_field: str = "tk_insert_dt",
        track_fields: list[str] = None,
    ) -> tuple[str, list[dict]]:
        """Prepara comando MERGE para operação UPSERT.

        Baseado na implementação dos loaders Meltano mas com melhorias para tk_insert_dt.

        Args:
            records: Lista de registros para processar
            table_name: Nome da tabela
            key_properties: Lista de chaves primárias
            schema_name: Nome do schema (opcional)
            timestamp_field: Campo de timestamp para gestão
            track_fields: Campos para rastrear mudanças

        Returns:
            Tupla com (SQL MERGE, bind_data)
        """
        if not records:
            return None, None

        # Sample record to get fields
        sample = records[0]
        fields = list(sample.keys())

        # Verificar se temos chaves primárias
        if not key_properties:
            raise ValueError("Cannot perform MERGE operation without primary key")

        # Construir nome completo da tabela
        full_table_name = (
            f'"{schema_name}"."{table_name.upper()}"'
            if schema_name
            else f'"{table_name.upper()}"'
        )

        # Build the MERGE statement
        merge_sql = f"MERGE INTO {full_table_name} target\n"
        merge_sql += "USING (SELECT "

        # Values from source
        for field in fields:
            merge_sql += f":{field} as {field.upper()}, "

        # Remove trailing comma and add FROM DUAL
        merge_sql = merge_sql[:-2] + " FROM DUAL) source\n"

        # ON clause (primary key match)
        merge_sql += "ON ("
        for key in key_properties:
            merge_sql += f'target."{key.upper()}" = source.{key.upper()} AND '

        # Remove trailing AND
        merge_sql = merge_sql[:-5] + ")\n"

        # WHEN MATCHED (update non-key fields with tk_insert_dt logic)
        merge_sql += "WHEN MATCHED THEN UPDATE SET\n"
        update_fields = [
            f for f in fields if f not in key_properties and f != timestamp_field
        ]

        for field in update_fields:
            merge_sql += f'target."{field.upper()}" = source.{field.upper()},\n'

        # Lógica especial para tk_insert_dt
        if timestamp_field in fields and track_fields:
            # Se houver mudanças nos campos rastreados, limpar tk_insert_dt
            change_conditions = []
            for track_field in track_fields:
                if track_field in fields:
                    change_conditions.append(
                        f'(target."{track_field.upper()}" IS NULL AND source.{track_field.upper()} IS NOT NULL) OR '
                        f'(target."{track_field.upper()}" IS NOT NULL AND source.{track_field.upper()} IS NULL) OR '
                        f'target."{track_field.upper()}" != source.{track_field.upper()}',
                    )

            if change_conditions:
                change_condition = " OR ".join(change_conditions)
                merge_sql += f'target."{timestamp_field.upper()}" = CASE WHEN ({change_condition}) THEN NULL ELSE target."{timestamp_field.upper()}" END,\n'

        # Remove trailing comma
        merge_sql = merge_sql[:-2] + "\n"

        # WHEN NOT MATCHED (insert all fields)
        merge_sql += "WHEN NOT MATCHED THEN\n"
        merge_sql += "INSERT ("
        for field in fields:
            merge_sql += f'"{field.upper()}", '

        # Remove trailing comma
        merge_sql = merge_sql[:-2] + ")\n"

        merge_sql += "VALUES ("
        for field in fields:
            if field == timestamp_field:
                merge_sql += "CURRENT_TIMESTAMP, "
            else:
                merge_sql += f"source.{field.upper()}, "

        # Remove trailing comma
        merge_sql = merge_sql[:-2] + ")"

        # Prepare bind data
        bind_data = []
        for record in records:
            # Fill in any missing fields with None
            row_data = {}
            for field in fields:
                row_data[field] = record.get(field)

                # Handle JSON data
                if isinstance(row_data[field], dict | list):
                    row_data[field] = json.dumps(row_data[field])

            bind_data.append(row_data)

        return merge_sql, bind_data


class SQLAlchemySchemaMapper:
    """Mapeador de schema usando SQLAlchemy para garantir compatibilidade Oracle."""

    def __init__(self, oracle_schema: dict, logger: logging.Logger):
        """Inicializa o mapeador de schema.

        Args:
            oracle_schema: Schema Oracle descoberto
            logger: Logger para registrar operações
        """
        self.oracle_schema = oracle_schema
        self.logger = logger
        self.metadata = MetaData()
        self.oracle_table = None
        self.field_mapping = {}
        self.oracle_columns = {}

        self._build_oracle_table_definition()

    def _build_oracle_table_definition(self):
        """Constrói definição da tabela Oracle usando SQLAlchemy."""
        table_name = self.oracle_schema.get("table_name", "WMS_ORDER_HDR")
        columns = []

        # Mapear tipos Oracle para SQLAlchemy
        type_mapping = {
            'NUMBER': Integer,
            'VARCHAR2': String,
            'DATE': DateTime,
            'TIMESTAMP': DateTime,
            'FLOAT': Float,
            'DECIMAL': Float,
            'CHAR': String,
            'CLOB': String,
        }

        for column_info in self.oracle_schema.get("columns", []):
            column_name = column_info["name"]
            oracle_type = column_info.get("data_type", "VARCHAR2").upper()

            # Mapear tipo Oracle para SQLAlchemy
            if oracle_type in type_mapping:
                sqlalchemy_type = type_mapping[oracle_type]
                if oracle_type in {'VARCHAR2', 'CHAR'} and 'length' in column_info:
                    sqlalchemy_type = String(column_info['length'])
            else:
                sqlalchemy_type = String

            # Criar coluna
            column = Column(column_name, sqlalchemy_type)
            columns.append(column)

            # Armazenar informações da coluna
            self.oracle_columns[column_name.lower()] = {
                'name': column_name,
                'type': oracle_type,
                'sqlalchemy_type': sqlalchemy_type,
                'nullable': column_info.get('nullable', True),
                'length': column_info.get('length'),
                'precision': column_info.get('precision'),
                'scale': column_info.get('scale'),
            }

        # Criar tabela SQLAlchemy
        self.oracle_table = Table(table_name, self.metadata, *columns)

        self.logger.info(f"Tabela Oracle mapeada: {table_name} com {len(columns)} colunas")

    def map_wms_fields_to_oracle(self, wms_fields: dict) -> dict:
        """Mapeia campos WMS para campos Oracle existentes.

        Args:
            wms_fields: Dicionário com campos WMS

        Returns:
            Dicionário com campos mapeados para Oracle
        """
        mapped_fields = {}
        unmapped_fields = []

        for wms_field, wms_value in wms_fields.items():
            oracle_field = self._find_oracle_field_mapping(wms_field)

            if oracle_field:
                # Converter valor para tipo Oracle
                converted_value = self._convert_value_for_oracle(
                    wms_value, oracle_field, self.oracle_columns[oracle_field.lower()],
                )
                mapped_fields[oracle_field] = converted_value
                self.field_mapping[wms_field] = oracle_field
            else:
                unmapped_fields.append(wms_field)

        if unmapped_fields:
            self.logger.debug(f"Campos WMS não mapeados: {unmapped_fields}")

        self.logger.debug(f"Campos mapeados: {len(mapped_fields)} de {len(wms_fields)}")
        return mapped_fields

    def _find_oracle_field_mapping(self, wms_field: str) -> str | None:
        """Encontra mapeamento de campo WMS para Oracle.

        Args:
            wms_field: Nome do campo WMS

        Returns:
            Nome do campo Oracle ou None se não encontrado
        """
        wms_field_lower = wms_field.lower()

        # 1. Busca direta (case-insensitive)
        for oracle_field in self.oracle_columns:
            if oracle_field == wms_field_lower:
                return self.oracle_columns[oracle_field]['name']

        # 2. Busca com variações comuns
        variations = [
            wms_field_lower,
            wms_field_lower.replace("_", ""),
            wms_field_lower.replace("-", "_"),
            f"wms_{wms_field_lower}",
            f"{wms_field_lower}_id" if not wms_field_lower.endswith("_id") else wms_field_lower[:-3],
        ]

        for variation in variations:
            for oracle_field in self.oracle_columns:
                if oracle_field == variation:
                    return self.oracle_columns[oracle_field]['name']

        # 3. Busca por similaridade (contém)
        for oracle_field in self.oracle_columns:
            if wms_field_lower in oracle_field or oracle_field in wms_field_lower:
                return self.oracle_columns[oracle_field]['name']

        return None

    def _convert_value_for_oracle(self, value: Any, oracle_field: str, column_info: dict) -> Any:
        """Converte valor para tipo Oracle usando informações da coluna.

        Args:
            value: Valor a ser convertido
            oracle_field: Nome do campo Oracle
            column_info: Informações da coluna Oracle

        Returns:
            Valor convertido
        """
        if value is None:
            return None

        oracle_type = column_info['type']

        try:
            # Conversões por tipo Oracle
            if oracle_type in {'NUMBER', 'INTEGER', 'DECIMAL', 'FLOAT'}:
                if isinstance(value, str):
                    # CORREÇÃO: Verificar se campo ID contém texto (deve ser VARCHAR, não NUMBER)
                    if ('_id' in oracle_field.lower() or oracle_field.lower().endswith('id')) and not value.isdigit():
                        # Campo ID com texto deve ser tratado como string, não número
                        self.logger.debug(f"Campo ID '{oracle_field}' contém texto '{value}', tratando como string")
                        return str(value)

                    # Mapeamentos específicos por nome de campo
                    if 'status' in oracle_field.lower():
                        status_map = {'PENDING': 10, 'ACTIVE': 40, 'PROCESSING': 30, 'COMPLETED': 99, 'CANCELLED': 0}
                        return status_map.get(value.upper(), 10)
                    if 'priority' in oracle_field.lower():
                        priority_map = {'LOW': 1, 'NORMAL': 2, 'HIGH': 3, 'URGENT': 4}
                        return priority_map.get(value.upper(), 2)
                    if 'type' in oracle_field.lower():
                        type_map = {'STANDARD': 1, 'EXPRESS': 2, 'BULK': 3, 'SPECIAL': 4}
                        return type_map.get(value.upper(), 1)
                    # Tentar converter para número
                    try:
                        return float(value) if '.' in str(value) else int(value)
                    except ValueError:
                        # Se não conseguir converter para número, retornar como string
                        self.logger.debug(f"Não foi possível converter '{value}' para número, mantendo como string")
                        return str(value)
                return value

            if oracle_type in {'VARCHAR2', 'CHAR', 'CLOB'}:
                str_value = str(value)
                max_length = column_info.get('length')
                if max_length and len(str_value) > max_length:
                    str_value = str_value[:max_length]
                return str_value

            if oracle_type in {'DATE', 'TIMESTAMP'}:
                # CORREÇÃO: Converter strings de data para datetime objects
                if isinstance(value, str):
                    from datetime import datetime
                    try:
                        # Tentar diferentes formatos de data
                        if len(value) == 10 and '-' in value:  # YYYY-MM-DD
                            return datetime.strptime(value, '%Y-%m-%d')
                        if len(value) == 19 and ' ' in value:  # YYYY-MM-DD HH:MM:SS
                            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                        if len(value) == 16 and ' ' in value:  # YYYY-MM-DD HH:MM
                            return datetime.strptime(value, '%Y-%m-%d %H:%M')
                        # Tentar ISO format
                        return datetime.fromisoformat(value.replace('T', ' '))
                    except ValueError:
                        # Se não conseguir converter, usar data atual
                        self.logger.warning(f"Não foi possível converter data '{value}', usando data atual")
                        return datetime.now()
                elif isinstance(value, datetime):
                    return value
                else:
                    # Para outros tipos, usar data atual
                    from datetime import datetime
                    return datetime.now()

            else:
                return str(value)

        except (ValueError, TypeError) as e:
            self.logger.warning(f"Erro ao converter {oracle_field}='{value}': {e}")
            # Valor padrão por tipo
            if oracle_type in {'NUMBER', 'INTEGER', 'DECIMAL', 'FLOAT'}:
                return 0
            if oracle_type in {'DATE', 'TIMESTAMP'}:
                from datetime import datetime
                return datetime.now()
            return str(value)

    def generate_insert_statement(self, mapped_data: dict) -> str:
        """Gera statement INSERT usando SQLAlchemy.

        Args:
            mapped_data: Dados mapeados para Oracle

        Returns:
            Statement SQL INSERT
        """
        if not mapped_data:
            return None

        # Usar SQLAlchemy para gerar INSERT
        insert_stmt = self.oracle_table.insert().values(**mapped_data)

        # Compilar para Oracle dialect
        compiled = insert_stmt.compile(
            dialect=oracle.dialect(),
            compile_kwargs={"literal_binds": True},
        )

        return str(compiled)

    def get_oracle_field_info(self) -> dict:
        """Retorna informações dos campos Oracle.

        Returns:
            Dicionário com informações dos campos
        """
        return self.oracle_columns.copy()

    def generate_simple_insert_sql(self, mapped_data: dict) -> str:
        """Gera statement INSERT simples baseado no mapeamento SQLAlchemy.

        CORREÇÃO: Gera SQL manualmente para evitar problemas de compilação.

        Args:
            mapped_data: Dados mapeados para Oracle

        Returns:
            Statement SQL INSERT
        """
        if not mapped_data:
            return None

        table_name = self.oracle_schema.get("table_name", "WMS_ORDER_HDR")

        # Construir lista de campos e valores
        fields = []
        values = []

        for field_name, field_value in mapped_data.items():
            # Verificar se campo existe no Oracle
            if field_name.lower() in self.oracle_columns:
                oracle_column = self.oracle_columns[field_name.lower()]
                oracle_field_name = oracle_column['name']
                oracle_type = oracle_column['type']

                fields.append(f'"{oracle_field_name}"')

                # Formatar valor baseado no tipo Oracle
                if field_value is None:
                    values.append("NULL")
                elif oracle_type in {'NUMBER', 'INTEGER', 'DECIMAL', 'FLOAT'}:
                    if isinstance(field_value, int | float):
                        values.append(str(field_value))
                    else:
                        # Tentar converter para número
                        try:
                            num_value = float(field_value) if '.' in str(field_value) else int(field_value)
                            values.append(str(num_value))
                        except (ValueError, TypeError):
                            # Se não conseguir converter, usar NULL
                            values.append("NULL")
                elif oracle_type in {'VARCHAR2', 'CHAR', 'CLOB'}:
                    str_value = str(field_value).replace("'", "''")  # Escape aspas
                    values.append(f"'{str_value}'")
                elif oracle_type in {'DATE', 'TIMESTAMP'}:
                    if hasattr(field_value, 'strftime'):
                        # É um datetime object
                        date_str = field_value.strftime('%Y-%m-%d %H:%M:%S')
                        values.append(f"TO_DATE('{date_str}', 'YYYY-MM-DD HH24:MI:SS')")
                    else:
                        # Tentar como string
                        date_str = str(field_value)
                        if len(date_str) == 10:  # YYYY-MM-DD
                            values.append(f"TO_DATE('{date_str}', 'YYYY-MM-DD')")
                        else:
                            values.append(f"TO_DATE('{date_str}', 'YYYY-MM-DD HH24:MI:SS')")
                else:
                    # Outros tipos como string
                    str_value = str(field_value).replace("'", "''")
                    values.append(f"'{str_value}'")

        if not fields:
            return None

        # Construir SQL INSERT
        fields_str = ", ".join(fields)
        values_str = ", ".join(values)

        return f'INSERT INTO "{table_name}" ({fields_str}) VALUES ({values_str})'

    def _filter_valid_oracle_fields(self, data: list[dict]) -> list[dict]:
        """Filtra apenas campos que existem na tabela Oracle.

        MODIFICAÇÃO: Agora permite TODOS os campos, criando mapeamento dinâmico
        para garantir que todos os dados do WMS sejam armazenados no Oracle.

        Args:
            data: Lista de registros com todos os campos

        Returns:
            Lista de registros com TODOS os campos (sem filtrar)
        """
        if not data:
            return data

        # NOVA ABORDAGEM: NÃO filtrar campos, manter TODOS
        self.logger.info("=== MANTENDO TODOS OS CAMPOS SEM FILTRAR ===")

        sample_record = data[0]
        total_fields = len(sample_record)

        self.logger.info(f"Total de campos por registro: {total_fields}")
        self.logger.info(f"Campos disponíveis: {sorted(sample_record.keys())}")

        # Coletar campos Oracle existentes para referência (mas não filtrar)
        oracle_columns = {}
        for column in self.oracle_schema.get("columns", []):
            oracle_columns[column["name"].lower()] = column

        # Identificar quais campos existem no Oracle vs novos
        existing_fields = []
        new_fields = []

        for field in sample_record:
            if field.lower() in oracle_columns:
                existing_fields.append(field)
            else:
                new_fields.append(field)

        self.logger.info(f"Campos que existem no Oracle: {len(existing_fields)} - {sorted(existing_fields)}")
        self.logger.info(f"Campos novos (serão criados dinamicamente): {len(new_fields)} - {sorted(new_fields)}")

        # Processar e converter TODOS os registros (sem filtrar)
        processed_data = []
        for record in data:
            processed_record = {}

            for field, value in record.items():
                # Converter valor se temos informação da coluna Oracle
                if field.lower() in oracle_columns:
                    oracle_column = oracle_columns[field.lower()]
                    converted_value = self._convert_value_to_oracle_type(value, oracle_column)
                    processed_record[field] = converted_value

                    # Log conversão se houve mudança
                    if str(converted_value) != str(value):
                        self.logger.debug(f"Convertido {field}: '{value}' -> '{converted_value}' (tipo: {oracle_column.get('data_type')})")
                # Campo novo, manter valor original mas fazer conversões básicas
                elif isinstance(value, dict):
                    # Para FKs e objetos complexos, converter para JSON string
                    import json
                    processed_record[field] = json.dumps(value)
                    self.logger.debug(f"Campo novo {field}: convertido dict para JSON")
                elif isinstance(value, list):
                    # Para arrays, converter para JSON string
                    import json
                    processed_record[field] = json.dumps(value)
                    self.logger.debug(f"Campo novo {field}: convertido list para JSON")
                else:
                    # Manter valor original
                    processed_record[field] = value

            processed_data.append(processed_record)

        self.logger.info("=== PROCESSAMENTO COMPLETO ===")
        self.logger.info(f"Registros processados: {len(processed_data)}")
        self.logger.info(f"Campos por registro: {len(processed_data[0]) if processed_data else 0}")
        self.logger.info("TODOS os campos serão inseridos no Oracle (sem filtrar)")

        return processed_data

    def generate_merge_statements(self, data: list[dict], resource: str) -> list[str]:
        """Gera comandos MERGE SQL usando MergeStatementGenerator.

        MODIFICAÇÃO: Cria INSERT simples para todos os campos quando há muitos campos novos.

        Args:
            data: Lista de registros para processar
            resource: Nome do recurso (para configuração)

        Returns:
            Lista de comandos SQL (INSERT ou MERGE)
        """
        if not data:
            return []

        # CORREÇÃO: Não filtrar campos, usar todos
        processed_data = self._filter_valid_oracle_fields(data)

        if not processed_data:
            self.logger.warning("Nenhum registro válido após processamento")
            return []

        schema_config = self.config["schemas"].get(resource, {})
        table_name = schema_config.get("table", resource.upper())
        primary_keys = schema_config.get("primary_keys", ["id"])
        schema_name = self.config["oracle"].get("schema_name")

        self.logger.info(f"Gerando SQL para {len(processed_data)} registros em {table_name}")
        self.logger.info(f"Campos por registro: {len(processed_data[0]) if processed_data else 0}")

        # Coletar campos Oracle existentes
        oracle_columns = set()
        for column in self.oracle_schema.get("columns", []):
            oracle_columns.add(column["name"].lower())

        # Verificar quantos campos são novos
        sample_record = processed_data[0]
        existing_fields = [f for f in sample_record if f.lower() in oracle_columns]
        new_fields = [f for f in sample_record if f.lower() not in oracle_columns]

        self.logger.info(f"Campos existentes no Oracle: {len(existing_fields)}")
        self.logger.info(f"Campos novos: {len(new_fields)}")

        # Se há muitos campos novos, usar INSERT simples apenas com campos existentes
        if len(new_fields) > len(existing_fields):
            self.logger.info("Muitos campos novos detectados, usando INSERT simples com campos existentes")
            return self._generate_simple_insert_statements(processed_data, table_name, existing_fields, schema_name)
        self.logger.info("Usando MERGE tradicional")
        return self._generate_traditional_merge_statements(processed_data, resource, table_name, primary_keys, schema_name)

    def _generate_simple_insert_statements(self, data: list[dict], table_name: str, valid_fields: list[str], schema_name: str = None) -> list[str]:
        """Gera comandos INSERT simples apenas com campos válidos.

        Args:
            data: Lista de registros
            table_name: Nome da tabela
            valid_fields: Lista de campos válidos
            schema_name: Nome do schema

        Returns:
            Lista de comandos INSERT
        """
        if not data or not valid_fields:
            return []

        # Construir nome completo da tabela
        full_table_name = f'"{schema_name}"."{table_name.upper()}"' if schema_name else f'"{table_name.upper()}"'

        insert_statements = []

        for record in data:
            # Filtrar apenas campos válidos
            valid_record = {field: record.get(field) for field in valid_fields if field in record}

            if not valid_record:
                continue

            # Construir INSERT statement
            fields_list = list(valid_record.keys())
            fields_str = ", ".join([f'"{field.upper()}"' for field in fields_list])

            values_list = []
            for field in fields_list:
                value = valid_record[field]
                if value is None:
                    values_list.append("NULL")
                elif isinstance(value, str):
                    # CORREÇÃO: Verificar se é um campo de data para usar TO_DATE
                    if any(date_keyword in field.lower() for date_keyword in ['date', '_dt', '_ts']):
                        # Para campos de data, usar TO_DATE do Oracle
                        if len(value) == 10 and '-' in value:  # Formato YYYY-MM-DD
                            values_list.append(f"TO_DATE('{value}', 'YYYY-MM-DD')")
                        elif len(value) == 19 and ' ' in value:  # Formato YYYY-MM-DD HH:MM:SS
                            values_list.append(f"TO_DATE('{value}', 'YYYY-MM-DD HH24:MI:SS')")
                        else:
                            # Formato desconhecido, tentar como string
                            escaped_value = value.replace("'", "''")
                            values_list.append(f"'{escaped_value}'")
                    else:
                        # Campo string normal
                        escaped_value = value.replace("'", "''")
                        values_list.append(f"'{escaped_value}'")
                elif isinstance(value, bool):
                    values_list.append("1" if value else "0")
                elif isinstance(value, int | float):
                    values_list.append(str(value))
                else:
                    # Para outros tipos, converter para string
                    str_value = str(value).replace("'", "''")
                    values_list.append(f"'{str_value}'")

            values_str = ", ".join(values_list)

            insert_sql = f"INSERT INTO {full_table_name} ({fields_str}) VALUES ({values_str})"
            insert_statements.append(insert_sql)

        self.logger.info(f"Gerados {len(insert_statements)} comandos INSERT simples")
        return insert_statements

    def _generate_traditional_merge_statements(self, data: list[dict], resource: str, table_name: str, primary_keys: list[str], schema_name: str = None) -> list[str]:
        """Gera comandos MERGE tradicionais usando MergeStatementGenerator.

        Args:
            data: Lista de registros
            resource: Nome do recurso
            table_name: Nome da tabela
            primary_keys: Lista de chaves primárias
            schema_name: Nome do schema

        Returns:
            Lista de comandos MERGE
        """
        schema_config = self.config["schemas"].get(resource, {})
        track_fields = schema_config.get("track_fields", [])
        timestamp_field = schema_config.get("timestamp_field", "tk_insert_dt")
        batch_size = self.config["oracle"]["merge_batch_size"]

        merge_statements = []

        # Processar registros em lotes usando MergeStatementGenerator
        for i in range(0, len(data), batch_size):
            batch = data[i : i + batch_size]

            try:
                # Usar MergeStatementGenerator reutilizado
                merge_sql, bind_data = self.merge_generator.prepare_merge(
                    batch,
                    table_name,
                    primary_keys,
                    schema_name,
                    timestamp_field,
                    track_fields,
                )

                if merge_sql:
                    # Para cada registro no batch, criar statement individual
                    for record_data in bind_data:
                        # Substituir placeholders pelos valores reais
                        individual_sql = merge_sql
                        for field, value in record_data.items():
                            placeholder = f":{field}"
                            if value is None:
                                formatted_value = "NULL"
                            elif isinstance(value, str):
                                escaped_value = value.replace("'", "''")
                                formatted_value = f"'{escaped_value}'"
                            elif isinstance(value, bool):
                                formatted_value = "1" if value else "0"
                            elif isinstance(value, int | float):
                                formatted_value = str(value)
                            else:
                                json_value = json.dumps(value).replace("'", "''")
                                formatted_value = f"'{json_value}'"

                            individual_sql = individual_sql.replace(
                                placeholder, formatted_value,
                            )

                        merge_statements.append(individual_sql)

            except Exception as e:
                self.logger.exception(f"Erro ao gerar MERGE para batch {i // batch_size + 1}: {e}")
                continue

        self.logger.info(f"Gerados {len(merge_statements)} comandos MERGE tradicionais")
        return merge_statements

    def generate_insert_statements_with_sqlalchemy(self, data: list[dict], resource: str) -> list[str]:
        """Gera comandos INSERT usando SQLAlchemy para garantir compatibilidade Oracle.

        CORREÇÃO: Usa SQLAlchemy para gerar SQL correto e compatível.

        Args:
            data: Lista de registros para processar
            resource: Nome do recurso (para configuração)

        Returns:
            Lista de comandos INSERT SQL
        """
        if not data:
            return []

        if not self.sqlalchemy_mapper:
            self.logger.error("SQLAlchemySchemaMapper não inicializado")
            return []

        self.logger.info(f"Gerando INSERT statements SQLAlchemy para {len(data)} registros")

        insert_statements = []

        for i, record in enumerate(data):
            try:
                # CORREÇÃO: Usar método simples em vez de compilação SQLAlchemy
                insert_sql = self.sqlalchemy_mapper.generate_simple_insert_sql(record)

                if insert_sql:
                    insert_statements.append(insert_sql)

                    if i == 0:  # Log do primeiro statement para debug
                        self.logger.debug(f"Primeiro INSERT SQL: {insert_sql}")
                else:
                    self.logger.warning(f"Não foi possível gerar INSERT para registro {i + 1}")

            except Exception as e:
                self.logger.exception(f"Erro ao gerar INSERT para registro {i + 1}: {e}")
                continue

        self.logger.info(f"Gerados {len(insert_statements)} comandos INSERT SQLAlchemy")
        return insert_statements

    def run_incremental_pipeline(
        self, resource: str, days_back: int = 7, **query_params,
    ) -> None:
        """Executa pipeline incremental reutilizando bibliotecas existentes.

        Args:
            resource: Recurso WMS para extrair
            days_back: Número de dias para buscar para trás (não usado atualmente)
            **query_params: Parâmetros adicionais de query
        """
        try:
            self.logger.info(
                "=== Pipeline Incremental Avançado (Bibliotecas Reutilizadas) ===",
            )
            self.logger.info(f"Recurso: {resource}")

            # Inicializar clientes
            self.initialize_clients()

            # Obter configuração da tabela Oracle
            schema_config = self.config["schemas"].get(resource, {})
            oracle_table = schema_config.get("table", f"WMS_{resource.upper()}")

            # Descobrir e mapear schemas usando bibliotecas existentes
            if self.config["pipeline"]["discover_schemas"]:
                mapping_success = self.discover_and_map_schemas(resource, oracle_table)
                if not mapping_success:
                    self.logger.error("Falha na descoberta/mapeamento de schemas")
                    return

            # Extrair dados do WMS usando API nativa com mapeamento dinâmico
            if self.config["pipeline"]["extract_complete_dataset"]:
                self.logger.info("Usando extração completa com paginação automática")
                data = self.extract_from_wms(resource, **query_params)
            else:
                self.logger.info("Usando extração padrão com limite")
                data = self.extract_from_wms(resource, **query_params)

            self.logger.info(f"Total de registros coletados e mapeados: {len(data)}")

            if data:
                # CORREÇÃO: Gerar comandos INSERT usando SQLAlchemy
                insert_statements = self.generate_insert_statements_with_sqlalchemy(data, resource)

                # Executar INSERT no Oracle usando API nativa
                if insert_statements:
                    self.execute_merge_sql(insert_statements)
                else:
                    self.logger.warning("Nenhum INSERT statement foi gerado")
            else:
                self.logger.info("Nenhum dado encontrado para processar")

            self.logger.info("=== Pipeline Incremental Concluído ===")

        except Exception as e:
            self.logger.exception(f"Erro no pipeline incremental: {str(e)}")
            raise
        finally:
            self.cleanup()

    def cleanup(self) -> None:
        """Limpa recursos e fecha conexões."""
        try:
            if self.db_client:
                self.db_client.close()
                self.logger.info("DbClient fechado")

            # WmsClient não precisa de fechamento explícito
            if self.wms_client:
                self.logger.info("WmsClient finalizado")

        except Exception as e:
            self.logger.warning(f"Erro durante cleanup: {str(e)}")

    def _discover_additional_fields_from_data(
        self, records: list, resource: str,
    ) -> None:
        """Descobre campos adicionais analisando os dados reais.

        MELHORIA: Agora suporta descoberta abrangente de campos quando habilitada
        na configuração, processando mais registros para descobrir todos os campos.

        Args:
            records: Lista de registros do WMS
            resource: Nome do recurso
        """
        try:
            comprehensive_discovery = self.config["pipeline"]["comprehensive_field_discovery"]

            if comprehensive_discovery:
                self.logger.info(
                    f"Descoberta abrangente de campos habilitada - analisando {len(records)} registros...",
                )
            else:
                self.logger.debug(
                    "Verificando campos adicionais dos dados reais (complementar)...",
                )

            all_fields = set()

            # Analisar todos os registros para descobrir campos
            for i, record in enumerate(records):
                processed_record = self._process_wms_record(record, resource)
                if processed_record:
                    all_fields.update(processed_record.keys())

                # Log de progresso para descoberta abrangente
                if comprehensive_discovery and i > 0 and i % 100 == 0:
                    self.logger.debug(f"Descoberta: processados {i} registros, {len(all_fields)} campos únicos encontrados")

            # Comparar com campos já conhecidos
            known_fields = set(self.field_mapping.keys())
            new_fields = all_fields - known_fields

            if new_fields:
                discovery_type = "abrangente" if comprehensive_discovery else "complementar"
                self.logger.info(
                    f"Descobertos {len(new_fields)} campos adicionais ({discovery_type}): {sorted(new_fields)}",
                )

                # Adicionar novos campos ao mapeamento
                for field in new_fields:
                    oracle_field = field.lower()
                    self.field_mapping[field] = oracle_field
                    self.logger.debug(
                        f"  Novo campo mapeado ({discovery_type}): {field} -> {oracle_field}",
                    )

                # Atualizar schema WMS também
                if "fields" not in self.wms_schema:
                    self.wms_schema["fields"] = {}

                for field in new_fields:
                    self.wms_schema["fields"][field] = {
                        "type": f"discovered_from_data_{discovery_type}",
                        "source": f"real_data_{discovery_type}",
                    }
            else:
                discovery_type = "abrangente" if comprehensive_discovery else "complementar"
                self.logger.debug(f"Nenhum campo adicional {discovery_type} descoberto")

            self.logger.info(
                f"Total de campos após descoberta: {len(self.field_mapping)} (analisados {len(records)} registros)",
            )

        except Exception as e:
            self.logger.warning(f"Erro na descoberta complementar de campos: {e}")


class WmsToOracleAdvancedPipeline:
    """Pipeline avançado para sincronização WMS-Oracle reutilizando bibliotecas existentes.

    Implementa funcionalidades avançadas de sincronização reutilizando:
    - UniversalSchemaConverter do WMS para conversão de schemas
    - SchemaExtractor e SchemaManager do Oracle DB
    - Funcionalidade MERGE dos loaders Meltano
    - ModelRegistry para gerenciamento de modelos
    """

    def __init__(self, config_file: str | None = None):
        """Inicializa o pipeline avançado.

        Args:
            config_file: Caminho para arquivo de configuração
        """
        self.setup_logging()
        self.config = self.load_config(config_file)

        # Inicializar clientes das APIs nativas
        self.wms_client: WmsClient | None = None
        self.db_client: DbClient | None = None

        # Inicializar componentes reutilizados das bibliotecas
        self.schema_converter: UniversalSchemaConverter | None = None
        self.schema_extractor: SchemaExtractor | None = None
        self.schema_manager: SchemaManager | None = None
        self.merge_generator = MergeStatementGenerator(self.logger)
        self.sqlalchemy_mapper: SQLAlchemySchemaMapper | None = None

        # Schemas descobertos
        self.wms_schema: dict[str, Any] = {}
        self.oracle_schema: dict[str, Any] = {}
        self.field_mapping: dict[str, str] = {}

        self.logger.info(
            "Pipeline avançado iniciado reutilizando bibliotecas existentes",
        )

    def setup_logging(self) -> None:
        """Configura logging avançado."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(
                    f"advanced_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
                ),
            ],
        )
        self.logger = logging.getLogger("AdvancedPipeline")

    def load_config(self, config_file: str | None) -> dict[str, Any]:
        """Carrega configuração avançada."""
        default_config = {
            "wms": {
                "timeout": 600,
                "max_retries": 3,
                "batch_size_days": 1,
                "debug_mode": False,
                # CONFIGURAÇÕES PARA EXTRAÇÃO COMPLETA
                "extract_all_data": True,  # Extrair todos os dados disponíveis
                "max_records_per_request": 10000,  # Máximo por requisição
                "discovery_sample_size": 100,  # Registros para descoberta de campos
                "enable_pagination": True,  # Habilitar paginação automática
                "pagination_size": 5000,  # Tamanho da página para paginação
            },
            "oracle": {
                "timeout": 900,
                "batch_size": 1000,
                "merge_batch_size": 500,
                "use_pool": True,
                "schema_name": None,
            },
            "pipeline": {
                "validate_data": True,
                "use_merge": True,
                "track_changes": True,
                "discover_schemas": True,
                "map_fields_dynamically": True,
                # CONFIGURAÇÕES PARA EXTRAÇÃO COMPLETA
                "extract_complete_dataset": True,  # Extrair dataset completo
                "comprehensive_field_discovery": True,  # Descoberta abrangente de campos
                "process_all_available_fields": True,  # Processar todos os campos disponíveis
            },
            "schemas": {
                "order_hdr": {
                    "table": "WMS_ORDER_HDR",
                    "primary_keys": ["id"],
                    "date_field": "order_date",
                    "track_fields": [
                        "status_id",
                        "customer_id",
                        "total_amount",
                        "order_type",
                    ],
                    "timestamp_field": "tk_insert_dt",
                },
            },
        }

        if config_file and Path(config_file).exists():
            with open(config_file, encoding="utf-8") as f:
                if config_file.endswith((".yaml", ".yml")):
                    user_config = yaml.safe_load(f)
                else:
                    user_config = json.load(f)
            default_config.update(user_config)

        return default_config

    def initialize_clients(self) -> None:
        """Inicializa os clientes WMS e Oracle usando as APIs nativas."""
        try:
            # Carregar variáveis de ambiente dos projetos
            from dotenv import load_dotenv

            # Carregar .env do projeto WMS
            wms_env_path = Path(__file__).parent / "dc-oracle-wms" / ".env"
            if wms_env_path.exists():
                load_dotenv(wms_env_path)
                self.logger.info(f"Carregadas variáveis WMS de {wms_env_path}")

            # Carregar .env do projeto Oracle DB
            db_env_path = Path(__file__).parent / "dc-oracle-db" / ".env"
            if db_env_path.exists():
                load_dotenv(db_env_path)
                self.logger.info(f"Carregadas variáveis DB de {db_env_path}")

            # Inicializar WmsClient usando configuração do ambiente
            self.logger.info("Inicializando WmsClient...")
            self.wms_client = WmsClient(
                debug_mode=self.config["wms"]["debug_mode"],
            )
            self.logger.info("WmsClient inicializado com sucesso")

            # Inicializar DbClient usando configuração do ambiente
            self.logger.info("Inicializando DbClient...")
            self.db_client = DbClient(
                use_pool=self.config["oracle"]["use_pool"],
            )
            self.logger.info("DbClient inicializado com sucesso")

            # Inicializar componentes das bibliotecas
            self.schema_converter = UniversalSchemaConverter()

            # SchemaExtractor e SchemaManager serão inicializados quando necessário
            # pois precisam de uma conexão ativa

        except WmsConnectionError as e:
            raise AdvancedPipelineError(f"Erro ao conectar no WMS: {e}")
        except DbConnectionError as e:
            raise AdvancedPipelineError(f"Erro ao conectar no Oracle: {e}")
        except Exception as e:
            raise AdvancedPipelineError(f"Erro ao inicializar clientes: {e}")

    def discover_and_map_schemas(self, wms_entity: str, oracle_table: str) -> bool:
        """Descobre schemas e cria mapeamento usando bibliotecas existentes.

        CORREÇÃO: Usa SchemaManager das bibliotecas WMS para carregar schema completo.

        Args:
            wms_entity: Nome da entidade WMS
            oracle_table: Nome da tabela Oracle

        Returns:
            True se mapeamento foi criado com sucesso
        """
        self.logger.info("=== Descoberta e Mapeamento de Schemas (SchemaManager WMS) ===")

        try:
            # ETAPA 1: Usar SchemaManager das bibliotecas WMS para carregar schema completo
            self.logger.info(f"ETAPA 1: Carregando schema completo WMS para entidade: {wms_entity}")

            # Importar SchemaManager das bibliotecas WMS
            from wms.schema import SchemaManager

            # Inicializar SchemaManager com cliente WMS
            wms_schema_manager = SchemaManager(
                client=self.wms_client,
                base_path=str(Path(__file__).parent / "dc-oracle-wms"),
                schema_dir=str(Path(__file__).parent / "dc-oracle-wms" / "schemas"),
            )

            # Carregar schema completo usando SchemaManager
            try:
                complete_schema = wms_schema_manager.get_schema(wms_entity, refresh=False, ignore_errors=False)
                self.wms_schema = complete_schema

                # Extrair campos do schema completo
                wms_fields_from_schema = complete_schema.get('fields', {})
                wms_parameters = complete_schema.get('parameters', [])

                self.logger.info(f"Schema WMS completo carregado: {len(wms_fields_from_schema)} campos, {len(wms_parameters)} parâmetros")

                # Log detalhado dos primeiros campos
                field_names = list(wms_fields_from_schema.keys())
                self.logger.info(f"Primeiros 10 campos: {field_names[:10]}")
                self.logger.info(f"Últimos 10 campos: {field_names[-10:]}")

            except Exception as e:
                self.logger.warning(f"Erro ao carregar schema via SchemaManager: {e}")
                # Fallback para método anterior
                self.logger.info("Usando fallback para método anterior...")
                response = self.wms_client.describe(wms_entity)
                if response.success:
                    self.wms_schema = response.data
                    wms_fields_from_schema = self.wms_schema.get('fields', {})
                    wms_parameters = self.wms_schema.get('parameters', [])
                else:
                    self.logger.exception(f"Fallback também falhou: {response.error}")
                    return False

            # ETAPA 2: Descobrir campos adicionais através de dados reais (complementar)
            self.logger.info("ETAPA 2: Descobrindo campos adicionais via dados reais (complementar)")
            wms_fields_from_data = {}

            try:
                # MELHORIA: Usar configuração para tamanho da amostra de descoberta
                discovery_sample_size = self.config["wms"]["discovery_sample_size"]
                self.logger.info(f"Usando {discovery_sample_size} registros para descoberta abrangente de campos")

                # Buscar mais registros para descobrir campos que possam não estar no schema
                sample_response = self.wms_client.search(
                    entity_name=wms_entity,
                    params={"limit": discovery_sample_size},  # Usar configuração em vez de valor fixo
                )

                if sample_response.success:
                    sample_data = sample_response.data
                    if isinstance(sample_data, dict):
                        if "results" in sample_data:
                            sample_records = sample_data["results"]
                        elif "items" in sample_data:
                            sample_records = sample_data["items"]
                        else:
                            sample_records = [sample_data] if sample_data else []
                    elif isinstance(sample_data, list):
                        sample_records = sample_data
                    else:
                        sample_records = []

                    self.logger.info(f"Obtidos {len(sample_records)} registros para descoberta complementar")

                    # Analisar registros para descobrir campos adicionais
                    all_discovered_fields = set()
                    for record in sample_records:
                        processed_record = self._process_wms_record(record, wms_entity)
                        if processed_record:
                            all_discovered_fields.update(processed_record.keys())

                    # Criar dicionário de campos descobertos dos dados (apenas os novos)
                    schema_fields = set(wms_fields_from_schema.keys())
                    new_fields_from_data = all_discovered_fields - schema_fields

                    for field in new_fields_from_data:
                        wms_fields_from_data[field] = {"type": "discovered_from_data", "source": "real_data"}

                    self.logger.info(f"Campos adicionais descobertos dos dados: {len(wms_fields_from_data)}")
                    if wms_fields_from_data:
                        self.logger.info(f"Novos campos: {sorted(wms_fields_from_data.keys())}")

                else:
                    self.logger.warning(f"Erro ao buscar dados para descoberta complementar: {sample_response.error}")

            except Exception as e:
                self.logger.warning(f"Erro na descoberta complementar via dados reais: {e}")

            # ETAPA 3: Combinar campos do schema completo + dados reais
            self.logger.info(f"ETAPA 3: Combinando campos do schema ({len(wms_fields_from_schema)}) + dados reais ({len(wms_fields_from_data)})")

            # Combinar campos, priorizando schema quando disponível
            combined_wms_fields = {}
            combined_wms_fields.update(wms_fields_from_data)  # Primeiro os dados reais
            combined_wms_fields.update(wms_fields_from_schema)  # Depois schema (sobrescreve)

            # Atualizar schema WMS com campos combinados
            self.wms_schema["fields"] = combined_wms_fields
            wms_fields = combined_wms_fields

            self.logger.info(f"TOTAL de campos WMS descobertos: {len(wms_fields)} campos")

            # Log estatísticas dos campos
            required_fields = sum(1 for field_info in wms_fields.values()
                                if isinstance(field_info, dict) and field_info.get('required', False))
            self.logger.info(f"Campos obrigatórios: {required_fields}")
            self.logger.info(f"Campos opcionais: {len(wms_fields) - required_fields}")

            # ETAPA 4: Descobrir schema Oracle usando SchemaExtractor
            self.logger.info(f"ETAPA 4: Descobrindo schema Oracle para tabela: {oracle_table}")

            with self.db_client.get_connection() as conn:
                # Inicializar SchemaExtractor com conexão
                self.schema_extractor = SchemaExtractor(conn)
                self.schema_manager = SchemaManager(conn)

                try:
                    # Extrair schema da tabela Oracle
                    table_schema = self.schema_extractor.extract_table_schema(oracle_table)
                    self.oracle_schema = table_schema.to_dict()

                    self.logger.info(f"Schema Oracle descoberto: {len(self.oracle_schema.get('columns', []))} colunas")

                except Exception as e:
                    self.logger.warning(f"Tabela {oracle_table} não existe ou erro ao extrair schema: {e}")
                    # Criar schema básico para tabela inexistente
                    self.oracle_schema = {
                        "table_name": oracle_table,
                        "columns": [],
                        "primary_keys": [],
                        "discovered": False,
                        "error": str(e),
                    }

            # ETAPA 5: Criar mapeamento usando SQLAlchemySchemaMapper
            self.logger.info("ETAPA 5: Criando mapeamento usando SQLAlchemySchemaMapper")

            # CORREÇÃO: Usar SQLAlchemySchemaMapper para mapeamento correto
            self.sqlalchemy_mapper = SQLAlchemySchemaMapper(self.oracle_schema, self.logger)

            # Criar metadata para conversão (manter compatibilidade)
            metadata = SchemaMetadata(
                name=wms_entity,
                type="entity",
                system_type="api",
                system_name="oracle-wms",
            )

            # Converter schema WMS para formato universal (manter compatibilidade)
            self.schema_converter.convert_oracle_wms_schema(
                self.wms_schema, metadata,
            )

            # MAPEAMENTO: Usar SQLAlchemy para mapeamento correto
            oracle_field_info = self.sqlalchemy_mapper.get_oracle_field_info()

            self.logger.info(f"Criando mapeamento SQLAlchemy para {len(oracle_field_info)} campos Oracle")

            self.logger.info("=== RESUMO DA DESCOBERTA COMPLETA ===")
            self.logger.info(f"Campos WMS (schema completo): {len(wms_fields_from_schema)}")
            self.logger.info(f"Campos WMS (dados reais complementares): {len(wms_fields_from_data)}")
            self.logger.info(f"Total campos WMS: {len(wms_fields)}")
            self.logger.info(f"Campos Oracle disponíveis: {len(oracle_field_info)}")
            self.logger.info("SQLAlchemy mapper inicializado com sucesso")

            # CORREÇÃO: Não verificar field_mapping aqui, pois será criado dinamicamente
            self.logger.info("Mapeamento SQLAlchemy pronto para uso dinâmico")
            return True

        except Exception as e:
            self.logger.exception(f"Erro na descoberta e mapeamento de schemas: {e}")
            return False

    def extract_from_wms(
        self, resource: str, limit: int = None, **query_params,
    ) -> list[dict]:
        """Extrai dados do WMS usando a API nativa com mapeamento dinâmico.

        CORREÇÃO: Usar query_entity com filtro de data para evitar erro "Entrada invalida"

        Args:
            resource: Nome do recurso WMS
            limit: Limite de registros (None = usar configuração padrão)
            **query_params: Parâmetros adicionais de query

        Returns:
            Lista de registros extraídos e mapeados do WMS
        """
        if not self.wms_client:
            raise AdvancedPipelineError("WmsClient não inicializado")

        # MELHORIA: Usar configuração para limite padrão se não especificado
        if limit is None:
            limit = self.config["wms"]["max_records_per_request"]

        self.logger.info(f"Extraindo dados de {resource} do WMS (limite: {limit})")

        try:
            # CORREÇÃO: Usar apenas search simples sem filtros avançados
            # Os filtros avançados estão causando "Entrada invalida"
            self.logger.info("Usando search simples sem filtros avançados (evitando 'Entrada invalida')")

            simple_params = {"limit": limit}
            simple_params.update(query_params)

            response = self.wms_client.search(
                entity_name=resource,
                params=simple_params,
            )

            if not response.success:
                self.logger.warning(f"Erro na busca WMS: {response.error}")
                return []

            # Extrair dados da resposta
            data = response.data
            if isinstance(data, dict):
                if "results" in data:
                    page_records = data["results"]
                elif "items" in data:
                    page_records = data["items"]
                else:
                    page_records = [data] if data else []
            elif isinstance(data, list):
                page_records = data
            else:
                page_records = []

            # Verificar se há dados na página
            if not page_records:
                self.logger.info("Página vazia, finalizando extração")
                return []

            page_count = len(page_records)
            self.logger.info(f"Página: {page_count} registros extraídos")

            # DESCOBERTA DINÂMICA: Descobrir campos adicionais dos dados reais (incluindo FKs)
            self._discover_additional_fields_from_data(page_records, resource)

            # Processar e mapear registros da página
            processed_page_records = []
            for record in page_records:
                mapped_record = self._map_wms_record_to_oracle(record, resource)
                if mapped_record:
                    processed_page_records.append(mapped_record)

            self.logger.info(f"Página processada: {len(processed_page_records)} registros mapeados")

            return processed_page_records

        except Exception as e:
            self.logger.exception(f"Erro inesperado durante extração de {resource}: {e}")
            return []

    def _map_wms_record_to_oracle(self, record: Any, resource: str) -> dict | None:
        """Mapeia um registro WMS para formato Oracle usando SQLAlchemySchemaMapper.

        CORREÇÃO: Usa SQLAlchemySchemaMapper para mapeamento correto de campos.

        Args:
            record: Registro do WMS
            resource: Nome do recurso

        Returns:
            Dicionário com campos mapeados para Oracle ou None se não conseguir processar
        """
        try:
            # Processar registro WMS para dict
            wms_data = self._process_wms_record(record, resource)
            if not wms_data:
                return None

            # CORREÇÃO: Usar SQLAlchemySchemaMapper para mapeamento correto
            if not self.sqlalchemy_mapper:
                self.logger.error("SQLAlchemySchemaMapper não inicializado")
                return None

            # Mapear campos WMS para Oracle usando SQLAlchemy
            oracle_data = self.sqlalchemy_mapper.map_wms_fields_to_oracle(wms_data)

            if not oracle_data:
                self.logger.warning("Nenhum campo WMS foi mapeado para Oracle")
                return None

            self.logger.debug(f"Registro mapeado: {len(wms_data)} campos WMS -> {len(oracle_data)} campos Oracle")

            # Log dos campos mapeados
            for wms_field, oracle_field in self.sqlalchemy_mapper.field_mapping.items():
                if oracle_field in oracle_data:
                    self.logger.debug(f"  {wms_field} -> {oracle_field} = {oracle_data[oracle_field]}")

            return oracle_data

        except Exception as e:
            self.logger.warning(f"Erro ao mapear registro WMS usando SQLAlchemy: {e}")
            return None

    def _process_wms_record(self, record: Any, resource: str) -> dict | None:
        """Processa um registro do WMS para padronizar formato.

        CORREÇÃO: Usa model_dump() ou dict() para obter TODOS os campos (127 campos)
        em vez de __dict__ que retorna apenas 7 campos.

        MELHORIA: Processa corretamente as FKs (foreign keys) que vêm no formato
        {id: valor, key: valor, url: valor}, extraindo id e key para o Oracle.

        Args:
            record: Registro do WMS
            resource: Nome do recurso

        Returns:
            Dicionário com campos processados ou None se não conseguir processar
        """
        try:
            # CORREÇÃO: Usar model_dump() ou dict() para obter TODOS os campos
            if hasattr(record, 'model_dump'):
                # Pydantic v2 - retorna TODOS os 127 campos
                fields = record.model_dump()
                self.logger.debug(f"Usando model_dump(): {len(fields)} campos extraídos")
            elif hasattr(record, 'dict'):
                # Pydantic v1 - retorna TODOS os 127 campos
                fields = record.dict()
                self.logger.debug(f"Usando dict(): {len(fields)} campos extraídos")
            elif isinstance(record, str):
                # Se é string, tentar processar como "order_hdr(id=2, status_id=99)"
                fields = self._parse_wms_result_string(record, resource)
            elif isinstance(record, dict):
                fields = dict(record)
            elif hasattr(record, "__dict__"):
                # FALLBACK: usar __dict__ apenas se não tiver model_dump/dict
                fields = dict(record.__dict__)
                self.logger.warning(f"Usando __dict__ como fallback: apenas {len(fields)} campos")
            else:
                self.logger.warning(f"Tipo de registro não suportado: {type(record)}")
                return None

            if not fields:
                return None

            self.logger.info(f"TOTAL de campos extraídos do WMS: {len(fields)} campos")

            # NOVA FUNCIONALIDADE: Processar FKs (foreign keys) corretamente
            processed_fields = {}

            for field_name, field_value in fields.items():
                # Verificar se é uma FK no formato {id: valor, key: valor, url: valor}
                if isinstance(field_value, dict) and any(key in field_value for key in ['id', 'key', 'url']):
                    self.logger.debug(f"Processando FK {field_name}: {field_value}")

                    # Extrair id e key da FK
                    fk_id = field_value.get('id')
                    fk_key = field_value.get('key')

                    # Adicionar campos separados para id e key
                    if fk_id is not None:
                        processed_fields[f"{field_name}_id"] = fk_id
                        self.logger.debug(f"  Extraído {field_name}_id: {fk_id}")

                    if fk_key is not None:
                        processed_fields[f"{field_name}_key"] = fk_key
                        self.logger.debug(f"  Extraído {field_name}_key: {fk_key}")

                    # Manter o campo original também (para compatibilidade)
                    processed_fields[field_name] = field_value

                else:
                    # Campo normal, manter como está
                    processed_fields[field_name] = field_value

            # Usar os campos processados
            fields = processed_fields

            # MELHORIA: Enriquecer dados com campos padrão mais completos
            current_time = datetime.now()

            # Campos de auditoria padrão (apenas se não existirem)
            if "created_date" not in fields:
                fields["created_date"] = current_time.strftime("%Y-%m-%d %H:%M:%S")
            if "updated_date" not in fields:
                fields["updated_date"] = current_time.strftime("%Y-%m-%d %H:%M:%S")
            if "created_by" not in fields:
                fields["created_by"] = "WMS_INTEGRATION"
            if "updated_by" not in fields:
                fields["updated_by"] = "WMS_INTEGRATION"

            # Campos específicos do ORDER_HDR com mais detalhes (apenas se não existirem)
            if resource == "order_hdr":
                record_id = fields.get("id", 0)

                # CORREÇÃO: Adicionar campos obrigatórios que estão faltando no Oracle (apenas se não existirem)
                if "facility_id" not in fields and "facility_id_id" not in fields:
                    fields["facility_id"] = 1  # Valor padrão obrigatório
                if "order_nbr" not in fields:
                    fields["order_nbr"] = f"ORD{record_id:08d}"
                if "order_type" not in fields:
                    fields["order_type"] = "STANDARD"
                if "ord_date" not in fields:
                    fields["ord_date"] = current_time.strftime("%Y-%m-%d")
                if "orig_sale_price" not in fields:
                    fields["orig_sale_price"] = 100.0  # Valor padrão obrigatório

                # Campos de empresa (obrigatórios no Oracle) (apenas se não existirem)
                if "company_id" not in fields and "company_id_id" not in fields:
                    fields["company_id"] = "001"  # Valor padrão
                if "company_code" not in fields:
                    fields["company_code"] = "MAIN"

                # Campos de sistema (apenas se não existirem)
                if "source_system" not in fields:
                    fields["source_system"] = "WMS"
                if "integration_id" not in fields:
                    fields["integration_id"] = (
                        f"INT_{current_time.strftime('%Y%m%d_%H%M%S')}_{record_id}"
                    )

            self.logger.info(
                f"Registro processado com {len(fields)} campos para {resource} (incluindo FKs processadas)",
            )

            # Log dos primeiros 10 campos para debug
            field_names = list(fields.keys())
            self.logger.debug(f"Primeiros 10 campos: {field_names[:10]}")
            self.logger.debug(f"Últimos 10 campos: {field_names[-10:]}")

            return fields

        except Exception as e:
            self.logger.warning(f"Erro ao processar registro WMS: {e}")
            return None

    def _parse_wms_result_string(
        self, result_string: str, resource: str,
    ) -> dict | None:
        """Processa string de resultado do WMS para extrair campos.

        Args:
            result_string: String como "order_hdr(id=2, status_id=99)"
            resource: Nome do recurso

        Returns:
            Dicionário com campos extraídos ou None se não conseguir processar
        """
        try:
            # Extrair conteúdo entre parênteses
            if "(" in result_string and ")" in result_string:
                content = result_string.split("(")[1].split(")")[0]

                # Processar pares chave=valor
                fields = {}
                for pair in content.split(", "):
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        key = key.strip()
                        value = value.strip()

                        # Tentar converter para número se possível
                        try:
                            if "." in value:
                                fields[key] = float(value)
                            else:
                                fields[key] = int(value)
                        except ValueError:
                            # Remover aspas se existirem
                            if value.startswith('"') and value.endswith('"') or value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                            fields[key] = value

                self.logger.debug(f"Campos extraídos da string: {fields}")
                return fields

        except Exception as e:
            self.logger.warning(f"Erro ao processar string WMS '{result_string}': {e}")

        return None

    def execute_merge_sql(self, merge_statements: list[str]) -> None:
        """Executa comandos MERGE no Oracle usando a API nativa.

        Args:
            merge_statements: Lista de comandos MERGE SQL
        """
        if not self.db_client:
            raise AdvancedPipelineError("DbClient não inicializado")

        if not merge_statements:
            self.logger.info("Nenhum comando MERGE para executar")
            return

        self.logger.info(f"Executando {len(merge_statements)} comandos MERGE no Oracle")

        try:
            # Executar comandos em transação
            with self.db_client.transaction():
                for i, merge_sql in enumerate(merge_statements):
                    try:
                        affected_rows = self.db_client.execute(merge_sql, commit=False)
                        self.logger.debug(
                            f"MERGE {i + 1}/{len(merge_statements)}: {affected_rows} linhas afetadas",
                        )
                    except DbError as e:
                        self.logger.exception(f"Erro no MERGE {i + 1}: {e}")
                        raise

                self.logger.info(
                    f"Todos os {len(merge_statements)} comandos MERGE executados com sucesso",
                )

        except DbError as e:
            raise AdvancedPipelineError(f"Erro ao executar MERGE no Oracle: {e}")
        except Exception as e:
            raise AdvancedPipelineError(f"Erro inesperado no MERGE: {e}")

    def _convert_value_to_oracle_type(self, value: Any, oracle_column: dict) -> Any:
        """Converte valor para o tipo esperado pelo Oracle.

        Args:
            value: Valor a ser convertido
            oracle_column: Informações da coluna Oracle

        Returns:
            Valor convertido para o tipo Oracle
        """
        if value is None:
            return None

        oracle_type = oracle_column.get('data_type', '').upper()
        column_name = oracle_column.get('name', '').upper()

        try:
            # Conversões numéricas
            if oracle_type in {'NUMBER', 'INTEGER', 'DECIMAL', 'NUMERIC'}:
                if isinstance(value, str):
                    # Mapeamentos específicos por nome de coluna
                    if 'PRIORITY' in column_name:
                        priority_map = {'LOW': 1, 'NORMAL': 2, 'HIGH': 3, 'URGENT': 4}
                        return priority_map.get(value.upper(), 2)
                    if 'STATUS' in column_name:
                        status_map = {'PENDING': 10, 'ACTIVE': 40, 'PROCESSING': 30, 'COMPLETED': 99, 'CANCELLED': 0}
                        return status_map.get(value.upper(), 10)
                    if 'ORDER_TYPE' in column_name or 'TYPE' in column_name:
                        # Mapeamento para ORDER_TYPE_ID
                        order_type_map = {
                            'STANDARD': 1,
                            'EXPRESS': 2,
                            'BULK': 3,
                            'SPECIAL': 4,
                            'URGENT': 5,
                            'NORMAL': 1,
                        }
                        return order_type_map.get(value.upper(), 1)
                    if 'COMPANY' in column_name:
                        # Converter company_id string para número
                        if value.isdigit():
                            return int(value)
                        # Mapear códigos de empresa para números
                        company_map = {'001': 1, 'MAIN': 1, 'DEFAULT': 1}
                        return company_map.get(value.upper(), 1)
                    # Tentar converter string para número genérico
                    if '.' in str(value):
                        return float(value)
                    return int(value)
                return value

            # Conversões de string
            if oracle_type in {'VARCHAR2', 'VARCHAR', 'CHAR', 'NVARCHAR2', 'NCHAR', 'CLOB'}:
                return str(value)

            # Conversões de data
            if oracle_type in {'DATE', 'TIMESTAMP'}:
                if isinstance(value, str):
                    return value  # Assumir que já está no formato correto
                return str(value)

            # Outros tipos
            return value

        except (ValueError, TypeError) as e:
            self.logger.warning(f"Erro ao converter valor '{value}' para tipo Oracle '{oracle_type}' (coluna: {column_name}): {e}")
            # Retornar valor padrão baseado no tipo
            if oracle_type in {'NUMBER', 'INTEGER', 'DECIMAL', 'NUMERIC'}:
                return 0
            if oracle_type in {'VARCHAR2', 'VARCHAR', 'CHAR', 'NVARCHAR2', 'NCHAR', 'CLOB'}:
                return str(value)
            return value


def main():
    """Função principal do pipeline avançado."""
    parser = argparse.ArgumentParser(
        description="Pipeline Avançado WMS para Oracle reutilizando bibliotecas existentes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

    # Pipeline incremental básico com descoberta automática - ORDER_HDR
    python wms_to_oracle_pipeline_advanced.py --resource order_hdr

    # EXTRAÇÃO COMPLETA - extrair TODOS os dados disponíveis
    python wms_to_oracle_pipeline_advanced.py --resource order_hdr --extract-all

    # Extração completa com paginação customizada
    python wms_to_oracle_pipeline_advanced.py --resource order_hdr --extract-all --pagination-size 10000

    # Extração completa sem paginação (uma única requisição grande)
    python wms_to_oracle_pipeline_advanced.py --resource order_hdr --extract-all --no-pagination --max-records 50000

    # Com limite de registros (modo tradicional)
    python wms_to_oracle_pipeline_advanced.py --resource order_hdr --limit 100

    # Com campos específicos
    python wms_to_oracle_pipeline_advanced.py --resource order_hdr --fields "order_id,order_date,status,customer_id"

    # Com configuração customizada
    python wms_to_oracle_pipeline_advanced.py --config advanced_config.json --resource order_hdr --extract-all

    # Modo verbose para debugging
    python wms_to_oracle_pipeline_advanced.py --resource order_hdr --extract-all --verbose
        """,
    )

    parser.add_argument("--config", help="Arquivo de configuração (JSON/YAML)")
    parser.add_argument("--resource", required=True, help="Recurso WMS para extrair")
    parser.add_argument(
        "--days-back",
        type=int,
        default=7,
        help="Número de dias para buscar para trás (default: 7)",
    )
    parser.add_argument("--limit", type=int, help="Limite de registros")
    parser.add_argument("--fields", help="Campos específicos para extrair")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Logging detalhado",
    )
    parser.add_argument(
        "--extract-all",
        action="store_true",
        help="Extrair TODOS os dados disponíveis (ignora limites)",
    )
    parser.add_argument(
        "--no-pagination",
        action="store_true",
        help="Desabilitar paginação automática",
    )
    parser.add_argument(
        "--pagination-size",
        type=int,
        help="Tamanho da página para paginação (padrão: 5000)",
    )
    parser.add_argument(
        "--max-records",
        type=int,
        help="Máximo de registros a extrair (padrão: 10000)",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Criar pipeline avançado
        pipeline = WmsToOracleAdvancedPipeline(args.config)

        # MELHORIA: Aplicar configurações de linha de comando para extração completa
        if args.extract_all:
            pipeline.config["wms"]["extract_all_data"] = True
            pipeline.config["pipeline"]["extract_complete_dataset"] = True
            pipeline.config["pipeline"]["comprehensive_field_discovery"] = True
            print("🚀 Modo de extração completa ativado - extraindo TODOS os dados disponíveis")

        if args.no_pagination:
            pipeline.config["wms"]["enable_pagination"] = False
            print("⚠️ Paginação desabilitada - limitado a uma única requisição")

        if args.pagination_size:
            pipeline.config["wms"]["pagination_size"] = args.pagination_size
            print(f"📄 Tamanho da página configurado para: {args.pagination_size}")

        if args.max_records:
            pipeline.config["wms"]["max_records_per_request"] = args.max_records
            print(f"🔢 Máximo de registros configurado para: {args.max_records}")

        # Preparar parâmetros de query
        query_params = {}
        if args.limit and not args.extract_all:
            query_params["limit"] = args.limit
            print(f"📊 Limite manual aplicado: {args.limit} registros")
        elif args.extract_all:
            print("♾️ Sem limite - extraindo todos os dados disponíveis")

        if args.fields:
            query_params["output_fields"] = args.fields.split(",")
            print(f"🎯 Campos específicos: {args.fields}")

        # Log das configurações finais
        print("⚙️ Configurações de extração:")
        print(f"   - Extração completa: {pipeline.config['wms']['extract_all_data']}")
        print(f"   - Paginação: {pipeline.config['wms']['enable_pagination']}")
        print(f"   - Tamanho da página: {pipeline.config['wms']['pagination_size']}")
        print(f"   - Máximo por requisição: {pipeline.config['wms']['max_records_per_request']}")
        print(f"   - Descoberta abrangente: {pipeline.config['pipeline']['comprehensive_field_discovery']}")

        # Executar pipeline incremental
        pipeline.run_incremental_pipeline(args.resource, args.days_back, **query_params)

        print("✅ Pipeline avançado executado com sucesso!")

    except AdvancedPipelineError as e:
        print(f"❌ Erro no pipeline avançado: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Pipeline interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

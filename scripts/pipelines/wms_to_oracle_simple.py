#!/usr/bin/env python3
"""Pipeline Simples WMS para Oracle usando SQLAlchemy para mapeamento correto.

Este script implementa um pipeline simples que:
- Usa SQLAlchemy para descobrir schema Oracle
- Mapeia apenas campos WMS que existem no Oracle
- Gera SQL INSERT correto e compatível
- Processa FKs corretamente

Uso:
    python wms_to_oracle_simple.py --resource order_hdr --limit 1
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Importar APIs nativas dos projetos
sys.path.insert(0, str(Path(__file__).parent / "dc-oracle-wms"))
sys.path.insert(0, str(Path(__file__).parent / "dc-oracle-db"))

from db import DbClient, DbError
from db.schema import SchemaExtractor
from wms import WmsClient


class SimplePipelineError(Exception):
    """Exceção customizada para erros do pipeline simples."""


class SimpleWmsToOraclePipeline:
    """Pipeline simples para sincronização WMS-Oracle usando SQLAlchemy."""

    def __init__(self) -> None:
        """Inicializa o pipeline simples."""
        self.setup_logging()

        # Clientes
        self.wms_client: WmsClient | None = None
        self.db_client: DbClient | None = None

        # Schemas
        self.oracle_columns = {}  # {nome_coluna_lower: info_coluna}
        self.field_mapping = {}  # {campo_wms: campo_oracle}

        self.logger.info("Pipeline simples iniciado")

    def setup_logging(self) -> None:
        """Configura logging."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
        )
        self.logger = logging.getLogger("SimplePipeline")

    def initialize_clients(self) -> None:
        """Inicializa os clientes WMS e Oracle."""
        try:
            from dotenv import load_dotenv

            # Carregar .env files
            load_dotenv(Path(__file__).parent / "dc-oracle-wms" / ".env")
            load_dotenv(Path(__file__).parent / "dc-oracle-db" / ".env")

            # Inicializar clientes
            self.wms_client = WmsClient(debug_mode=False)
            self.db_client = DbClient(use_pool=True)

            self.logger.info("Clientes inicializados com sucesso")

        except Exception as e:
            msg = f"Erro ao inicializar clientes: {e}"
            raise SimplePipelineError(msg)

    def discover_oracle_schema(self, table_name: str) -> bool:
        """Descobre schema da tabela Oracle.

        Args:
            table_name: Nome da tabela Oracle

        Returns:
            True se schema foi descoberto com sucesso

        """
        try:
            self.logger.info("Descobrindo schema Oracle para tabela: %s", table_name")

            with self.db_client.get_connection() as conn:
                extractor = SchemaExtractor(conn)
                table_schema = extractor.extract_table_schema(table_name)
                oracle_schema = table_schema.to_dict()

                # Processar colunas
                for column in oracle_schema.get("columns", []):
                    column_name = column["name"]
                    self.oracle_columns[column_name.lower()] = {
                        "name": column_name,
                        "type": column.get("data_type", "VARCHAR2").upper(),
                        "nullable": column.get("nullable", True),
                        "length": column.get("length"),
                        "precision": column.get("precision"),
                        "scale": column.get("scale"),
                    }

                self.logger.info(
                    f"Schema Oracle descoberto: {len(self.oracle_columns)} colunas",
                )
                return True

        except Exception as e:
            self.logger.exception(f"Erro ao descobrir schema Oracle: {e}")
            return False

    def extract_wms_data(self, resource: str, limit: int = 1) -> list[dict]:
        """Extrai dados do WMS.

        Args:
            resource: Nome do recurso WMS
            limit: Limite de registros

        Returns:
            Lista de registros processados

        """
        try:
            self.logger.info("Extraindo %s", limit registros de %s", resource do WMS")

            response = self.wms_client.search(
                entity_name=resource,
                params={"limit": limit},
            )

            if not response.success:
                self.logger.error("Erro na busca WMS: %s", response.error")
                return []

            # Extrair registros
            data = response.data
            if isinstance(data, dict) and "results" in data:
                records = data["results"]
            elif isinstance(data, list):
                records = data
            else:
                records = [data] if data else []

            self.logger.info("Extraídos %s", len(records) registros do WMS")

            # Processar registros
            processed_records = []
            for record in records:
                processed = self._process_wms_record(record)
                if processed:
                    processed_records.append(processed)

            self.logger.info("Processados %s", len(processed_records) registros")
            return processed_records

        except Exception as e:
            self.logger.exception(f"Erro ao extrair dados WMS: {e}")
            return []

    def _process_wms_record(self, record: Any) -> dict | None:
        """Process a single WMS record into a dictionary."""
        try:
            # CORREÇÃO: Usar model_dump() ou dict() para obter TODOS os campos
            if hasattr(record, "model_dump"):
                fields = record.model_dump()
                self.logger.debug(f"Using model_dump(): {len(fields)} fields extracted")
            elif hasattr(record, "dict"):
                fields = record.dict()
                self.logger.debug(f"Using dict(): {len(fields)} fields extracted")
            elif isinstance(record, str):
                # Formato string: "order_hdr(id=2, status_id=99)"
                # Extrair nome da entidade e campos
                if not ("(" in record and ")" in record):
                    self.logger.warning("Invalid string format for record: %s", record")
                    return None
                record.split("(")[0]
                content = record.split("(")[1].split(")")[0]
                fields = {}
                for pair in content.split(", "):
                    key, value = pair.split("=")
                    fields[key.strip()] = value.strip()
                # Adicionar o nome da entidade como um campo, se necessário
                # fields["entity_name"] = entity_name
                self.logger.debug(f"Parsed string record: {fields}")
            else:
                self.logger.warning(
                    f"Record is not a Pydantic model or string: {type(record)}",
                )
                return None

            if not fields:
                return None

            self.logger.info("TOTAL de campos extraídos do WMS: %s", len(fields) campos")

            # Processar FKs (foreign keys)
            processed_fields = {}
            for field_name, field_value in fields.items():
                if isinstance(field_value, dict) and any(
                    key in field_value for key in ["id", "key", "url"]
                ):
                    # É uma FK, extrair id e key
                    fk_id = field_value.get("id")
                    fk_key = field_value.get("key")

                    if fk_id is not None:
                        processed_fields[f"{field_name}_id"] = fk_id
                        self.logger.debug(f"  Extraído {field_name}_id: {fk_id}")
                    if fk_key is not None:
                        processed_fields[f"{field_name}_key"] = fk_key
                        self.logger.debug(f"  Extraído {field_name}_key: {fk_key}")

                    # Manter original como JSON
                    processed_fields[field_name] = json.dumps(field_value)
                else:
                    processed_fields[field_name] = field_value

            # Adicionar campos padrão se necessário
            current_time = datetime.now()

            # CORREÇÃO: Usar colunas de auditoria que existem na tabela Oracle
            # Usar campos corretos: CREATED_DATE, UPDATED_DATE, CREATED_BY, UPDATED_BY

            # Campos de auditoria Oracle (apenas se não existirem)
            if "created_date" not in processed_fields:
                processed_fields["created_date"] = current_time
            if "updated_date" not in processed_fields:
                processed_fields["updated_date"] = current_time
            if "created_by" not in processed_fields:
                processed_fields["created_by"] = "WMS_INTEGRATION"
            if "updated_by" not in processed_fields:
                processed_fields["updated_by"] = "WMS_INTEGRATION"

            self.logger.debug(
                f"Registro WMS processado: {len(processed_fields)} campos"
            )
            return processed_fields

        except Exception as e:
            self.logger.exception(f"Erro ao processar registro WMS: {e}")
            return None

    def _parse_wms_string(self, wms_string: str) -> dict:
        """Processa string WMS para extrair campos.

        Args:
            wms_string: String como "order_hdr(id=2, status_id=99)"

        Returns:
            Dicionário com campos extraídos

        """
        try:
            if "(" in wms_string and ")" in wms_string:
                content = wms_string.split("(")[1].split(")")[0]
                fields = {}

                for pair in content.split(", "):
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        key = key.strip()
                        value = value.strip()

                        # Tentar converter para número
                        try:
                            if "." in value:
                                fields[key] = float(value)
                            else:
                                fields[key] = int(value)
                        except ValueError:
                            # Remover aspas se existirem
                            if (value.startswith('"') and value.endswith('"')) or (
                                value.startswith("'") and value.endswith("'")
                            ):
                                value = value[1:-1]
                            fields[key] = value

                return fields
        except Exception as e:
            self.logger.warning("Erro ao processar string WMS: %s", e")

        return {}

    def map_wms_to_oracle(self, wms_records: list[dict]) -> list[dict]:
        """Mapeia registros WMS para campos Oracle existentes.

        CORREÇÃO: Prioriza campos _id das FKs para campos Oracle numéricos.

        Args:
            wms_records: Lista de registros WMS

        Returns:
            Lista de registros mapeados para Oracle

        """
        if not wms_records:
            return []

        self.logger.info("Mapeando %s", len(wms_records) registros WMS para Oracle")

        # Descobrir mapeamentos
        sample_record = wms_records[0]

        # CORREÇÃO: Priorizar campos _id para campos Oracle numéricos
        for wms_field in sample_record:
            oracle_field = self._find_oracle_mapping(wms_field)
            if oracle_field:
                # Verificar se campo Oracle é numérico e se existe versão _id
                oracle_column = self.oracle_columns[oracle_field.lower()]
                if oracle_column["type"] in {"NUMBER", "INTEGER", "DECIMAL", "FLOAT"}:
                    # Se campo Oracle é numérico, verificar se existe campo _id correspondente
                    id_field = f"{wms_field}_id"
                    if id_field in sample_record:
                        # Usar campo _id em vez do campo original
                        self.field_mapping[id_field] = oracle_field
                        self.logger.debug(
                            f"Priorizando FK: {id_field} -> {oracle_field} (numérico)",
                        )
                        continue

                # Usar mapeamento normal
                self.field_mapping[wms_field] = oracle_field

        self.logger.info("Mapeamentos criados: %s", len(self.field_mapping)")
        for wms_field, oracle_field in self.field_mapping.items():
            self.logger.debug(f"  {wms_field} -> {oracle_field}")

        # Mapear registros
        mapped_records = []
        for record in wms_records:
            mapped_record = {}

            for wms_field, value in record.items():
                if wms_field in self.field_mapping:
                    oracle_field = self.field_mapping[wms_field]
                    oracle_column = self.oracle_columns[oracle_field.lower()]

                    # Converter valor para tipo Oracle
                    converted_value = self._convert_to_oracle_type(value, oracle_column)
                    mapped_record[oracle_field] = converted_value

            if mapped_record:
                mapped_records.append(mapped_record)

        self.logger.info("Registros mapeados: %s", len(mapped_records)")

        # Log do primeiro registro mapeado para debug
        if mapped_records:
            first_record = mapped_records[0]
            self.logger.debug(f"Primeiro registro mapeado: {len(first_record)} campos")
            for field, value in list(first_record.items())[:10]:
                self.logger.debug(f"  {field}: {value} (tipo: {type(value)})")

        return mapped_records

    def _find_oracle_mapping(self, wms_field: str) -> str | None:
        """Encontra mapeamento de campo WMS para Oracle.

        CORREÇÃO: Prioriza campos _id das FKs para campos Oracle que esperam números.

        Args:
            wms_field: Nome do campo WMS

        Returns:
            Nome do campo Oracle ou None se não encontrado

        """
        wms_field_lower = wms_field.lower()

        # CORREÇÃO: Para campos que terminam com _id, verificar se existe campo Oracle correspondente
        if wms_field_lower.endswith("_id"):
            # Buscar campo Oracle direto
            for oracle_field in self.oracle_columns:
                if oracle_field == wms_field_lower:
                    oracle_column = self.oracle_columns[oracle_field]
                    # Se é campo numérico no Oracle, usar o campo _id
                    if oracle_column["type"] in {
                        "NUMBER",
                        "INTEGER",
                        "DECIMAL",
                        "FLOAT",
                    }:
                        return oracle_column["name"]

        # Busca direta
        for oracle_field in self.oracle_columns:
            if oracle_field == wms_field_lower:
                oracle_column = self.oracle_columns[oracle_field]
                # CORREÇÃO: Se campo Oracle é numérico mas WMS field não é _id,
                # verificar se existe versão _id
                if oracle_column["type"] in {"NUMBER", "INTEGER", "DECIMAL", "FLOAT"}:
                    # Verificar se existe campo _id correspondente nos dados processados
                    # Esta verificação será feita no mapeamento
                    pass
                return oracle_column["name"]

        # Busca com variações
        variations = [
            wms_field_lower,
            wms_field_lower.replace("_", ""),
            wms_field_lower.replace("-", "_"),
            f"wms_{wms_field_lower}",
        ]

        for variation in variations:
            for oracle_field in self.oracle_columns:
                if oracle_field == variation:
                    return self.oracle_columns[oracle_field]["name"]

        return None

    def _convert_to_oracle_type(self, value: Any, oracle_column: dict) -> Any:
        """Converte valor para tipo Oracle.

        Args:
            value: Valor a ser convertido
            oracle_column: Informações da coluna Oracle

        Returns:
            Valor convertido

        """
        if value is None:
            return None

        oracle_type = oracle_column["type"]

        try:
            if oracle_type in {"NUMBER", "INTEGER", "DECIMAL", "FLOAT"}:
                if isinstance(value, str):
                    return float(value) if "." in str(value) else int(value)
                return value

            if oracle_type in {"VARCHAR2", "CHAR", "CLOB"}:
                str_value = str(value)
                max_length = oracle_column.get("length")
                if max_length and len(str_value) > max_length:
                    str_value = str_value[:max_length]
                return str_value

            if oracle_type in {"DATE", "TIMESTAMP"}:
                if isinstance(value, str):
                    return value
                return str(value)

            return str(value)

        except (ValueError, TypeError):
            # Valor padrão por tipo
            if oracle_type in {"NUMBER", "INTEGER", "DECIMAL", "FLOAT"}:
                return 0
            return str(value)

    def generate_insert_sql(
        self,
        mapped_records: list[dict],
        table_name: str,
    ) -> list[str]:
        """Gera comandos INSERT SQL.

        CORREÇÃO: Converte valores booleanos corretamente para Oracle.

        Args:
            mapped_records: Lista de registros mapeados
            table_name: Nome da tabela Oracle

        Returns:
            Lista de comandos INSERT SQL

        """
        if not mapped_records:
            return []

        self.logger.info("Gerando INSERT SQL para %s", len(mapped_records) registros")

        insert_statements = []

        for record in mapped_records:
            if not record:
                continue

            # Construir INSERT
            fields = list(record.keys())
            fields_str = ", ".join([f'"{field}"' for field in fields])

            values = []
            for field in fields:
                value = record[field]
                if value is None:
                    values.append("NULL")
                elif isinstance(value, bool):
                    # CORREÇÃO: Converter booleanos para números Oracle
                    values.append("1" if value else "0")
                elif isinstance(value, str):
                    # CORREÇÃO: Verificar se string representa booleano
                    if value.lower() in {"true", "false"}:
                        values.append("1" if value.lower() == "true" else "0")
                    # CORREÇÃO: Verificar se é timestamp com timezone (ISO format)
                    elif (
                        "T" in value
                        and (":" in value)
                        and ("+" in value or "-" in value[-6:])
                    ):
                        # Timestamp ISO com timezone: 2020-11-20T11:57:00.620477-03:00
                        try:
                            # Extrair apenas a parte da data e hora, ignorando timezone e microsegundos
                            if "." in value:
                                # Remover microsegundos
                                datetime_part = value.split(".")[0]
                            else:
                                datetime_part = (
                                    value.split("+")[0].split("-")[0]
                                    if "+" in value
                                    else value.rsplit("-", 1)[0]
                                )

                            # Converter T para espaço
                            datetime_str = datetime_part.replace("T", " ")
                            values.append(
                                f"TO_DATE('{datetime_str}', 'YYYY-MM-DD HH24:MI:SS')",
                            )
                        except:
                            # Se falhar, tratar como string normal
                            escaped_value = value.replace("'", "''")
                            values.append(f"'{escaped_value}'")
                    # CORREÇÃO: Verificar se é campo de data E se o valor parece uma data
                    elif any(
                        date_keyword in field.lower()
                        for date_keyword in ["date", "_dt", "_ts"]
                    ) and not any(
                        text_keyword in field.lower()
                        for text_keyword in ["by", "user", "name"]
                    ):
                        # Verificar se o valor realmente parece uma data
                        if (
                            len(value) == 10 and "-" in value and value.count("-") == 2
                        ):  # YYYY-MM-DD
                            values.append(f"TO_DATE('{value}', 'YYYY-MM-DD')")
                        elif (
                            len(value) == 19 and " " in value and "-" in value
                        ):  # YYYY-MM-DD HH:MM:SS
                            values.append(
                                f"TO_DATE('{value}', 'YYYY-MM-DD HH24:MI:SS')",
                            )
                        else:
                            # Não parece uma data, tratar como string
                            escaped_value = value.replace("'", "''")
                            values.append(f"'{escaped_value}'")
                    else:
                        escaped_value = value.replace("'", "''")
                        values.append(f"'{escaped_value}'")
                elif isinstance(value, int | float):
                    values.append(str(value))
                # CORREÇÃO: Para outros tipos, verificar se é booleano
                elif str(value).lower() in {"true", "false"}:
                    values.append("1" if str(value).lower() == "true" else "0")
                else:
                    str_value = str(value).replace("'", "''")
                    values.append(f"'{str_value}'")

            values_str = ", ".join(values)
            insert_sql = (
                f'INSERT INTO "{table_name}" ({fields_str}) VALUES ({values_str})'
            )
            insert_statements.append(insert_sql)

        self.logger.info("Gerados %s", len(insert_statements) comandos INSERT")

        # Log do primeiro SQL para debug
        if insert_statements:
            first_sql = insert_statements[0]
            self.logger.debug(
                f"Primeiro SQL (primeiros 300 chars): {first_sql[:300]}...",
            )

        return insert_statements

    def execute_sql(self, sql_statements: list[str]) -> None:
        """Executa comandos SQL no Oracle.

        CORREÇÃO: Usar commit=True para garantir persistência dos dados.

        Args:
            sql_statements: Lista de comandos SQL

        """
        if not sql_statements:
            self.logger.info("Nenhum comando SQL para executar")
            return

        self.logger.info("Executando %s", len(sql_statements) comandos SQL no Oracle")

        try:
            # CORREÇÃO: Usar commit=True em vez de transaction() para garantir persistência
            for i, sql in enumerate(sql_statements):
                try:
                    affected_rows = self.db_client.execute(sql, commit=True)
                    self.logger.debug(f"SQL {i + 1}: {affected_rows} linhas afetadas")

                    if i == 0:  # Log do primeiro SQL
                        self.logger.info("Primeiro SQL executado: %s", sql[:100]...")

                except DbError as e:
                    self.logger.exception(f"Erro no SQL {i + 1}: {e}")
                    raise

            self.logger.info(
                f"Todos os {len(sql_statements)} comandos executados com sucesso",
            )

        except Exception as e:
            self.logger.exception(f"Erro ao executar SQL: {e}")
            raise

    def run_pipeline(self, resource: str, limit: int = 1) -> None:
        """Executa o pipeline completo.

        Args:
            resource: Recurso WMS para extrair
            limit: Limite de registros

        """
        try:
            self.logger.info("=== INICIANDO PIPELINE SIMPLES ===")
            self.logger.info("Recurso: %s", resource, Limite: %s", limit")

            # 1. Inicializar clientes
            self.initialize_clients()

            # 2. Descobrir schema Oracle
            table_name = f"WMS_{resource.upper()}"
            if not self.discover_oracle_schema(table_name):
                msg = "Falha na descoberta do schema Oracle"
                raise SimplePipelineError(msg)

            # 3. Extrair dados WMS
            wms_records = self.extract_wms_data(resource, limit)
            if not wms_records:
                self.logger.info("Nenhum dado WMS encontrado")
                return

            # 4. Mapear para Oracle
            mapped_records = self.map_wms_to_oracle(wms_records)
            if not mapped_records:
                self.logger.warning("Nenhum registro foi mapeado para Oracle")
                return

            # 5. Gerar SQL
            sql_statements = self.generate_insert_sql(mapped_records, table_name)
            if not sql_statements:
                self.logger.warning("Nenhum SQL foi gerado")
                return

            # 6. Executar SQL
            self.execute_sql(sql_statements)

            self.logger.info("=== PIPELINE CONCLUÍDO COM SUCESSO ===")

        except Exception as e:
            self.logger.exception(f"Erro no pipeline: {e}")
            raise
        finally:
            if self.db_client:
                self.db_client.close()


def main() -> None:
    """Função principal."""
    parser = argparse.ArgumentParser(description="Pipeline Simples WMS para Oracle")
    parser.add_argument("--resource", required=True, help="Recurso WMS para extrair")
    parser.add_argument("--limit", type=int, default=1, help="Limite de registros")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Logging detalhado",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        pipeline = SimpleWmsToOraclePipeline()
        pipeline.run_pipeline(args.resource, args.limit)
        print("✅ Pipeline executado com sucesso!")

    except Exception as e:
        print(f"❌ Erro no pipeline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

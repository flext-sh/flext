#!/usr/bin/env python3
"""Pipeline para transferir dados do WMS para Oracle DB via CLI.

Este script orquestra a extração de dados do Oracle WMS usando o CLI do dc-oracle-wms
e a inserção desses dados no Oracle Database usando o CLI do dc-oracle-db.

Funcionalidades:
- Extração de dados do WMS via CLI com suporte a filtros e queries
- Transformação de dados para formato compatível com Oracle DB
- Inserção de dados no Oracle DB via CLI
- Logging detalhado de todas as operações
- Tratamento de erros robusto
- Configuração flexível via arquivo JSON/YAML

Uso:
    python wms_to_oracle_pipeline.py --config pipeline_config.json
    python wms_to_oracle_pipeline.py --resource orders --table WMS_ORDERS
"""

import argparse
import json
import logging
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


class PipelineError(Exception):
    """Exceção customizada para erros do pipeline."""


class WmsToOraclePipeline:
    """Pipeline para transferir dados do WMS para Oracle Database.

    Esta classe orquestra a extração de dados do Oracle WMS usando CLI
    e a inserção no Oracle Database, incluindo transformação de dados,
    tratamento de erros e logging detalhado.
    """

    def __init__(self, config_file: str | None = None) -> None:
        """Inicializa o pipeline.

        Args:
            config_file: Caminho para arquivo de configuração (JSON/YAML)

        """
        self.setup_logging()
        self.config = self.load_config(config_file)
        self.temp_dir = Path(tempfile.mkdtemp(prefix="wms_oracle_pipeline_"))
        self.logger.info(f"Pipeline iniciado. Diretório temporário: {self.temp_dir}")

    def setup_logging(self) -> None:
        """Configura o sistema de logging."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            ],
        )
        self.logger = logging.getLogger("WmsToOraclePipeline")

    def load_config(self, config_file: str | None) -> dict[str, Any]:
        """Carrega configuração do arquivo ou usa padrões.

        Args:
            config_file: Caminho para arquivo de configuração

        Returns:
            Dicionário com configurações

        """
        default_config = {
            "wms": {
                "base_path": "/home/marlonsc/pyauto/dc-oracle-wms",
                "timeout": 300,
                "max_retries": 3,
            },
            "oracle": {
                "base_path": "/home/marlonsc/pyauto/dc-oracle-db",
                "timeout": 300,
                "batch_size": 1000,
            },
            "pipeline": {
                "temp_dir": "/tmp/wms_oracle_pipeline",
                "cleanup_temp": True,
                "validate_data": True,
            },
        }

        if config_file and Path(config_file).exists():
            self.logger.info(f"Carregando configuração de: {config_file}")
            with open(config_file, encoding="utf-8") as f:
                if config_file.endswith((".yaml", ".yml")):
                    user_config = yaml.safe_load(f)
                else:
                    user_config = json.load(f)

            # Merge configurações
            default_config.update(user_config)

        return default_config

    def extract_from_wms(self, resource: str, **query_params) -> Path:
        """Extrai dados do WMS usando CLI.

        Args:
            resource: Nome do recurso WMS (ex: orders, items, locations)
            **query_params: Parâmetros de query (limit, filter, etc.)

        Returns:
            Caminho para arquivo JSON com dados extraídos

        Raises:
            PipelineError: Se extração falhar

        """
        self.logger.info(f"Iniciando extração do WMS - Recurso: {resource}")

        output_file = self.temp_dir / f"wms_data_{resource}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Construir comando CLI do WMS
        cmd = [
            "python", "-m", "wms.cli", "query", resource,
            "--format", "json",
            "--output-file", str(output_file),
        ]

        # Adicionar parâmetros de query
        if query_params.get("limit"):
            cmd.extend(["--limit", str(query_params["limit"])])

        if query_params.get("query"):
            cmd.extend(["--query", query_params["query"]])

        if query_params.get("filter"):
            for filter_param in query_params["filter"]:
                cmd.extend(["--filter", filter_param])

        if query_params.get("fields"):
            cmd.extend(["--fields", query_params["fields"]])

        try:
            self.logger.info(f"Executando comando WMS: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=self.config["wms"]["base_path"],
                capture_output=True,
                text=True,
                timeout=self.config["wms"]["timeout"],
                check=True,
            )

            self.logger.info(f"Extração WMS concluída. Output: {result.stdout}")

            if not output_file.exists():
                msg = f"Arquivo de saída não foi criado: {output_file}"
                raise PipelineError(msg)

            # Validar dados extraídos
            with open(output_file, encoding="utf-8") as f:
                data = json.load(f)
                self.logger.info(f"Extraídos {len(data) if isinstance(data, list) else 1} registros")

            return output_file

        except subprocess.TimeoutExpired:
            msg = f"Timeout na extração WMS após {self.config['wms']['timeout']}s"
            raise PipelineError(msg)
        except subprocess.CalledProcessError as e:
            msg = f"Erro na extração WMS: {e.stderr}"
            raise PipelineError(msg)
        except Exception as e:
            msg = f"Erro inesperado na extração WMS: {e!s}"
            raise PipelineError(msg)

    def transform_data(self, data_file: Path, table_name: str) -> Path:
        """Transforma dados para formato compatível com Oracle DB.

        Args:
            data_file: Arquivo JSON com dados do WMS
            table_name: Nome da tabela Oracle de destino

        Returns:
            Caminho para arquivo SQL com comandos INSERT

        """
        self.logger.info(f"Iniciando transformação de dados para tabela: {table_name}")

        with open(data_file, encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            data = [data]

        sql_file = self.temp_dir / f"insert_{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

        with open(sql_file, "w", encoding="utf-8") as f:
            f.write(f"-- Inserção de dados WMS na tabela {table_name}\n")
            f.write(f"-- Gerado em: {datetime.now().isoformat()}\n")
            f.write(f"-- Total de registros: {len(data)}\n\n")

            for i, record in enumerate(data):
                if i % self.config["oracle"]["batch_size"] == 0 and i > 0:
                    f.write("COMMIT;\n\n")

                # Gerar INSERT statement
                columns = list(record.keys())
                values = []

                for value in record.values():
                    if value is None:
                        values.append("NULL")
                    elif isinstance(value, str):
                        # Escapar aspas simples
                        escaped_value = value.replace("'", "''")
                        values.append(f"'{escaped_value}'")
                    elif isinstance(value, int | float):
                        values.append(str(value))
                    elif isinstance(value, bool):
                        values.append("1" if value else "0")
                    else:
                        # Para objetos complexos, converter para JSON
                        json_value = json.dumps(value).replace("'", "''")
                        values.append(f"'{json_value}'")

                insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});\n"
                f.write(insert_sql)

            f.write("\nCOMMIT;\n")

        self.logger.info(f"Transformação concluída. Arquivo SQL: {sql_file}")
        return sql_file

    def load_to_oracle(self, sql_file: Path) -> None:
        """Carrega dados no Oracle DB usando CLI.

        Args:
            sql_file: Arquivo SQL com comandos INSERT

        Raises:
            PipelineError: Se inserção falhar

        """
        self.logger.info(f"Iniciando carregamento no Oracle DB: {sql_file}")

        cmd = [
            "python", "-m", "db.cli", "run", str(sql_file),
        ]

        try:
            self.logger.info(f"Executando comando Oracle: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=self.config["oracle"]["base_path"],
                capture_output=True,
                text=True,
                timeout=self.config["oracle"]["timeout"],
                check=True,
            )

            self.logger.info(f"Carregamento Oracle concluído. Output: {result.stdout}")

        except subprocess.TimeoutExpired:
            msg = f"Timeout no carregamento Oracle após {self.config['oracle']['timeout']}s"
            raise PipelineError(msg)
        except subprocess.CalledProcessError as e:
            msg = f"Erro no carregamento Oracle: {e.stderr}"
            raise PipelineError(msg)
        except Exception as e:
            msg = f"Erro inesperado no carregamento Oracle: {e!s}"
            raise PipelineError(msg)

    def run_pipeline(self, resource: str, table_name: str, **query_params) -> None:
        """Executa o pipeline completo.

        Args:
            resource: Recurso WMS para extrair
            table_name: Tabela Oracle de destino
            **query_params: Parâmetros de query WMS

        """
        try:
            self.logger.info("=== Iniciando Pipeline WMS -> Oracle ===")
            self.logger.info(f"Recurso: {resource} -> Tabela: {table_name}")

            # 1. Extrair dados do WMS
            data_file = self.extract_from_wms(resource, **query_params)

            # 2. Transformar dados
            sql_file = self.transform_data(data_file, table_name)

            # 3. Carregar no Oracle
            self.load_to_oracle(sql_file)

            self.logger.info("=== Pipeline concluído com sucesso ===")

        except Exception as e:
            self.logger.exception(f"Erro no pipeline: {e!s}")
            raise
        finally:
            if self.config["pipeline"]["cleanup_temp"]:
                self.cleanup()

    def cleanup(self) -> None:
        """Remove arquivos temporários."""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            self.logger.info(f"Diretório temporário removido: {self.temp_dir}")
        except Exception as e:
            self.logger.warning(f"Erro ao remover diretório temporário: {e!s}")


def main() -> None:
    """Função principal do script."""
    parser = argparse.ArgumentParser(
        description="Pipeline WMS para Oracle Database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Pipeline básico
  python wms_to_oracle_pipeline.py --resource orders --table WMS_ORDERS

  # Com filtros e limite
  python wms_to_oracle_pipeline.py --resource items --table WMS_ITEMS --limit 1000 --filter "status:eq:ACTIVE"

  # Com arquivo de configuração
  python wms_to_oracle_pipeline.py --config pipeline_config.json --resource locations --table WMS_LOCATIONS

  # Com query específica
  python wms_to_oracle_pipeline.py --resource orders --table WMS_ORDERS --query "order_date >= '2024-01-01'"
        """,
    )

    parser.add_argument("--config", help="Arquivo de configuração (JSON/YAML)")
    parser.add_argument("--resource", required=True, help="Recurso WMS para extrair")
    parser.add_argument("--table", required=True, help="Tabela Oracle de destino")
    parser.add_argument("--limit", type=int, help="Limite de registros")
    parser.add_argument("--query", help="Query string para filtrar dados")
    parser.add_argument("--filter", action="append", help="Filtros avançados (pode ser usado múltiplas vezes)")
    parser.add_argument("--fields", help="Campos específicos para extrair (separados por vírgula)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Logging detalhado")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Criar pipeline
        pipeline = WmsToOraclePipeline(args.config)

        # Preparar parâmetros de query
        query_params = {}
        if args.limit:
            query_params["limit"] = args.limit
        if args.query:
            query_params["query"] = args.query
        if args.filter:
            query_params["filter"] = args.filter
        if args.fields:
            query_params["fields"] = args.fields

        # Executar pipeline
        pipeline.run_pipeline(args.resource, args.table, **query_params)

        print("✅ Pipeline executado com sucesso!")

    except PipelineError as e:
        print(f"❌ Erro no pipeline: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Pipeline interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

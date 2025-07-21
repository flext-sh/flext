#!/usr/bin/env python3
"""Script para detectar código duplicado no workspace Flext.

Este script usa uma abordagem robusta baseada em análise de similaridade
textual e estrutural para detectar duplicações de código.
"""

import hashlib
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DuplicateMatch:
    """Representa uma duplicação encontrada."""

    file1: str
    file2: str
    similarity: float
    lines1: tuple[int, int]
    lines2: tuple[int, int]
    content: str


@dataclass
class AnalysisResult:
    """Resultado da análise de duplicação."""

    duplicates: list[DuplicateMatch]
    total_files: int
    analyzed_files: int
    errors: list[str]


class FlextDuplicateDetector:
    """Detector de código duplicado específico para o Flext."""

    def __init__(
        self,
        similarity_threshold: float = 0.8,
        min_lines: int = 10,
        file_extensions: list[str] | None = None,
        analyze_all_files: bool = False,
    ):
        """Inicializa o detector.

        Args:
            similarity_threshold: Limite de similaridade (0.0 a 1.0)
            min_lines: Número mínimo de linhas para considerar duplicação
            file_extensions: Extensões de arquivo para analisar
            analyze_all_files: Se True, analisa todos os arquivos rastreáveis pelo git

        """
        self.similarity_threshold = similarity_threshold
        self.min_lines = min_lines
        self.analyze_all_files = analyze_all_files

        if analyze_all_files:
            # Extensões de arquivos de texto comuns que o git pode rastrear
            self.file_extensions = [
                # Código fonte
                "py",
                "js",
                "ts",
                "jsx",
                "tsx",
                "java",
                "go",
                "rs",
                "cpp",
                "c",
                "h",
                "hpp",
                "cs",
                "php",
                "rb",
                "swift",
                "kt",
                "scala",
                "clj",
                "hs",
                "ml",
                "elm",
                # Web
                "html",
                "htm",
                "css",
                "scss",
                "sass",
                "less",
                "vue",
                "svelte",
                # Configuração
                "json",
                "yaml",
                "yml",
                "toml",
                "ini",
                "cfg",
                "conf",
                "config",
                "xml",
                "properties",
                "env",
                "gitignore",
                "dockerignore",
                # Documentação
                "md",
                "rst",
                "txt",
                "adoc",
                "tex",
                "org",
                # Scripts
                "sh",
                "bash",
                "zsh",
                "fish",
                "ps1",
                "bat",
                "cmd",
                # Dados
                "csv",
                "tsv",
                "sql",
                "graphql",
                "proto",
                # Makefiles e builds
                "mk",
                "cmake",
                "gradle",
                "pom",
                "requirements",
                # Outros
                "log",
                "lock",
                "sum",
                "mod",
            ]
        else:
            self.file_extensions = file_extensions or ["py", "js", "ts", "java", "go"]

        # Diretórios do Flext
        self.flext_modules = [
            "flext-core/src",
            "flext-ldap/src",
            "flext-grpc/src",
            "flext-api/src",
            "flext-auth/src",
            "flext-cli/src",
            "flext-db-oracle/src",
            "flext-dbt-ldap/src",
            "flext-dbt-ldif/src",
            "flext-dbt-oracle/src",
            "flext-dbt-oracle-wms/src",
            "flext-ldif/src",
            "flext-meltano/src",
            "flext-observability/src",
            "flext-oracle-oic-ext/src",
            "flext-oracle-wms/src",
            "flext-plugin/src",
            "flext-quality/src",
            "flext-tap-ldap/src",
            "flext-tap-ldif/src",
            "flext-tap-oracle/src",
            "flext-tap-oracle-oic/src",
            "flext-tap-oracle-wms/src",
            "flext-target-ldap/src",
            "flext-target-ldif/src",
            "flext-target-oracle/src",
            "flext-target-oracle-oic/src",
            "flext-target-oracle-wms/src",
            "flext-web/src",
            "scripts",
        ]

        self.exclude_patterns = [
            "__pycache__",
            ".pytest_cache",
            "node_modules",
            ".git",
            "docs",
            "reports",
            "target",
            "build",
            "dist",
            "tests",
            "test",
            ".venv",
            "venv",
            ".env",
        ]

    def _should_skip_file(self, file_path: str) -> bool:
        """Verifica se um arquivo deve ser ignorado."""
        file_path_lower = file_path.lower()

        # Ignorar padrões específicos
        for pattern in self.exclude_patterns:
            if pattern in file_path_lower:
                return True

        # Se analisando todos os arquivos, usar lógica mais abrangente
        if self.analyze_all_files:
            # Verificar se é arquivo binário comum
            binary_extensions = {
                "exe",
                "dll",
                "so",
                "dylib",
                "a",
                "lib",
                "o",
                "obj",
                "png",
                "jpg",
                "jpeg",
                "gif",
                "bmp",
                "ico",
                "svg",
                "webp",
                "mp4",
                "avi",
                "mov",
                "wmv",
                "flv",
                "webm",
                "mp3",
                "wav",
                "ogg",
                "pdf",
                "doc",
                "docx",
                "xls",
                "xlsx",
                "ppt",
                "pptx",
                "zip",
                "tar",
                "gz",
                "rar",
                "7z",
                "bz2",
                "xz",
                "whl",
                "egg",
                "jar",
                "war",
                "deb",
                "rpm",
                "pyc",
                "pyo",
                "pyd",
                "class",
                "cache",
            }

            # Extrair extensão
            if "." in file_path:
                ext = file_path.split(".")[-1].lower()
                if ext in binary_extensions:
                    return True

            # Verificar arquivos sem extensão comuns
            filename = Path(file_path_lower).name
            if filename in {
                "makefile",
                "dockerfile",
                "vagrantfile",
                "procfile",
                "license",
                "changelog",
                "readme",
            }:
                return False

            # Se tem extensão, verificar se está na lista permitida
            if "." in file_path:
                ext = file_path.split(".")[-1].lower()
                return ext not in self.file_extensions
            # Arquivos sem extensão - verificar se são de texto
            return not self._is_text_file(file_path)
        # Modo original - apenas extensões específicas
        return bool(
            not any(file_path.endswith(f".{ext}") for ext in self.file_extensions),
        )

    def _is_text_file(self, file_path: str) -> bool:
        """Verifica se um arquivo é de texto."""
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(1024)
                if not chunk:
                    return True  # Arquivo vazio é considerado texto

                # Verificar se contém bytes nulos (indicativo de binário)
                if b"\0" in chunk:
                    return False

                # Verificar se a maioria dos bytes são ASCII/UTF-8 válidos
                try:
                    chunk.decode("utf-8")
                    return True
                except UnicodeDecodeError:
                    try:
                        chunk.decode("latin-1")
                        return True
                    except UnicodeDecodeError:
                        return False
        except Exception:
            return False

    def _normalize_code(self, content: str) -> str:
        """Normaliza código removendo comentários, strings e espaços."""
        try:
            # Para Python, usar AST
            if (
                content.strip().endswith(".py")
                or "import " in content
                or "def " in content
            ):
                return self._normalize_python_code(content)
            return self._normalize_generic_code(content)
        except Exception:
            return self._normalize_generic_code(content)

    def _normalize_python_code(self, content: str) -> str:
        """Normaliza código Python usando AST."""
        try:
            # Remover comentários e docstrings
            lines = []
            for line in content.split("\n"):
                line_content = line
                # Remover comentários
                if "#" in line_content:
                    line_content = line_content[: line_content.index("#")]
                # Manter apenas linhas com conteúdo
                line_content = line_content.strip()
                if (
                    line_content
                    and not line_content.startswith('"""')
                    and not line_content.startswith("'''")
                ):
                    lines.append(line_content)

            normalized = "\n".join(lines)

            # Normalizar espaços
            normalized = re.sub(r"\s+", " ", normalized)

            return normalized.strip()
        except Exception:
            return self._normalize_generic_code(content)

    def _normalize_generic_code(self, content: str) -> str:
        """Normaliza código genérico."""
        # Remover comentários de linha
        content = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
        content = re.sub(r"#.*$", "", content, flags=re.MULTILINE)

        # Remover comentários de bloco
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

        # Remover strings
        content = re.sub(r'".*?"', '""', content)
        content = re.sub(r"'.*?'", "''", content)

        # Normalizar espaços
        content = re.sub(r"\s+", " ", content)

        return content.strip()

    def _get_file_blocks(self, content: str) -> list[tuple[str, int, int]]:
        """Divide arquivo em blocos de código."""
        lines = content.split("\n")
        blocks = []

        current_block: list[str] = []
        start_line = 0

        for i, line in enumerate(lines):
            line_content = line.strip()

            if not line_content:
                if current_block and len(current_block) >= self.min_lines:
                    block_content = "\n".join(current_block)
                    blocks.append((block_content, start_line, i))
                current_block = []
                start_line = i + 1
            else:
                current_block.append(line_content)

        # Último bloco
        if current_block and len(current_block) >= self.min_lines:
            block_content = "\n".join(current_block)
            blocks.append((block_content, start_line, len(lines)))

        return blocks

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridade entre dois textos usando hash rápido."""
        if not text1 or not text2:
            return 0.0

        # Normalizar textos
        norm1 = self._normalize_code(text1)
        norm2 = self._normalize_code(text2)

        if not norm1 or not norm2:
            return 0.0

        # Fast exact match check first
        if norm1 == norm2:
            return 1.0

        # Use simple word-based similarity for speed
        words1 = set(norm1.split())
        words2 = set(norm2.split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _find_exact_duplicates(
        self,
        files_content: dict[str, str],
    ) -> list[DuplicateMatch]:
        """Encontra duplicatas exatas baseadas em hash."""
        duplicates = []
        hash_to_files = defaultdict(list)

        for file_path, content in files_content.items():
            normalized = self._normalize_code(content)
            if len(normalized) > 50:  # Ignorar arquivos muito pequenos
                content_hash = hashlib.sha256(normalized.encode()).hexdigest()
                hash_to_files[content_hash].append(file_path)

        for file_list in hash_to_files.values():
            if len(file_list) > 1:
                for i in range(len(file_list)):
                    for j in range(i + 1, len(file_list)):
                        file1, file2 = file_list[i], file_list[j]
                        duplicates.append(
                            DuplicateMatch(
                                file1=file1,
                                file2=file2,
                                similarity=1.0,
                                lines1=(1, len(files_content[file1].split("\n"))),
                                lines2=(1, len(files_content[file2].split("\n"))),
                                content=files_content[file1][:200] + "...",
                            ),
                        )

        return duplicates

    def _find_similar_blocks(
        self,
        files_content: dict[str, str],
    ) -> list[DuplicateMatch]:
        """Encontra blocos similares entre arquivos."""
        duplicates = []
        file_blocks = {}

        # Extrair blocos de cada arquivo
        for file_path, content in files_content.items():
            blocks = self._get_file_blocks(content)
            file_blocks[file_path] = blocks

        # Comparar blocos entre arquivos
        file_paths = list(file_blocks.keys())
        for i in range(len(file_paths)):
            for j in range(i + 1, len(file_paths)):
                file1, file2 = file_paths[i], file_paths[j]

                for block1, start1, end1 in file_blocks[file1]:
                    for block2, start2, end2 in file_blocks[file2]:
                        # Skip blocks with very different sizes (optimization)
                        if (
                            abs(len(block1) - len(block2))
                            > max(len(block1), len(block2)) * 0.5
                        ):
                            continue

                        similarity = self._calculate_similarity(block1, block2)

                        if similarity >= self.similarity_threshold:
                            duplicates.append(
                                DuplicateMatch(
                                    file1=file1,
                                    file2=file2,
                                    similarity=similarity,
                                    lines1=(start1, end1),
                                    lines2=(start2, end2),
                                    content=block1[:200] + "...",
                                ),
                            )

        return duplicates

    def _find_similar_blocks_batched(
        self,
        files_content: dict[str, str],
        batch_size: int = 20,
    ) -> list[DuplicateMatch]:
        """Encontra blocos similares processando em lotes menores."""
        duplicates = []
        file_paths = list(files_content.keys())

        # Processar em lotes
        for i in range(0, len(file_paths), batch_size):
            batch_files = file_paths[i : i + batch_size]
            batch_content = {f: files_content[f] for f in batch_files}

            print(
                f"📦 Processando lote {i // batch_size + 1}/{(len(file_paths) + batch_size - 1) // batch_size}...",
            )

            batch_duplicates = self._find_similar_blocks(batch_content)
            duplicates.extend(batch_duplicates)

        return duplicates

    def _collect_files(self, modules: list[str]) -> dict[str, str]:
        """Coleta conteúdo dos arquivos para análise."""
        files_content = {}
        errors = []

        for module in modules:
            if not Path(module).exists():
                errors.append(f"Módulo não encontrado: {module}")
                continue

            for root, dirs, files in os.walk(module):
                # Filtrar diretórios
                dirs[:] = [
                    d
                    for d in dirs
                    if not any(
                        pattern in d.lower() for pattern in self.exclude_patterns
                    )
                ]

                for file in files:
                    file_path = os.path.join(root, file)

                    if self._should_skip_file(file_path):
                        continue

                    try:
                        with open(file_path, encoding="utf-8", errors="ignore") as f:
                            content = f.read()

                        # Filtrar arquivos muito pequenos ou vazios
                        if len(content.strip()) < 100:
                            continue

                        files_content[file_path] = content

                    except Exception as e:
                        errors.append(f"Erro ao ler {file_path}: {e}")

        return files_content

    def analyze_workspace(self) -> AnalysisResult:
        """Analisa todo o workspace para duplicações."""
        print("🔍 Analisando workspace Flext para código duplicado...")

        # Filtrar módulos existentes
        existing_modules = [m for m in self.flext_modules if Path(m).exists()]

        if not existing_modules:
            return AnalysisResult([], 0, 0, ["Nenhum módulo encontrado"])

        print(f"📦 Analisando {len(existing_modules)} módulos...")

        # Coletar arquivos
        files_content = self._collect_files(existing_modules)

        if not files_content:
            return AnalysisResult([], 0, 0, ["Nenhum arquivo válido encontrado"])

        print(f"📄 Analisando {len(files_content)} arquivos...")

        # Encontrar duplicações
        duplicates = []

        # 1. Duplicatas exatas
        exact_duplicates = self._find_exact_duplicates(files_content)
        duplicates.extend(exact_duplicates)
        print(f"🔍 Encontradas {len(exact_duplicates)} duplicações exatas")

        # 2. Blocos similares (processar em lotes para performance)
        if len(files_content) > 50:
            print("⚡ Muitos arquivos detectados, processando em lotes...")
            similar_blocks = self._find_similar_blocks_batched(files_content)
        else:
            similar_blocks = self._find_similar_blocks(files_content)
        duplicates.extend(similar_blocks)
        print(f"🔍 Encontrados {len(similar_blocks)} blocos similares")

        return AnalysisResult(
            duplicates=duplicates,
            total_files=len(files_content),
            analyzed_files=len(files_content),
            errors=[],
        )

    def analyze_modules(self, modules: list[str]) -> AnalysisResult:
        """Analisa módulos específicos."""
        print(f"🔍 Analisando módulos: {', '.join(modules)}")

        files_content = self._collect_files(modules)

        if not files_content:
            return AnalysisResult([], 0, 0, ["Nenhum arquivo encontrado"])

        duplicates = []
        duplicates.extend(self._find_exact_duplicates(files_content))
        duplicates.extend(self._find_similar_blocks(files_content))

        return AnalysisResult(
            duplicates=duplicates,
            total_files=len(files_content),
            analyzed_files=len(files_content),
            errors=[],
        )

    def generate_report(
        self,
        result: AnalysisResult,
        output_file: str | None = None,
    ) -> None:
        """Gera relatório detalhado."""
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO DE CÓDIGO DUPLICADO - FLEXT WORKSPACE")
        print("=" * 80)

        print("📈 ESTATÍSTICAS:")
        print(f"   📁 Arquivos analisados: {result.analyzed_files}")
        print(f"   🔍 Total de duplicações: {len(result.duplicates)}")

        if not result.duplicates:
            print("✅ Nenhuma duplicação encontrada!")
            print("🎉 O código está bem estruturado!")
            return

        # Agrupar por tipo
        exact_matches = [d for d in result.duplicates if d.similarity >= 0.99]
        high_similarity = [d for d in result.duplicates if 0.9 <= d.similarity < 0.99]
        medium_similarity = [d for d in result.duplicates if 0.8 <= d.similarity < 0.9]

        print(f"   🚨 Duplicações exatas (≥99%): {len(exact_matches)}")
        print(f"   ⚠️  Alta similaridade (90-99%): {len(high_similarity)}")
        print(f"   ℹ️  Média similaridade (80-90%): {len(medium_similarity)}")

        # Mostrar duplicações críticas
        if exact_matches:
            print("\n🚨 DUPLICAÇÕES EXATAS:")
            for dup in exact_matches[:10]:  # Mostrar apenas as primeiras 10
                print(f"   📄 {dup.file1}")
                print(f"   📄 {dup.file2}")
                print(f"   📊 Similaridade: {dup.similarity:.1%}")
                print()

        if high_similarity:
            print("\n⚠️  ALTA SIMILARIDADE:")
            for dup in high_similarity[:5]:
                print(f"   📄 {dup.file1} (linhas {dup.lines1[0]}-{dup.lines1[1]})")
                print(f"   📄 {dup.file2} (linhas {dup.lines2[0]}-{dup.lines2[1]})")
                print(f"   📊 Similaridade: {dup.similarity:.1%}")
                print()

        # Salvar relatório
        if output_file:
            try:
                report_data = {
                    "summary": {
                        "total_files": result.total_files,
                        "analyzed_files": result.analyzed_files,
                        "total_duplicates": len(result.duplicates),
                        "exact_matches": len(exact_matches),
                        "high_similarity": len(high_similarity),
                        "medium_similarity": len(medium_similarity),
                    },
                    "duplicates": [
                        {
                            "file1": d.file1,
                            "file2": d.file2,
                            "similarity": d.similarity,
                            "lines1": d.lines1,
                            "lines2": d.lines2,
                        }
                        for d in result.duplicates
                    ],
                }

                import json

                Path(output_file).parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(report_data, f, indent=2)
                print(f"\n💾 Relatório salvo em: {output_file}")
            except Exception as e:
                print(f"\n⚠️  Erro ao salvar relatório: {e}")

        # Recomendações
        print("\n💡 RECOMENDAÇÕES:")
        if exact_matches:
            print("   🚨 CRÍTICO: Eliminar duplicações exatas imediatamente")
            print("   🔧 Criar funções/classes compartilhadas")
        if high_similarity:
            print("   ⚠️  Refatorar código com alta similaridade")
            print("   📚 Usar padrões de design para reutilização")
        if len(result.duplicates) > 10:
            print("   📈 Alto número de duplicações detectadas")
            print("   🏗️  Considerar refatoração arquitetural")

        print("   🎯 Seguir padrões FLEXT para código limpo")
        print("   🔄 Implementar revisões de código regulares")


def main() -> None:
    """Função principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Detecta código duplicado no workspace Flext",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--modules",
        nargs="+",
        help="Módulos específicos para analisar",
    )
    parser.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.8,
        help="Limite de similaridade (0.0-1.0, padrão: 0.8)",
    )
    parser.add_argument(
        "--min-lines",
        type=int,
        default=10,
        help="Número mínimo de linhas (padrão: 10)",
    )
    parser.add_argument("--output", help="Arquivo de saída JSON")
    parser.add_argument(
        "--ci-mode",
        action="store_true",
        help="Modo CI/CD - falha se encontrar duplicações críticas",
    )
    parser.add_argument(
        "--all-files",
        action="store_true",
        help="Analisa todos os arquivos rastreáveis pelo git (não apenas código)",
    )

    args = parser.parse_args()

    # Criar detector
    detector = FlextDuplicateDetector(
        similarity_threshold=args.similarity_threshold,
        min_lines=args.min_lines,
        analyze_all_files=args.all_files,
    )

    # Executar análise
    if args.modules:
        result = detector.analyze_modules(args.modules)
    else:
        result = detector.analyze_workspace()

    # Gerar relatório
    detector.generate_report(result, args.output)

    # Verificar modo CI/CD
    if args.ci_mode:
        critical_duplicates = len([
            d for d in result.duplicates if d.similarity >= 0.95
        ])
        if critical_duplicates > 0:
            print(
                f"\n❌ CI/CD: {critical_duplicates} duplicações críticas encontradas!",
            )
            sys.exit(1)
        else:
            print("\n✅ CI/CD: Nenhuma duplicação crítica!")

    print("\n✅ Análise concluída!")


if __name__ == "__main__":
    main()

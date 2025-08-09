#!/usr/bin/env python3
"""Script para detectar código duplicado no workspace Flext.

Este script usa uma abordagem robusta baseada em análise de similaridade
textual e estrutural para detectar duplicações de código.
"""

import argparse
import hashlib
import json
import multiprocessing as mp
import os
import re
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
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
class AntiPatternMatch:
    """Representa um anti-pattern encontrado."""

    file_path: str
    pattern_type: str
    suggested_replacement: str
    lines: tuple[int, int]
    content: str
    severity: str  # 'critical', 'high', 'medium', 'low'


@dataclass
class AnalysisResult:
    """Resultado da análise de duplicação."""

    duplicates: list[DuplicateMatch]
    anti_patterns: list[AntiPatternMatch]
    total_files: int
    analyzed_files: int
    errors: list[str]


class FlextDuplicateDetector:
    """Detector de código duplicado específico para o Flext."""

    def __init__(
        self,
        similarity_threshold: float = 0.65,  # Reduzido para capturar mais padrões
        min_lines: int = 5,  # Reduzido para detectar pequenos padrões anti-pattern
        file_extensions: list[str] | None = None,
        *,
        analyze_all_files: bool = False,
    ) -> None:
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
            self.file_extensions = file_extensions or [
                "py",
                "js",
                "ts",
                "java",
                "go",
                "md",
                "rst",
                "txt",
                "sh",
                "bash",
                "zsh",
                "fish",
            ]

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
            # Adicionar diretórios raiz para análise de documentação
            ".",  # Para README.md, CLAUDE.md, etc. na raiz
            "docs",  # Se houver pasta docs
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
                ext = file_path.rsplit(".", maxsplit=1)[-1].lower()
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
                ext = file_path.rsplit(".", maxsplit=1)[-1].lower()
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
            with Path(file_path).open("rb") as f:
                chunk = f.read(1024)
                if not chunk:
                    return True  # Arquivo vazio é considerado texto

                # Verificar se contém bytes nulos (indicativo de binário)
                if b"\0" in chunk:
                    return False

                # Verificar se a maioria dos bytes são ASCII/UTF-8 válidos
                try:
                    chunk.decode("utf-8")
                except UnicodeDecodeError:
                    try:
                        chunk.decode("latin-1")
                    except UnicodeDecodeError:
                        return False
                    else:
                        return True
                else:
                    return True
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
            # Para Markdown, usar normalização específica
            if "# " in content or "## " in content or "```" in content:
                return self._normalize_markdown_code(content)
            # Para shell scripts, usar normalização específica
            if (
                content.startswith(("#!/bin/bash", "#!/bin/sh"))
                or "function " in content
                or "if [" in content
            ):
                return self._normalize_shell_code(content)
            return self._normalize_generic_code(content)
        except Exception:
            return self._normalize_generic_code(content)

    def _normalize_markdown_code(self, content: str) -> str:
        """Normaliza código Markdown preservando estrutura semântica."""
        try:
            lines = []
            in_code_block = False

            for line in content.split("\n"):
                line_content = line.strip()

                # Detectar blocos de código
                if line_content.startswith("```"):
                    in_code_block = not in_code_block
                    continue

                # Pular linhas vazias
                if not line_content:
                    continue

                # Se estiver em bloco de código, manter conteúdo
                if in_code_block:
                    lines.append(line_content)
                    continue

                # Normalizar headers - manter apenas o nível
                if line_content.startswith("#"):
                    header_level = len(line_content) - len(line_content.lstrip("#"))
                    header_text = line_content.lstrip("# ").strip()
                    if header_text:  # Só adicionar se não for vazio
                        lines.append(f"{'#' * header_level} {header_text.lower()}")
                    continue

                # Remover links mas manter texto
                line_content = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line_content)

                # Remover formatação markdown mas manter conteúdo
                line_content = re.sub(r"\*\*([^*]+)\*\*", r"\1", line_content)  # bold
                line_content = re.sub(r"\*([^*]+)\*", r"\1", line_content)  # italic
                line_content = re.sub(r"`([^`]+)`", r"\1", line_content)  # inline code

                # Normalizar listas
                line_content = re.sub(r"^[-*+]\s+", "- ", line_content)
                line_content = re.sub(r"^\d+\.\s+", "1. ", line_content)

                if line_content.strip():
                    lines.append(line_content.lower())

            normalized = "\n".join(lines)
            # Normalizar múltiplos espaços
            normalized = re.sub(r"\s+", " ", normalized)

            return normalized.strip()
        except Exception:
            return self._normalize_generic_code(content)

    def _normalize_shell_code(self, content: str) -> str:
        """Normaliza código shell preservando estrutura lógica."""
        try:
            lines = []

            for line in content.split("\n"):
                line_content = line.strip()

                # Pular linhas vazias
                if not line_content:
                    continue

                # Pular shebangs (já identificados)
                if line_content.startswith("#!"):
                    continue

                # Remover comentários completos
                if line_content.startswith("#"):
                    continue

                # Remover comentários inline
                if "#" in line_content:
                    # Cuidado com strings que contêm #
                    line_content.find("#")
                    # Verificar se não está dentro de aspas
                    in_quotes = False
                    quote_char = None
                    for i, char in enumerate(line_content):
                        if char in {'"', "'"} and (
                            i == 0 or line_content[i - 1] != "\\"
                        ):
                            if not in_quotes:
                                in_quotes = True
                                quote_char = char
                            elif char == quote_char:
                                in_quotes = False
                                quote_char = None
                        elif char == "#" and not in_quotes:
                            line_content = line_content[:i].strip()
                            break

                if not line_content:
                    continue

                # Normalizar comandos comuns
                line_content = re.sub(r"\s+", " ", line_content)  # Múltiplos espaços
                line_content = re.sub(
                    r"\$\{([^}]+)\}",
                    r"$\1",
                    line_content,
                )  # ${var} -> $var

                # Normalizar strings (manter conteúdo mas simplificar quotes)
                line_content = re.sub(r'"([^"]*)"', r'"\1"', line_content)
                line_content = re.sub(r"'([^']*)'", r"'\1'", line_content)

                lines.append(line_content.lower())

            normalized = "\n".join(lines)
            return normalized.strip()
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
        """Calcula similaridade usando Jaccard optimizado com early exit."""
        if not text1 or not text2:
            return 0.0

        # Fast length check - skip if very different sizes
        if abs(len(text1) - len(text2)) > max(len(text1), len(text2)) * 0.7:
            return 0.0

        # Normalizar textos
        norm1 = self._normalize_code(text1)
        norm2 = self._normalize_code(text2)

        if not norm1 or not norm2:
            return 0.0

        # Fast exact match check first
        if norm1 == norm2:
            return 1.0

        # Quick hash comparison for speed
        hash1 = hash(norm1)
        hash2 = hash(norm2)
        if hash1 == hash2:
            return 1.0

        # Use n-grams for better similarity detection
        ngrams1 = self._get_ngrams(norm1, 3)
        ngrams2 = self._get_ngrams(norm2, 3)

        if not ngrams1 or not ngrams2:
            return 0.0

        intersection = len(ngrams1 & ngrams2)
        union = len(ngrams1 | ngrams2)

        return intersection / union if union > 0 else 0.0

    def _get_ngrams(self, text: str, n: int = 3) -> set[str]:
        """Gera n-gramas para comparação mais eficiente."""
        # Remove espaços extras e converte para lowercase
        text = " ".join(text.split()).lower()

        if len(text) < n:
            return {text}

        return {text[i : i + n] for i in range(len(text) - n + 1)}

    def _get_shingles(self, text: str, k: int = 4) -> set[int]:
        """Gera shingles (hashes de k-grams) para detecção ultra-rápida."""
        text = " ".join(text.split()).lower()
        if len(text) < k:
            return {hash(text)}

        return {hash(text[i : i + k]) for i in range(len(text) - k + 1)}

    def _compute_minhash(self, shingles: set[int], num_hashes: int = 64) -> list[int]:
        """Computa MinHash para estimativa rápida de similaridade Jaccard."""
        if not shingles:
            return [0] * num_hashes

        # Use diferentes seeds para simular diferentes hash functions
        minhashes = []
        for seed in range(num_hashes):
            min_hash = min(hash((seed, s)) for s in shingles)
            minhashes.append(min_hash)

        return minhashes

    def _minhash_similarity(self, minhash1: list[int], minhash2: list[int]) -> float:
        """Calcula similaridade estimada usando MinHash."""
        if not minhash1 or not minhash2:
            return 0.0

        matches = sum(1 for h1, h2 in zip(minhash1, minhash2, strict=False) if h1 == h2)
        return matches / len(minhash1)

    def _create_file_signatures(
        self,
        files_content: dict[str, str],
    ) -> dict[str, tuple[str, set[str], list[int]]]:
        """Cria assinaturas avançadas para detecção ultra-rápida."""
        signatures = {}

        print(f"🔄 Processando {len(files_content)} arquivos para assinaturas...")

        # Use multiprocessing para acelerar a criação de assinaturas
        with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
            future_to_file = {
                executor.submit(
                    self._process_file_signature,
                    content,
                ): file_path
                for file_path, content in files_content.items()
            }

            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    if result:
                        signatures[file_path] = result
                except (OSError, ValueError, TypeError) as e:
                    print(f"⚠️ Erro processando {file_path}: {e}")

        return signatures

    def _process_file_signature(
        self,
        content: str,
    ) -> tuple[str, set[str], list[int]] | None:
        """Processa assinatura de um arquivo individual."""
        normalized = self._normalize_code(content)
        if len(normalized) < 50:
            return None

        # Hash para exact match
        content_hash = hashlib.sha256(normalized.encode()).hexdigest()[:16]

        # N-grams para similarity básica
        ngrams = self._get_ngrams(normalized, 3)

        # MinHash para similarity ultra-rápida
        shingles = self._get_shingles(normalized, 4)
        minhash = self._compute_minhash(shingles, 32)  # Reduzido para performance

        return (content_hash, ngrams, minhash)

    def _find_exact_duplicates(
        self,
        signatures: dict[str, tuple[str, set[str], list[int]]],
        files_content: dict[str, str],
    ) -> list[DuplicateMatch]:
        """Encontra duplicatas exatas usando assinaturas pré-computadas."""
        duplicates = []
        hash_to_files = defaultdict(list)

        # Agrupar por hash
        for file_path, (content_hash, _, _) in signatures.items():
            hash_to_files[content_hash].append(file_path)

        # Gerar pares de duplicatas
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
        signatures: dict[str, tuple[str, set[str], list[int]]],
        files_content: dict[str, str],
    ) -> list[DuplicateMatch]:
        """Encontra blocos similares usando pre-filtering com assinaturas."""
        duplicates = []
        file_blocks = {}

        # Extrair blocos apenas de arquivos que passaram pelo filtro inicial
        for file_path, content in files_content.items():
            if file_path in signatures:
                blocks = self._get_file_blocks(content)
                file_blocks[file_path] = blocks

        # Pre-filter: só comparar arquivos com overlap mínimo de n-grams
        candidate_pairs = self._find_candidate_pairs(signatures)

        print(
            f"🔍 Comparando {len(candidate_pairs)} pares candidatos"
            f" (filtrados de {len(files_content)}²)",
        )

        # Comparar apenas pares candidatos
        for file1, file2 in candidate_pairs:
            if file1 not in file_blocks or file2 not in file_blocks:
                continue

            for block1, start1, end1 in file_blocks[file1]:
                for block2, start2, end2 in file_blocks[file2]:
                    # Skip blocks with very different sizes
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

    def _find_candidate_pairs(
        self,
        signatures: dict[str, tuple[str, set[str], list[int]]],
    ) -> list[tuple[str, str]]:
        """Encontra pares candidatos usando MinHash ultra-rápido."""
        candidates = []
        file_paths = list(signatures.keys())

        print(f"🚀 Filtrando candidatos com MinHash para {len(file_paths)} arquivos...")
        start_time = time.time()

        # Pre-filtro ultra rápido com MinHash
        for i in range(len(file_paths)):
            for j in range(i + 1, len(file_paths)):
                file1, file2 = file_paths[i], file_paths[j]
                _, _, minhash1 = signatures[file1]
                _, _, minhash2 = signatures[file2]

                # MinHash similarity - ultra rápido
                minhash_sim = self._minhash_similarity(minhash1, minhash2)

                # Threshold mais baixo para MinHash (pode ter falsos negativos)
                if minhash_sim >= self.similarity_threshold * 0.6:
                    candidates.append((file1, file2))

        elapsed = time.time() - start_time
        print(f"⚡ MinHash filtering: {len(candidates)} candidatos em {elapsed:.2f}s")

        return candidates

    def _detect_flext_anti_patterns(
        self,
        files_content: dict[str, str],
    ) -> list[AntiPatternMatch]:
        """Detecta anti-patterns que deveriam usar bibliotecas base do FLEXT."""
        anti_patterns = []

        print("🔍 Detectando anti-patterns FLEXT...")

        for file_path, content in files_content.items():
            # Pular arquivos que não são Python
            if not str(file_path).endswith(".py"):
                continue

            # Detectar vários tipos de anti-patterns
            anti_patterns.extend(
                self._detect_manual_result_handling(file_path, content),
            )
            anti_patterns.extend(self._detect_manual_logging_setup(file_path, content))
            anti_patterns.extend(
                self._detect_manual_config_handling(file_path, content),
            )
            anti_patterns.extend(self._detect_manual_domain_models(file_path, content))
            anti_patterns.extend(
                self._detect_manual_service_patterns(file_path, content),
            )
            anti_patterns.extend(
                self._detect_manual_connection_handling(file_path, content),
            )
            anti_patterns.extend(self._detect_manual_error_handling(file_path, content))

        return anti_patterns

    def _detect_manual_result_handling(
        self,
        file_path: str,
        content: str,
    ) -> list[AntiPatternMatch]:
        """Detecta manipulação manual de resultados que deveria usar FlextResult."""
        patterns = []
        lines = content.split("\n")

        # Padrões que indicam resultado manual ao invés de FlextResult
        anti_pattern_indicators = [
            (
                r"return\s+\(\s*True\s*,\s*[^)]+\s*\)",
                "Manual tuple result instead of FlextResult.ok()",
            ),
            (
                r"return\s+\(\s*False\s*,\s*[^)]+\s*\)",
                "Manual tuple result instead of FlextResult(success=False, )",
            ),
            (
                r'return\s+\{\s*["\']success["\']\s*:\s*True',
                "Manual dict result instead of FlextResult.ok()",
            ),
            (
                r'return\s+\{\s*["\']success["\']\s*:\s*False',
                "Manual dict result instead of FlextResult(success=False, )",
            ),
            (
                r'return\s+\{\s*["\']error["\']\s*:',
                "Manual error dict instead of FlextResult(success=False, )",
            ),
            (
                r"if\s+result\[0\]\s*:",
                "Manual tuple unpacking instead of FlextResult.success",
            ),
            (
                r'if\s+result\[["\']success["\']\]\s*:',
                "Manual dict access instead of FlextResult.success",
            ),
        ]

        for i, line in enumerate(lines):
            line_content = line.strip()
            if not line_content or line_content.startswith("#"):
                continue

            for pattern, _description in anti_pattern_indicators:
                if re.search(pattern, line_content):
                    patterns.append(
                        AntiPatternMatch(
                            file_path=file_path,
                            pattern_type="Manual Result Handling",
                            suggested_replacement="Use FlextResult from"
                            " flext-core: {description}",
                            lines=(i + 1, i + 1),
                            content=line_content,
                            severity="high",
                        ),
                    )

        return patterns

    def _detect_manual_logging_setup(
        self,
        file_path: str,
        content: str,
    ) -> list[AntiPatternMatch]:
        """Detecta configuração manual de logging que deveria usar flext-core."""
        patterns = []
        lines = content.split("\n")

        # Padrões que indicam logging manual
        anti_pattern_indicators = [
            (
                r"import\s+logging",
                "Direct logging import instead of flext-core",
            ),
            (
                r"logging\.getLogger\s*\(",
                "Manual logger creation instead of get_logger from flext-core",
            ),
            (
                r"logging\.basicConfig\s*\(",
                "Manual logging config instead of flext-core get_logger",
            ),
            (
                r"logger\s*=\s*logging\.getLogger",
                "Manual logger creation instead of get_logger",
            ),
        ]

        for i, line in enumerate(lines):
            line_content = line.strip()
            if not line_content or line_content.startswith("#"):
                continue

            for pattern, description in anti_pattern_indicators:
                if re.search(pattern, line_content):
                    # Verificar se já está usando flext-core
                    if "from flext_core" in content or "flext_core.logging" in content:
                        continue

                    patterns.append(
                        AntiPatternMatch(
                            file_path=file_path,
                            pattern_type="Manual Logging Setup",
                            suggested_replacement=f"Use flext_core: {description}",
                            lines=(i + 1, i + 1),
                            content=line_content,
                            severity="medium",
                        ),
                    )

        return patterns

    def _detect_manual_config_handling(
        self,
        file_path: str,
        content: str,
    ) -> list[AntiPatternMatch]:
        """Detecta manipulação manual de configuração que deveria usar BaseConfig."""
        patterns = []
        lines = content.split("\n")

        # Padrões que indicam config manual
        anti_pattern_indicators = [
            (
                r"os\.environ\.get\s*\(",
                "Manual environment variable access instead of BaseConfig",
            ),
            (
                r"os\.getenv\s*\(",
                "Manual environment variable access instead of BaseConfig",
            ),
            (
                r"class\s+\w+Config.*:",
                "Manual config class instead of inheriting from BaseConfig",
            ),
            (r"def\s+load_config\s*\(", "Manual config loading instead of BaseConfig"),
        ]

        for i, line in enumerate(lines):
            line_content = line.strip()
            if not line_content or line_content.startswith("#"):
                continue

            for pattern, description in anti_pattern_indicators:
                if re.search(pattern, line_content):
                    # Verificar se já está usando flext-core BaseConfig
                    if "from flext_core" in content and "BaseConfig" in content:
                        continue

                    patterns.append(
                        AntiPatternMatch(
                            file_path=file_path,
                            pattern_type="Manual Config Handling",
                            suggested_replacement=f"Use BaseConfig from"
                            f" flext-core: {description}",
                            lines=(i + 1, i + 1),
                            content=line_content,
                            severity="medium",
                        ),
                    )

        return patterns

    def _detect_manual_domain_models(
        self,
        file_path: str,
        content: str,
    ) -> list[AntiPatternMatch]:
        """Detecta modelos de domínio manuais que deveriam usar FlextDomainBaseModel."""
        patterns = []
        lines = content.split("\n")

        # Padrões que indicam domain models manuais
        anti_pattern_indicators = [
            (
                r"from\s+pydantic\s+import\s+BaseModel",
                "Direct BaseModel import instead of FlextDomainBaseModel",
            ),
            (
                r"class\s+\w+\(BaseModel\)",
                "Manual BaseModel inheritance instead of FlextDomainBaseModel",
            ),
            (
                r"from\s+dataclasses\s+import\s+dataclass",
                "Dataclass instead of FlextDomainBaseModel for domain objects",
            ),
            (
                r"@dataclass",
                "Dataclass decorator instead of FlextDomainBaseModel fordomain objects",
            ),
        ]

        for i, line in enumerate(lines):
            line_content = line.strip()
            if not line_content or line_content.startswith("#"):
                continue

            for pattern, description in anti_pattern_indicators:
                if re.search(pattern, line_content):
                    # Verificar se já está usando flext-core
                    if "from flext_core" in content and (
                        "FlextDomainBaseModel" in content
                        or "FlextValueObject" in content
                    ):
                        continue

                    # Pular se estiver em arquivo de teste ou config
                    if "test" in file_path.lower() or "config" in file_path.lower():
                        continue

                    patterns.append(
                        AntiPatternMatch(
                            file_path=file_path,
                            pattern_type="Manual Domain Models",
                            suggested_replacement="Use FlextDomainBaseModel ou"
                            f"FlextValueObject from flext-core: {description}",
                            lines=(i + 1, i + 1),
                            content=line_content,
                            severity="medium",
                        ),
                    )

        return patterns

    def _detect_manual_service_patterns(
        self,
        file_path: str,
        content: str,
    ) -> list[AntiPatternMatch]:
        """Detecta padrões de serviço manuais que deveriam seguir arquitetura FLEXT."""
        patterns = []
        lines = content.split("\n")

        # Padrões que indicam serviços não seguindo padrão FLEXT
        indicators = [
            (
                r"def\s+\w+\s*\([^)]*\)\s*:\s*\n.*try:",
                "Manual try/catch instead of FlextResult pattern",
            ),
            (
                r"raise\s+Exception\s*\(",
                "Generic Exception instead of domain-specific exceptions",
            ),
            (
                r"raise\s+ValueError\s*\(",
                "ValueError instead of FlextResult(success=False, )",
            ),
            (
                r"raise\s+RuntimeError\s*\(",
                "RuntimeError instead of FlextResult(success=False, )",
            ),
        ]

        for i, line in enumerate(lines):
            line_content = line.strip()
            if not line_content or line_content.startswith("#"):
                continue

            for pattern, description in indicators:
                if (
                    re.search(pattern, line_content)
                    and i > 0
                    and (
                        "service" in lines[i - 1].lower() or "async def" in lines[i - 1]
                    )
                ):
                    patterns.append(
                        AntiPatternMatch(
                            file_path=file_path,
                            pattern_type="Manual Service Patterns",
                            suggested_replacement=f"Follow FLEXT service patterns: {description}",
                            lines=(i + 1, i + 1),
                            content=line_content,
                            severity="medium",
                        ),
                    )

        return patterns

    def _detect_manual_connection_handling(
        self,
        file_path: str,
        content: str,
    ) -> list[AntiPatternMatch]:
        """Detecta manipulação manual de conexões que deveria usar serviços FLEXT."""
        patterns = []
        lines = content.split("\n")

        # Padrões para diferentes tipos de conexão
        connection_patterns = [
            (
                r"import\s+cx_Oracle",
                "cx_Oracle instead of modern oracledb and FLEXT services",
            ),
            (
                r"import\s+psycopg2",
                "Direct psycopg2 instead of FLEXT database services",
            ),
            (r"import\s+pymongo", "Direct pymongo instead of FLEXT database services"),
            (r"import\s+redis", "Direct redis instead of FLEXT caching services"),
            (r"import\s+ldap", "Direct python-ldap instead of FLEXT LDAP services"),
            (
                r"\.connect\s*\(",
                "Manual connection management instead of FLEXT connection services",
            ),
            (
                r"\.close\s*\(\s*\)",
                "Manual connection closing instead of FLEXT context managers",
            ),
        ]

        for i, line in enumerate(lines):
            line_content = line.strip()
            if not line_content or line_content.startswith("#"):
                continue

            for pattern, description in connection_patterns:
                if re.search(pattern, line_content):
                    patterns.append(
                        AntiPatternMatch(
                            file_path=file_path,
                            pattern_type="Manual Connection Handling",
                            suggested_replacement=f"Use FLEXT connection services: {description}",
                            lines=(i + 1, i + 1),
                            content=line_content,
                            severity="high",
                        ),
                    )

        return patterns

    def _detect_manual_error_handling(
        self,
        file_path: str,
        content: str,
    ) -> list[AntiPatternMatch]:
        """Detecta tratamento manual de erros que deveria usar padrões FLEXT."""
        patterns = []
        lines = content.split("\n")

        # Padrões de error handling que não seguem FLEXT
        error_patterns = [
            (
                r"except\s+Exception\s+as\s+e:\s*\n.*print\s*\(",
                "Print for error instead of structured logging",
            ),
            (
                r"except.*:\s*\n.*pass",
                "Silent exception swallowing instead of proper error handling",
            ),
            (
                r"try:\s*\n.*\n.*except.*:\s*\n.*return\s+None",
                "Return None on error instead of FlextResult(success=False, )",
            ),
            (
                r"try:\s*\n.*\n.*except.*:\s*\n.*return\s+False",
                "Return False on error instead of FlextResult(success=False, )",
            ),
        ]

        for i, line in enumerate(lines):
            line_content = line.strip()
            if not line_content or line_content.startswith("#"):
                continue

            for pattern, description in error_patterns:
                if re.search(pattern, line_content):
                    patterns.append(
                        AntiPatternMatch(
                            file_path=file_path,
                            pattern_type="Manual Error Handling",
                            suggested_replacement=f"Use FLEXT error handling patterns: {description}",
                            lines=(i + 1, i + 1),
                            content=line_content,
                            severity="high",
                        ),
                    )

        return patterns

    def _find_similar_blocks_batched(
        self,
        signatures: dict[str, tuple[str, set[str], list[int]]],
        files_content: dict[str, str],
        batch_size: int = 100,
    ) -> list[DuplicateMatch]:
        """Processa em lotes usando assinaturas pré-computadas."""
        duplicates = []
        list(signatures.keys())

        # Pre-filter global para reduzir candidate pairs
        all_candidates = self._find_candidate_pairs(signatures)

        # Dividir candidates em batches
        for i in range(0, len(all_candidates), batch_size):
            batch_candidates = all_candidates[i : i + batch_size]

            print(
                f"📦 Processando lote {i // batch_size + 1}/{(len(all_candidates) + batch_size - 1) // batch_size} ({len(batch_candidates)} pares)...",
            )

            # Processar apenas os candidates deste batch
            batch_files = set()
            for file1, file2 in batch_candidates:
                batch_files.add(file1)
                batch_files.add(file2)

            batch_content = {
                f: files_content[f] for f in batch_files if f in files_content
            }
            batch_signatures = {
                f: signatures[f] for f in batch_files if f in signatures
            }

            batch_duplicates = self._find_similar_blocks(
                batch_signatures,
                batch_content,
            )
            duplicates.extend(batch_duplicates)

        return duplicates

    def _collect_files(self, modules: list[str]) -> dict[str, str]:
        """Coleta conteúdo dos arquivos para análise com otimização de memória."""
        files_content: dict[str, str] = {}
        errors = []
        max_file_size = 2 * 1024 * 1024  # 2MB limit per file (aumentado)
        total_size = 0
        max_total_size = 512 * 1024 * 1024  # 512MB total limit

        for module in modules:
            if not Path(module).exists():
                errors.append(f"Módulo não encontrado: {module}")
                continue

            # Para diretório raiz, processar arquivos de documentação e configuração
            if module == ".":
                for file in Path().iterdir():
                    file_str = str(file)
                    # Incluir arquivos de documentação, configuração e scripts
                    if (
                        file.is_file()
                        and not self._should_skip_file(file_str)
                        and (
                            file_str.endswith(
                                (
                                    ".md",
                                    ".rst",
                                    ".txt",
                                    ".sh",
                                    ".bash",
                                    ".zsh",
                                    ".fish",
                                ),
                            )
                            or file_str
                            in {
                                "Makefile",
                                "Dockerfile",
                                "LICENSE",
                                "CHANGELOG",
                                "CONTRIBUTING",
                            }
                            or self._is_text_file(file_str)
                        )
                    ):
                        try:
                            file_size = file.stat().st_size

                            if file_size > max_file_size:
                                print(
                                    f"⚠️ Pulando arquivo muito grande: {file_str} "
                                    f"({file_size // 1024}KB)",
                                )
                                continue

                            if total_size + file_size > max_total_size:
                                print(
                                    "⚠️ Limite de memória atingido, "
                                    "processando em lotes...",
                                )
                                break

                            with file.open(
                                encoding="utf-8",
                                errors="ignore",
                            ) as f:
                                content = f.read()

                            if len(content.strip()) >= 50:
                                files_content[file_str] = content
                                total_size += len(content)

                        except (OSError, ValueError, TypeError) as e:
                            errors.append(f"Erro ao ler {file_str}: {e}")
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

                for filename in files:
                    file_path: str = str(Path(root) / filename)

                    if self._should_skip_file(file_path):
                        continue

                    try:
                        # Check file size before reading
                        file_size = Path(file_path).stat().st_size

                        # Skip files that are too large
                        if file_size > max_file_size:
                            print(
                                f"⚠️ Pulando arquivo muito grande: {file_path} "
                                f"({file_size // 1024}KB)",
                            )
                            continue

                        # Check total memory usage
                        if total_size + file_size > max_total_size:
                            print(
                                "⚠️ Limite de memória atingido, processando em lotes...",
                            )
                            break

                        # Read file efficiently
                        if file_size > 256 * 1024:  # 256KB
                            content = self._read_file_chunked(file_path)
                        else:
                            with Path(file_path).open(
                                encoding="utf-8",
                                errors="ignore",
                            ) as f:
                                content = f.read()

                        # Filtrar arquivos muito pequenos ou vazios
                        if len(content.strip()) < 50:  # Reduzido de 100 para 50
                            continue

                        files_content[file_path] = content
                        total_size += len(content)

                    except (OSError, ValueError, TypeError) as e:
                        errors.append(f"Erro ao ler {file_path}: {e}")

        print(
            f"📁 Coletados {len(files_content)} arquivos "
            f"({total_size // 1024 // 1024}MB)",
        )
        return files_content

    def _read_file_chunked(self, file_path: str) -> str:
        """Lê arquivo em chunks para economizar memória."""
        try:
            with Path(file_path).open(encoding="utf-8", errors="ignore") as f:
                chunks = []
                while True:
                    chunk = f.read(8192)  # 8KB chunks
                    if not chunk:
                        break
                    chunks.append(chunk)
                return "".join(chunks)
        except Exception:
            return ""

    def analyze_workspace(self) -> AnalysisResult:
        """Analisa todo o workspace para duplicações."""
        print("🔍 Analisando workspace Flext para código duplicado...")

        # Filtrar módulos existentes
        existing_modules = [m for m in self.flext_modules if Path(m).exists()]

        if not existing_modules:
            return AnalysisResult([], [], 0, 0, ["Nenhum módulo encontrado"])

        print(f"📦 Analisando {len(existing_modules)} módulos...")

        # Coletar arquivos
        files_content = self._collect_files(existing_modules)
        if not files_content:
            return AnalysisResult([], [], 0, 0, ["Nenhum arquivo válido encontrado"])

        print(f"📄 Analisando {len(files_content)} arquivos...")

        # Criar assinaturas para otimização
        print("🔄 Criando assinaturas de arquivos...")
        signatures = self._create_file_signatures(files_content)
        print(f"✅ {len(signatures)} assinaturas criadas")

        # Encontrar duplicações
        duplicates = []

        # 1. Duplicatas exatas
        exact_duplicates = self._find_exact_duplicates(signatures, files_content)
        duplicates.extend(exact_duplicates)
        print(f"🔍 Encontradas {len(exact_duplicates)} duplicações exatas")

        # 2. Blocos similares (sempre usar versão otimizada)
        if len(files_content) > 20:
            print("⚡ Processando similaridade em lotes ultra-otimizados...")
            similar_blocks = self._find_similar_blocks_batched(
                signatures,
                files_content,
            )
        else:
            similar_blocks = self._find_similar_blocks(signatures, files_content)
        duplicates.extend(similar_blocks)
        print(f"🔍 Encontrados {len(similar_blocks)} blocos similares")

        # 3. Anti-patterns FLEXT
        anti_patterns = self._detect_flext_anti_patterns(files_content)
        print(f"🚨 Encontrados {len(anti_patterns)} anti-patterns FLEXT")

        return AnalysisResult(
            duplicates=duplicates,
            anti_patterns=anti_patterns,
            total_files=len(files_content),
            analyzed_files=len(files_content),
            errors=[],
        )

    def analyze_modules(self, modules: list[str]) -> AnalysisResult:
        """Analisa módulos específicos."""
        print(f"🔍 Analisando módulos: {', '.join(modules)}")

        files_content = self._collect_files(modules)
        if not files_content:
            return AnalysisResult([], [], 0, 0, ["Nenhum arquivo encontrado"])

        # Criar assinaturas
        signatures = self._create_file_signatures(files_content)

        duplicates = []
        duplicates.extend(self._find_exact_duplicates(signatures, files_content))
        duplicates.extend(self._find_similar_blocks(signatures, files_content))

        # Detectar anti-patterns também nos módulos específicos
        anti_patterns = self._detect_flext_anti_patterns(files_content)

        return AnalysisResult(
            duplicates=duplicates,
            anti_patterns=anti_patterns,
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
        print(f"   🚨 Total de anti-patterns: {len(result.anti_patterns)}")

        if not result.duplicates and not result.anti_patterns:
            print("✅ Nenhuma duplicação ou anti-pattern encontrado!")
            print("🎉 O código está bem estruturado!")
            return

        # Agrupar por tipo
        exact_matches = [d for d in result.duplicates if d.similarity >= 0.99]
        high_similarity = [d for d in result.duplicates if 0.9 <= d.similarity < 0.99]
        medium_similarity = [d for d in result.duplicates if 0.8 <= d.similarity < 0.9]

        print(f"   🚨 Duplicações exatas (≥99%): {len(exact_matches)}")
        print(f"   ⚠️  Alta similaridade (90-99%): {len(high_similarity)}")
        print(f"   i Média similaridade (80-90%): {len(medium_similarity)}")

        # Agrupar anti-patterns por severidade e tipo
        critical_patterns = [
            p for p in result.anti_patterns if p.severity == "critical"
        ]
        high_patterns = [p for p in result.anti_patterns if p.severity == "high"]
        medium_patterns = [p for p in result.anti_patterns if p.severity == "medium"]
        low_patterns = [p for p in result.anti_patterns if p.severity == "low"]

        print(f"   🔴 Anti-patterns críticos: {len(critical_patterns)}")
        print(f"   🟠 Anti-patterns altos: {len(high_patterns)}")
        print(f"   🟡 Anti-patterns médios: {len(medium_patterns)}")
        print(f"   🟢 Anti-patterns baixos: {len(low_patterns)}")

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

        # Mostrar anti-patterns críticos
        if critical_patterns or high_patterns:
            print("\n🚨 ANTI-PATTERNS CRÍTICOS/ALTOS:")
            for pattern in (critical_patterns + high_patterns)[
                :10
            ]:  # Mostrar apenas os primeiros 10
                print(f"   📄 {pattern.file_path} (linha {pattern.lines[0]})")
                print(f"   🏷️  Tipo: {pattern.pattern_type}")
                print(f"   💡 Sugestão: {pattern.suggested_replacement}")
                print(f"   📝 Código: {pattern.content[:80]}...")
                print()

        if medium_patterns:
            print(f"\n🟡 ANTI-PATTERNS MÉDIOS ({len(medium_patterns)} encontrados):")
            # Agrupar por tipo para melhor visualização
            by_type: dict[str, list[AntiPatternMatch]] = {}
            for pattern in medium_patterns:
                if pattern.pattern_type not in by_type:
                    by_type[pattern.pattern_type] = []
                by_type[pattern.pattern_type].append(pattern)

            for pattern_type, patterns in by_type.items():
                print(f"   📋 {pattern_type}: {len(patterns)} ocorrências")
                for pattern in patterns[:3]:  # Mostrar apenas 3 exemplos por tipo
                    print(f"      📄 {pattern.file_path} (linha {pattern.lines[0]})")

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
                        "total_anti_patterns": len(result.anti_patterns),
                        "critical_patterns": len(critical_patterns),
                        "high_patterns": len(high_patterns),
                        "medium_patterns": len(medium_patterns),
                        "low_patterns": len(low_patterns),
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
                    "anti_patterns": [
                        {
                            "file_path": p.file_path,
                            "pattern_type": p.pattern_type,
                            "suggested_replacement": p.suggested_replacement,
                            "lines": p.lines,
                            "content": p.content,
                            "severity": p.severity,
                        }
                        for p in result.anti_patterns
                    ],
                }
                Path(output_file).parent.mkdir(parents=True, exist_ok=True)
                with Path(output_file).open("w", encoding="utf-8") as f:
                    json.dump(report_data, f, indent=2)
                print(f"\n💾 Relatório salvo em: {output_file}")
            except (OSError, ValueError, TypeError) as e:
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
    result = (
        detector.analyze_modules(args.modules)
        if args.modules
        else detector.analyze_workspace()
    )

    # Gerar relatório
    detector.generate_report(result, args.output)

    # Verificar modo CI/CD
    if args.ci_mode:
        critical_duplicates = len(
            [d for d in result.duplicates if d.similarity >= 0.95],
        )
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

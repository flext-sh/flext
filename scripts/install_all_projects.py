#!/usr/bin/env python3
"""Script para instalar todos os projetos FLEXT em modo de desenvolvimento.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

Este script instala todos os projetos FLEXT em modo de desenvolvimento
com suas dependências completas via Poetry.
"""

import shutil
import subprocess
import sys
from pathlib import Path


def get_project_directories() -> list[str]:
    """Obter lista de diretórios de projetos principais FLEXT.

    Varre recursivamente o workspace raiz para encontrar todos os projetos
    FLEXT válidos baseado na presença de arquivos pyproject.toml. Automaticamente
    exclui diretórios de sistema, backups e arquivos temporários.

    Returns:
        Lista de caminhos de diretórios dos projetos descobertos, ordenada
        alfabeticamente.

    Example:
        >>> projects = get_project_directories()
        >>> print(f"Encontrados {len(projects)} projetos")
        >>> for project in projects:
        ...     print(f"  - {Path(project).name}")

    Note:
        Exclui automaticamente:
        - Diretórios .venv (ambientes virtuais)
        - Diretórios .flext_backups (backups do sistema)
        - Diretórios test_failures (falhas de teste)
        - O diretório workspace raiz

    """
    workspace_root = Path(__file__).parent.parent
    projects = []

    # Projetos principais (excluindo backups e arquivos temporários)
    for pyproject in workspace_root.rglob("pyproject.toml"):
        if any(
            exclude in str(pyproject)
            for exclude in [".venv", ".flext_backups", "test_failures"]
        ):
            continue

        project_dir = pyproject.parent
        if project_dir != workspace_root:  # Excluir workspace root
            projects.append(str(project_dir))

    return sorted(projects)


def run_poetry_install(project_dir: str) -> tuple[bool, str]:
    """Executar poetry install em um projeto específico.

    Executa o comando 'poetry install' em um diretório de projeto, com
    tratamento abrangente de erros, timeout e validação de segurança.

    Args:
        project_dir: Caminho para o diretório do projeto onde executar
                    a instalação. Deve conter um arquivo pyproject.toml.

    Returns:
        Tupla contendo:
        - bool: True se instalação foi bem-sucedida, False caso contrário
        - str: Mensagem de status (sucesso ou erro detalhado)

    Raises:
        Não levanta exceções - todos os erros são capturados e retornados
        como mensagens de status na tupla de retorno.

    Example:
        >>> success, message = run_poetry_install("/path/to/flext-core")
        >>> if success:
        ...     print(f"Instalação bem-sucedida: {message}")
        ... else:
        ...     print(f"Falha na instalação: {message}")

    Note:
        - Timeout de 5 minutos por projeto
        - Valida presença do executável poetry
        - Captura stdout e stderr para diagnóstico
        - Usa shell=False para segurança

    """
    try:
        print(f"📦 Instalando {Path(project_dir).name}...")

        # Verificar se existe pyproject.toml
        pyproject_path = Path(project_dir) / "pyproject.toml"  # PTH118
        if not pyproject_path.exists():
            return False, f"pyproject.toml não encontrado em {project_dir}"

        # Encontrar o caminho completo para o executável 'poetry'
        poetry_executable = shutil.which("poetry")
        if not poetry_executable:
            return False, "❌ Erro: Executável 'poetry' não encontrado no PATH"

        # Executar poetry install
        result = subprocess.run(  # noqa: S603
            [poetry_executable, "install"],  # Validated: uses poetry from shutil.which
            check=False,
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutos timeout
            shell=False,
        )

        if result.returncode == 0:
            return True, "✅ Sucesso"
        return False, f"❌ Erro: {result.stderr}"

    except subprocess.TimeoutExpired:
        return False, "❌ Timeout (5 minutos)"
    except (OSError, ValueError, TypeError) as e:
        return False, f"❌ Exceção: {e!s}"


def main() -> int:
    """Função principal para instalação completa de todos os projetos FLEXT.

    Executa o processo completo de descoberta de projetos e instalação
    via Poetry, com relatório detalhado de sucessos e falhas.

    Returns:
        Código de saída do processo:
        - 0: Todos os projetos foram instalados com sucesso
        - 1: Um ou mais projetos falharam na instalação

    Example:
        Executar como script:
        ```bash
        python scripts/install_all_projects.py
        ```

        Ou programaticamente:
        ```python
        exit_code = main()
        if exit_code == 0:
            print("Todos os projetos instalados!")
        ```

    Note:
        Produz saída detalhada incluindo:
        - Lista de projetos descobertos
        - Progresso de instalação de cada projeto
        - Resumo final com estatísticas de sucesso/falha
        - Lista de projetos que falharam (se houver)

    """
    print("🚀 INSTALADOR DE TODOS OS PROJETOS FLEXT")
    print("=" * 50)

    # Obter projetos
    projects = get_project_directories()
    print(f"📋 Encontrados {len(projects)} projetos para instalar:")

    for project in projects:
        print(f"  - {Path(project).name}")

    print("\n" + "=" * 50)

    # Instalar projetos
    results = []
    for project in projects:
        success, message = run_poetry_install(project)
        results.append((project, success, message))
        print(f"  {Path(project).name}: {message}")

    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DA INSTALAÇÃO:")

    successful = sum(1 for _, success, _ in results if success)
    failed = len(results) - successful

    print(f"✅ Sucessos: {successful}")
    print(f"❌ Falhas: {failed}")

    if failed > 0:
        print("\n❌ PROJETOS COM FALHA:")
        for project, success, message in results:
            if not success:
                print(f"  - {Path(project).name}: {message}")

    print(
        "\n🎉 Instalação concluída! "
        f"{successful}/{len(results)} projetos instalados com sucesso."
    )

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

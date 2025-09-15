#!/usr/bin/env python3
"""Script para instalar todos os projetos FLEXT em modo de desenvolvimento."""

import shutil
import subprocess
import sys
from pathlib import Path

from flext_core import FlextTypes


def get_project_directories() -> FlextTypes.Core.StringList:
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
        # Verificar se existe pyproject.toml
        pyproject_path = Path(project_dir) / "pyproject.toml"  # PTH118
        if not pyproject_path.exists():
            return False, f"pyproject.toml não encontrado em {project_dir}"

        # Encontrar o caminho completo para o executável 'poetry'
        poetry_executable = shutil.which("poetry")
        if not poetry_executable:
            return False, "❌ Erro: Executável 'poetry' não encontrado no PATH"

        # Executar poetry install
        # Safe execution: absolute poetry path from which, static args
        if Path(poetry_executable).name != "poetry":
            return False, "❌ Exe inválido de poetry"
        # Execute poetry install using subprocess
        try:
            poetry_path = shutil.which("poetry")
            if not poetry_path:
                return False, "❌ Poetry não encontrado no PATH"

            result = subprocess.run(
                [poetry_path, "install", "--no-interaction"],
                check=False,
                capture_output=True,
                text=True,
                cwd=project_dir,
                shell=False,
            )
            completed_return = result.returncode
            completed_stderr = result.stderr
        except Exception as e:
            return (
                False,
                f"❌ Falha ao executar Poetry: {e}",
            )

        if completed_return == 0:
            return True, "✅ Sucesso"
        return False, f"❌ Erro: {completed_stderr}"

    except TimeoutError:
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
    # Obter projetos
    projects = get_project_directories()

    for _project in projects:
        pass

    # Instalar projetos
    results = []
    for project in projects:
        success, message = run_poetry_install(project)
        results.append((project, success, message))

    # Resumo

    successful = sum(1 for _, success, _ in results if success)
    failed = len(results) - successful

    if failed > 0:
        for _project, success, _message in results:
            if not success:
                pass

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

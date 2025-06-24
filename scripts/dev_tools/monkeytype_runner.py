#!/usr/bin/env python3
"""MonkeyType Runner Script - Type Collection for Python Projects.

This script runs tests with MonkeyType instrumentation to collect runtime type information,
which can then be applied to code to help with type annotations for mypy and pydantic.

Usage:
    python monkeytype_runner.py run --flx_project <project_dir> [--tests <test_path>]
    python monkeytype_runner.py apply --flx_project <project_dir> --module <module_path>
    python monkeytype_runner.py list --flx_project <project_dir>
    python monkeytype_runner.py stub --flx_project <project_dir> --module <module_path>

Examples:
    # Run all tests in a flx_project with MonkeyType tracing
    python monkeytype_runner.py run --flx_project dc-api-x

    # Run specific test file with MonkeyType
    python monkeytype_runner.py run --flx_project dc-api-x --tests tests/unit/test_config.py

    # list collected modules with type information
    python monkeytype_runner.py list --flx_project dc-api-x

    # Apply collected types to a specific module
    python monkeytype_runner.py apply --flx_project dc-api-x --module dc_api_x.config

    # Generate stub file from collected types
    python monkeytype_runner.py stub --flx_project dc-api-x --module dc_api_x.config

"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


class MonkeyTypeRunner:
    """Runner for MonkeyType type collection and application."""

    def __init__(self, workspace_root: str | Path | None = None) -> None:
        """Initialize the runner with workspace path."""
        if workspace_root is None:
            # Try to find the workspace root (git root or current directory)
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "--show-toplevel"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.workspace_root = (
                    Path(result.stdout.strip())
                    if result.returncode == 0
                    else Path.cwd()
                )
            except (FileNotFoundError, subprocess.SubprocessError):
                self.workspace_root = Path.cwd()
            self.workspace_root = Path(workspace_root)

        self.venv_dir = self.workspace_root / ".venv"
        self.python_exe = self.venv_dir / "bin" / "python"
        self.monkeytype_exe = self.venv_dir / "bin" / "monkeytype"

        # Create database directory if it doesn't exist
        self.db_dir = self.workspace_root / ".monkeytype"
        self.db_dir.mkdir(exist_ok=True)

    def run_tests_with_monkeytype(
        self,
        project_dir: str,
        test_path: str | None = None,
    ) -> int:
        """Run pytest with MonkeyType instrumentation."""
        project_path = self.workspace_root / project_dir

        if not project_path.exists():
            print(f"Error: Project directory {project_path} not found")
            return 1

        os.chdir(project_path)

        # Set up the database file specific to this flx_project
        db_file = self.db_dir / f"{project_dir}.sqlite"
        db_file_absolute = str(db_file.absolute())
        os.environ["MONKEYTYPE_DB"] = f"sqlite:///{db_file_absolute}"

        print(f"MonkeyType database: {db_file_absolute}")

        # Build the pytest command with monkeytype
        cmd = [
            str(self.python_exe),
            "-m",
            "monkeytype",
            "run",
            "-m",
            "pytest",
        ]

        # Add the test path if specified
        if test_path:
            test_path_full = project_path / test_path
            if not test_path_full.exists():
                print(f"Error: Test path {test_path_full} not found")
                return 1
            cmd.append(str(test_path))

        print(f"Running tests with MonkeyType in {project_dir}")
        result = subprocess.run(cmd, check=False)

        if result.returncode == 0:
            print("\nMonkeyType successfully collected types during test execution.")
            print("\nTo apply collected types:")
            print(
                f"  python {Path(__file__).name} apply --flx_project {
                    project_dir
                } --module <module_path>",
            )
            print("\nTo list modules with type information:")
            print(f"  python {Path(__file__).name} list --flx_project {project_dir}")

        return result.returncode

    def list_modules(self, project_dir: str) -> int:
        """List modules with collected type information."""
        db_file = self.db_dir / f"{project_dir}.sqlite"
        db_file_absolute = str(db_file.absolute())

        if not db_file.exists():
            print(f"Error: No type information database found for {project_dir}")
            print(
                f"Run tests first: python {Path(__file__).name} run --flx_project {
                    project_dir
                }",
            )
            return 1

        os.environ["MONKEYTYPE_DB"] = f"sqlite:///{db_file_absolute}"
        print(f"Using database: {db_file_absolute}")

        cmd = [str(self.monkeytype_exe), "list-modules"]

        print(f"Listing modules with type information for {project_dir}:")
        result = subprocess.run(cmd, check=False)
        return result.returncode

    def apply_types(self, module_path: str) -> int:
        """Aplica tipos coletados a um módulo.

        Args:
            module_path: Caminho do módulo para aplicar os tipos

        Returns:
            Código de retorno do comando

        """
        # Aplica os tipos usando o comando monkeytype apply diretamente
        # O MonkeyType encontrará o módulo por si só, sem necessidade de
        # verificarmos o caminho
        cmd = [
            "monkeytype",
            "apply",
            module_path,
        ]

        print(f"Aplicando tipos ao módulo {module_path}")
        result = subprocess.run(cmd, check=False)

        if result.returncode == 0:
            print(f"\nTipos aplicados com sucesso ao módulo {module_path}")
            print(
                "Não se esqueça de verificar as alterações e executar mypy para validar os tipos.",
            )
            print("\nPara verificar a conformidade dos tipos:")
            print(
                f"  cd {self.workspace_root} && python -m mypy src/{
                    module_path.replace('.', '/')
                }.py",
            )

            # Guia para modelos Pydantic
            if "models" in module_path or "schema" in module_path:
                print("\nDica para integração com Pydantic:")
                print(
                    "  Para classes de modelo, você pode converter anotações de tipo para campos Pydantic:",
                )
                print("  Em vez de:")
                print("    def __init__(self, name: str, age: Optional[int] = None):")
                print("  Use:")
                print("    class User(BaseModel):")
                print("        name: str")
                print("        age: Optional[int] = None")

        return result.returncode

    def generate_stub(self, module_path: str) -> int:
        """Gera stub com tipos coletados.

        Args:
            module_path: Caminho do módulo para gerar o stub

        Returns:
            Código de retorno do comando

        """
        # Gera o stub usando o comando monkeytype stub diretamente
        # O MonkeyType encontrará o módulo por si só, sem necessidade de
        # verificarmos o caminho
        cmd = [
            "monkeytype",
            "stub",
            module_path,
        ]

        print(f"Gerando stub de tipos para o módulo {module_path}")
        result = subprocess.run(cmd, check=False)

        if result.returncode == 0:
            print(f"\nStub de tipos gerado com sucesso para {module_path}")
            print(
                "Revise o stub gerado e aplique-o manualmente ao seu código, se necessário.",
            )

            # Dicas para integração com Pydantic
            if "models" in module_path or "schema" in module_path:
                print("\nDica para integração com Pydantic:")
                print(
                    "  Para classes de modelo, converta as anotações de tipo para campos Pydantic:",
                )
                print("  Exemplo:")
                print("    # Stub gerado pelo MonkeyType")
                print("    class User:")
                print("        name: str")
                print("        email: str")
                print("        age: Optional[int]")
                print("    ")
                print("    # Convertido para Pydantic")
                print("    class User(BaseModel):")
                print("        name: str")
                print("        email: EmailStr  # Com validação adicional")
                print("        age: Optional[int] = None")

        return result.returncode


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run tests with MonkeyType for type collection and application.",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    subparsers.required = True

    # Run command
    run_parser = subparsers.add_parser("run", help="Run tests with MonkeyType tracing")
    run_parser.add_argument(
        "--flx_project", required=True, help="Target flx_project directory"
    )
    run_parser.add_argument("--tests", help="Specific test path within the flx_project")

    # list command
    list_parser = subparsers.add_parser(
        "list",
        help="list modules with collected types",
    )
    list_parser.add_argument(
        "--flx_project",
        required=True,
        help="Target flx_project directory",
    )

    # Apply command
    apply_parser = subparsers.add_parser(
        "apply",
        help="Apply collected types to a module",
    )
    apply_parser.add_argument(
        "--module",
        required=True,
        help="Module path to apply types to",
    )

    # Stub command
    stub_parser = subparsers.add_parser(
        "stub",
        help="Generate stub file with collected types",
    )
    stub_parser.add_argument(
        "--module",
        required=True,
        help="Module path to generate stub for",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()
    runner = MonkeyTypeRunner()

    if args.command == "run":
        return runner.run_tests_with_monkeytype(args.flx_project, args.tests)
    if args.command == "list":
        return runner.list_modules(args.flx_project)
    if args.command == "apply":
        return runner.apply_types(args.module)
    if args.command == "stub":
        return runner.generate_stub(args.module)
    print(f"Unknown command: {args.command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())

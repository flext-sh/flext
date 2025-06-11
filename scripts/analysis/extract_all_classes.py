#!/usr/bin/env python3
"""Script para extrair TODAS as classes e funções do FLX para o relatório MD."""

import ast
from pathlib import Path
from typing import Any


def extract_all_classes_and_functions(file_path: Path) -> dict[str, Any]:
    """Extract ALL classes and functions from a Python file with full details."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        result = {
            "classes": [],
            "standalone_functions": [],
            "constants": [],
            "imports": [],
            "exports": [],
        }

        # Extract classes with ALL details
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "line_start": node.lineno,
                    "bases": [
                        ast.unparse(base) if hasattr(ast, "unparse") else str(base)
                        for base in node.bases
                    ],
                    "decorators": [
                        ast.unparse(dec) if hasattr(ast, "unparse") else str(dec)
                        for dec in node.decorator_list
                    ],
                    "methods": [],
                    "properties": [],
                    "class_methods": [],
                    "static_methods": [],
                    "async_methods": [],
                }

                # Extract all methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = {
                            "name": item.name,
                            "line": item.lineno,
                            "args": [arg.arg for arg in item.args.args],
                            "decorators": [
                                (
                                    ast.unparse(dec)
                                    if hasattr(ast, "unparse")
                                    else str(dec)
                                )
                                for dec in item.decorator_list
                            ],
                            "docstring": ast.get_docstring(item) or "",
                            "returns": (
                                ast.unparse(item.returns)
                                if item.returns and hasattr(ast, "unparse")
                                else None
                            ),
                        }

                        # Classify method type
                        decorator_names = [str(dec) for dec in item.decorator_list]
                        if any("property" in str(dec) for dec in decorator_names):
                            class_info["properties"].append(method_info)
                        elif any("classmethod" in str(dec) for dec in decorator_names):
                            class_info["class_methods"].append(method_info)
                        elif any("staticmethod" in str(dec) for dec in decorator_names):
                            class_info["static_methods"].append(method_info)
                        else:
                            class_info["methods"].append(method_info)

                    elif isinstance(item, ast.AsyncFunctionDef):
                        method_info = {
                            "name": item.name,
                            "line": item.lineno,
                            "args": [arg.arg for arg in item.args.args],
                            "decorators": [
                                (
                                    ast.unparse(dec)
                                    if hasattr(ast, "unparse")
                                    else str(dec)
                                )
                                for dec in item.decorator_list
                            ],
                            "docstring": ast.get_docstring(item) or "",
                            "returns": (
                                ast.unparse(item.returns)
                                if item.returns and hasattr(ast, "unparse")
                                else None
                            ),
                            "is_async": True,
                        }
                        class_info["async_methods"].append(method_info)

                result["classes"].append(class_info)

        # Extract standalone functions (not inside classes)
        class_lines = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_lines.update(
                    range(
                        node.lineno,
                        (
                            node.end_lineno + 1
                            if hasattr(node, "end_lineno")
                            else node.lineno + 50
                        ),
                    ),
                )

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                if node.lineno not in class_lines:
                    func_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "decorators": [
                            ast.unparse(dec) if hasattr(ast, "unparse") else str(dec)
                            for dec in node.decorator_list
                        ],
                        "docstring": ast.get_docstring(node) or "",
                        "returns": (
                            ast.unparse(node.returns)
                            if node.returns and hasattr(ast, "unparse")
                            else None
                        ),
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                    }
                    result["standalone_functions"].append(func_info)

        # Extract constants
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        result["constants"].append(
                            {"name": target.id, "line": node.lineno},
                        )

        # Extract imports and exports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append(
                        {
                            "type": "import",
                            "module": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno,
                        },
                    )
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    result["imports"].append(
                        {
                            "type": "from_import",
                            "module": node.module or "",
                            "name": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno,
                        },
                    )
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, ast.List):
                            for item in node.value.elts:
                                if isinstance(
                                    item, ast.Str | ast.Constant,
                                ) and isinstance(
                                    getattr(
                                        item,
                                        "value",
                                        item.s if hasattr(item, "s") else None,
                                    ),
                                    str,
                                ):
                                    value = getattr(
                                        item,
                                        "value",
                                        item.s if hasattr(item, "s") else None,
                                    )
                                    result["exports"].append(
                                        {"name": value, "line": node.lineno},
                                    )

        return result

    except Exception as e:
        return {"error": str(e)}


def generate_markdown_table():
    """Generate complete markdown table with all classes and functions."""
    flx_path = Path("flx/src/flx")
    all_items = []

    for py_file in flx_path.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        rel_path = py_file.relative_to(flx_path)
        directory = str(rel_path.parent) if rel_path.parent != Path(".") else "root"
        filename = py_file.name

        analysis = extract_all_classes_and_functions(py_file)

        if "error" in analysis:
            continue

        # Add classes
        for cls in analysis["classes"]:
            methods_summary = []
            if cls["methods"]:
                methods_summary.append(f"{len(cls['methods'])} methods")
            if cls["properties"]:
                methods_summary.append(f"{len(cls['properties'])} properties")
            if cls["class_methods"]:
                methods_summary.append(f"{len(cls['class_methods'])} classmethods")
            if cls["static_methods"]:
                methods_summary.append(f"{len(cls['static_methods'])} staticmethods")
            if cls["async_methods"]:
                methods_summary.append(f"{len(cls['async_methods'])} async methods")

            all_methods = (
                cls["methods"]
                + cls["properties"]
                + cls["class_methods"]
                + cls["static_methods"]
                + cls["async_methods"]
            )

            method_names = [m["name"] for m in all_methods[:5]]
            if len(all_methods) > 5:
                method_names.append("...")

            bases_str = ", ".join(cls["bases"]) if cls["bases"] else "object"
            decorators_str = ", ".join(cls["decorators"]) if cls["decorators"] else ""

            all_items.append(
                {
                    "directory": directory,
                    "file": filename,
                    "type": "CLASS",
                    "name": cls["name"],
                    "line": cls["line_start"],
                    "signature": f"class {cls['name']}({bases_str})",
                    "methods_count": len(all_methods),
                    "methods_summary": (
                        "; ".join(methods_summary) if methods_summary else "No methods"
                    ),
                    "main_methods": ", ".join(method_names),
                    "decorators": decorators_str,
                    "category": (
                        "DDD_ENTITY"
                        if any(
                            base in {"FlxEntity", "FlxAggregateRoot", "BaseModel"}
                            for base in cls["bases"]
                        )
                        else (
                            "ADAPTER"
                            if "Adapter" in cls["name"]
                            else (
                                "PORT"
                                if "Port" in cls["name"]
                                else (
                                    "SERVICE"
                                    if "Service" in cls["name"]
                                    else (
                                        "CONFIG"
                                        if "Config" in cls["name"]
                                        else (
                                            "MANAGER"
                                            if "Manager" in cls["name"]
                                            else (
                                                "PLUGIN"
                                                if "Plugin" in cls["name"]
                                                else (
                                                    "EXCEPTION"
                                                    if "Error" in cls["name"]
                                                    or "Exception" in cls["name"]
                                                    else (
                                                        "PROTOCOL"
                                                        if any(
                                                            base in {"Protocol"}
                                                            for base in cls["bases"]
                                                        )
                                                        else (
                                                            "MIXIN"
                                                            if "Mixin" in cls["name"]
                                                            else (
                                                                "FACTORY"
                                                                if "Factory"
                                                                in cls["name"]
                                                                else (
                                                                    "BUILDER"
                                                                    if "Builder"
                                                                    in cls["name"]
                                                                    else (
                                                                        "VALIDATOR"
                                                                        if "Validator"
                                                                        in cls["name"]
                                                                        else (
                                                                            "LOGGER"
                                                                            if "Log"
                                                                            in cls[
                                                                                "name"
                                                                            ]
                                                                            else (
                                                                                "CLIENT"
                                                                                if "Client"
                                                                                in cls[
                                                                                    "name"
                                                                                ]
                                                                                else "CORE"
                                                                            )
                                                                        )
                                                                    )
                                                                )
                                                            )
                                                        )
                                                    )
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    ),
                },
            )

        # Add standalone functions
        for func in analysis["standalone_functions"]:
            args_str = ", ".join(func["args"][:3])
            if len(func["args"]) > 3:
                args_str += ", ..."

            signature = (
                f"{'async ' if func['is_async'] else ''}def {func['name']}({args_str})"
            )
            if func["returns"]:
                signature += f" -> {func['returns']}"

            decorators_str = ", ".join(func["decorators"]) if func["decorators"] else ""

            all_items.append(
                {
                    "directory": directory,
                    "file": filename,
                    "type": "FUNCTION",
                    "name": func["name"],
                    "line": func["line"],
                    "signature": signature,
                    "methods_count": 0,
                    "methods_summary": "N/A",
                    "main_methods": "N/A",
                    "decorators": decorators_str,
                    "category": (
                        "ASYNC_FUNCTION"
                        if func["is_async"]
                        else (
                            "FACTORY_FUNCTION"
                            if "create" in func["name"] or "build" in func["name"]
                            else (
                                "VALIDATOR_FUNCTION"
                                if "validate" in func["name"]
                                else (
                                    "HELPER_FUNCTION"
                                    if func["name"].startswith("_")
                                    else "PUBLIC_FUNCTION"
                                )
                            )
                        )
                    ),
                },
            )

        # Add constants
        for const in analysis["constants"]:
            all_items.append(
                {
                    "directory": directory,
                    "file": filename,
                    "type": "CONSTANT",
                    "name": const["name"],
                    "line": const["line"],
                    "signature": const["name"],
                    "methods_count": 0,
                    "methods_summary": "N/A",
                    "main_methods": "N/A",
                    "decorators": "",
                    "category": "CONSTANT",
                },
            )

    # Sort by directory, file, line
    all_items.sort(key=lambda x: (x["directory"], x["file"], x["line"]))

    # Generate markdown
    markdown_lines = [
        "## 📋 **INVENTÁRIO COMPLETO - TODAS AS CLASSES E FUNÇÕES**",
        "",
        "### 🎯 **Legenda de Categorias**",
        "",
        "| **Categoria** | **Descrição** | **Exemplos** |",
        "|---------------|---------------|--------------|",
        "| **DDD_ENTITY** | Entidades do Domain-Driven Design | FlxEntity, FlxAggregateRoot |",
        "| **ADAPTER** | Adapters da Arquitetura Hexagonal | FlxIngoingCliAdapter, SecondaryDatabaseAdapter |",
        "| **PORT** | Ports (Interfaces) da Arquitetura Hexagonal | FlxDatabasePort, FlxQueryPort |",
        "| **SERVICE** | Serviços de aplicação e domínio | FlxGenericPaginationService |",
        "| **MANAGER** | Gerenciadores de recursos | FlxPluginManager, FlxConnectionManager |",
        "| **PLUGIN** | Sistema de plugins | HTTPPlugin, DatabasePlugin |",
        "| **FACTORY** | Padrão Factory para criação de objetos | FlxEntityFactory, PluginFactory |",
        "| **VALIDATOR** | Validadores e verificadores | FlxValidator, FlxDatabaseValidator |",
        "| **CLIENT** | Clientes para sistemas externos | FlxHttpClient, FlxLdapClient |",
        "| **CONFIG** | Classes de configuração | FlxHttpConfig, FlxBrokerConfig |",
        "| **CORE** | Classes centrais do framework | FlxApplication, FlxLogger |",
        "",
        "---",
        "",
        "### 📊 **INVENTÁRIO DETALHADO**",
        "",
        "| **#** | **Diretório** | **Arquivo** | **Tipo** | **Nome** | **Linha** | **Categoria** | **Métodos** | **Principais Métodos** | **Assinatura** |",
        "|-------|---------------|-------------|----------|----------|-----------|---------------|-------------|------------------------|----------------|",
    ]

    for i, item in enumerate(all_items, 1):
        methods_info = (
            f"{item['methods_count']} ({item['methods_summary']})"
            if item["type"] == "CLASS"
            else "N/A"
        )

        # Truncate long signatures and method lists
        signature = (
            item["signature"][:80] + "..."
            if len(item["signature"]) > 80
            else item["signature"]
        )
        methods = (
            item["main_methods"][:50] + "..."
            if len(item["main_methods"]) > 50
            else item["main_methods"]
        )

        markdown_lines.append(
            f"| **{i}** | `{item['directory']}` | `{item['file']}` | **{item['type']}** | `{item['name']}` | {item['line']} | **{item['category']}** | {methods_info} | {methods} | `{signature}` |",
        )

    markdown_lines.extend(
        [
            "",
            f"**Total de itens:** {len(all_items)} | **Classes:** {len([i for i in all_items if i['type'] == 'CLASS'])} | **Funções:** {len([i for i in all_items if i['type'] == 'FUNCTION'])} | **Constantes:** {len([i for i in all_items if i['type'] == 'CONSTANT'])}",
            "",
        ],
    )

    return "\n".join(markdown_lines)


if __name__ == "__main__":
    try:
        print("🔍 Extraindo TODAS as classes e funções do FLX...")
        markdown_content = generate_markdown_table()

        with open("flx_complete_inventory.md", "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print("✅ Inventário completo gerado em: flx_complete_inventory.md")

        # Also print summary
        flx_path = Path("flx/src/flx")
        total_classes = 0
        total_functions = 0
        total_constants = 0

        for py_file in flx_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            analysis = extract_all_classes_and_functions(py_file)
            if "error" not in analysis:
                total_classes += len(analysis["classes"])
                total_functions += len(analysis["standalone_functions"])
                total_constants += len(analysis["constants"])

        print("\n📊 RESUMO FINAL:")
        print(f"   Classes: {total_classes}")
        print(f"   Funções: {total_functions}")
        print(f"   Constantes: {total_constants}")
        print(f"   Total: {total_classes + total_functions + total_constants}")

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback

        traceback.print_exc()

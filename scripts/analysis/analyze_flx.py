#!/usr/bin/env python3
"""Análise completa e detalhada do projeto FLX usando Grimp e AST."""

import ast
import re
from collections import defaultdict
from pathlib import Path

import grimp


def count_lines(file_path):
    """Count lines in a file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            return len(f.readlines())
    except (OSError, UnicodeDecodeError):
        return 0


def extract_complete_analysis(file_path):
    """Extract ALL classes, methods, functions, imports, exports from a Python file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        analysis = {
            "classes": [],
            "functions": [],
            "imports": [],
            "exports": [],
            "decorators": [],
            "constants": [],
            "async_functions": [],
            "properties": [],
            "class_methods": [],
            "static_methods": [],
        }

        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    analysis["imports"].append(
                        f"import {alias.name}"
                        + (f" as {alias.asname}" if alias.asname else ""),
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    analysis["imports"].append(
                        f"from {module} import {alias.name}"
                        + (f" as {alias.asname}" if alias.asname else ""),
                    )

        # Extract exports (__all__)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, ast.List):
                            for item in node.value.elts:
                                if isinstance(item, ast.Str):
                                    analysis["exports"].append(item.s)
                                elif isinstance(item, ast.Constant) and isinstance(
                                    item.value, str,
                                ):
                                    analysis["exports"].append(item.value)

        # Extract classes and their methods
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "methods": [],
                    "properties": [],
                    "class_methods": [],
                    "static_methods": [],
                    "bases": [
                        base.id if isinstance(base, ast.Name) else str(base)
                        for base in node.bases
                    ],
                    "decorators": [
                        dec.id if isinstance(dec, ast.Name) else str(dec)
                        for dec in node.decorator_list
                    ],
                }

                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = {
                            "name": item.name,
                            "args": [arg.arg for arg in item.args.args],
                            "decorators": [
                                dec.id if isinstance(dec, ast.Name) else str(dec)
                                for dec in item.decorator_list
                            ],
                            "is_async": False,
                        }

                        # Classify method type
                        if any("property" in str(dec) for dec in item.decorator_list):
                            class_info["properties"].append(method_info)
                        elif any(
                            "classmethod" in str(dec) for dec in item.decorator_list
                        ):
                            class_info["class_methods"].append(method_info)
                        elif any(
                            "staticmethod" in str(dec) for dec in item.decorator_list
                        ):
                            class_info["static_methods"].append(method_info)
                        else:
                            class_info["methods"].append(method_info)

                    elif isinstance(item, ast.AsyncFunctionDef):
                        method_info = {
                            "name": item.name,
                            "args": [arg.arg for arg in item.args.args],
                            "decorators": [
                                dec.id if isinstance(dec, ast.Name) else str(dec)
                                for dec in item.decorator_list
                            ],
                            "is_async": True,
                        }
                        class_info["methods"].append(method_info)

                analysis["classes"].append(class_info)

        # Extract standalone functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function is not inside a class
                is_standalone = True
                for class_node in ast.walk(tree):
                    if isinstance(class_node, ast.ClassDef):
                        for item in class_node.body:
                            if item == node:
                                is_standalone = False
                                break
                        if not is_standalone:
                            break

                if is_standalone:
                    func_info = {
                        "name": node.name,
                        "args": [arg.arg for arg in node.args.args],
                        "decorators": [
                            dec.id if isinstance(dec, ast.Name) else str(dec)
                            for dec in node.decorator_list
                        ],
                        "is_async": False,
                    }
                    analysis["functions"].append(func_info)

            elif isinstance(node, ast.AsyncFunctionDef):
                # Check if async function is not inside a class
                is_standalone = True
                for class_node in ast.walk(tree):
                    if isinstance(class_node, ast.ClassDef):
                        for item in class_node.body:
                            if item == node:
                                is_standalone = False
                                break
                        if not is_standalone:
                            break

                if is_standalone:
                    func_info = {
                        "name": node.name,
                        "args": [arg.arg for arg in node.args.args],
                        "decorators": [
                            dec.id if isinstance(dec, ast.Name) else str(dec)
                            for dec in node.decorator_list
                        ],
                        "is_async": True,
                    }
                    analysis["async_functions"].append(func_info)

        # Extract constants
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        analysis["constants"].append(target.id)

        return analysis

    except Exception as e:
        return {"error": str(e)}


def get_detailed_file_purpose(file_path, analysis):
    """Get detailed purpose of a file based on content analysis."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        purposes = []

        # Check docstring
        lines = content.split("\n")
        for line in lines[:20]:
            if '"""' in line or "'''" in line:
                docstring_match = re.search(r'"""([^"]+)"""', content, re.DOTALL)
                if docstring_match:
                    doc = docstring_match.group(1).strip().split("\n")[0][:200]
                    purposes.append(f"DOC: {doc}")
                break

        # Analyze patterns
        if analysis.get("classes"):
            class_count = len(analysis["classes"])
            purposes.append(f"CLASSES: {class_count} classes")

        if analysis.get("functions"):
            func_count = len(analysis["functions"])
            purposes.append(f"FUNCTIONS: {func_count} functions")

        if analysis.get("exports"):
            export_count = len(analysis["exports"])
            purposes.append(f"EXPORTS: {export_count} items")

        # Pattern detection
        if any("Exception" in cls["name"] for cls in analysis.get("classes", [])):
            purposes.append("TYPE: Exception classes")
        elif any("Protocol" in cls["bases"] for cls in analysis.get("classes", [])):
            purposes.append("TYPE: Protocol definitions")
        elif any("BaseModel" in cls["bases"] for cls in analysis.get("classes", [])):
            purposes.append("TYPE: Pydantic models")
        elif any("test_" in func["name"] for func in analysis.get("functions", [])):
            purposes.append("TYPE: Test module")
        elif (
            len(analysis.get("exports", [])) > 0
            and len(analysis.get("classes", [])) == 0
        ):
            purposes.append("TYPE: Export module")
        elif "__init__.py" in str(file_path):
            purposes.append("TYPE: Package initializer")

        return " | ".join(purposes) if purposes else "Unknown"

    except Exception:
        return "Error analyzing purpose"


def format_method_signature(method_info):
    """Format method signature with args and decorators."""
    signature = method_info["name"]
    if method_info.get("args"):
        args_str = ", ".join(method_info["args"][:5])  # Limit args display
        if len(method_info["args"]) > 5:
            args_str += ", ..."
        signature += f"({args_str})"
    else:
        signature += "()"

    if method_info.get("decorators"):
        decorators = ", ".join(method_info["decorators"][:2])
        signature = f"@{decorators} {signature}"

    if method_info.get("is_async"):
        signature = f"async {signature}"

    return signature


def main():
    """Main analysis function with complete details."""
    try:
        print("🔍 Starting COMPLETE FLX analysis with ALL details...")

        # Try Grimp analysis first
        try:
            graph = grimp.build_graph("flx.src.flx")
            print(f"✅ Grimp analysis successful. Modules: {len(list(graph.modules))}")

            # Get dependency information
            module_dependencies = {}
            for module in graph.modules:
                try:
                    deps = graph.find_children(module)
                    module_dependencies[module] = len(deps) if deps else 0
                except Exception:
                    module_dependencies[module] = 0

        except Exception as e:
            print(f"⚠️ Grimp analysis failed: {e}")
            print("📂 Proceeding with manual file analysis...")
            graph = None
            module_dependencies = {}

        # Manual detailed file analysis
        flx_path = Path("flx/src/flx")
        results = []

        print(f"📁 Scanning directory: {flx_path}")

        for py_file in flx_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            print(f"🔍 Analyzing: {py_file.name}")

            rel_path = py_file.relative_to(flx_path)
            directory = str(rel_path.parent) if rel_path.parent != Path(".") else "root"
            filename = py_file.name

            line_count = count_lines(py_file)
            analysis = extract_complete_analysis(py_file)
            purpose = get_detailed_file_purpose(py_file, analysis)

            # Get module dependencies if available
            module_name = str(rel_path).replace("/", ".").replace(".py", "")
            full_module_name = (
                f"flx.{module_name}" if module_name != "__init__" else "flx"
            )
            dependencies = module_dependencies.get(full_module_name, 0)

            results.append(
                {
                    "directory": directory,
                    "filename": filename,
                    "line_count": line_count,
                    "analysis": analysis,
                    "purpose": purpose,
                    "dependencies": dependencies,
                    "module_name": module_name,
                },
            )

        # Sort results
        results.sort(key=lambda x: (x["directory"], x["filename"]))

        # Create comprehensive report
        print("\n" + "=" * 200)
        print("🎯 COMPLETE FLX PROJECT ANALYSIS REPORT")
        print("=" * 200)

        # Header for detailed table
        print(
            f"{'Directory':<35} | {'File':<30} | {'Classes':<15} | {'Methods':<15} | {'Functions':<15} | {'Lines':<8} | {'Deps':<6} | {'Purpose & Details':<60}",
        )
        print("-" * 200)

        total_classes = 0
        total_methods = 0
        total_functions = 0
        total_lines = 0

        # Print detailed results
        for result in results:
            analysis = result["analysis"]

            if "error" in analysis:
                classes_count = "ERROR"
                methods_count = "ERROR"
                functions_count = "ERROR"
            else:
                classes_count = len(analysis.get("classes", []))
                methods_count = sum(
                    len(cls["methods"])
                    + len(cls["properties"])
                    + len(cls["class_methods"])
                    + len(cls["static_methods"])
                    for cls in analysis.get("classes", [])
                )
                functions_count = len(analysis.get("functions", [])) + len(
                    analysis.get("async_functions", []),
                )

                total_classes += classes_count
                total_methods += methods_count
                total_functions += functions_count

            total_lines += result["line_count"]

            purpose = (
                result["purpose"][:58] + "..."
                if len(result["purpose"]) > 58
                else result["purpose"]
            )

            print(
                f"{result['directory']:<35} | {result['filename']:<30} | {classes_count:<15} | {methods_count:<15} | {functions_count:<15} | {result['line_count']:<8} | {result['dependencies']:<6} | {purpose:<60}",
            )

        print("-" * 200)
        print(
            f"{'TOTALS:':<35} | {len(results)} files | {total_classes:<15} | {total_methods:<15} | {total_functions:<15} | {total_lines:<8} | {'N/A':<6} | {'Complete analysis':<60}",
        )
        print("=" * 200)

        # Detailed breakdown section
        print("\n🔍 DETAILED CLASS AND METHOD BREAKDOWN:")
        print("=" * 150)

        for result in results:
            if "error" in result["analysis"]:
                continue

            analysis = result["analysis"]
            if not analysis.get("classes") and not analysis.get("functions"):
                continue

            print(
                f"\n📁 {result['directory']}/{result['filename']} ({result['line_count']} lines)",
            )
            print("-" * 100)

            # Show imports
            if analysis.get("imports"):
                print(f"📥 IMPORTS ({len(analysis['imports'])}):")
                for imp in analysis["imports"][:10]:  # Limit display
                    print(f"   • {imp}")
                if len(analysis["imports"]) > 10:
                    print(f"   ... and {len(analysis['imports']) - 10} more")
                print()

            # Show exports
            if analysis.get("exports"):
                print(f"📤 EXPORTS ({len(analysis['exports'])}):")
                exports_str = ", ".join(analysis["exports"])
                if len(exports_str) > 100:
                    exports_str = exports_str[:100] + "..."
                print(f"   {exports_str}")
                print()

            # Show classes
            for cls in analysis.get("classes", []):
                print(f"🏛️  CLASS: {cls['name']}")
                if cls["bases"]:
                    print(f"   └─ Inherits: {', '.join(cls['bases'])}")
                if cls["decorators"]:
                    print(f"   └─ Decorators: {', '.join(cls['decorators'])}")

                # Methods
                if cls["methods"]:
                    print(f"   ├─ METHODS ({len(cls['methods'])}):")
                    for method in cls["methods"]:
                        signature = format_method_signature(method)
                        print(f"   │  • {signature}")

                # Properties
                if cls["properties"]:
                    print(f"   ├─ PROPERTIES ({len(cls['properties'])}):")
                    for prop in cls["properties"]:
                        print(f"   │  • @property {prop['name']}")

                # Class methods
                if cls["class_methods"]:
                    print(f"   ├─ CLASS METHODS ({len(cls['class_methods'])}):")
                    for method in cls["class_methods"]:
                        print(f"   │  • @classmethod {method['name']}")

                # Static methods
                if cls["static_methods"]:
                    print(f"   └─ STATIC METHODS ({len(cls['static_methods'])}):")
                    for method in cls["static_methods"]:
                        print(f"      • @staticmethod {method['name']}")

                print()

            # Show standalone functions
            if analysis.get("functions") or analysis.get("async_functions"):
                all_functions = analysis.get("functions", []) + analysis.get(
                    "async_functions", [],
                )
                print(f"⚙️  FUNCTIONS ({len(all_functions)}):")
                for func in all_functions:
                    signature = format_method_signature(func)
                    print(f"   • {signature}")
                print()

            # Show constants
            if analysis.get("constants"):
                print(f"📋 CONSTANTS ({len(analysis['constants'])}):")
                constants_str = ", ".join(analysis["constants"])
                if len(constants_str) > 100:
                    constants_str = constants_str[:100] + "..."
                print(f"   {constants_str}")
                print()

        # Summary statistics
        print("\n📊 SUMMARY STATISTICS:")
        print("=" * 80)

        # Directory summary
        dir_summary = defaultdict(
            lambda: {"files": 0, "lines": 0, "classes": 0, "methods": 0, "functions": 0},
        )
        for result in results:
            analysis = result["analysis"]
            if "error" not in analysis:
                dir_summary[result["directory"]]["files"] += 1
                dir_summary[result["directory"]]["lines"] += result["line_count"]
                dir_summary[result["directory"]]["classes"] += len(
                    analysis.get("classes", []),
                )
                dir_summary[result["directory"]]["methods"] += sum(
                    len(cls["methods"])
                    + len(cls["properties"])
                    + len(cls["class_methods"])
                    + len(cls["static_methods"])
                    for cls in analysis.get("classes", [])
                )
                dir_summary[result["directory"]]["functions"] += len(
                    analysis.get("functions", []),
                ) + len(analysis.get("async_functions", []))

        print(
            f"{'Directory':<40} | {'Files':<6} | {'Lines':<8} | {'Classes':<8} | {'Methods':<8} | {'Functions':<8}",
        )
        print("-" * 90)
        for directory, stats in sorted(dir_summary.items()):
            print(
                f"{directory:<40} | {stats['files']:>6} | {stats['lines']:>8} | {stats['classes']:>8} | {stats['methods']:>8} | {stats['functions']:>8}",
            )

        print("\n✅ Analysis complete!")
        print(
            f"📊 Total: {len(results)} files, {total_classes} classes, {total_methods} methods, {total_functions} functions, {total_lines} lines",
        )

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

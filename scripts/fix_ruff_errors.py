import json
import pathlib

ERRORS_FILE = "ruff_errors.json"
MODELS_IMPORT = "from flext_core.models import m"
TYPINGS_IMPORT = "from flext_core.typings import t"


def load_errors():
    if not pathlib.Path(ERRORS_FILE).exists():
        return []
    with pathlib.Path(ERRORS_FILE).open(encoding="utf-8") as f:
        return json.load(f)


def fix_file(filename, errors) -> None:
    if not pathlib.Path(filename).exists():
        return

    with pathlib.Path(filename).open(encoding="utf-8") as f:
        lines = f.readlines()

    modified = False

    # Check what needs to be fixed
    needs_m = False
    needs_t = False

    for error in errors:
        msg = error["message"]
        row = error["location"]["row"] - 1  # 0-indexed

        if "Undefined name `m`" in msg:
            needs_m = True
        elif "Undefined name `t`" in msg:
            needs_t = True
        elif "Undefined name `adict`" in msg:
            # Replace adict -> m.ConfigMap (and ensure m import)
            if 0 <= row < len(lines):
                lines[row] = lines[row].replace("adict", "m.ConfigMap")
                modified = True
                needs_m = True
        elif "Undefined name `ConfigurationDict`" in msg:
            if 0 <= row < len(lines):
                lines[row] = lines[row].replace("ConfigurationDict", "m.ConfigMap")
                modified = True
                needs_m = True
        # Add other replacements as needed based on analysis

    # Add imports if missing
    if needs_m:
        has_m = any("from flext_core.models import m" in line for line in lines)
        if not has_m:
            # Insert after last import
            idx = 0
            for i, line in enumerate(lines):
                if line.startswith(("import ", "from ")):
                    idx = i + 1
            lines.insert(idx, MODELS_IMPORT + "\n")
            modified = True

    if needs_t:
        has_t = any("from flext_core.typings import t" in line for line in lines)
        if not has_t:
            idx = 0
            for i, line in enumerate(lines):
                if line.startswith(("import ", "from ")):
                    idx = i + 1
            lines.insert(idx, TYPINGS_IMPORT + "\n")
            modified = True

    if modified:
        with pathlib.Path(filename).open("w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"Fixed: {filename}")


def main() -> None:
    errors = load_errors()
    files_errors = {}
    for e in errors:
        fname = e["filename"]
        if fname not in files_errors:
            files_errors[fname] = []
        files_errors[fname].append(e)

    for fname, errs in files_errors.items():
        fix_file(fname, errs)


if __name__ == "__main__":
    main()

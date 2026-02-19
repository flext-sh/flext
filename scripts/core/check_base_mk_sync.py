#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
from __future__ import annotations

import hashlib
import sys
from pathlib import Path


def sha256_text(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    source = root / "base.mk"
    if not source.exists():
        print("[base-mk-sync] missing root base.mk", file=sys.stderr)
        return 1

    source_hash = sha256_text(source)
    mismatched: list[Path] = []
    missing: list[Path] = []

    for pyproject in sorted(root.glob("*/pyproject.toml")):
        project_dir = pyproject.parent
        local_base = project_dir / "base.mk"
        if not local_base.exists():
            missing.append(local_base.relative_to(root))
            continue
        if sha256_text(local_base) != source_hash:
            mismatched.append(local_base.relative_to(root))

    if missing or mismatched:
        for path in missing:
            print(f"[base-mk-sync] missing: {path}")
        for path in mismatched:
            print(f"[base-mk-sync] drift: {path}")
        return 1

    print("[base-mk-sync] all vendored base.mk copies are in sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

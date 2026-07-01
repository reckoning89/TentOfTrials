#!/usr/bin/env python3
"""Verify files mentioning legacy also contain LEGACY in a comment."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "node_modules", "diagnostic", "__pycache__", "vendor"}
TEXT_EXT = {
    ".py", ".go", ".ts", ".tsx", ".js", ".jsx", ".rb", ".lua", ".pl",
    ".c", ".cpp", ".h", ".hpp", ".css", ".html", ".md", ".yaml", ".yml",
    ".json", ".toml", ".rs", ".java", ".cs", ".sql", ".sh",
}

COMMENT_PATTERNS = [
    re.compile(r"//.*LEGACY"),
    re.compile(r"#.*LEGACY"),
    re.compile(r"--.*LEGACY"),
    re.compile(r"/\*[^*]*LEGACY[^*]*\*/"),
    re.compile(r"<!--[^>]*LEGACY[^>]*-->"),
]

LEGACY_REF = re.compile(r"legacy", re.I)


def is_comment_line(line: str, ext: str) -> bool:
    s = line.strip()
    if ext in {".py", ".rb", ".pl", ".sh", ".yaml", ".yml"}:
        return s.startswith("#")
    if ext in {".go", ".ts", ".tsx", ".js", ".jsx", ".java", ".cs", ".c", ".cpp", ".h", ".hpp", ".rs"}:
        return s.startswith("//")
    if ext == ".lua":
        return s.startswith("--")
    if ext == ".css":
        return "/*" in s
    if ext == ".html":
        return s.startswith("<!--")
    return False


def has_legacy_comment(text: str) -> bool:
    if "LEGACY" in text:
        return True
    for pat in COMMENT_PATTERNS:
        if pat.search(text):
            return True
    return False


def iter_files() -> list[Path]:
    out = []
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix.lower() in TEXT_EXT or p.name in {"Dockerfile", "Makefile"}:
            out.append(p)
    return out


def audit() -> list[Path]:
    bad = []
    for path in iter_files():
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if not LEGACY_REF.search(text):
            continue
        if has_legacy_comment(text):
            continue
        bad.append(path)
    return bad


def main() -> int:
    violations = audit()
    if violations:
        print(f"LEGACY comment violations: {len(violations)}", file=sys.stderr)
        for p in sorted(violations):
            print(p.relative_to(ROOT), file=sys.stderr)
        return 1
    print("All legacy references include LEGACY comment marker.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Add LEGACY comment marker to files flagged by legacy_caps_audit."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "tools" / "legacy_caps_audit.py"

MARKERS = {
    ".py": "# LEGACY: file contains legacy references\n",
    ".go": "// LEGACY: file contains legacy references\n",
    ".rs": "// LEGACY: file contains legacy references\n",
    ".ts": "// LEGACY: file contains legacy references\n",
    ".tsx": "// LEGACY: file contains legacy references\n",
    ".lua": "-- LEGACY: file contains legacy references\n",
    ".md": "<!-- LEGACY: file contains legacy references -->\n",
    ".sql": "-- LEGACY: file contains legacy references\n",
    ".yaml": "# LEGACY: file contains legacy references\n",
    ".yml": "# LEGACY: file contains legacy references\n",
}


def fix_file(path: Path):
    ext = path.suffix.lower()
    marker = MARKERS.get(ext, f"# LEGACY: file contains legacy references\n")
    text = path.read_text(encoding="utf-8", errors="replace")
    if "LEGACY" in text:
        return
    if text.startswith("#!"):
        first_nl = text.index("\n") + 1
        path.write_text(text[:first_nl] + marker + text[first_nl:], encoding="utf-8")
    else:
        path.write_text(marker + text, encoding="utf-8")


def main():
    r = subprocess.run([sys.executable, str(AUDIT)], capture_output=True, text=True, cwd=ROOT)
    if r.returncode == 0:
        print("nothing to fix")
        return
    for line in r.stderr.splitlines()[1:]:
        line = line.strip()
        if not line or line.startswith("LEGACY"):
            continue
        fix_file(ROOT / line)
    r2 = subprocess.run([sys.executable, str(AUDIT)], cwd=ROOT)
    sys.exit(r2.returncode)


if __name__ == "__main__":
    main()

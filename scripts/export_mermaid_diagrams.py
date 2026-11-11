"""Export the 15 original Mermaid blocks referenced by docs/diagram/index.html.

The HTML remains the canonical approved diagram. This utility only creates
matching .mmd download files; it never modifies the HTML or the ERD.

Usage:
    python scripts/export_mermaid_diagrams.py --write
    python scripts/export_mermaid_diagrams.py --check
"""

from __future__ import annotations

import argparse
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "diagram" / "index.html"
PATTERN = re.compile(
    r'<header>.*?<a href="([^"/]+\.mmd)" download>.*?</header>\s*'
    r'<div class="drawing"><pre class="mermaid">(.*?)</pre>',
    flags=re.DOTALL,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="Export missing files")
    group.add_argument("--check", action="store_true", help="Check existing files")
    args = parser.parse_args()

    blocks = PATTERN.findall(SOURCE.read_text(encoding="utf-8"))
    if len(blocks) != 15 or len({name for name, _ in blocks}) != 15:
        raise SystemExit(f"Expected 15 unique embedded diagrams, found {len(blocks)}")

    mismatches: list[str] = []
    for name, escaped_mermaid in blocks:
        if Path(name).name != name:
            raise SystemExit(f"Refusing unsafe path in diagram link: {name!r}")

        target = SOURCE.parent / name
        expected = unescape(escaped_mermaid).strip() + "\n"
        if target.exists():
            if target.read_text(encoding="utf-8") != expected:
                mismatches.append(name)
            continue

        if args.check:
            mismatches.append(name)
        else:
            target.write_text(expected, encoding="utf-8")
            print(f"Created {target.relative_to(ROOT)}")

    if mismatches:
        raise SystemExit("Missing/different from canonical HTML: " + ", ".join(mismatches))
    print("All 15 diagrams match docs/diagram/index.html; original HTML untouched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

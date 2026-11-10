"""Read the preserved design independently of application model definitions."""

import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def erd_tables() -> dict[str, dict[str, tuple[str, str]]]:
    page = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    blocks = re.findall(r'<pre class="mermaid">(.*?)</pre>', page, re.S)
    tables = {}
    for block in blocks[2:5]:
        for table, body in re.findall(r"^  (\w+) \{\n(.*?)^  \}", unescape(block), re.M | re.S):
            if table.lower() in tables:
                continue
            columns = {}
            for line in body.strip().splitlines():
                parts = line.strip().split()
                columns[parts[1]] = (parts[0], parts[2] if len(parts) > 2 else "")
            tables[table.lower()] = columns
    return tables


def approved_nullables() -> dict[str, set[str]]:
    document = (ROOT / "docs/phase-2-database-implementation.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\| ([A-Z_]+) \| ([^|]+) \|", document, re.M)
    # The nullability table precedes the later model mapping table.
    result = {}
    for table, columns in rows:
        if table.lower() not in result:
            result[table.lower()] = (
                set()
                if columns.strip() == "None"
                else {name.strip() for name in columns.split(",")}
            )
    return result

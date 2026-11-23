"""List active insights from the Obsidian agent memory that match a lesson.

Usage: python insights.py <project> [--topic T ...] [--applies A ...]
  e.g. python insights.py projects/my-course --topic crewai --applies tracker-build

Prints one block per matching note (path, frontmatter type/topic/seen, body),
so an agent reads only what applies instead of loading the whole folder.
A note matches when it is `status: active` and its `topic` is one of --topic
OR its `applies_to` shares a value with --applies. No filters: all active.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from vault import root  # noqa: E402


def frontmatter(text: str) -> tuple[dict, str]:
    """Tiny parser for this memory's flat frontmatter: `key: value` and `[a, b]` lists."""
    m = re.match(r"---\n(.*?)\n---\n?(.*)", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        val = val.split(" #")[0].strip().strip('"')
        if val.startswith("[") and val.endswith("]"):
            val = [v.strip().strip('"') for v in val[1:-1].split(",") if v.strip()]
        meta[key.strip()] = val
    return meta, m.group(2).strip()


def matches(meta: dict, topics: list[str], applies: list[str]) -> bool:
    if meta.get("status") != "active":
        return False
    if not topics and not applies:
        return True
    a = meta.get("applies_to", [])
    return meta.get("topic") in topics or bool(
        set(a if isinstance(a, list) else [a]) & set(applies)
    )


def main(argv: list[str]) -> None:
    project, topics, applies, flag = argv[0], [], [], None
    for arg in argv[1:]:
        if arg in ("--topic", "--applies"):
            flag = arg
        elif flag == "--topic":
            topics.append(arg)
        elif flag == "--applies":
            applies.append(arg)
    folder = root() / project / "insights"
    if not folder.is_dir():
        sys.exit(f"no insights folder at {folder} (project is the vault path, e.g. projects/my-course)")
    hits = 0
    for note in sorted(folder.glob("*.md")):
        meta, body = frontmatter(note.read_text(encoding="utf-8"))
        if matches(meta, topics, applies):
            hits += 1
            print(
                f"## {note.stem}  ({meta.get('type')}, {meta.get('topic')}, seen {meta.get('seen')})"
            )
            print(body + "\n")
    print(f"{hits} active insight(s) matched in {folder}")


if __name__ == "__main__":
    main(sys.argv[1:])

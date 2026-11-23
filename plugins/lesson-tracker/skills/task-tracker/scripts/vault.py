"""Where tracker data lives: the user's Obsidian vault, configured once.

    python vault.py setup              list the vaults Obsidian knows, numbered
    python vault.py setup <N | path>   save that vault (must contain .obsidian/)
    python vault.py where              print the vault root
    python vault.py find <feature>     print each projects/*/trackers/<feature>/ found
    python vault.py project <repo>     print the vault project saved for a repo
    python vault.py set-project <repo> <projects/name>

Lookup order: env TRACKER_VAULT, then ~/.config/lesson-tracker/config.json.
Neither: exit non-zero with one line telling the agent to run setup. No personal path
lives in this file, so the skill can be shared.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

CONFIG = Path(
    os.environ.get("LESSON_TRACKER_CONFIG", "~/.config/lesson-tracker/config.json")
).expanduser()
NO_VAULT = "No vault set. Say 'set up the tracker vault' or run: python vault.py setup"


def load() -> dict:
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"vault": "", "projects": {}}


def save(cfg: dict) -> None:
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")


def root() -> Path:
    """The vault folder, or exit with NO_VAULT."""
    path = os.environ.get("TRACKER_VAULT") or load().get("vault")
    if not path:
        sys.exit(NO_VAULT)
    return Path(path).expanduser()


def obsidian_vaults() -> list[Path]:
    """Vaults listed in Obsidian's own obsidian.json (macOS, Linux, Windows)."""
    home = Path.home()
    places = [
        home / "Library/Application Support/obsidian/obsidian.json",
        home / ".config/obsidian/obsidian.json",
        Path(os.environ.get("APPDATA", home)) / "obsidian/obsidian.json",
    ]
    if os.environ.get("OBSIDIAN_JSON"):  # tests
        places = [Path(os.environ["OBSIDIAN_JSON"])]
    for p in places:
        if p.exists():
            vaults = json.loads(p.read_text(encoding="utf-8")).get("vaults", {})
            return [Path(v["path"]) for v in vaults.values() if v.get("path")]
    return []


def setup(choice: str | None) -> None:
    found = obsidian_vaults()
    if choice is None:
        if not found:
            print("Obsidian not found. Run: python vault.py setup <path to a folder>")
            return
        for i, v in enumerate(found, 1):
            print(f"{i}. {v.name}  ({v})")
        print("Pick one: python vault.py setup <number>")
        return
    path = found[int(choice) - 1] if choice.isdigit() else Path(choice).expanduser()
    if not (path / ".obsidian").is_dir():
        sys.exit(f"{path} is not an Obsidian vault (no .obsidian/ folder)")
    cfg = load()
    cfg["vault"] = str(path)
    save(cfg)
    print(f"vault set: {path}  (saved in {CONFIG})")


def find(feature: str) -> list[Path]:
    return sorted(
        p.parent for p in root().glob(f"projects/*/trackers/{feature}/tracker.json")
    )


def main(argv: list[str]) -> None:
    cmd, args = (argv[0], argv[1:]) if argv else ("where", [])
    if cmd == "setup":
        setup(args[0] if args else None)
    elif cmd == "where":
        print(root())
    elif cmd == "find":
        hits = find(args[0])
        print("\n".join(map(str, hits)) if hits else f"no tracker named {args[0]!r}")
    elif cmd == "project":
        project = load().get("projects", {}).get(args[0])
        if not project:
            sys.exit(
                f"no vault project saved for repo {args[0]!r}; ask the user, then set-project"
            )
        print(project)
    elif cmd == "set-project":
        cfg = load()
        cfg.setdefault("projects", {})[args[0]] = args[1]
        save(cfg)
        print(f"{args[0]} -> {args[1]}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])

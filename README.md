# Nily's Claude Code Plugins

A personal collection of [Claude Code](https://code.claude.com) plugins I build to
automate my own work and daily life — and share with anyone who finds them useful.

The idea is simple: every time a daily ritual becomes repetitive (opening a Jira
ticket in the morning, posting a progress update, checking a design, writing the
same kind of report), it becomes a plugin. Each one packages the whole workflow —
skills, slash commands, and the MCP servers it needs — into something installable
with one command, on any machine, in any repo.

This repository is a **plugin marketplace**: a catalog that Claude Code can
register once and install plugins from individually.

## Available plugins

| Plugin | What it automates |
|---|---|
| [`jira-flow`](./plugins/jira-flow) | The daily Jira ritual: `/jira-flow:story` reads a ticket, its comments, and any linked Figma for a morning kickoff; `/jira-flow:wrap-up` posts an approved, high-level progress comment back to the ticket in its own language. |
| [`quartermaster`](./plugins/quartermaster) | Parallel review orchestration: `/quartermaster:plan` proposes a risk tier and file inventory during planning; `/quartermaster:review` dispatches code + security reviews by tier, synthesizes the findings, and fingerprints the approval to the exact diff. |
| [`lesson-tracker`](./plugins/lesson-tracker) | Learning by hand with an agent: `/lesson-tracker:task-tracker` builds a tracker where every task has an owner (you or an agent), a testable goal and a check; `/lesson-tracker:work-from-tracker` does or teaches the work by those rules and, at lesson close, writes typed lessons into an Obsidian agent memory that the next tracker reads. |

More coming as my workflows demand them. Each plugin has its own README with
prerequisites, setup, and usage — and **[USAGE.md](./USAGE.md)** walks through installing and
using every plugin end to end.

## Install

Register the marketplace once:

```
/plugin marketplace add <owner>/<this-repo>
```

(Or from a local clone: `/plugin marketplace add /path/to/this/repo` — the path
must be this repo's root, where `.claude-plugin/marketplace.json` lives.)

Then install any plugin from the table:

```
/plugin install jira-flow@nily-plugins
```

To get updates later: `/plugin marketplace update nily-plugins`.

## Repo structure

```
.
├── .claude-plugin/
│   └── marketplace.json      ← the catalog: one entry per plugin
└── plugins/
    └── jira-flow/            ← one folder per plugin
        ├── .claude-plugin/plugin.json
        ├── .mcp.json         ← bundled MCP servers (if any)
        ├── skills/           ← the plugin's commands/skills
        └── README.md
```

## Adding a new plugin

1. Create `plugins/<name>/` with a `.claude-plugin/plugin.json` manifest and its
   `skills/` (plus `.mcp.json`, `agents/`, or `hooks/` if needed).
2. Add an entry to the `plugins` array in `.claude-plugin/marketplace.json`:
   ```json
   { "name": "<name>", "source": "./plugins/<name>", "description": "..." }
   ```
3. Validate: `claude plugin validate .` (checks the marketplace and every plugin).
4. Push. Anyone with the marketplace registered gets it via
   `/plugin marketplace update` + `/plugin install <name>@nily-plugins`.

## Design principles

- **One marketplace, many plugins** — register once, install what you need.
- **Self-contained** — each plugin bundles the MCP servers it depends on and
  degrades gracefully when optional tools aren't available.
- **Safe by default** — anything outward-facing (posting comments, sending
  messages) always shows a draft and waits for explicit approval.
- **Portable** — nothing is tied to a specific repo, machine, or person; personal
  details (like your name) are asked once at install via plugin `userConfig`.

## License

MIT — use, fork, and adapt freely.
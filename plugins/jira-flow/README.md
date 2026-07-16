# Jira Flow

A Claude Code plugin for the daily Jira ritual, in two commands:

| Command | What it does |
|---|---|
| `/jira-flow:story <jira-url> [figma-url]` | Morning kickoff — reads the ticket, its existing comments, and any linked Figma design, briefs you, then brainstorms the work with you. |
| `/jira-flow:wrap-up` | End of session — drafts a high-level progress comment in your voice and in the ticket's language, and posts it to Jira only after you approve both the ticket and the text. |

Works in any repo. Each repo tracks its own active story (state is kept at
`~/.claude/plans/active-story-<project>.md`), so switching projects never mixes
tickets up.

## Prerequisites

- **Claude Code** v2.x or later (plugin support).
- **An Atlassian Cloud site** (`*.atlassian.net`). Your site admin must have the
  Remote MCP server enabled (Rovo + Remote MCP toggles in Atlassian Admin).
- **Optional — Figma MCP**: if you have it connected, `/story` reads linked designs;
  if not, the flow simply continues without them.
- **Optional — `superpowers` plugin**: kickoff hands off to
  `superpowers:brainstorming` when available, and falls back to an inline
  brainstorm when not.

The plugin bundles the official Atlassian remote MCP server (`.mcp.json`, endpoint
`https://mcp.atlassian.com/v1/mcp/authv2`) — you don't need to configure it yourself,
only authenticate once (see First-run setup).

## Install

Plugins install from a *marketplace* — a catalog repo. This plugin lives in one, so
installation is two steps: register the marketplace, then install the plugin.

**From the Git repo** (recommended):

```
/plugin marketplace add <owner>/claude-plugins
/plugin install jira-flow@nily-plugins
```

Replace `<owner>/claude-plugins` with this repository's GitHub path. Any Git URL
also works (GitLab, Bitbucket, self-hosted): `/plugin marketplace add https://…/claude-plugins.git`.

**From a local clone** (for development):

```bash
git clone <repo-url> ~/Developer/claude-plugins
claude plugin marketplace add ~/Developer/claude-plugins
claude plugin install jira-flow@nily-plugins
```

The path you register must be the folder that contains
`.claude-plugin/marketplace.json` — not its parent, not the plugin folder inside it.

To pick up new versions later: `/plugin marketplace update nily-plugins`, then
reinstall or `/reload-plugins`.

## First-run setup

1. When enabling the plugin, Claude Code asks for **Your name** — wrap-up comments
   are written in first person as you.
2. In a Claude Code session, run `/mcp` and complete the Atlassian OAuth login with
   your work account. MCP actions run with *your* Jira permissions.

## Usage

From inside any project repo:

```
/jira-flow:story https://yoursite.atlassian.net/browse/PROJ-123
```

Optionally pass a Figma link as a second argument. Claude reads the ticket, its
comment history, and the design, gives you a short briefing, and brainstorms the
implementation with you. Then work as usual. At the end of the session:

```
/jira-flow:wrap-up
```

Claude drafts a short, non-technical progress comment from the session's work and
git history. Built-in safety rules:

- It confirms the **destination ticket** whenever the key was recovered from a
  state file or the state isn't from today — it never assumes.
- It **never posts without your explicit approval** of the drafted text.
- It never commits or pushes git changes.

## Troubleshooting

**"not found in any configured marketplace"** — you skipped the
`/plugin marketplace add` step, or ran `plugin install` with a path (paths aren't
supported; install by `name@marketplace`).

**"Marketplace file not found"** — the path you added doesn't contain
`.claude-plugin/marketplace.json`. Register the marketplace root folder itself.

**Commands don't appear after install** — run `/reload-plugins` or restart Claude
Code. If they still don't show (known quirk with local-directory marketplaces):

```bash
rm -rf ~/.claude/plugins/cache
```

then reinstall. Verify anytime with `claude plugin validate <marketplace-path>`.

**Jira tools fail with "Rovo not enabled" or auth errors** — ask your Atlassian
admin to enable Rovo + Remote MCP for the site, then re-run `/mcp` to authenticate.

## Uninstall

`/plugin uninstall jira-flow@nily-plugins` (or disable it from `/plugin`). State
files under `~/.claude/plans/active-story-*.md` can be deleted manually.

# Using the plugins

Three plugins live in this marketplace. `jira-flow` is the original, Jira-only flow;
`quartermaster` is its evolution — the same kickoff idea but tracker-agnostic (Jira **or**
Linear), plus risk-tiered parallel review. `lesson-tracker` is separate: progress trackers
that an agent and a human both work against, with an Obsidian agent memory.

| Plugin | Trackers | Commands |
|---|---|---|
| `jira-flow` | Jira only | `/jira-flow:story`, `/jira-flow:wrap-up` |
| `quartermaster` | Jira **or** Linear | `/quartermaster:story`, `/quartermaster:plan`, `/quartermaster:review` |
| `lesson-tracker` | none (any brief: lesson card, plan, card) | `/lesson-tracker:task-tracker`, `/lesson-tracker:work-from-tracker` |

You can install any of them — they don't conflict.

## 1. Register the marketplace (once)

From a local clone (path must be the repo root, where `.claude-plugin/marketplace.json` lives):

```
/plugin marketplace add ~/Developer/claude-plugins
```

Or from GitHub: `/plugin marketplace add <owner>/claude-plugins`.

To pull updates later: `/plugin marketplace update nily-plugins`.

## 2. Install the plugin(s) you want

```
/plugin install jira-flow@nily-plugins
/plugin install quartermaster@nily-plugins
/plugin install lesson-tracker@nily-plugins
```

Both ask for your name once at install (`engineer_name`) — wrap-up/kickoff comments are written
in first person as that person.

## 3. Authenticate the tracker MCP (first use)

Both plugins bundle remote MCP servers that authenticate via OAuth the first time you use a
command that needs them:

- **Jira / Confluence** → `atlassian` (`mcp.atlassian.com`) — used by both plugins
- **Linear** → `linear` (`mcp.linear.app`) — bundled by `quartermaster` only

Whichever tracker you don't use just stays unauthenticated and is ignored.

---

## jira-flow — the beginner flow (Jira only)

The daily Jira ritual.

```
/jira-flow:story https://your-site.atlassian.net/browse/PROJ-123 [figma-url]
```
Reads the ticket, its comments, and any linked Figma; briefs you; then brainstorms the work.

```
/jira-flow:wrap-up
```
Drafts a high-level progress comment in the ticket's own language and posts it to Jira **only
after you approve** the destination and the text.

---

## quartermaster — the evolution (Jira or Linear)

Same kickoff, tracker-agnostic, plus a planned + orchestrated review.

### `/quartermaster:story <issue-url-or-key> [figma-url]`

Kicks off an issue. It figures out the tracker for you:

- `*.atlassian.net/browse/PROJ-123` → **Jira**
- `linear.app/<workspace>/issue/ENG-123/...` → **Linear**
- a **bare key** (`PROJ-123`, `ENG-123`) or no argument → it **asks** "Jira or Linear?", since
  the keys are indistinguishable

Then it reads the issue + comments (via the matching MCP) and any Figma, briefs you, and writes
the story contract to `.local/<KEY>/assumptions.md`.

### `/quartermaster:plan <issue-key>`

Proposes a **risk tier** (`high` / `med` / `low`) and estimates the file inventory, appending
both to the story contract. The tier decides how much review muscle gets dispatched later.

### `/quartermaster:review`

When the work is done: runs your gates, then dispatches reviews **by tier** —

- **high / med** → `code-review` + `security-review` in parallel (opus)
- **low** → one `code-review` (sonnet)

— synthesizes the findings side-by-side, and on your approval records `.local/<KEY>/review.md`
with a **fingerprint of the exact diff**. If the code changes afterward, the fingerprint no
longer matches, so a stale approval can't ride along.

### Typical flow

```
/quartermaster:story https://linear.app/acme/issue/ENG-42/add-rate-limit
/quartermaster:plan ENG-42
# ...implement...
/quartermaster:review
```

> **Note:** `plan` and `review` expect a review harness in the workspace
> (`.local/preflight.sh`, `.local/<KEY>/assumptions.md`). `story` creates the assumptions file;
> the gate script is yours to provide.

---

## lesson-tracker — learning by hand, with an agent

No tracker MCP needed. The data lives in your Obsidian vault.

### First use: pick your vault

The first time it needs the vault, the agent reads Obsidian's own vault list and asks you to
pick one by number (`vault.py setup`). It's saved in `~/.config/lesson-tracker/config.json`.
The first tracker made from a repo also asks which vault project (`projects/<name>`) the repo
belongs to, once.

### `/lesson-tracker:task-tracker`

Paste a lesson card, point at a plan, or share a Linear / Jira card. It builds the tracker:
one task per deliverable, each with an owner (**you** or **agent**), a one-sentence goal, a
check (`run` / `ask` / `review`), the data shapes and plain-word steps. Open questions go in
**decisions** at the top of the page, not into a silent choice. It publishes the page as an
Artifact (the same link on every update) and writes `tracker.json` + `tracker.md` to
`<vault>/projects/<project>/trackers/<feature>/`. Before writing tasks it reads matching
insights from earlier lessons, so a known pitfall shows up in the right task.

### `/lesson-tracker:work-from-tracker`

Say "let's do task 2", "continue", "check task 3" or "is this done?".

- **Your task**: it shows the shapes, walks the steps one at a time, reviews your code
  against the goal, and doesn't write it unless you ask.
- **Its task**: it does it, as a fixed workflow or, when the path is unknown, through a
  subagent; either way it runs the check itself.
- A task is done only when its check passes in this session. A failed check stays in progress,
  with the failure on the page.

### Retro

When the last task is done it offers a retro. On yes it writes `retros/YYYY-MM-DD-<lesson>.md`
(fixed properties and sections) and confirms, adds or retires notes in `insights/`. An
insight confirmed twice becomes a proposed edit to a skill; you approve it.

### Typical flow

```
/lesson-tracker:task-tracker          # paste the lesson card
# "let's do task 1" ... "check task 1" ... "continue"
# "let's do the retro"
```


# Quartermaster

Tracker-agnostic story-to-review flow. Kicks off an issue from Jira or Linear, plans the
review, then dispatches code + security reviews in parallel by risk tier, synthesizes the
findings, and records an approval fingerprinted to the exact diff.

## Commands

| Command | What it does |
|---|---|
| `/quartermaster:story <issue-url-or-key> [figma-url]` | Kick off an issue from **Jira or Linear** — detects the tracker from the URL, asks when it can't tell, reads the issue + comments + any Figma, briefs you, and writes the story contract |
| `/quartermaster:plan <issue-key>` | Propose a risk tier and estimate the file inventory during planning |
| `/quartermaster:review` | Run gates, dispatch review workers by tier, synthesize findings, record approval |

## How it works

**Risk-based dispatch**

- **high / med** — `code-review` (opus) + `security-review` (opus) in parallel
- **low** — `code-review` (sonnet)

**Synthesis & approval**

1. Dispatches workers with a diff boundary, the tier, and a report path
2. Awaits each worker's short summary (~10–20 lines; never the full report)
3. Presents findings side-by-side
4. Records a fingerprint tying the approval to this exact diff

**Fingerprint lock** — if the code moves after approval, the fingerprint changes and
`/wrap-up` catches the stale approval.

## Prerequisites

- Claude Code with plugin support
- The review harness available to the workspace (`.local/preflight.sh`, `.local/<KEY>/assumptions.md`)
- A tier proposal from `/quartermaster:plan` before running `/quartermaster:review`

## Trackers

`/quartermaster:story` detects the tracker from the issue URL — `*.atlassian.net/browse/…` →
Jira, `linear.app/…/issue/…` → Linear — and asks you which one only when given a bare key it
can't disambiguate. Everything downstream reads `.local/<KEY>/assumptions.md`, so `plan` and
`review` don't care which tracker produced it. Both tracker MCPs ship bundled in `.mcp.json`:

| Tracker | MCP server | Auth |
|---|---|---|
| Jira / Confluence | `atlassian` (`mcp.atlassian.com`) | OAuth on first use |
| Linear | `linear` (`mcp.linear.app`) | OAuth on first use |

Either one you don't use simply stays unauthenticated — it degrades gracefully.

## Install

From the `nily-plugins` marketplace:

```
/plugin marketplace update nily-plugins
/plugin install quartermaster@nily-plugins
```

---
name: story
description: Start a session on an issue in Jira or Linear — detect the tracker from the URL (ask when it can't tell), read the issue, its comments, and any linked Figma, brief the engineer, then brainstorm. Use when invoked as /quartermaster:story <issue-url-or-key> [figma-url], or to start/open/kick off an issue.
---

# Quartermaster — Story Kickoff

Tracker-agnostic morning kickoff. Reads an issue from **Jira or Linear**, briefs the engineer,
and writes the story contract that `/quartermaster:plan` and `/quartermaster:review` build on.

Arguments: `$ARGUMENTS` — the first is the issue URL or key, the second is a Figma URL (either
may be omitted).

Create a todo per step and work through them in order.

## Tools

This plugin bundles **both tracker MCP servers** (`.mcp.json`): `atlassian` and `linear`. Use
their tools by capability — exact names depend on how each server is namespaced in this
session, so discover them with ToolSearch if they aren't already loaded.

- **Jira** — read an issue (typically `getJiraIssue`); if a `cloudId` is required and unknown,
  first call the accessible-resources tool (typically `getAccessibleAtlassianResources`).
  Include comments via the read call's fields/expand.
- **Linear** — read an issue (typically `get_issue`) and its comments (typically
  `list_comments`).
- **Figma MCP** is optional and NOT bundled — only use it if the user has it connected AND a
  Figma URL is present (tools like `get_design_context`, `get_screenshot`, `get_metadata`).

Never invent issue keys, ticket fields, or Figma node data — read them from the tools.

## Steps

### 1. Identify the tracker and key

Decide which tracker this is, then extract the key:

- **Jira URL** — host is `*.atlassian.net`, path `.../browse/PROJ-123` → tracker `jira`, key is
  the segment after `/browse/`.
- **Linear URL** — host is `linear.app`, path `.../issue/ENG-123/...` → tracker `linear`, key
  is the `TEAM-NNN` identifier segment.
- **Bare key or no argument** — the tracker is ambiguous (`VMNC-123` and `ENG-123` look
  alike), so **ask the engineer: "Which tracker — Jira or Linear?"** and for the URL/key if
  missing, before continuing.

If a Figma URL is missing, ask whether to continue without it (some issues have no design).

### 2. Read the issue

Call the matching tracker's issue-read tool with the key. Capture: title, description, status,
and acceptance criteria. For Jira, resolve `cloudId` first if the read needs it.

### 3. Read existing comments

Include comments (Jira: fields/expand on the read; Linear: `list_comments`). The point is to
be caught up — do NOT re-ask about things already decided in the comments.

### 4. Read the Figma (optional)

Only if a URL was given or the issue links one. If there's no Figma, skip silently. If a URL
is present but the Figma MCP isn't connected, say so briefly and continue. Otherwise use the
design-context tool (plus screenshot/metadata as useful) on the node in the URL.

### 5. Write the story contract

Create `.local/<KEY>/assumptions.md` (where `<KEY>` is the issue key). Overwrite any previous
contents with:

```yaml
- **tracker:** <jira | linear>
- **issue_key:** <KEY>
- **issue_url:** <url>
- **figma_url:** <url, if any>
- **title:** <short one-line title>
- **date:** <today, ISO>

## Story
<a few lines: what the issue asks for, plus the acceptance criteria>
```

This is the contract `/quartermaster:plan` appends its risk tier and file inventory to.

### 6. Brief the engineer

Short, plain briefing: what the issue asks for, what's already been decided in the comments (so
nothing is repeated), and what the design shows. A few bullets, not a wall of text.

### 7. Brainstorm the work

If the `superpowers:brainstorming` skill is available, invoke it, carrying the issue + design
context into it. If it is NOT available, do NOT fail or install anything — run a brief inline
brainstorm instead: propose 2–3 approaches with tradeoffs, recommend one, and confirm the plan.

## Next step

Run `/quartermaster:plan <KEY>` to propose the risk tier and file inventory.

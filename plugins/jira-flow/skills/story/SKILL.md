---
name: story
description: Start a morning session on a Jira story — read the ticket, its existing comments, and any linked Figma design, brief the engineer, then brainstorm the work. Use when invoked as /jira-flow:story <jira-url> [figma-url], or when asked to start/open/kick off a Jira story.
---

# Jira Flow — Story Kickoff

Morning kickoff for a Jira story in **any project**. Arguments: `$ARGUMENTS` — the
first is the Jira story URL, the second is a Figma URL (either may be omitted).

Create a todo per step and work through them in order.

## Tools

This plugin bundles the **Atlassian MCP server** (`.mcp.json`). Use its tools by
capability — exact tool names depend on how the server is namespaced in this session,
so discover them with ToolSearch if they aren't already loaded:

- **Read a Jira issue** (typically named like `getJiraIssue`) — pass the issue key;
  if a `cloudId` is required and unknown, first call the accessible-resources tool
  (typically `getAccessibleAtlassianResources`).
- **Figma MCP** is optional and NOT bundled — only use it if the user has it
  connected AND a Figma URL is present (tools like `get_design_context`,
  `get_screenshot`, `get_metadata`).

Never invent Jira keys, ticket fields, or Figma node data — read them from the tools.

## Steps

1. **Get the links.** Parse the Jira key from the URL: the segment after `/browse/`
   (e.g. `https://<site>.atlassian.net/browse/PROJ-123` -> `PROJ-123`).
   - If the Jira URL is missing, ask for it before continuing.
   - If the Figma URL is missing, ask whether to continue without it (some tickets
     have no design).

2. **Read the ticket.** Call the Jira issue-read tool with the key. Capture: title,
   description, status, and acceptance criteria.

3. **Read existing comments.** Include comments in the issue-read call
   (fields/expand) so you see the full discussion. The point is to be caught up —
   do NOT re-ask about things already decided in the ticket comments.

4. **Read the Figma** (optional — only if a URL was given or the ticket links one).
   If there's no Figma, skip this step silently and don't ask for one. If a URL is
   present but the Figma MCP is not connected, say so briefly and continue without
   it. Otherwise use the design-context tool (plus screenshot/metadata as useful) on
   the node in the URL. Note the key screens/components and any design notes.

5. **Write the state file** at `~/.claude/plans/active-story-<project>.md`, where
   `<project>` is the current repo/working-directory folder name
   (`basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"`). Keying it per
   project lets each repo have its own active story. Never commit planning artifacts
   into a repo. Overwrite any previous contents for this project with:
   - `date:` today's date in ISO format (used by wrap-up to detect stale state)
   - `jira_key:` the key
   - `jira_url:` the URL
   - `figma_url:` the URL, if any
   - `title:` a short one-line title

6. **Brief the engineer.** Give a short, plain briefing: what the story asks for,
   what has already been said in the comments (so nothing is repeated), and what the
   design shows. Keep it tight — a few bullet points, not a wall of text.

7. **Brainstorm the work.** If the `superpowers:brainstorming` skill is available,
   invoke it, carrying the ticket + design context into it. If it is NOT available,
   do NOT fail or install anything — run a brief inline brainstorm instead: propose
   2–3 implementation approaches with tradeoffs, recommend one, and confirm the plan
   before any code is written. This is the end of the kickoff.

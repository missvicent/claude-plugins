---
name: wrap-up
description: Wrap up the session — draft a high-level summary of the work in the engineer's voice and post it to the Jira story only after explicit approval. Use when invoked as /jira-flow:wrap-up, or when asked to wrap up / post the Jira progress comment.
---

# Jira Flow — Wrap-up

Close out a work session by posting a high-level progress comment to the Jira story,
written in first person as **${user_config.engineer_name}**.

Create a todo per step and work through them in order.

## Tools

This plugin bundles the **Atlassian MCP server** (`.mcp.json`). Use its tools by
capability — discover exact names with ToolSearch if needed:

- **Add a comment to a Jira issue** (typically named like `addCommentToJiraIssue`).
- **Read a Jira issue** (typically `getJiraIssue`) — to re-check the ticket's
  language/convention if it isn't in context.

## Steps

1. **Recover the ticket.** Get the Jira key from the current conversation. If it
   isn't in context, read `~/.claude/plans/active-story-<project>.md` for the current
   project (`basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"`). If
   still unknown, ask for the Jira URL.

2. **Confirm the destination.** Posting to the wrong ticket is the worst failure
   mode of this flow. If the key came from the state file (not from this
   conversation), OR the state file's `date` is not today, explicitly confirm before
   drafting: "I'll post the wrap-up to **<KEY> — <title>**. Correct?" Wait for a yes,
   or a different ticket, before continuing.

3. **Gather what was done.** Look at the git diff and log for the session's work
   (`git diff`, `git log --oneline`, `git status`) plus what was actually worked on
   in the conversation. Focus on outcomes and behavior, not code internals.

4. **Draft the comment** as ${user_config.engineer_name}:
   - **Language: match the ticket.** Write in whatever language the ticket's
     description and existing comments use (Spanish, English, etc.) — mirror the
     project's convention rather than forcing one language. First person,
     casual-professional.
   - **High-level, not deeply technical.** Describe what was built/changed and its
     effect for the story, not implementation detail (no class names, no file paths,
     no framework jargon unless the ticket itself is about it).
   - A few sentences or short bullets. Concise.

5. **Show the draft and WAIT.** Print the drafted comment and ask for approval or
   edits. **Never post without explicit approval** — this is an outward-facing
   action. If edited, revise and show again.

6. **Post it.** On approval, call the add-comment tool with the key and the approved
   text. Confirm success and give the ticket link. If the post fails, show the error
   and the approved text so nothing is lost — do not silently retry more than once.

## Rules

- Never post to Jira without explicit approval of both the **destination ticket**
  and the **comment text**.
- Do not commit or push git changes as part of this flow.
- Never invent Jira keys or ticket fields — read them from the tools.

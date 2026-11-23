# Brief sources

How to turn each source into `tracker.json` fields. Whatever the source, the
brief goes in verbatim; tasks are derived from it, then checked against the
real state of the work.

## Lesson card (pasted)

Course exercise cards often look like this (an invented example):

```
LAB.2
Build a link shortener that never loses a link
faded
proves implement
Write the store behind the shortener and the checks that prove it: every code
maps to one URL, a deleted code is never reused, ... Then load it at 10, 100
and 1000 links, checking the counts at each step.

repo: phase2-web/02-link-shortener
~60 min · ~2 h first pass
solution notes
```

| Card line | Field |
|---|---|
| `LAB.2` (an id like `EX.3`, `LAB.2`) | `eyebrow` |
| the line after the id | `heading` |
| short lowercase lines before the paragraph (`faded`, `proves implement`) | `tags` |
| the paragraph | `brief`, verbatim |
| `repo: …` | `meta.Repo`, in backticks; also where to check status |
| `~60 min · …` | `meta.Time` |
| `solution notes` and other link labels | drop; they were links in the source |

`feature` is the last part of the repo path without its number
(`phase2-web/02-link-shortener` → `link-shortener`). `title` is a short name such as
"Link Shortener Work".

Tasks come from the brief's own requirements, one row per deliverable; the
parts a deliverable lists go in its `details`, not in rows of their own. For
the example: "write the store", "write the checks" (details: the four checks
it names), and "load at 10, 100 and 1000 links" (details: check the counts at
each step). Then look in the repo for what the brief
assumes (stub files, test files) and add rows for those.

## Plan or spec file

Plans from brainstorming or a planning step (`docs/superpowers/plans/*.md`,
`docs/superpowers/specs/*.md`, or a plan written in the conversation).

| Plan | Field |
|---|---|
| plan title | `heading` |
| goal / summary paragraph | `brief`, verbatim |
| file path | `meta.Plan` |
| each numbered step or task | a task, in order; its checklist items become `details` |
| open questions, risks, "decide later" items | `problems` (severity `edge`) |

A plan usually comes before code, so every task starts as `todo` (see "No
code yet" in SKILL.md). Plan checkboxes already ticked (`- [x]`) are a
starting point for `done`, then checked against the code like card statuses.

## Linear card

The Linear MCP server comes from the claude.ai Linear connector. Its tools are
deferred: load the ones needed in one call first, e.g.
`ToolSearch("select:mcp__claude_ai_Linear__get_issue,mcp__claude_ai_Linear__list_comments,mcp__claude_ai_Linear__list_issues")`.

1. `get_issue` with the id from the link or text (`ENG-123`).
2. `list_comments` on it, for decisions made after the card was written.
3. Sub-issues, if any (`list_issues` filtered by parent).

| Linear | Field |
|---|---|
| title | `heading` |
| description | `brief` |
| identifier + URL | `meta.Card` |
| sub-issues | tasks; their state gives a first `status` (Done → `done`, In Progress → `wip`, else `todo`) |
| checklist items in the description | tasks |
| blocking comments, open questions | `problems` |

A sub-issue's Linear state is a starting point, not the answer: still check
the code (step 3 of the workflow), and say so when they disagree.

## Jira card

The Atlassian MCP server comes from the `jira-flow` plugin. Load its tools
first, e.g.
`ToolSearch("select:mcp__plugin_jira-flow_atlassian__getAccessibleAtlassianResources,mcp__plugin_jira-flow_atlassian__getJiraIssue")`.

1. `getAccessibleAtlassianResources` to get the `cloudId` for the site in the
   link (`<site>.atlassian.net`).
2. `getJiraIssue` with that `cloudId` and the key (`PROJ-42`). Its comments
   come with the issue.

| Jira | Field |
|---|---|
| summary | `heading` |
| description | `brief` |
| key + URL | `meta.Card` |
| subtasks | tasks, status mapped as for Linear |
| acceptance criteria | tasks, or "done when" `details` on the task they belong to |
| blocker comments, flagged issues | `problems` |

## When an integration isn't there

The MCP tools don't exist, the server needs authentication, or the call
errors: don't retry in a loop. Tell the user in one line which integration
isn't available, and ask them to paste the card's title, description and any
checklist. Treat the paste like a card from that tool: same field mapping,
with `meta.Card` set to the key or link they give.

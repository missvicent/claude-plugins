# Lesson Tracker

Trackers that an agent and a human can both work against. Every task says **who
does it** (you or an agent), **what done means** (a goal a stranger could test),
and **how to prove it** (a check). An autonomous agent does and verifies its own
tasks; a teaching agent guides you through yours without writing them for you.
When a lesson ends, a retro turns what went wrong into typed notes in your
Obsidian vault, and the next tracker reads them back.

Built for learning by hand (courses, workbooks, katas), and works just as well
for a Linear or Jira card.

## Commands

| Command | What it does |
|---|---|
| `/lesson-tracker:task-tracker` | Build or update the tracker for a lesson, plan, card or feature: the brief, a table of tasks with owner, goal, check, shapes and steps, open decisions, problems and a suggested order. Publishes it as an Artifact (same link on every update) and keeps the data in your vault. |
| `/lesson-tracker:work-from-tracker` | Do or check the work: "let's do task 6", "continue", "is this done?", "let's do the retro". |

Both also trigger on their own when you talk about the work, so you rarely type them.

## How it works

**Each task is a contract**

| Field | Meaning |
|---|---|
| `by` | `you` (you write it, the agent guides and reviews) or `agent` |
| `goal` | one sentence about the result, testable by a stranger |
| `check` | `run` (a command and what it must print), `ask` (same, but asks you first: local model, money, or you at the keyboard), or `review` (a list of what must be present) |
| `shapes` | the data a code task reads and returns, so you never guess a dict key |
| `steps` | what to do, in plain words, never code |
| `run_as` | for agent tasks: `workflow` (follow the steps exactly) or `subagent` (path unknown, hand it off, then re-run the check) |

**Rules the agent keeps** (`work-from-tracker`)

1. Respects `by`: never writes your task unless you ask.
2. Marks a task done only after its check passes in this session, not on "it works".
3. Reports a failed check plainly; status stays in progress.
4. Never decides silently: critical points become problems, open questions become decisions on the page.
5. Follows `workflow` steps as written; a step that can't be done is reported, not improvised.
6. Logs every check (last 5 kept per task) and updates the page.
7. When the lesson is done, offers a retro.

**Learning loop**

```
check runs ──► log ──► retro at lesson close ──► insights/ (typed notes)
                                                     │
next tracker reads matching insights ◄───────────────┘
```

Insights are one note each, with properties `type` (pitfall, practice,
preference, tool-fact), `topic`, `applies_to`, `status` and `seen`. A
`memory.base` file shows them as tables in Obsidian. An insight confirmed in two
retros becomes a proposed edit to a skill, which you approve.

## Where your data lives

Nothing personal is stored in the plugin. Everything is in your vault:

```
<vault>/projects/<project>/
├── trackers/<feature>/   tracker.json (source), tracker.md (readable), tracker.html, artifact-url.txt
├── insights/             one note per lesson learned
├── retros/               one note per finished lesson
└── memory.base           optional Bases views over insights/
```

## Setup

On first use the agent runs `vault.py setup`, which reads Obsidian's own list of
vaults and asks you to pick one by number. The choice is saved in
`~/.config/lesson-tracker/config.json`; each repo is mapped to a vault project
the first time you make a tracker from it. Say "change my tracker vault" to
pick again. No Obsidian? Give it any folder that contains `.obsidian/`.

`TRACKER_VAULT=/path` overrides the saved vault for one run.

## Prerequisites

- Claude Code with plugin support
- Python 3.9+ (the scripts use only the standard library)
- An Obsidian vault (or any folder with a `.obsidian/` folder in it)
- Google Chrome, only if you want PDF copies

## Install

From the `nily-plugins` marketplace:

```
/plugin marketplace update nily-plugins
/plugin install lesson-tracker@nily-plugins
```

## Develop

`bash skills/task-tracker/scripts/selfcheck.sh` checks the vault lookup, setup,
log cap and insights filter in a temp folder. Each skill's `evals/` folder holds
test cases in the `claude plugin eval` format.

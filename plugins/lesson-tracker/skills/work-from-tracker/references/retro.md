# Retro and insights

Read this when running a retro (rule 7). Paths below are relative to the
tracker's vault project folder: the `projects/<project>/` folder that holds
`trackers/<feature>/` (two levels above `tracker.json`), e.g.
`<vault>/projects/my-course/`. `<task-tracker>` below is the task-tracker
skill's base directory.
The vault's notes are for an agent *and* a human, so every note is typed and
short; free-form prose doesn't get reused.

## 1. Gather (read only)

- `tracker.json`: each task's `log`, `log_summary`, `decisions`, `problems`.
- This session: where the human asked follow-ups (unclear steps), what took
  longer than planned.
- Existing insights that could be confirmed:
  `python <task-tracker>/scripts/insights.py projects/<project> --topic <this lesson's topics>`

## 2. Write the retro note: `retros/YYYY-MM-DD-<feature>.md`

Always exactly these properties and sections; write "none" in an empty section
rather than dropping it, so every retro compares with every other.

```markdown
---
lesson: <feature>
date: YYYY-MM-DD
time_budget: "<from the tracker meta, if any>"
time_actual: "<ask the human if you don't know; never guess>"
tasks: <required task count>
first_try_passes: <tasks whose first log entry is pass>
tracker: "[[<feature>]]"
---
## What failed first
- task N: <the first failing note, and the cause>

## Unclear steps
- task N, step M: <what the human had to ask>

## Decisions made
- <question> → <answer>

## Insights created or confirmed
- [[<insight-slug>]] (new | confirmed, seen N)
```

Write about the work, not the person: "step 2's shape didn't say `args` is a
dict", not "the user got confused".

## 3. Update insights: `insights/<slug>.md`

For each thing a future session should do differently:

1. **Is it worth keeping?** Only if it would change what an agent does next
   time (a trap, a working method, a user preference, a tool fact). A one-off
   typo is not an insight.
2. **Does it exist?** Run `insights.py` with its topic; compare the rule, not
   the wording.
   - Same rule → **confirm**: `seen + 1`, `last_seen` = today, add this retro to
     the body's "Seen in" line.
   - Contradicted by this lesson → set the old one `status: retired`, then
     write the new one.
   - New → **create** it:

```markdown
---
type: pitfall | practice | preference | tool-fact
topic: <one library or area, lowercase-hyphen: langgraph, pydantic-ai, crewai, testing, process>
applies_to: [coding | teaching | tracker-build]
status: active
seen: 1
first_seen: YYYY-MM-DD
last_seen: YYYY-MM-DD
source: "[[YYYY-MM-DD-<feature>]]"
---
<One sentence: the rule.>
**Why it matters:** <one sentence: what it cost or saved.>
Seen in: [[YYYY-MM-DD-<feature>]]
```

The file name (slug) is the rule in kebab-case, e.g. `crewai-needs-py312`, so
duplicates show up by name. Keep the active set small (about 40): retiring is
as important as adding.

A `preference` about the user that must hold in *every* session (not just
tracked work) belongs in Claude's memory instead; the insight may link to it,
never copy it.

## 4. Promote

For each active insight with `seen >= 2` whose `applies_to` names a skill's job
(`tracker-build` → task-tracker, `teaching` or `coding` → work-from-tracker or
the lesson's CLAUDE.md), draft the one-paragraph change to that skill's text and
show it to the human. Apply only on their yes.

## 5. Report

Tell the human: the retro note's link, insights created / confirmed / retired
(by name), and any proposed skill edit. Mention that `vault-push` can back the
vault up; run it only if they ask.

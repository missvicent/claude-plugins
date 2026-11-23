---
name: work-from-tracker
description: Rules for doing or checking work that a task tracker (from the task-tracker skill) tracks — respect who owns each task (`by: you` means the human writes it and you only guide and review; `by: agent` means you do it), mark a task done only after its check (run / ask / review) passes in this session, stop and report critical problems and open decisions instead of choosing, log every check, offer a retro that writes structured lessons into the Obsidian agent memory when the lesson is done, and run agent tasks as a fixed workflow or hand them to a subagent when the path can't be listed. Use this whenever the user says "let's do task 6", "continue the lesson", "next task", "check task 3", "is this done?", "work through the tracker", "review my code for the tracker", "let's do the retro", "what did we learn", or starts working on any feature, lesson or exercise that already has a tracker (kept in the user's Obsidian vault), even if they don't mention the tracker.
---

# Work from a tracker

A tracker (made by the `task-tracker` skill) is a contract: each task says who
does it (`by`), what "done" means (`goal`), and how to prove it (`check`). This
skill is how you keep that contract, whether you are doing the work yourself or
teaching a human who writes it by hand.

The tracker lives in the user's Obsidian vault at
`<vault>/projects/<project>/trackers/<feature>/tracker.json`. Find it with
`python <task-tracker skill>/scripts/vault.py find <feature>` (the task-tracker
skill's base directory; it sits next to this skill). "No vault set" means
first use: follow task-tracker's step 1 to set it up.
Its field meanings are in that skill's `SKILL.md` ("Content rules" and
"Schema"); read them if a field here is unclear. After every check, update the
tracker through the `task-tracker` skill (rebuild and republish to the same
link), so its page never disagrees with what you just verified.

## Before starting a task

1. Read `tracker.json`. Find the task the user means; if they just say
   "continue", take the first task in `order` (or table order) that isn't
   `done`.
2. If any earlier task in the order isn't `done`, say so and ask before
   skipping ahead. Later tasks usually build on earlier ones, and starting out
   of order is how a lesson ends up with code that passes nothing.
3. If an `open` decision blocks this task, ask it first (question plus
   options). Don't pick an option yourself.

## Rule 1: respect `by`

**`by: agent`**: do the work, then run the check (rule 2).

**`by: you`**: the human writes it, usually to learn by doing, so writing it for
them takes the lesson away even when it would be faster. Instead:
- Show the task's `shapes` first (the data it reads and returns), then walk the
  `steps` one at a time, in plain words.
- When they share code, review it against the `goal` and `shapes`: say what is
  right, then name each problem, where it is, and why. Let them fix it.
- Write their code only if they explicitly ask you to ("write it", "fix it for
  me"). A question like "how do I…?" is a request for an explanation, not code.
- A tracker without `by` (older format): look in `details` for "you write it"
  or "Claude writes it"; if nothing says, ask.

## Rule 2: status comes from the check, in this session

A task becomes `done` only when its check passed *now*, not because it passed
yesterday, the human says it works, or a subagent reported success.

| `check.kind` | What you do |
|---|---|
| `run` | Run `cmd`. Compare the output with `expect`. |
| `ask` | Ask the human before running `cmd` (it needs a local model, money, or the human at the keyboard). On yes, run it and compare; if the human must run it, ask them to paste the output and compare that. |
| `review` | No command. Read the work and check each `look_for` item: list each missing one, or confirm all are present. |

No `check` on the task (older tracker)? Use any "done when …" in `details`; if
there is none, propose a check to the human and add it to the tracker once they
agree.

## Rule 3: report a failed check plainly

Status stays `wip`, and `now` says exactly what failed ("8 of 10 passed: the 2
resume tests fail"). Tell the human the same thing with the real output. Never
round a failure up to done, and never call a partial pass "basically working".

## Rule 4: stop and report, never decide silently

Some things aren't yours to settle, and guessing hides them in the work where
nobody notices until much later.

- **Critical point**: the goal or plan looks wrong, a check can never pass as
  written, data could be lost, or it needs money or secrets. Stop that task,
  add a `problems` row with severity `bad` and its location, and tell the human
  now.
- **Decision**: two valid ways forward, or the brief doesn't say which. Add an
  `open` entry to `decisions` (question, options, the task it blocks) and ask.
  That task waits; tasks that don't depend on it can go on.

When the human answers, set the decision to `decided` with their `answer`, so
the page keeps a record of why things are the way they are.

## Rule 5: `run_as` for agent tasks

- **`workflow`** (the default): the path is known. Follow `steps` exactly, in
  order, adding none. A step that can't be done as written is a critical point
  (rule 4), not an invitation to improvise.
- **`subagent`**: the path can't be listed ahead (research, debugging, "find
  why X fails"). Hand a subagent the task's `goal`, `check` and `shapes`, with
  `steps` as hints, and tell it to follow rules 1–4: escalate decisions and
  critical points back instead of choosing. The `run_as: subagent` field is the
  human's permission to spawn it. When it reports back, run the check yourself;
  its report is a claim, not evidence.

## Rule 6: update the tracker after every check

Pass or fail, append one entry to the task's `log`
(`{"date": "YYYY-MM-DD", "result": "pass" | "fail", "note": "<one line: what passed or failed>"}`),
update `status` and `now`, add or close problems and decisions, rebuild, and
republish (through `task-tracker`). `build.py` trims the log; don't. Then tell
the human in one line what changed on the tracker.

The log is what later sessions learn from: a note like "8 of 10: wrong key
`pendng`" says much more at retro time than "fail".

## Rule 7: offer the retro when the lesson is done

When the last required task becomes `done`, offer it in one line: "Lesson done.
Retro now?". Run it only on yes, or when the human asks ("let's do the retro"),
because it writes notes into their Obsidian vault. Follow
`references/retro.md`: it writes one retro note with fixed properties and
sections, then confirms, adds or retires insight notes in the tracker's own
vault project (the `projects/<project>/` folder the tracker sits in). An insight confirmed in 2+ retros that
names a skill's job is a candidate skill edit: propose the edit to the human,
never apply it yourself.


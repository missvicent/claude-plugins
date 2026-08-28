---
name: plan
description: Plan the review orchestration for an issue — propose a risk tier (which decides how many parallel review workers run at review time) and estimate the file inventory. Tracker-agnostic (Jira, Linear, or any /story upstream). Use when invoked as /quartermaster:plan <issue-key>, or during story planning after the story contract is written.
---

# Quartermaster — Plan (Stage 2)

Set up the orchestration strategy for an issue: propose the **risk tier** (which
determines how many parallel review workers get dispatched at review time) and estimate
which files will be touched (so the review step can use that as a boundary).

Runs after `/quartermaster:story` (or any `/story` upstream) has written the story contract,
as part of the planning phase. Quartermaster is tracker-agnostic — it only consumes
`assumptions.md`, so it doesn't care whether Jira or Linear produced it.
Argument: `$ARGUMENTS` — the issue key (e.g. `VMNC-123` in Jira, `ENG-123` in Linear).

Create a todo per step and work through them in order.

## Prerequisites

- `.local/<KEY>/assumptions.md` exists (written by `/quartermaster:story`, or any equivalent `/story` upstream)
- You've read the ticket, the design, and the code it touches

## Steps

### 1. Classify the risk tier

Does this story touch any of these?

- **Authentication** — login, session, token handling, password reset
- **Cryptography** — encryption, key derivation, signing
- **Money movement** — transfers, payments, balance updates
- **Personally identifiable information (PII)** — addresses, government IDs, phone numbers
- **Network security** — certificate pinning, TLS enforcement, hostname verification

- **Yes to any** → `high`
- **Touches important business logic but none of the above** → `med`
- **UI / cosmetic / refactor only** → `low`

### 2. Write the tier to assumptions.md

Add this section to `.local/<KEY>/assumptions.md`:

```yaml
## Orchestration (Quartermaster)

- **Risk tier (plan proposal):** <high | med | low>
- **Rationale:** <one sentence — why this tier>
- **Review override:** [left blank — filled in by /quartermaster:review if the tier changes]
```

### 3. Estimate the file inventory

List the files you expect to touch in `.local/<KEY>/file-inventory-proposed.txt`, one per
line, relative to repo root. The review step uses this as a boundary check.

### 4. Brief the engineer

Tell them the tier you proposed and why, in one or two lines.

### 5. Ready for build

Planning is complete — the tier and inventory are recorded for `/quartermaster:review`.

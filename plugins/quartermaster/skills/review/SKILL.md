---
name: review
description: Orchestrated review of completed work — run gates, dispatch parallel code + security reviews by risk tier, synthesize findings, and record an approval fingerprinted to the exact diff. Use when invoked as /quartermaster:review, or when the implementation is complete and ready for sign-off.
---

# Quartermaster — Review (Stage 5)

Conduct an orchestrated review of the completed work:

1. **Assess risk tier** — the plan step proposed it; you can override based on the actual code
2. **Dispatch by tier** — high/med runs two reviews in parallel, low runs one
3. **Await workers** — each worker signals done with a short findings summary
4. **Synthesize & present** — show findings side-by-side
5. **Approve or request fixes**
6. **Record fingerprint** — tie the approval to this exact diff

Create a todo per step and work through them in order.

## Prerequisites

- `.local/preflight.sh` passes (gates are green)
- Implementation is complete
- `.local/<KEY>/assumptions.md` exists with a tier proposal from `/quartermaster:plan`

## Steps

### 1. Confirm gates passed

Run `bash .local/preflight.sh`. Every gate must exit 0. If any fail, stop and fix first.

### 2. Re-assess the risk tier

Read the tier proposed by `/quartermaster:plan`. Does it still hold given the real diff? To
override, record it in `.local/<KEY>/assumptions.md`:

```yaml
- **Review override:** Changed low → med after seeing the implementation.
```

### 3. Dispatch by tier

- **high or med** — two parallel reviews: `code-review` (opus) + `security-review` (opus)
- **low** — one review: `code-review` (sonnet)

Dispatch the workers in parallel (single message, one Agent call per worker). Give each a
short spec: the diff boundary (`file-inventory-proposed.txt`), the tier, and a
`--report-path` to write its summary to.

### 4. Await worker findings

Each worker writes a short summary (~10–20 lines) to its report path and exits. Wait for all
dispatched workers to finish before synthesizing.

### 5. Synthesize & present

Read the summaries only (never the full reports) and present the findings side-by-side to the
engineer.

### 6. Device pass (if UI-facing)

If the work is UI-facing, take a screenshot on a real device before approving.

### 7. Request fixes or approve

After seeing the findings, decide. For high/med, **both** reviews must come back clean (or
have their findings resolved) before approval.

### 8. Record approval + fingerprint

Write `.local/<KEY>/review.md` with the tier, findings, the approval, and a fingerprint of the
current diff (e.g. `git diff | shasum`). This ties the approval to this exact diff.

## Rules

- An approval only counts against findings actually presented.
- For high/med, both reviews must succeed — no half-approvals.
- The fingerprint is immutable. If the code moves after approval, the fingerprint changes and
  `/wrap-up` catches the stale approval.
- Device pass is mandatory for UI work.

## Next steps

With approval recorded, wrap-up can run — it verifies the fingerprint still matches before
posting anything.

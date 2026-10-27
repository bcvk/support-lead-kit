---
name: qa-review
description: Review a support ticket, chat or email reply against a weighted QA scorecard and produce a 0 to 100 score with per criterion reasoning and coaching ready feedback. Use when the user pastes a support conversation and asks to QA it, grade it, review it, or check it against the scorecard.
---

# QA review

Score the reply the agent wrote, not the customer's behavior. Default scorecard: `${CLAUDE_PLUGIN_ROOT}/scorecards/default.yaml`. If the user's repo or message contains another scorecard, use that one.

## Procedure

1. Read the whole conversation once before scoring. Identify what the customer actually asked (there is often more than one thing).
2. For each criterion give 0, 1 or 2 and one sentence of evidence quoting the ticket. No evidence, no score.
3. Auto fail criteria at 0 set the final score to 0. Say so plainly at the top.
4. Compute: criterion points = weight × value / 2, then sum. Show the per category subtotal. Pass threshold is in the scorecard (default 85).
5. For every criterion scored 0 or 1, tag the root cause with exactly one of: `agent` (knew the right thing, did not do it), `knowledge` (did not know; KB or training gap), `process` (followed a process or macro that produced the bad outcome), `tooling` (system, access or data problem). Only `agent` and `knowledge` belong in the agent's coaching note; `process` and `tooling` go to the team lead's own backlog. Say this split explicitly, it is the thing most QA programs get wrong: agents get coached for macro errors.
6. Write the feedback in SBI form (situation, behavior, impact), two strengths and one thing to change. The thing to change must be an observable behavior tied to a criterion id, not a trait.
7. If the user gives a CSV of many reviews, do not score by hand; run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/score.py --scorecard <file> --input <csv> --by agent`.

## Output shape

```
Score: 78.5 / 100  (pass threshold 85)  FAIL
Auto fail: none

Accuracy 28/35 · Communication 25/30 · Efficiency 13/20 · Empathy 12.5/15

correct_info 2  "the 14 day window is stated correctly"
resolved     1  "refund promised but no date given"            root cause: agent
policy       1  "macro M12 still says 7 days, agent used it"   root cause: process (fix the macro, not the agent)
...

Feedback for the agent
Strengths: ...
Change one thing: ...
```

Do not soften a 0. Do not invent context the ticket does not contain. If a criterion cannot be judged from the text (for example internal notes you cannot see), mark it "not visible" and exclude its weight from the denominator, and say that the score is rescaled.

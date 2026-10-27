---
name: nesting-review
description: Review a new agent's nesting or onboarding week (volume, QA, AHT, CSAT, escalations), decide on_track / at_risk / extended / graduate, and draft the weekly feedback email. Use when the user mentions nesting, onboarding week, new hire ramp, graduation to production, or shares the nesting tracker.
---

# Nesting review

Playbook and targets: `${CLAUDE_PLUGIN_ROOT}/templates/nesting-playbook.md`. Tracker format: `${CLAUDE_PLUGIN_ROOT}/templates/nesting-tracker.csv`.

## Procedure

1. Read this week's row and the previous weeks for the same agent. Trend matters more than one number.
2. Compare to the week's targets from the playbook, or to the user's own targets if they give them.
3. Decide the status with the playbook rule: all targets met → on_track; one missed with a plan → at_risk; week 4 with one target missing → extended (one week, one plan); week 4 with two or more missing → escalate to the manager, do not extend silently.
4. Draft the weekly feedback email in the playbook's shape: verdict in the first paragraph and the last line, two specifics that went well with ticket ids, one thing to work on, the numbers, next week's plan.
5. Append the tracker row the user should paste, including status and blocker.

Keep the email under 200 words. Agents in their second week do not need a performance review, they need to know whether they are okay and what one thing to do next.

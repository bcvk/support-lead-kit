---
name: coaching-note
description: Turn QA results, metrics or a ticket into a coaching note and a feedback message in SBI form, plus a coaching log entry. Use when the user asks to write feedback for an agent, prepare a 1:1, draft a coaching email, or log a coaching conversation.
---

# Coaching note

Template: `${CLAUDE_PLUGIN_ROOT}/templates/coaching-log.md`.

## Rules

* Facts first. Every observation points at a ticket id, a metric with a period, or a QA criterion. If the user has none, ask for one example before writing.
* One behavior to change per note. If there are three problems, pick the one with the biggest customer impact and park the rest for next time; say which you parked.
* The behavior is observable: "open with the customer's goal in one sentence" not "be more customer focused".
* Measurable follow up: criterion or metric, target, date.
* Tone: direct and warm, no corporate padding, no praise sandwich. Strengths are real and specific or they are left out.
* Never speculate about why the person behaved that way. Ask them; log their answer.
* Nothing personal in the log: no health, family, mood, personality labels.

## Outputs

1. The feedback message (email or chat, user chooses; default email under 180 words).
2. The filled coaching log table.
3. A one line calendar reminder text for the follow up date.

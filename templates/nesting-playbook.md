# Nesting playbook (4 weeks from training to production)

Nesting is the window where a new agent handles real tickets with a safety net. The tracker in `nesting-tracker.csv` has one row per agent per week. Fill it every Friday; it takes ten minutes and it is the only thing that makes the week 4 go or no go decision defensible.

## Weekly targets

| Week | Volume | QA target | Reviews | Shadowing | Other |
|---|---|---|---|---|---|
| 1 | 25 to 50% of a full queue | none, baseline only | 4 | 2 sessions (they watch you) | Every ticket reviewed before send if possible |
| 2 | 50 to 70% | 80 | 5 | 1 session (you watch them) | Introduce macros and tagging |
| 3 | 70 to 90% | 82 | 5 | as needed | First solo escalation |
| 4 | 90 to 100% | 85 (the scorecard pass threshold) | 6 | none | Go or no go decision |

Targets are starting points. Set yours from your team's actual pass threshold and the median AHT of agents in their first three months, not from the top performer.

## Weekly feedback email

Send one every week, same day, same shape. Agents read the first paragraph and the last line; put the verdict in both.

```
Subject: Week 2 nesting summary, [name]

Hi [name],

Short version: you are on track. QA moved from 78 to 84 and the refund flow issue from last week is gone.

What went well
* [specific, with ticket id]
* [specific]

One thing to work on this week
* [one behavior, observable, with the criterion it maps to]

Numbers
* Tickets: 41 (target 40 to 55)
* QA: 84.0 over 5 reviews (target 80)
* AHT: 11.8 min (team median 10.5)
* Escalations: 0

Next week: [shadowing session or focus], and I will review 5 more tickets.

Status: on track
```

## Go or no go at week 4

Graduate when all of these hold over weeks 3 and 4 combined: QA at or above the team pass threshold, no auto fail, volume at 90% or more of a full queue, and no open blocker in the tracker. If one is missing, extend by one week with a written plan for that one thing. If two or more are missing in week 4, that is a conversation with your manager, not another extension.

## Status values

`on_track`, `at_risk` (one target missed, plan in place), `extended` (week 5 or later), `graduate`, `exit`.

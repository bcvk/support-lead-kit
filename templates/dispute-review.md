# QA dispute (appeal) process

An agent who thinks a QA score is wrong should be able to say so without it being a fight. A dispute process also feeds calibration: every upheld dispute is a criterion whose wording failed.

## Rules

* Window: 5 working days from the review being shared.
* Who decides: a reviewer who did not do the original review. Never the original reviewer, never the agent's own lead if they were the reviewer.
* SLA: decision within 5 working days. Silence counts as upheld for the agent.
* Outcomes: `upheld` (score changes), `partly upheld` (one or more criteria change), `rejected` (score stands, with a written reason per criterion disputed).
* Every `upheld` and `partly upheld` goes on the next calibration session agenda with the criterion id.

## Dispute form

| Field | Entry |
|---|---|
| Ticket id | |
| Original score and reviewer | |
| Criteria disputed (ids) | |
| Agent's reasoning, per criterion, quoting the ticket | |
| Second reviewer | |
| Decision per criterion | upheld / rejected, with one sentence of reasoning each |
| New score | |
| Calibration note | which criterion wording caused the disagreement, if any |

## What a good dispute looks like

"Criterion `resolved` was scored 1 because no date was given. I wrote 'you will see the refund in 3 to 5 business days' in the second paragraph." That is a dispute. "I think the score is harsh" is not; send it back with a request for the criterion and the quote.

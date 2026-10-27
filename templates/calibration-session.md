# Calibration session (45 minutes, monthly)

Calibration is how you make a QA score mean the same thing no matter who gave it. Without it, agents learn which reviewer to hope for, and your QA trend measures reviewer mood.

## Before the session

1. Pick 5 tickets from the last month. Two that scored high, two in the middle, one with an auto fail or a complaint. Do not pick only hard cases; you also need to confirm the easy ones agree.
2. Every evaluator scores all 5 independently, using the scorecard, without talking. Deadline the day before.
3. Collect the scores in a CSV (ticket_id, evaluator, score) and run:

```
python3 scripts/calibrate.py --input calibration_round.csv --tolerance 5
```

4. Bring the output. The "tickets to discuss" list is your agenda, highest spread first.

## In the session

For each ticket on the list: the highest and lowest scorer each explain their reasoning in under two minutes, criterion by criterion. The question is never "who is right"; it is "which reading of the criterion do we adopt from now on". Write that reading down in the scorecard's notes column. A criterion that produces a disagreement two months in a row needs rewriting, not another discussion.

Skip tickets everyone agreed on unless someone asks.

## After the session

* Update scorecard wording for any criterion you clarified; bump the version.
* Reviewers flagged `lenient` or `strict` by the script get a one line note from you with their bias number. No drama, it is just a number to watch.
* Target: 80% of scores within ±5 of consensus and Krippendorff alpha at or above 0.80. Below 0.67, pause using QA scores for anything consequential until the next round.

## Why alpha and not just "within 5"

"Within 5" is easy to read but goes up for free when all your tickets score 90 plus. Alpha corrects for how much the tickets themselves vary, so it stays honest on a month with little spread. Report both.

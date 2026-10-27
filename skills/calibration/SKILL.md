---
name: calibration
description: Analyze a QA calibration round where several evaluators scored the same tickets; report reviewer bias, agreement within tolerance, Krippendorff alpha, and which tickets to discuss. Use when the user mentions calibration, inter rater agreement, reviewer consistency, or shares a CSV with ticket_id, evaluator, score.
---

# Calibration analysis

Run the script, do not estimate:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/calibrate.py --input <csv> --tolerance 5
```

Input needs columns `ticket_id, evaluator, score`. If the user gives per criterion scores instead, first run `score.py` to get totals, then feed its CSV output to `calibrate.py` (it ignores extra columns).

## How to read the result for the user

* Krippendorff alpha at or above 0.80: scores are trustworthy. 0.67 to 0.80: usable for coaching, not for consequences. Below 0.67: do not use this month's QA for anything that affects pay, PIPs or promotions; run a calibration session first.
* "Within tolerance" alone can look fine on a month where all tickets scored 90 plus; always report alpha next to it.
* An evaluator flagged `lenient` or `strict` has a mean bias larger than the tolerance. Report the number without judgment.
* The tickets list is the session agenda, highest spread first. Offer to draft the agenda using `${CLAUDE_PLUGIN_ROOT}/templates/calibration-session.md`.

Never name an evaluator as "wrong". Consensus is the median, and the goal of the session is to agree on a reading of the criterion, not to pick a winner.

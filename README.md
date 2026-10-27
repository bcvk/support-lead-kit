# Support Lead Kit

An open source operating kit for people who run customer support teams: a weighted QA scorecard, a calibration analysis that tells you whether your reviewers agree, a coaching log that fits on one screen, a four week nesting playbook, a Google Sheets workbook that wires it all together, and Claude Code skills that use the same files.

Every vendor in this space gives away a scorecard PDF to collect your email. The open source side has single form examples. Nothing covers the part that actually makes QA trustworthy: calibration. This kit does, with real math (Krippendorff's alpha, not just "within 5 points").

Written by someone who has run a 20 person multilingual support team for five years. The templates are the ones that survived.

## What is in the box

| Piece | File | What it does |
|---|---|---|
| Scorecard | `scorecards/default.yaml` | 10 criteria in 4 categories, weights sum to 100, two auto fail items. Edit the weights, keep the shape. |
| Scoring | `scripts/score.py` | Scores a CSV of reviews (0, 1, 2 per criterion), aggregates by agent, evaluator or category. |
| Calibration | `scripts/calibrate.py` | Several evaluators score the same tickets; you get per reviewer bias, agreement within tolerance, Krippendorff alpha (interval), the tickets to discuss, and per criterion disagreement with who drifts on which criterion. |
| Drift | `scripts/drift.py` | Month over month: did the team change or did a reviewer change? Flags reviewers whose gap to the team moved. |
| Disputes | `templates/dispute-review.md` | Appeal window, who decides, SLA, and how upheld disputes feed calibration. |
| Coaching log | `templates/coaching-log.md` | One table per conversation, SBI feedback shape, what not to log. |
| Nesting | `templates/nesting-playbook.md`, `templates/nesting-tracker.csv` | Weekly targets, weekly email template, go or no go rule at week 4. |
| Calibration session | `templates/calibration-session.md` | 45 minute monthly agenda built from the script output. |
| Google Sheets | `sheets/Code.gs` | One Apps Script file that builds Scorecard, Reviews, Agents and Calibration tabs with live formulas. |
| Claude Code skills | `skills/` | `qa-review` (with agent vs knowledge vs process vs tooling root cause tags), `calibration`, `coaching-note`, `nesting-review`, `bot-qa` (same rubric for AI agents). |

No dependencies. Python 3 standard library only.

## Quick start

```bash
git clone https://github.com/bcvk/support-lead-kit
cd support-lead-kit

# score the example month
python3 scripts/score.py --scorecard scorecards/default.yaml --input examples/reviews.csv --by agent

# analyze the example calibration round
python3 scripts/calibrate.py --input examples/calibration_round.csv
```

Example calibration output:

```
Calibration round: 10 tickets, 3 evaluators, 30 scores
Within ±5 of consensus: 70.0%   mean abs deviation: 3.8
Krippendorff alpha (interval): 0.196  poor (<0.67), recalibrate

evaluator          n   bias    MAD  within%  flag
Lead A            10   -0.8    0.8    100.0
Lead B            10   +3.1    8.1     30.0
Lead C            10   -2.6    2.6     80.0

Tickets to discuss (spread > 10):
  C4: consensus 95, spread 25  {'Lead A': 95.0, 'Lead B': 70.0, 'Lead C': 95.0}
  ...
```

With criterion columns in the CSV you also get this, which is the part reviewers actually argue about:

```
Criteria by disagreement (share of tickets where evaluators gave different values):
  tone             100.0%   Lead B -0.67
  acknowledge       83.3%   Lead B -1.00
  ownership         83.3%   no consistent drift
```

That is the whole point of the kit in one screen: "within 5" says 70%, which sounds acceptable, and alpha says the scores are not yet usable for anything consequential. Both are true.

## Why not one of the 17 "qa-scorecard" repos

There are many scorecard repos on GitHub and all of them stop at the scorecard. A scorecard without calibration measures reviewer mood. This kit's center of gravity is calibration (per reviewer, per criterion, over time), the agent vs process root cause split, disputes, and nesting; the scorecard is just the input format. If you want a hosted platform with dashboards, look at commercial tools; this is the lightweight Sheets plus Claude layer for teams that do not have one.

## Google Sheets

Open a blank sheet, Extensions > Apps Script, paste `sheets/Code.gs`, save, reload, then Lead Kit > Set up workbook. Weights live in the Scorecard tab; Reviews computes score, auto fail and pass per row; Agents and Calibration are formula driven. Paste a calibration round into the Calibration tab and the bias per evaluator appears on the right.

## Claude Code

```
/plugin marketplace add bcvk/support-lead-kit
/plugin install support-lead-kit@bcvk
```

Then paste a ticket and say "QA this", or share a calibration CSV and ask what it means, or say "write the week 2 nesting email for Taylor". The skills call the same scripts, so the numbers match what the Sheet shows.

## Adapting the scorecard

Keep three rules and change everything else: weights sum to 100, every criterion is scored 0, 1 or 2 with written evidence, and auto fail is reserved for things that would get a ticket escalated by a customer (wrong information, policy breach, data exposure). More than three auto fail criteria and your QA turns into a compliance audit nobody learns from.

## Calibration targets

| Metric | Use scores for coaching | Use scores for consequences |
|---|---|---|
| Within ±5 of consensus | 70% or more | 80% or more |
| Krippendorff alpha | 0.67 or more | 0.80 or more |

Run a round monthly with 5 tickets and every evaluator. The session agenda is the script's "tickets to discuss" list.

## Privacy

Example data is synthetic. When you use the kit, keep customer and agent personal data out of the repo and out of coaching logs; log the constraint, not the reason.

## Contributing

Issues and PRs welcome: scorecards for other channels (voice, social), localized templates, a conversational alpha for nominal scales. If you run a team and something here does not match how it works in practice, say so, that is the most useful kind of issue.

## License

MIT

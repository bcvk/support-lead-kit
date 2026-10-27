#!/usr/bin/env python3
"""Drift report: is QA moving because agents changed, or because reviewers changed?

Input: the output of score.py (or any CSV with columns date, agent, evaluator, score).
Groups by period (month by default) and reports, per period: team average, per evaluator
average and the evaluator's gap to the team, and per agent average. Flags an evaluator whose
gap to the team moved by more than --threshold points between consecutive periods: that is
reviewer drift, not agent performance, and it should go to the next calibration round.

  python3 drift.py --input scored.csv
  python3 drift.py --input scored.csv --period week --threshold 4 --json
"""
import argparse
import csv
import datetime as dt
import json
import statistics as st
from collections import defaultdict


def period_key(d, period):
    d = dt.date.fromisoformat(d[:10])
    if period == "week":
        y, w, _ = d.isocalendar()
        return f"{y}-W{w:02d}"
    return d.strftime("%Y-%m")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", required=True)
    p.add_argument("--period", choices=["month", "week"], default="month")
    p.add_argument("--threshold", type=float, default=5.0)
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    rows = []
    with open(a.input, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("score", "") == "" or not r.get("date"):
                continue
            rows.append({"period": period_key(r["date"], a.period), "agent": r["agent"],
                         "evaluator": r["evaluator"], "score": float(r["score"])})
    if not rows:
        raise SystemExit("no rows with date and score")

    periods = sorted({r["period"] for r in rows})
    report = []
    prev_gap = {}
    flags = []
    for pe in periods:
        rs = [r for r in rows if r["period"] == pe]
        team = st.mean(r["score"] for r in rs)
        by_ev = defaultdict(list)
        by_ag = defaultdict(list)
        for r in rs:
            by_ev[r["evaluator"]].append(r["score"])
            by_ag[r["agent"]].append(r["score"])
        evs = {}
        for e, v in sorted(by_ev.items()):
            gap = st.mean(v) - team
            evs[e] = {"reviews": len(v), "avg": round(st.mean(v), 1), "gap_to_team": round(gap, 1)}
            if e in prev_gap and abs(gap - prev_gap[e]) > a.threshold:
                flags.append({"evaluator": e, "period": pe, "gap_change": round(gap - prev_gap[e], 1)})
            prev_gap[e] = gap
        report.append({"period": pe, "reviews": len(rs), "team_avg": round(team, 1), "evaluators": evs,
                       "agents": {ag: round(st.mean(v), 1) for ag, v in sorted(by_ag.items())}})

    if a.json:
        print(json.dumps({"periods": report, "reviewer_drift_flags": flags}, indent=2))
        return
    for pr in report:
        print(f"{pr['period']}  reviews {pr['reviews']}  team avg {pr['team_avg']}")
        for e, v in pr["evaluators"].items():
            print(f"   reviewer {e:14} n={v['reviews']:<3} avg {v['avg']:>5}  gap {v['gap_to_team']:+.1f}")
        for ag, v in pr["agents"].items():
            print(f"   agent    {ag:14} avg {v:>5}")
    print("\nReviewer drift flags (gap to team moved more than "
          f"{a.threshold:g} points vs previous period):")
    for fl in flags:
        print(f"  {fl['evaluator']} in {fl['period']}: {fl['gap_change']:+.1f}")
    if not flags:
        print("  none")


if __name__ == "__main__":
    main()

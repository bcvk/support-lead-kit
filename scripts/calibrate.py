#!/usr/bin/env python3
"""Calibration analysis: how consistently do your evaluators score the same tickets?

Input: a CSV where several evaluators scored the SAME tickets (a calibration round).
Columns: ticket_id, evaluator, score (0 to 100). Any extra NUMERIC columns are treated as per
criterion values (0, 1, 2) and get their own disagreement report, so a raw review CSV with the
criterion columns plus a score column works directly; other extra columns are ignored.

  python3 calibrate.py --input calibration_round.csv
  python3 calibrate.py --input calibration_round.csv --tolerance 5 --json

What you get:
  * per evaluator: mean bias vs the ticket consensus (positive = lenient), mean absolute
    deviation, share of their scores within tolerance of consensus
  * per ticket: spread (max minus min) and which tickets need a calibration discussion
  * overall agreement: share of all scores within tolerance, and Krippendorff style
    "agreement ratio" (1 minus observed disagreement over expected disagreement, interval metric)

Consensus = median of the evaluators' scores for that ticket (robust to one outlier).
"""
import argparse
import csv
import json
import statistics as st
import sys
from collections import defaultdict
from itertools import combinations


RESERVED = {"ticket_id", "evaluator", "score", "agent", "comment", "date"}


def load(path):
    """Returns (by_ticket, criteria) where criteria maps criterion -> {ticket: {evaluator: value}}.
    Criterion columns are any extra numeric columns (for example the 0/1/2 columns of a scorecard)."""
    by_ticket = defaultdict(dict)
    criteria = defaultdict(lambda: defaultdict(dict))
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            by_ticket[r["ticket_id"]][r["evaluator"]] = float(r["score"])
            for k, v in r.items():
                if k in RESERVED or v is None or v.strip() == "":
                    continue
                try:
                    criteria[k][r["ticket_id"]][r["evaluator"]] = float(v)
                except ValueError:
                    pass
    by_ticket = {t: ev for t, ev in by_ticket.items() if len(ev) >= 2}
    if not by_ticket:
        sys.exit("need at least one ticket scored by two or more evaluators")
    return by_ticket, dict(criteria)


def criterion_report(criteria):
    """Per criterion: how often evaluators disagree, and who drifts. Values are usually 0/1/2."""
    out = []
    for name, tickets in criteria.items():
        tickets = {t: ev for t, ev in tickets.items() if len(ev) >= 2}
        if not tickets:
            continue
        disagree = sum(1 for ev in tickets.values() if max(ev.values()) != min(ev.values()))
        ev_dev = defaultdict(list)
        for ev in tickets.values():
            med = st.median(ev.values())
            for e, v in ev.items():
                ev_dev[e].append(v - med)
        drifters = {e: round(st.mean(d), 2) for e, d in ev_dev.items() if abs(st.mean(d)) >= 0.5}
        out.append({"criterion": name, "tickets": len(tickets),
                    "disagreement_pct": round(100 * disagree / len(tickets), 1),
                    "evaluator_bias": drifters})
    out.sort(key=lambda x: -x["disagreement_pct"])
    return out


def alpha_interval(by_ticket):
    """Krippendorff's alpha, interval metric, for unit = ticket, coders = evaluators."""
    units = [list(ev.values()) for ev in by_ticket.values() if len(ev) >= 2]
    n = sum(len(u) for u in units)
    if n < 2:
        return None
    # observed disagreement
    do = 0.0
    for u in units:
        m = len(u)
        do += sum((a - b) ** 2 for a, b in combinations(u, 2)) * 2 / (m - 1)
    do /= n
    # expected disagreement over all values pooled
    allv = [v for u in units for v in u]
    de = sum((a - b) ** 2 for a, b in combinations(allv, 2)) * 2 / (n - 1) / n
    return None if de == 0 else round(1 - do / de, 3)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", required=True)
    p.add_argument("--tolerance", type=float, default=5.0, help="points from consensus that count as agreement")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    by_ticket, criteria = load(a.input)
    consensus = {t: st.median(ev.values()) for t, ev in by_ticket.items()}

    ev_dev = defaultdict(list)
    for t, ev in by_ticket.items():
        for e, s in ev.items():
            ev_dev[e].append(s - consensus[t])

    evaluators = []
    for e, devs in sorted(ev_dev.items()):
        within = sum(1 for d in devs if abs(d) <= a.tolerance)
        evaluators.append({
            "evaluator": e, "tickets": len(devs),
            "bias": round(st.mean(devs), 1),
            "mean_abs_dev": round(st.mean(abs(d) for d in devs), 1),
            "within_tolerance_pct": round(100 * within / len(devs), 1),
            "flag": "lenient" if st.mean(devs) > a.tolerance else "strict" if st.mean(devs) < -a.tolerance else "",
        })

    tickets = []
    for t, ev in by_ticket.items():
        spread = max(ev.values()) - min(ev.values())
        tickets.append({"ticket_id": t, "consensus": consensus[t], "spread": round(spread, 1),
                        "evaluators": len(ev), "discuss": spread > 2 * a.tolerance,
                        "scores": {e: s for e, s in sorted(ev.items())}})
    tickets.sort(key=lambda x: -x["spread"])

    all_devs = [d for devs in ev_dev.values() for d in devs]
    overall = {
        "tickets": len(by_ticket), "evaluators": len(ev_dev), "scores": len(all_devs),
        "within_tolerance_pct": round(100 * sum(1 for d in all_devs if abs(d) <= a.tolerance) / len(all_devs), 1),
        "mean_abs_dev": round(st.mean(abs(d) for d in all_devs), 1),
        "krippendorff_alpha_interval": alpha_interval(by_ticket),
        "tickets_to_discuss": sum(1 for t in tickets if t["discuss"]),
    }
    crit = criterion_report(criteria)
    out = {"overall": overall, "evaluators": evaluators, "tickets": tickets, "criteria": crit}

    if a.json:
        print(json.dumps(out, indent=2))
        return
    o = overall
    print(f"Calibration round: {o['tickets']} tickets, {o['evaluators']} evaluators, {o['scores']} scores")
    print(f"Within ±{a.tolerance:g} of consensus: {o['within_tolerance_pct']}%   mean abs deviation: {o['mean_abs_dev']}")
    alpha = o["krippendorff_alpha_interval"]
    verdict = "n/a" if alpha is None else "good (≥0.80)" if alpha >= 0.8 else "tentative (0.67 to 0.80)" if alpha >= 0.67 else "poor (<0.67), recalibrate"
    print(f"Krippendorff alpha (interval): {alpha}  {verdict}\n")
    print(f"{'evaluator':16} {'n':>3} {'bias':>6} {'MAD':>6} {'within%':>8}  flag")
    for e in evaluators:
        print(f"{e['evaluator']:16} {e['tickets']:>3} {e['bias']:>+6.1f} {e['mean_abs_dev']:>6.1f} {e['within_tolerance_pct']:>8.1f}  {e['flag']}")
    print(f"\nTickets to discuss (spread > {2*a.tolerance:g}):")
    for t in tickets:
        if t["discuss"]:
            print(f"  {t['ticket_id']}: consensus {t['consensus']:g}, spread {t['spread']:g}  {t['scores']}")
    if not o["tickets_to_discuss"]:
        print("  none")
    if crit:
        print("\nCriteria by disagreement (share of tickets where evaluators gave different values):")
        for c in crit:
            bias = ", ".join(f"{e} {b:+.2f}" for e, b in c["evaluator_bias"].items()) or "no consistent drift"
            print(f"  {c['criterion']:16} {c['disagreement_pct']:>5.1f}%   {bias}")


if __name__ == "__main__":
    main()

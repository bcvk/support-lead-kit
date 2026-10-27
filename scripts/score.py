#!/usr/bin/env python3
"""Score one or many tickets against a weighted scorecard.

Input CSV columns: ticket_id, agent, evaluator, then one column per criterion id
with values 0, 1 or 2. Optional column "comment".

  python3 score.py --scorecard ../scorecards/default.yaml --input reviews.csv
  python3 score.py --scorecard ../scorecards/default.yaml --input reviews.csv --by agent
  python3 score.py --scorecard ../scorecards/default.yaml --input reviews.csv --json

No dependencies beyond the standard library (tiny YAML subset parser included, enough for the
scorecard format; do not use it for arbitrary YAML).
"""
import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path


def load_scorecard(path):
    """Minimal parser for the scorecard YAML layout used in this repo."""
    sc = {"categories": []}
    cat = crit = None
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        s = line.strip()
        if indent == 0:
            k, _, v = s.partition(":")
            if k != "categories":
                sc[k] = v.strip()
        elif s.startswith("- id:") and indent == 2:
            cat = {"id": s.split(":", 1)[1].strip(), "criteria": []}
            sc["categories"].append(cat)
            crit = None
        elif s.startswith("- id:") and indent >= 6:
            crit = {"id": s.split(":", 1)[1].strip(), "auto_fail": False}
            cat["criteria"].append(crit)
        else:
            k, _, v = s.partition(":")
            v = v.strip()
            if k == "criteria":
                continue
            target = crit if (crit is not None and indent >= 8) else cat
            if k == "weight":
                target["weight"] = float(v)
            elif k == "auto_fail":
                target["auto_fail"] = v.lower() == "true"
            else:
                target[k] = v
    sc["pass_threshold"] = float(sc.get("pass_threshold", 85))
    total = sum(c["weight"] for cat in sc["categories"] for c in cat["criteria"])
    if abs(total - 100) > 0.01:
        sys.exit(f"criterion weights sum to {total}, expected 100")
    return sc


def score_row(sc, row):
    total = 0.0
    auto_failed = []
    per_cat = {}
    for cat in sc["categories"]:
        cat_score = 0.0
        for c in cat["criteria"]:
            raw = row.get(c["id"], "").strip()
            if raw == "":
                sys.exit(f"ticket {row.get('ticket_id')}: missing value for {c['id']}")
            v = int(raw)
            if v not in (0, 1, 2):
                sys.exit(f"ticket {row.get('ticket_id')}: {c['id']} must be 0, 1 or 2")
            if v == 0 and c["auto_fail"]:
                auto_failed.append(c["id"])
            cat_score += c["weight"] * v / 2
        per_cat[cat["id"]] = round(cat_score, 1)
        total += cat_score
    final = 0.0 if auto_failed else round(total, 1)
    return {"ticket_id": row.get("ticket_id"), "agent": row.get("agent"), "evaluator": row.get("evaluator"),
            "date": row.get("date", ""),
            "score": final, "raw_score": round(total, 1), "auto_fail": auto_failed,
            "passed": final >= sc["pass_threshold"], "categories": per_cat}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--scorecard", required=True)
    p.add_argument("--input", required=True, help="CSV of reviews")
    p.add_argument("--by", choices=["agent", "evaluator", "category"], help="aggregate")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    sc = load_scorecard(a.scorecard)
    with open(a.input, newline="", encoding="utf-8") as f:
        rows = [score_row(sc, r) for r in csv.DictReader(f)]

    if a.by in ("agent", "evaluator"):
        g = defaultdict(list)
        for r in rows:
            g[r[a.by]].append(r)
        out = []
        for k, rs in sorted(g.items()):
            out.append({a.by: k, "reviews": len(rs),
                        "avg_score": round(sum(r["score"] for r in rs) / len(rs), 1),
                        "pass_rate": round(100 * sum(r["passed"] for r in rs) / len(rs), 1),
                        "auto_fails": sum(1 for r in rs if r["auto_fail"])})
    elif a.by == "category":
        out = []
        for cat in sc["categories"]:
            vals = [r["categories"][cat["id"]] for r in rows]
            out.append({"category": cat["id"], "weight": cat["weight"],
                        "avg_points": round(sum(vals) / len(vals), 1),
                        "avg_pct_of_weight": round(100 * sum(vals) / len(vals) / cat["weight"], 1)})
    else:
        out = rows

    if a.json:
        print(json.dumps(out, indent=2))
    else:
        keys = list(out[0].keys())
        w = csv.DictWriter(sys.stdout, fieldnames=keys)
        w.writeheader()
        for r in out:
            w.writerow({k: (json.dumps(v) if isinstance(v, (dict, list)) else v) for k, v in r.items()})


if __name__ == "__main__":
    main()

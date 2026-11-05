#!/usr/bin/env python3
"""Cross-domain ideation ledger: add / list / score / board.

Stdlib only. Append-only JSONL so a long sourcing session survives interruptions.

  python ideas.py add --problem P --donor D --source URL --mechanism M \\
      [--conflict C] [--analogy structural|surface] [--invariants "a;b"] [--test T] \\
      [--transfer-cost n] [--novelty-risk n] [--payoff n] [--test-cost n] \\
      [--prior-art novel|adjacent|blocked|buyable] [--note "..."]

  python ideas.py list [--problem SUBSTR] [--top N] [--md]
  python ideas.py score
  python ideas.py board [--out board.html]

Scores are 1-5 (5 = best payoff / lowest cost). Composite (max 25):
  insight + payoff + (6-transfer_cost) + (6-novelty_risk) + (6-test_cost) - 5
where insight = 5 for a structural analogy, 2 for a surface one.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import sys
import time

DEFAULT_DIR = "cross-domain-ideas"
LEDGER = "candidates.jsonl"

VERDICT_CUTS = ((20, "BUILD NOW"), (16, "SPIKE IT"), (12, "PARK IT"), (0, "DROP"))


def ledger_path(args) -> str:
    return os.path.join(args.dir, LEDGER)


def load(args):
    p = ledger_path(args)
    if not os.path.exists(p):
        return []
    rows = []
    with open(p, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                print("warning: skipping malformed line in %s" % p, file=sys.stderr)
    return rows


def field(args, name, default=""):
    v = getattr(args, name)
    return v if v not in (None, "") else default


def insight_of(row) -> int:
    """Only a deliberately-classified structural analogy earns full insight credit."""
    return 5 if row.get("analogy") == "structural" else 2


def composite(row) -> int:
    s = row["scores"]
    return (insight_of(row) + s["payoff"] + (6 - s["transfer_cost"])
            + (6 - s["novelty_risk"]) + (6 - s["test_cost"]) - 5)


def verdict_of(score: int) -> str:
    for cut, label in VERDICT_CUTS:
        if score >= cut:
            return label
    return "DROP"


def clamp(v, lo=1, hi=5):
    return max(lo, min(hi, v))


def cmd_add(args):
    os.makedirs(args.dir, exist_ok=True)
    if not args.source:
        print("error: --source is required; a donor claim without a URL cannot be checked.",
              file=sys.stderr)
        return 2
    if args.analogy == "surface" and not args.force:
        print("error: --analogy surface is a resemblance, not a transfer. Record it with\n"
              "       --force if you want it kept as a rejected candidate, or find the\n"
              "       mechanism that actually resolves the conflict.", file=sys.stderr)
        return 2
    if args.analogy == "unclassified":
        print("error: classify the analogy — --analogy structural (the mechanism transfers)\n"
              "       or --analogy surface (it only looks alike). Unclassified rows score\n"
              "       at surface level so a lazy row can't outrank a reasoned one.", file=sys.stderr)
        return 2
    row = {
        "id": "%d" % int(time.time() * 1000),
        "ts": time.strftime("%Y-%m-%d %H:%M"),
        "problem": args.problem,
        "donor": args.donor,
        "source": args.source,
        "mechanism": args.mechanism,
        "conflict": field(args, "conflict", "unspecified"),
        "analogy": args.analogy,
        "invariants": [s.strip() for s in (args.invariants or "").split(";") if s.strip()],
        "test": field(args, "test", "TBD"),
        "prior_art": args.prior_art,
        "note": field(args, "note", ""),
        "scores": {
            "transfer_cost": clamp(args.transfer_cost),
            "novelty_risk": clamp(args.novelty_risk),
            "payoff": clamp(args.payoff),
            "test_cost": clamp(args.test_cost),
        },
    }
    with open(ledger_path(args), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print("added %s | %s -> %s | score %d (%s)"
          % (row["id"], row["donor"], row["problem"], composite(row), verdict_of(composite(row))))
    if not row["invariants"]:
        print("note: no --invariants given; the transfer audit is incomplete.")
    return 0


def sort_rows(rows):
    return sorted(rows, key=lambda r: (-composite(r), r["donor"]))


def fmt_row(r, w=44):
    return "%-4s %-26s %-*s %s" % (
        composite(r), r["donor"][:26], w, r["mechanism"][:w], verdict_of(composite(r)))


def cmd_list(args):
    rows = load(args)
    if args.problem:
        rows = [r for r in rows if args.problem.lower() in r["problem"].lower()]
    rows = sort_rows(rows)
    if args.top:
        rows = rows[: args.top]
    if not rows:
        print("no candidates yet (dir=%s)" % args.dir)
        return 1
    if args.md:
        print("| Score | Donor | Mechanism | Conflict | Test | Prior art | Source |")
        print("|---|---|---|---|---|---|---|")
        for r in rows:
            print("| %d %s | %s | %s | %s | %s | %s | %s |" % (
                composite(r), verdict_of(composite(r)), r["donor"], r["mechanism"],
                r["conflict"], r["test"], r["prior_art"], r["source"]))
    else:
        print("%-4s %-26s %-44s %s" % ("SCR", "DONOR", "MECHANISM", "VERDICT"))
        for r in rows:
            print(fmt_row(r))
        print("\n%d candidate(s) in %s" % (len(rows), ledger_path(args)))
    surface = [r for r in rows if r["analogy"] != "structural"]
    if surface:
        print("\nflagged: %d surface/rejected row(s): %s"
              % (len(surface), ", ".join(r["donor"] for r in surface)))
    return 0


def cmd_score(args):
    rows = load(args)
    if not rows:
        print("no candidates yet (dir=%s)" % args.dir)
        return 1
    for r in sort_rows(rows):
        s = r["scores"]
        print("%-4d %-8s %s" % (composite(r), verdict_of(composite(r)), r["donor"]))
        print("      insight %d (analogy=%s) + payoff %d + (6-transfer %d) + (6-novelty %d) + (6-test %d) - 5"
              % (insight_of(r), r["analogy"], s["payoff"], s["transfer_cost"],
                 s["novelty_risk"], s["test_cost"]))
        if not r["invariants"] or r["test"] == "TBD":
            print("      incomplete: invariants=%s test=%s" % (r["invariants"] or "none", r["test"]))
        if r["prior_art"] not in ("novel",):
            print("      prior art: %s" % r["prior_art"])
    return 0


def cmd_board(args):
    rows = sort_rows(load(args))
    if not rows:
        print("no candidates yet (dir=%s)" % args.dir)
        return 1
    out = args.out or os.path.join(args.dir, "board.html")
    cards = []
    for r in rows:
        sc = composite(r)
        pct = int(sc / 25 * 100)
        cards.append("""<section class="card">
  <header><span class="score">{sc}<small>/25</small></span>
    <span class="verdict v-{slug}">{verdict}</span>
    <h3>{donor}</h3><p class="prob">{problem}</p></header>
  <p class="mech">{mechanism}</p>
  <dl><dt>Conflict</dt><dd>{conflict}</dd>
      <dt>Invariants</dt><dd>{invariants}</dd>
      <dt>Cheapest test</dt><dd>{test}</dd>
      <dt>Prior art</dt><dd>{prior_art}</dd></dl>
  <div class="bar"><i style="width:{pct}%"></i></div>
  <a href="{source}">{srclabel}</a>
</section>""".format(
            sc=sc, verdict=verdict_of(sc), slug=verdict_of(sc).split()[0].lower(),
            donor=html.escape(r["donor"]), problem=html.escape(r["problem"]),
            mechanism=html.escape(r["mechanism"]), conflict=html.escape(r["conflict"]),
            invariants=html.escape("; ".join(r["invariants"]) or "not stated"),
            test=html.escape(r["test"]), prior_art=html.escape(r["prior_art"]),
            pct=pct, source=html.escape(r["source"]),
            srclabel=html.escape(r["source"][:60])))
    doc = """<!doctype html><meta charset="utf-8"><title>Cross-domain candidates</title>
<style>
 .wrap{color:var(--foreground,#111);font:14px/1.5 inherit;max-width:1100px}
 h2{font-size:16px;margin:0 0 2px}
 .sub{color:var(--muted-foreground,#666);margin:0 0 14px}
 .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px}
 .card{border:1px solid var(--border,#ddd);border-radius:10px;padding:12px 14px;
       background:var(--card,transparent)}
 .card header{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap}
 .score{font-size:20px;font-weight:600}.score small{font-size:11px;opacity:.6}
 h3{font-size:14px;margin:0}.prob{margin:2px 0 8px;color:var(--muted-foreground,#666);font-size:12px;width:100%}
 .verdict{font-size:11px;padding:1px 7px;border-radius:999px;border:1px solid currentColor}
 .v-build{color:#0a7d4b}.v-spike{color:#8a6100}.v-park{color:#666}.v-drop{color:#a33}
 .mech{margin:0 0 10px}
 dl{display:grid;grid-template-columns:92px 1fr;gap:3px 10px;margin:0 0 10px;font-size:12.5px}
 dt{color:var(--muted-foreground,#666)}dd{margin:0}
 .bar{height:4px;border-radius:3px;background:var(--border,#eee);overflow:hidden;margin:0 0 8px}
 .bar i{display:block;height:100%;background:var(--accent,#2b6cb0)}
 a{font-size:11.5px;color:var(--accent,#2b6cb0);word-break:break-all;text-decoration:none}
</style>
<div class="wrap"><h2>Cross-domain candidate ledger</h2>
<p class="sub">@@N@@ candidates &middot; ranked by composite (max 25: insight + payoff + transfer/novelty/test costs)</p>
<div class="grid">@@CARDS@@</div></div>"""
    doc = doc.replace("@@N@@", str(len(rows))).replace("@@CARDS@@", "\n".join(cards))
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(doc)
    print(os.path.abspath(out))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Cross-domain ideation ledger")
    ap.add_argument("--dir", default=DEFAULT_DIR, help="ledger directory (default %s)" % DEFAULT_DIR)
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add")
    a.add_argument("--problem", required=True)
    a.add_argument("--donor", required=True)
    a.add_argument("--source", required=True)
    a.add_argument("--mechanism", required=True)
    a.add_argument("--conflict", default="")
    a.add_argument("--analogy", choices=["structural", "surface", "unclassified"],
                   default="unclassified")
    a.add_argument("--invariants", default="")
    a.add_argument("--test", default="")
    a.add_argument("--prior-art", choices=["novel", "adjacent", "blocked", "buyable", "unknown"],
                   default="unknown")
    a.add_argument("--note", default="")
    a.add_argument("--force", action="store_true", help="keep a surface analogy as a rejected row")
    for k in ("transfer-cost", "novelty-risk", "payoff", "test-cost"):
        a.add_argument("--" + k, type=int, default=3, dest=k.replace("-", "_"))
    a.set_defaults(func=cmd_add)

    l = sub.add_parser("list")
    l.add_argument("--problem", default="")
    l.add_argument("--top", type=int, default=0)
    l.add_argument("--md", action="store_true")
    l.set_defaults(func=cmd_list)

    s = sub.add_parser("score")
    s.set_defaults(func=cmd_score)

    b = sub.add_parser("board")
    b.add_argument("--out", default="")
    b.set_defaults(func=cmd_board)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""ai_capacity_modeler.py — the AI capacity model.

Deterministic, stdlib-only. No LLM calls. Mirrors the prototype's
derive() / sweep() / classifyRegime() exactly.

What it does that classical Erlang-C capacity planning does NOT:
  1. Treats AI attempts as the swept lever.
  2. Models the minimum human team set by (1 - success): even at 100%
     AI attempts, volume x (1 - success) tickets always reach a human.
  3. Models remaining-contact handle time rising as AI removes the easy tickets first,
     so the surviving human pile gets harder on its own.
  4. Emits a BLENDED AI-vs-human cost-per-contact curve and names its
     regime — and proves there is no interior cost middle optimum.

It does NOT do queue/service-level sizing. Once you have the remaining
human workload, hand it to an Erlang-C tool (e.g. the `capacity-planner`
skill) for P90/SLA staffing. This sizes the *labor*; that sizes the *queue*.

Usage:
  python ai_capacity_modeler.py --sample
  python ai_capacity_modeler.py --input scenario.json --output markdown
  python ai_capacity_modeler.py --input scenario.json --output json
"""

import argparse
import json
import sys

SAMPLE = {
    "volume": 10000,        # weekly contact volume
    "coverage": 0.70,       # AI attempts (the swept lever), 0..1
    "success": 0.85,        # AI resolution rate -> sets the minimum human team, 0..1
    "easy_aht": 4.0,        # easy-ticket AHT, minutes
    "hard_aht": 25.0,       # hard-ticket AHT, minutes
    "productive_hrs": 32.0, # productive hrs / agent / week
    "human_rate": 28.0,     # human $/hr
    "billing_mode": "resolution",  # "attempt" | "resolution"
    "ai_fee": 0.90,         # AI fee, interpreted per the selected mode
}


def derive(coverage, p):
    """Every line traces to the model doc. AI attempts in [0,1]."""
    a = coverage * p["success"]                                   # effective automation
    human_tickets = p["volume"] * (1 - a)
    base_aht = (p["easy_aht"] + p["hard_aht"]) / 2                # flat-average math uses this
    res_aht = p["easy_aht"] + (p["hard_aht"] - p["easy_aht"]) * (1 + a) / 2  # avg over slice [a,1]
    human_hours = human_tickets * res_aht / 60
    headcount = human_hours / p["productive_hrs"]
    naive_hc = human_tickets * base_aht / 60 / p["productive_hrs"]

    attempts = p["volume"] * coverage
    resolutions = p["volume"] * a
    ai_cost = attempts * p["ai_fee"] if p["billing_mode"] == "attempt" else resolutions * p["ai_fee"]
    human_cost = human_hours * p["human_rate"]
    blended = (ai_cost + human_cost) / p["volume"]

    return {
        "a": a,
        "human_tickets": human_tickets,
        "base_aht": base_aht,
        "res_aht": res_aht,
        "human_hours": human_hours,
        "headcount": headcount,
        "naive_headcount": naive_hc,
        "attempts": attempts,
        "resolutions": resolutions,
        "ai_cost": ai_cost,
        "human_cost": human_cost,
        "blended": blended,
    }


def sweep(p, n=101):
    rows = []
    for i in range(n):
        cov = i / (n - 1)
        d = derive(cov, p)
        rows.append({"coverage": cov, "headcount": d["headcount"],
                     "naive": d["naive_headcount"], "blended": d["blended"]})
    return rows


def classify_regime(rows):
    """Blended cost is concave in AI attempts, so its only interior extremum
    is a MAXIMUM — an interior minimum (a 'middle optimum') is impossible.
    The minimum is therefore always at an endpoint."""
    cost = [r["blended"] for r in rows]
    start, end = cost[0], cost[-1]
    max_idx = max(range(len(cost)), key=lambda i: cost[i])
    interior_max = 1 < max_idx < len(cost) - 2
    cheap_end = "MAX" if end <= start else "ZERO"
    worst_cov = round(rows[max_idx]["coverage"] * 100)
    if interior_max:
        return {"kind": "worst-in-middle",
                "verdict": f"WORST at {worst_cov}% AI attempts — cheapest at {cheap_end}",
                "worst_coverage_pct": worst_cov}
    if cheap_end == "MAX":
        return {"kind": "monotone-down", "verdict": "Cheapest at MAX AI attempts", "worst_coverage_pct": None}
    return {"kind": "monotone-up", "verdict": "Cheapest at ZERO coverage (AI never pays)", "worst_coverage_pct": None}


def analyze(p):
    now = derive(p["coverage"], p)
    floor = derive(1.0, p)                     # headcount at 100% AI attempts = the minimum human team
    rows = sweep(p)
    regime = classify_regime(rows)
    fully_loaded = p["human_rate"] * p["productive_hrs"]
    gap = now["headcount"] - now["naive_headcount"]
    return {
        "inputs": p,
        "now": now,
        "floor_headcount": floor["headcount"],
        "fully_loaded_per_agent_wk": fully_loaded,
        "naive_vs_model_gap": gap,
        "model_staffing_per_wk": now["headcount"] * fully_loaded,
        "regime": regime,
        "sweep": rows,
    }


def render_markdown(r):
    p, now, reg = r["inputs"], r["now"], r["regime"]
    L = []
    L.append("# AI Capacity — Scenario Result\n")
    L.append(f"Volume **{p['volume']:,}**/wk · AI attempts **{p['coverage']*100:.0f}%** · "
             f"resolution rate **{p['success']*100:.0f}%** · AHT **{p['easy_aht']:g}→{p['hard_aht']:g} min** · "
             f"billing **{p['billing_mode']}** @ ${p['ai_fee']:.2f}\n")

    L.append("## Moment 1 — Agents needed after AI (the hero)")
    L.append(f"- Effective automation `a = AI attempts x AI resolution rate` = **{now['a']*100:.1f}%**")
    L.append(f"- Remaining-contact handle time (survivors get harder) = **{now['res_aht']:.2f} min** "
             f"(vs flat-average baseline {now['base_aht']:.2f} min)")
    L.append(f"- Agents needed at this setting = **{now['headcount']:.0f} people**")
    L.append(f"- **Minimum human team = {r['floor_headcount']:.0f} people** at 100% AI attempts — set by "
             f"`(1 - AI resolution rate)`. Pushing AI attempts higher cannot remove it.\n")

    L.append("## Moment 2 — No middle cost optimum")
    L.append(f"- Blended cost / contact at this setting = **${now['blended']:.2f}**")
    L.append(f"- Regime: **{reg['verdict']}**")
    L.append("- Blended cost is *concave* in AI attempts (`d2/da2 = -(W/60)·aht'(a) <= 0`), so it is "
             "monotone or worst-in-the-middle — **never** best-in-the-middle. There is no interior optimum.\n")

    L.append("## Moment 3 — Flat-average vs difficulty-aware")
    L.append(f"- Flat-average math (baseline AHT) says: **{now['naive_headcount']:.0f} people**")
    L.append(f"- Difficulty-aware plan says: **{now['headcount']:.0f} people**")
    sign = "under-staff by" if r["naive_vs_model_gap"] > 0 else "gap"
    L.append(f"- You would **{sign} {abs(r['naive_vs_model_gap']):.0f} people**\n")

    L.append("## Budget readout")
    L.append(f"- Fully-loaded $/agent/wk = **${r['fully_loaded_per_agent_wk']:,.0f}**")
    L.append(f"- Difficulty-aware staffing = **${r['model_staffing_per_wk']/1000:.1f}k / wk**\n")

    L.append("## Hand-off")
    L.append("This sized the remaining human **labor** (hours → FTE via productive hours). For "
             "queue-aware **service-level** sizing of that remaining work — P90 demand, shrinkage, P(SLA "
             "breach) — feed `human_tickets` and `res_aht` into an Erlang-C tool (the `capacity-planner` "
             "skill). This skill answers *how the AI layer reshapes the work*; Erlang-C answers *how to "
             "staff the queue that's left*.")
    return "\n".join(L)


def load_inputs(path):
    with open(path) as f:
        raw = json.load(f)
    p = dict(SAMPLE)
    p.update(raw)
    if p["billing_mode"] not in ("attempt", "resolution"):
        sys.exit("billing_mode must be 'attempt' or 'resolution'")
    for k in ("coverage", "success"):
        if not 0 <= p[k] <= 1:
            sys.exit(f"{k} must be in [0,1] (got {p[k]})")
    return p


def main():
    ap = argparse.ArgumentParser(description="AI capacity model (deterministic, stdlib-only).")
    ap.add_argument("--input", help="path to scenario JSON (keys: " + ", ".join(SAMPLE) + ")")
    ap.add_argument("--output", choices=["markdown", "json"], default="markdown")
    ap.add_argument("--sample", action="store_true", help="run the built-in default scenario")
    args = ap.parse_args()

    if not args.input and not args.sample:
        ap.print_help()
        sys.exit(0)

    p = dict(SAMPLE) if args.sample else load_inputs(args.input)
    result = analyze(p)
    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print(render_markdown(result))


if __name__ == "__main__":
    main()

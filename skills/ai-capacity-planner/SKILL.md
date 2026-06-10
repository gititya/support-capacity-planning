---
name: ai-capacity-planner
description: "Use when an ops leader (Director of CX, Head of Support, VP Ops) is sizing a support team in a contact center where an AI agent resolves part of the volume, and needs to know how many humans are still required, what the residual work costs, and whether pushing AI coverage higher actually saves money. Models AI coverage as the swept lever, the headcount FLOOR set by (1 - AI success), residual handle-time rising as AI removes the easy tickets first, and a blended AI-vs-human cost-per-contact curve with its regime. Run before committing an AI-deflection headcount plan, or when leadership claims 'AI does 80% so we can cut 80% of staff.' This is NOT classical queue sizing — for P90/SLA/shrinkage staffing of the residual, hand off to capacity-planner (Erlang-C)."
version: 0.1.0
author: gititya
license: MIT
tags: [bizops, capacity, headcount, ai-automation, deflection, blended-cost, customer-support, cx, wfm]
compatible_tools: [claude-code, codex-cli, cursor, gemini-cli]
---

# ai-capacity-planner

The **delta** on top of classical capacity planning. Classical
WFM (Erlang-C) sizes a queue assuming a fixed handle time and no AI. This
skill models what an AI agent does to that queue **before** you size it:
it removes the easy tickets, leaves a harder residual, sets a headcount
floor, and reshapes the cost curve. Deterministic, stdlib-only, no LLM calls.

## Purpose

Leadership says "the AI agent handles 80% of contacts, so we can cut 80%
of the team." That is wrong in two specific, provable ways, and this skill
shows both with arithmetic:

1. **Headcount drops to a FLOOR, not to zero.** Effective automation is
   `a = coverage x success`. Because AI success < 100%, `volume x (1 - success)`
   contacts always reach a human. The floor is set by the success rate,
   not by coverage — buying more coverage can't remove it.
2. **The floor costs MORE than naive math says.** AI resolves the *easiest*
   tickets first, so the survivors are the hard ones. Naive math multiplies
   the residual volume by the *baseline* average AHT; the honest model
   multiplies by the *residual* AHT, which is strictly larger. The gap is
   real headcount you'd be short.

Then it asks the cost question classical WFM never does: **does pushing
coverage higher actually save money per contact?** — and shows there is
**no interior cost sweet spot** (proof in references).

## The model (every line reproducible)

```
a (effective automation) = coverage x success
human tickets            = volume x (1 - a)
baseline AHT             = (Easy + Hard) / 2                    <- naive math uses this
residual AHT             = Easy + (Hard - Easy) x (1 + a) / 2   <- mean over surviving slice [a,1]
human hours              = human tickets x residual AHT / 60
headcount                = human hours / productive hrs per agent
attempts                 = volume x coverage
resolutions              = volume x a
AI cost                  = attempts x fee (attempt mode)  OR  resolutions x fee (resolution mode)
human cost               = human hours x human $/hr
blended $/contact        = (AI cost + human cost) / volume
fully-loaded $/agent/wk  = human $/hr x productive hrs per agent
```

See `references/the_model.md` for the residual-AHT derivation and the
explicit difficulty-shape assumption (straight-line ramp, easy-first).

## Workflow

1. **Gather inputs.** Weekly volume, AI coverage %, AI success %, easy- and
   hard-ticket AHT (the two endpoints — pull from your help desk's fastest
   and slowest intent cohorts), productive hrs/agent/wk, human $/hr, AI
   billing mode (per attempt | per resolution — match your vendor; leading
   AI agents bill per resolution), AI fee.
2. **Run the model.** `python scripts/ai_capacity_modeler.py --input scenario.json`
   (or `--sample` for the worked default). Read the three moments.
3. **Read the floor.** That is the headcount you cannot automate away.
   Pushing coverage to 100% lands you there, not at zero.
4. **Read the regime.** The blended-cost verdict tells you whether more
   AI is cheaper (cheapest at MAX), never pays (cheapest at ZERO), or is
   worst somewhere in the middle. It is never *best* in the middle.
5. **Hand off to Erlang-C.** Take `human_tickets` and `res_aht` from the
   output and size the residual queue for P90 demand / SLA / shrinkage
   with the `capacity-planner` skill. This skill reshapes the work; that
   one staffs the queue that's left.

## Scripts

- `scripts/ai_capacity_modeler.py` — derive + 0→100% coverage sweep +
  regime classification. `--input <json>`, `--output {markdown,json}`,
  `--sample`, `--help`. Stdlib only, deterministic.

## References

- `references/the_model.md` — full model, the residual-AHT integral
  derivation, the stated easy-first simplification and its known limitation.
- `references/no_sweet_spot_proof.md` — the concavity proof that an
  interior cost minimum cannot exist, the three regimes, and the
  real-world caveats that *can* reintroduce an optimum.

## Assumptions (state them up front)

- **AI resolves the easiest `a` fraction.** A net-effect abstraction: real
  AI attempts some hard tickets and fails, and failures skew harder than
  average — so this model if anything *understates* residual cost. It errs
  conservative, not flattering. See the references for why we keep it clean.
- **Difficulty is a straight-line ramp** from Easy to Hard. Two AHT
  endpoints alone don't determine the residual average — the shape does,
  and this is the stated shape.
- **Continuous coverage, smooth difficulty, linear per-unit costs.** The
  no-sweet-spot proof holds *within this clean model*. Stepwise staffing,
  vendor tiers/volume discounts, fixed platform fees, or SLA penalties can
  reintroduce an interior optimum in the real world — name those before an
  interviewer does.

## Distinct from

- **`business-operations/capacity-planner`** sizes a queue with Erlang-C,
  P90 demand, shrinkage, and a hiring sequence — assuming a *fixed* AHT and
  *no AI*. This skill is the layer *before* it: it computes the residual
  volume and the residual AHT that AI leaves behind. **Order of operations:
  ai-capacity-planner first → capacity-planner second.** Sizing a queue
  with pre-AI AHT over-staffs the easy work and under-staffs the hard.
- **Classical deflection calculators** report "% deflected" and stop. They
  treat the deflected and residual tickets as equally hard. They have no
  floor, no rising residual AHT, and no blended-cost regime.

## The falsifiable dare

Hand someone the sliders: *"find me the automation level that minimizes
cost per contact."* There isn't one in this model — cost is monotone or
worst-in-the-middle, provably never best-in-the-middle. If they find an
interior minimum, an input is wrong (or they've added a real-world
nonlinearity the clean model deliberately excludes — which is the
interesting conversation).

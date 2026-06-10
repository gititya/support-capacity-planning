# capacity-planning-support

an AI-first capacity planner for customer support. one screen, one lever.

you sweep AI coverage and watch two things move, headcount and blended cost per contact, plus a planning lens that reads why the leftover work is slow. that's it. no scheduling, no rostering, no saved scenarios. on purpose.

it's a proof-of-work artifact for a WFM / CX context, not a product. the point is the model, not the polish.

## the one idea

everyone says "AI does 80% of tickets so cut 80% of the team." that's wrong in two ways i can prove with arithmetic, and the screen makes you feel both:

1. **headcount drops to a floor, not zero.** effective automation is `coverage x success`. AI success isn't 100%, so `volume x (1 - success)` always bounces to a human. the floor is set by the success rate, not coverage. buying more coverage can't remove it.
2. **the floor costs more than naive math says.** AI eats the easy tickets first, so the survivors are the hard ones. the human average handle time drifts up on its own as coverage rises. naive math multiplies the leftover volume by the *baseline* AHT, honest math multiplies by the *residual* AHT, which is bigger. on the defaults that gap is 13 people (44 vs 31).

then the cost question nobody asks: does pushing coverage higher actually save money per contact? answer, there's no sweet spot. blended cost is concave in coverage, so it's monotone or worst-in-the-middle, never best-in-the-middle. the chart shows which regime your inputs land in. hand someone the sliders and dare them to find the optimum, there isn't one in the clean model.

## what's in here

- `index.html` — the whole prototype. single file, plain JS, no build, no framework, no typescript. charts are Chart.js + the annotation plugin off a CDN. open it in a browser, done.
- `skills/ai-capacity-planner/` — the same model packaged as an agent skill (SKILL.md + a deterministic stdlib-only python port + references). it's positioned as the AI-first layer that runs *before* classical Erlang-C capacity planning.
- `wfm-capacity-the full screen + model.md` — the model, the derivation, the hand-checked numbers. source of truth for the math.
- `wfm-capacity-planner-HANDOFF.md` — the design conversation, decisions locked and rejected.

## run it

open `index.html`. needs internet the first time for the chart CDN. that's the only dependency.

skill:

```
python skills/ai-capacity-planner/scripts/ai_capacity_modeler.py --sample
```

## the methods

the math is named methods, not vibes:

- **deterministic workload staffing** (hours -> FTE). `headcount = human hours / productive hrs per agent`. this is the Erlang-C-free side of WFM, the one used for deferred / async work.
- **truncated-mean selection** for the rising AHT. lay difficulty on [0,1], AI removes the bottom slice, residual AHT is the conditional mean over the surviving tail. cream-skimming, basically.
- **concavity / second-derivative** for the no-sweet-spot proof. `d2/da2 = -(W/60)·aht'(a) <= 0`, so concave, so no interior minimum. for any prices.
- **blended unit-cost accounting** for $/contact.

**why no Erlang-C.** Erlang-C sizes a real-time queue against a service-level target (answer 80% in 20s, random arrivals, shared pool). this model doesn't target a service level and doesn't model arrival randomness, it sizes labor-hours. so it stops short of Erlang-C on purpose and hands the residual off to it. the two are complementary, not the same method. the honest seam: if the leftover tickets are synchronous (chat, phone), you need Erlang-C on top and this FTE is an understatement, because Erlang-C wants occupancy headroom for randomness.

## where it came from

the model is the union of three things, a published staffing model (the headcount mechanics), a cost lens (blended AI vs human per contact), and my own mechanism (residual AHT rises as AI takes the easy work). the union is the whole point, none of the three alone is defensible.

it got hardened the same way [MARS](https://github.com/gititya/MARS) hardens an idea, two models pressure-testing each other as peers until the overclaims fell out. the first draft had a cost sweet spot. the debate killed it, the concavity proof is what's left. that's the kind of result i trust, the one that survived getting argued with.

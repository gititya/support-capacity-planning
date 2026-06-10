# Capacity Planning - Support

My take on capacity planning for customer support. Use your own levers, sweep AI coverage, and watch headcount and blended cost per contact move - a simulation of something that's probably been sitting at the back of your head. You might be surprised.

Open `index.html` in a browser. That's the whole thing.

## The one idea

2025 was "customer support is dead because of LLMs," or "AI does 80% of tickets so cut 80% of the team." No citations needed - everyone heard it.

But here's what the 2026 data actually says:

> "Just 31% have implemented, or are planning, frontline workforce reductions through layoffs... large-scale layoffs remain the exception rather than the norm, underscoring a broader shift toward workforce redesign rather than elimination." (85% are expanding agent responsibilities.)
> - [Gartner, Apr 28 2026](https://www.gartner.com/en/newsroom/press-releases/2026-04-28-gartner-survey-finds-eighty-five-percent-of-service-and-support-leaders-are-expanding-human-agent-responsibilities-despite-expectations-of-mass-ai-layoffs)

> "Over 50% of customer service organizations will double their technology spend [by 2028], without an equivalent reduction in talent." ... "Technology spend is rising rapidly, yet talent needs are evolving - not disappearing."
> - [Gartner, Mar 31 2026](https://www.gartner.com/en/newsroom/press-releases/2026-03-31-gartner-predicts-over-50-percent-of-customer-service-organizations-will-double-their-technology-spend-by-2028)

> "55% of administrative and customer support leaders plan to increase permanent headcount in the second half of 2026." ... admin job postings "up 9% from 2024."
> - [Robert Half, 2026](https://www.roberthalf.com/us/en/insights/research/data-reveals-which-administrative-and-customer-support-roles-are-in-highest-demand)

And the reason the survivors are slower - the exact mechanism this prototype is built around:

> "As AI absorbs routine interactions, the cases that reach a human are no longer average. They're the unresolved edge cases... the exceptions or the moments where the model lacked context or confidence." ... "Automation reduces repetitive labor while heightening accountability."
> - [Ryan Wang (Assembled), Forbes, Apr 2 2026](https://www.forbes.com/councils/forbestechcouncil/2026/04/02/why-the-impact-of-ai-on-customer-support-isnt-what-leaders-expected/)

The part the headcount-cut math misses: if AI handles 70% of contacts, you can't just staff the remaining 30% at your old numbers. Once the easy contacts are gone, it stops being a volume game and becomes an AHT game - the contacts that survive are the slow, hard ones. Staffing for "30% of volume" silently understaffs.

So my answer is:

1. **Headcount drops to a floor, not zero.** Effective automation is `coverage x success`. AI success isn't 100%, so `volume x (1 - success)` always bounces to a human. The floor is set by the resolution rate, not coverage. Buying more coverage can't remove it.
2. **The floor costs more than the headcount-cut math says.** AI clears the easy tickets first, so the survivors are the hard ones. The average handle time of what's left drifts up on its own as coverage rises. The shortcut sizes the leftover volume at your *average* AHT; the real plan sizes it at the AHT of *what's actually left*, which is higher. On the defaults that gap is 13 people (44 vs 31).

Then the cost question: does more AI actually lower your cost per contact? There's no magic middle setting. Depending on your AI price, cost per contact either keeps dropping as you add AI, keeps rising, or is worst somewhere in the middle - but it is never *cheapest* in the middle. The chart tells you which case you're in. So if someone asks you to "find the AI level that minimizes cost," there isn't one to hunt for: the cheapest point is always all-in or none.

## The model

The math is standard, named methods. Every line is reproducible:

```
a (effective automation) = coverage x success
human tickets            = volume x (1 - a)
baseline AHT             = (easy + hard) / 2                  <- naive math uses this
residual AHT             = easy + (hard - easy) x (1 + a)/2   <- conditional mean over the surviving slice [a,1]
human hours              = human tickets x residual AHT / 60
headcount                = human hours / productive hrs per agent
attempts                 = volume x coverage
resolutions              = volume x a
AI cost                  = attempts x fee (per-attempt)  OR  resolutions x fee (per-resolution)
human cost               = human hours x human $/hr
blended $/contact        = (AI cost + human cost) / volume
```

We assume difficulty rises evenly from easy to hard, and AI takes the easy contacts first. So as AI handles more, the average handle time of what's left climbs toward the hard end.

Inputs: weekly volume, % sent to AI, AI resolution rate, easy-contact AHT, hard-contact AHT, productive hrs/agent/wk, human $/hr, AI billing mode (per attempt | per resolution), AI fee.

## What this is not

1. NOT a forecast, and not a replacement for WFM planning.
2. NOT a costing model.
3. NOT Erlang-C / queue sizing. It has no service-level target and no arrival randomness. It hands the residual off to that (see below).
4. NOT a scheduling or rostering platform. One screen, one lever - no shifts, no saved scenarios, no headcount-by-interval.

## What's in here

1. `index.html` - the whole prototype. Single file, plain JS, no build, no framework, no TypeScript. Charts are Chart.js + the annotation plugin off a CDN. Open it in a browser, done.
2. `skills/ai-capacity-planner/` - the same model packaged as an agent skill (SKILL.md + a deterministic stdlib-only Python port + references). Positioned as the layer that runs *before* classical Erlang-C capacity planning.

### Want to run the skill?

```bash
python skills/ai-capacity-planner/scripts/ai_capacity_modeler.py --sample
```

## Methods this is derived from

1. **Deterministic workload staffing** (hours -> FTE). `headcount = human hours / productive hrs per agent`. The Erlang-C-free side of WFM, the one used for deferred / async work.
2. **Truncated-mean selection** for the rising AHT. Lay difficulty on [0,1], let AI remove the bottom slice, and take the conditional mean over the surviving tail. Cream-skimming, basically.
3. **Blended unit-cost accounting** for $/contact.
4. **Concavity / second derivative.** Within the clean continuous model, blended cost has no interior minimum - it's monotone or most expensive in the middle.

## Why no Erlang-C

Erlang-C sizes a real-time queue against a service-level target (answer 80% in 20s, random arrivals, shared pool). This model doesn't target a service level and doesn't model arrival randomness - it sizes labor-hours. So it stops short of Erlang-C on purpose and hands the residual off to it. The two are complementary, not the same method. The honest seam: if the leftover tickets are synchronous (chat, phone), you need Erlang-C on top, and this FTE is an understatement, because Erlang-C wants occupancy headroom for randomness.

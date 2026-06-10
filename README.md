# Capacity Planning - Support

My take on capacity planning for customer support. Set your own numbers, move the coverage slider, and watch headcount and blended cost per contact shift.

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

My answer is simple: automation cuts ticket volume, but it doesn't cut support work in a straight line.

The bot handles the easy stuff first, so the work left for humans gets harder. Even when volume drops, the average handle time of what's left goes up. That's why "the bot handled 70%, so cut 70%" doesn't hold.

Three things this tool shows:

1. **You never get to zero people.** The bot doesn't resolve every contact it tries, and whatever it misses lands on a human. That leaves a floor no amount of extra automation can push below.
2. That floor also needs **more people than the headline math suggests**. The bot skims the easy contacts first, so the ones left for humans are the slow, hard ones. Size that leftover at your average handle time and you'll under-hire - fewer tickets, but each takes longer.
3. On cost, there's no sweet spot in the middle. Cost per contact usually bottoms out at one extreme, barely any automation or almost all of it. Vendor pricing can move that, so read the chart as a pressure test, not a procurement answer.

Move the coverage slider and watch the tradeoff: fewer human tickets, harder remaining tickets, changing headcount, and blended cost per contact. Treat it as a sanity check for the lazy version of capacity planning, not a forecast.

## The model

One assumption drives everything: the bot picks off the easier contacts first, so the contacts that reach a human are the harder leftovers.

From there it works out four things:

1. How many contacts the bot attempts.
2. How many it resolves.
3. How many fall back to a human.
4. How long that leftover human work takes.

Staffing is based on those labor hours, not the raw ticket count. That's the whole point: a team can get fewer tickets and still not get the headcount cut people expect, because the tickets that are left are slower.

### Model details

For anyone checking the math:

- effective automation = AI coverage × AI success rate
- human tickets = total volume × unresolved share
- human hours = human tickets × handle time of the remaining tickets
- headcount = human hours ÷ productive hours per agent
- blended cost/contact = (AI cost + human labor cost) ÷ total contacts

The one opinionated piece is the handle-time curve: because the bot removes the easier contacts first, the average handle time of the contacts left for humans rises as coverage goes up.

<details>
<summary>Full formulas, exact</summary>

```
a (effective automation) = coverage x success
human tickets            = volume x (1 - a)
baseline AHT             = (easy + hard) / 2                  <- naive math uses this
residual AHT             = easy + (hard - easy) x (1 + a)/2   <- mean over the surviving slice [a,1]
human hours              = human tickets x residual AHT / 60
headcount                = human hours / productive hrs per agent
attempts                 = volume x coverage
resolutions              = volume x a
AI cost                  = attempts x fee (per-attempt)  OR  resolutions x fee (per-resolution)
human cost               = human hours x human $/hr
blended $/contact        = (AI cost + human cost) / volume
```

Inputs: weekly volume, % sent to AI, AI resolution rate, easy-contact AHT, hard-contact AHT, productive hrs/agent/wk, human $/hr, AI billing mode (per attempt | per resolution), AI fee.

</details>

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

## Where the logic comes from

Four standard methods, named, in plain terms:

1. **[Workload-to-FTE staffing](https://www.indeed.com/hire/c/info/full-time-equivalent)** - the WFM way of turning a pile of work-hours into a headcount. Add up the hours the leftover tickets will take, then divide by the hours one agent actually works in a week.
2. **[Truncated mean](https://en.wikipedia.org/wiki/Truncated_mean)**, a.k.a. conditional tail expectation: the average of a range once you've lopped off one end. The bot takes the easy tickets, so what you're averaging is the handle time of the hard ones left behind, which runs higher than the all-tickets average.
3. **[Cost per contact](https://www.calabrio.com/glossary/cost-per-call/)** - the standard contact-center efficiency metric. Add bot cost to human labor cost and divide by total contacts; "blended" just means both sit in one number.
4. **[Erlang C](https://en.wikipedia.org/wiki/Erlang_(unit))** is the queue-sizing math real WFM uses for live channels, and this tool deliberately stops before it. If the leftover work is phone or chat you still need Erlang-C on top; this only sizes the work left after the bot.

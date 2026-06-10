# The model — derivation & assumptions

## The difficulty model

Line every ticket up from easiest to hardest on a 0→1 scale. Handle time
rises in a straight line from the easy endpoint to the hard endpoint:

```
aht(p) = Easy + (Hard - Easy) · p          for p in [0, 1]
```

AI resolves the **easiest** fraction first. Effective automation
`a = coverage × success` is the share of all tickets AI actually resolves,
so AI clears `[0, a]` and humans keep the harder slice `[a, 1]`.

## Where residual AHT comes from

Average handle time over the surviving slice `[a, 1]`:

```
residual AHT = (1 / (1 - a)) · ∫ₐ¹ [Easy + (Hard - Easy)·p] dp
             = Easy + (Hard - Easy) · (1 + a) / 2
```

Sanity check: at `a = 0` it equals the all-ticket mean `(Easy + Hard)/2`;
as `a → 1` it equals `Hard`. The survivors get slower on their own as AI
eats the easy end — no tuned slider, no magic ramp.

## The full model

```
a (effective automation) = coverage × success
human tickets            = volume × (1 - a)
baseline AHT             = (Easy + Hard) / 2                    ← naive math uses this
residual AHT             = Easy + (Hard - Easy) · (1 + a) / 2   ← mean over [a,1]
human hours              = human tickets × residual AHT / 60
headcount                = human hours / productive hrs per agent
attempts                 = volume × coverage
resolutions              = volume × a
AI cost (one mode only)  = attempts × fee  (per-attempt)  OR  resolutions × fee  (per-resolution)
human cost               = human hours × human $/hr
blended $/contact        = (AI cost + human cost) / volume
fully-loaded $/agent/wk  = human $/hr × productive hrs per agent
```

## Worked sample (defaults, a = 0.595)

| Quantity | Value | From |
|---|---|---|
| baseline AHT | 14.5 min | (4 + 25)/2 |
| residual AHT | 20.75 min | 4 + 21·(1.595)/2 |
| human tickets | 4,050 | 10,000·(1 - 0.595) |
| human hours | 1,400.5 | 4,050·20.75/60 |
| **naive headcount** | **31** | 4,050·14.5/60 ÷ 32 |
| **model headcount** | **44** | 1,400.5 ÷ 32 |
| under-staff gap | **13** | 44 - 31 |
| headcount floor | **18** | at coverage = 100%, a = 0.85 |
| blended $/contact (per-resolution) | $4.46 | (39,214 + 5,355)/10,000 |
| fully-loaded $/agent/wk | $896 | 28·32 |
| model staffing $/wk | $39.2k | 44·896 |

## Stated simplification (don't hide it)

We model the *net* effect as "AI resolves the easiest `a` fraction." In
reality some AI attempts fail and escalate, and those escalations aren't
strictly the hard ones — but easy-first is the honest first-order story and
keeps the formula reproducible.

## Known limitation (do NOT build around it)

Easy-first treats the human pile as only "the tickets AI never touched." But
AI also *attempts* some hard tickets and *fails*, and failures plausibly skew
*harder* than average (that's likely why they failed). So the real residual
pile is probably a bit harder than this model assumes — meaning the model, if
anything, slightly *understates* human cost/headcount. **It errs conservative,
not flattering.** Capturing the skew means tracking attempts vs. resolutions
separately and modeling difficulty among failures — too much machinery for a
sizing tool, and it doesn't change the headline. Keep the clean version on
purpose; be ready to name this if someone probes the edges.

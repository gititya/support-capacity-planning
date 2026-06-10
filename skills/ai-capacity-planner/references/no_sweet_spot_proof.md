# No middle cost optimum — the proof

## Claim

Blended cost per contact has **no interior minimum** as a function of AI
attempts, for any prices and any increasing difficulty curve. There is no
"middle-best automation level." Cost is monotone or worst-in-the-middle,
**never** best-in-the-middle.

## Proof (concavity)

Per contact, write blended cost against effective automation `a`:

```
blended(a)  = (AI marginal term, linear in a) + (W/60) · ∫ₐ¹ aht(p) dp
d/da        = (AI marginal cost) - (W/60) · aht(a)
d²/da²      = -(W/60) · aht'(a)
```

Difficulty is increasing, so `aht'(a) ≥ 0`, so the second derivative is
`≤ 0` **everywhere**: blended cost is **concave** in AI attempts. A concave
function's only interior extremum is a *maximum*. Therefore an interior
cost *minimum* cannot exist — for any prices, any increasing difficulty
curve. Adding a second AI fee (attempt + resolution) only adds linear
terms and doesn't change the sign of the second derivative.

**Intuition.** AI eats the cheap tickets first, so each extra slice of
automation displaces a *more* valuable human ticket than the slice before —
savings per step grow, they don't shrink. A valley would require shrinking
savings. Impossible.

## The three regimes (the only possibilities)

| Condition | Curve | Marker |
|---|---|---|
| AI marginal cost ≤ human cost of the *easiest* ticket | falls throughout | **Cheapest at MAX AI attempts** |
| AI marginal cost ≥ human cost of the *hardest* ticket | rises throughout | **Cheapest at ZERO AI attempts (AI never pays)** |
| in between | rises then falls | **WORST at X% — cheapest at an end** |

The model's `classify_regime()` detects which one the inputs land in by
finding the maximum of the swept cost array: an interior maximum ⇒
worst-in-the-middle; otherwise the cheaper endpoint wins.

## Scope of the proof (state it up front)

This holds *within the simplified continuous model*: continuous AI attempts,
smooth difficulty, linear per-unit costs. Real WFM **can** reintroduce
interior optima via:

- **stepwise staffing** (you hire whole agents, not fractional FTE),
- **minimum shift coverage** (you can't staff below a required staffing per interval),
- **vendor tiers / volume discounts** (AI fee isn't linear),
- **fixed platform fees** (a constant that shifts the curve),
- **SLA penalties** (a nonlinear cost on breaches).

Frame the claim as "**no middle optimum in the clean model**," not as a
universal law — and name these caveats before an interviewer does. The
scoped version is more defensible than the overclaim.

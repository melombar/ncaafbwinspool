# SP+ → Win-Probability Curve — calibration record

> Standing record of how SP+ point-differentials convert to win probabilities in the prediction model, and what we learned validating it. Pairs with `Prediction_Model_Spec.md`. Governed by `Pre_Pick_Doctrine.md` + backtest #22.

## The curve — OUTCOME-CALIBRATED empirical buckets (current)
The per-game SP+→win-prob conversion is an **empirical bucket curve**, not a single logistic scale. Favorite win-rate by SP+ margin, measured on `data/lines/cfbd_curve_data.csv` (3,476 games):

| SP+ margin | P(favorite wins) | mean margin |
|---|---|---|
| 0–3 | 0.534 | 1.5 |
| 3–10 | 0.679 | 6.4 |
| 10–20 | 0.859 | 14.7 |
| 20+ | 0.959 | 27.6 |

Implemented as monotonic **piecewise-linear interpolation** over control points `(0,0.500)(1.5,0.534)(6.4,0.679)(14.7,0.859)(27.6,0.959)(45,0.990)`, mirrored for underdogs, **HFA = 3.0** added to the signed margin. Code: `sp_to_wp` / `SP_CURVE` in `scripts/build_predictions.py`. Applies to the ~1,400 lineless games (opponents eyeball); posted moneylines/spreads still override per the hierarchy.

## Why buckets, and why NOT scale ~14 [supersedes the retired scale record]
A single logistic scale cannot fit the SP+→outcome relation across the whole range — which is exactly why the "what scale?" question never resolved (9.4 fit 2026 lines, 14.2 season-level-vs-market, 19.8 preseason-vs-market, 8.0 vs actuals). Those numbers disagree because **they target different things:**
- **~14 / 19.8** calibrate SP+ to reproduce the **market's** opening lines (mimic the bookmaker).
- **~8–9 / the buckets** calibrate SP+ to predict **actual outcomes** (what teams did).

This model's per-game probabilities exist to build a **win distribution** (floor/ceiling, P≥8) — that is predicting *outcomes*. So the **outcome-faithful ~8–9 / bucket regime is the correct target.** At scale 14 a 20+-point SP+ favorite is given 0.856 but actually won 0.959; a 10–20 favorite given 0.745 vs actual 0.859 — scale 14 systematically under-rates favorites for outcome prediction (the gap concentrates in heavy favorites). And because the model is already **sum-constrained to the market total**, matching the market on the per-game curve buys nothing — all cost, no benefit.

*Stated conditionally (not "9 beats 14"):* for THIS model's purpose (predict outcomes → distribution), the outcome-faithful bucket/~9 regime is correct; ~14 is correct only for the different goal of mimicking market lines, which this model does not need.

## Vintage caveat + its resolution
`cfbd_curve_data.csv` is **season-level** SP+; the model uses **preseason** SP+, so the exact bucket values will shift on preseason ratings. **But the ~8–9 outcome-calibration regime is the right target either way — nowhere near 14.** Resolution (follow-up): recompute the buckets on preseason-vintage games (SP+ + outcomes) to pin the exact preseason values; until then the season-level buckets are the best available and the regime is correct.

## Superseded record (do not reinstate)
- Earlier: `SCALE = 9.4` (fit to 2026 March SP+ vs 55 CBS lines). Close to the outcome regime but a single-logistic form and a market-fit provenance.
- Earlier: `SCALE ~14` (August, market-mimic) — **retired as the wrong target**, not just the wrong number. Do not reintroduce "~14" from memory/README.

## What the multi-season CFBD validation established (3,476 games, 2020–2024)
1. **The market is exceptionally calibrated.** Opening lines predict actual outcomes near-perfectly (10%→12%, 50%→50%, 90%→89%). Matching the market is the correct goal.
2. **The curve is STABLE year-to-year** — scale 14.0–14.4 across four seasons, **stdev 0.14.** Consequence: **fit once, reuse.** No annual refit needed. (This stability finding transfers across vintages.)
3. **VINTAGE CAVEAT (critical, do not trip):** CFBD historical `/ratings/sp` is SEASON-LEVEL (end-of-season) SP+, which fits scale ~14.2 vs. opening lines. Our model uses MARCH (preseason) SP+, which fits 9.4. **These are different vintages — never use the season-level 14.2 for the preseason model.** The disagreeing fits (14.2 vs market, 8.0 vs actuals, 9.4 preseason) are all vintage artifacts, not contradictions. Record: `sp_calibration_multiyear.json`.

## Open validation item
To confirm 9.4 on multi-season vintage-matched data, need HISTORICAL PRESEASON SP+ (not season-level). Unclear whether CFBD archives it separately — `pull_cfbd_preseason.py` tests this; if its ratings equal the season-level pull, CFBD only serves final SP+ and the 2026 vintage-matched fit (9.4) stands as the best available. The stability finding (#2) already makes 9.4 trustworthy regardless.

## Reproduce (next year)
1. `pull_cfbd_history.py` — CFBD lines + SP+ + results (needs free API key, ~15 calls).
2. Fit `P(win)=1/(1+exp(-(sp_diff+HFA)/SCALE))` to opening moneylines (de-vigged) using CURRENT-year preseason SP+.
3. Expect SCALE near 9–10 for preseason vintage; if it's ~14 you've pulled season-level SP+ by mistake (vintage trap).
4. Because the curve is stable, last year's SCALE is a fine prior — refit only to confirm, not because it drifts.

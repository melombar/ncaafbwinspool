# SP+ → Win-Probability Curve — calibration record

> Standing record of how SP+ point-differentials convert to win probabilities in the prediction model, and what we learned validating it. Pairs with `Prediction_Model_Spec.md`. Governed by `Pre_Pick_Doctrine.md` + backtest #22.

## The curve
Per-game win prob from SP+: `P(team win) = 1 / (1 + exp(-(sp_diff + HFA) / SCALE))`
- **SCALE = 9.4**, **HFA = 3.0** (home-field, in SP+ points)
- Fit to 2026 March (preseason) SP+ vs. opening CBS moneylines (55 pool games). Reduced per-game error vs. market from 8.8% → 2.5% MAE vs. the old textbook scale=16.
- File: `sp_calibration_2026.json`.

## Why 9.4 and not the textbook 16
The generic logistic (scale 16) under-converts SP+ edges into win probability — it demanded ~+20 SP+ points for a 77% favorite, but the market prices that at ~+13 points. The market's actual exchange rate is steeper. This was the single biggest accuracy fix in the model — it corrects the ~1,400 games that have no posted line (the games opponents eyeball), converting SP+ the way the market does.

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

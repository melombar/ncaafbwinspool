# Predictor-Accuracy Backtest — spec & result

> How well does each PRESEASON predictor forecast ACTUAL regular-season wins (CCG stripped, bowls/playoff excluded), per team, 2022–2025? Governed by `Pre_Pick_Doctrine.md` + `Prediction_Model_Spec.md` + backtest #22. Script: `scripts/backtest_predictors.py`. Result: `build/backtest_predictors_2022_2025.json` (+ `build/ccg_winners_2022_2025.json`).

## Ground truth (the absolute benchmark)
Actual **regular-season** wins = CFBD `regularSeason.wins` **minus the conference-championship-game win**. CFBD's regular-season record INCLUDES the CCG (Georgia 2022 = 13 = 12 + SEC CCG), which a preseason win total does not, so the CCG is stripped: pull `/games` (regular season), flag intra-conference games in the 10 FBS championship-playing conferences whose `notes` contain "championship", dock each winner −1. This is a real CFBD lookup, not imputation. (~9–10 CCGs/year; the script prints them + an audit of unflagged FBS same-conference late games.)

## Predictors tested (each vs actual wins)
- **Market win total** — `data/market_totals/sbd_preseason_2018_2025.json`. Used RAW as a blind forecast (no fit). Years 2022–2025; 2023/24 are P4-heavy (~69 teams).
- **SP+ rating** — `data/sp_plus/sp_final_preseason_hist.json` (`sp_final`). NO fixed curve imposed. Converted to wins by **leave-one-year-out OLS** (actual ~ a + b·rating; fit on the other 3 seasons, predict the held-out season → out-of-sample residuals). The empirical slope stands in for the schedule-free conversion.
- **Collin projection** & **net TARP** — `data/edge/edge2025.json`, **2025 only** (2022/23 TARP unrecoverable, excluded — not fabricated). Collin as a wins prediction; net TARP (a ± adjustment, not wins) tested as correlation with the market residual.

## Method
Per season (year partition) and pooled: MAE + RMSE + bias(pred−actual). Market tested ALONE; then market+SP+ IN COMBINATION via LOYO OLS on the shared team set, compared to market-fit (actual~market) LOYO. **Falsification rule:** if market-raw RMSE ≤ market+SP+ RMSE, SP+ adds no forecasting value over market. Teams joined on records-canonical names (9-name alias map in the script). No imputation: a team-year missing a predictor is dropped.

## Result (2022–2025, CCG-stripped)
| Predictor | Pooled MAE | Pooled RMSE | Read |
|---|---|---|---|
| **Market (blind)** | **1.76** | **2.21** | Best; unbiased (~0). Matches Spread_Bands sd 2.27. |
| SP+ (LOYO OOS) | 1.86 | 2.28 | Worse than market — despite being FIT to these seasons. |
| Market-fit (actual~market) | 1.75 | 2.16 | reference |
| Market + SP+ | 1.76 | 2.16 | No lift (RMSE tie, MAE slightly worse). |
| Collin 2025 alone | 2.43 | 3.12 | Worse than market (2.50) same teams. corr(Collin, actual−market) = −0.24. |
| TARP 2025 | — | — | corr(net_tarp, actual−market) = **−0.01** (zero). |

Per-year market RMSE: 2022 2.10 · 2023 1.78 · 2024 2.46 · 2025 2.33.

## Findings — each stated WITH its guardrail (anti-flattening)
1. **The market win total is the best win forecaster; nothing beat it.** SP+ loses on RMSE even with a fit advantage the market never had (blind forecast). *Guardrail:* this is FORECASTING accuracy of point-estimate wins — it does NOT say the market is unbeatable for POOL VALUE, where the Pre-Pick Doctrine's tier asymmetry (cheap-upside tail, 7–8.5 trap) is the edge. Market = level; doctrine = shape.
2. **SP+ adds no forecasting value over the market win total.** *Guardrail:* concerns win LEVEL (consistent with #22). SP+ retains its role as per-game SHAPE in the prediction model, not as a win-total signal.
3. **Collin and TARP (2025) add nothing over market; TARP corr with the market residual ≈ 0.** *Guardrail:* **single year, 2025 only** — a LEAD, not a verdict (year-partition + the 6-Win% single-year-variance trap). Resolving test: recover multi-year TARP, or test as actual−PREDICTED within pre-registered tier/conference subsets in next August's backtest, before any standing conclusion.

## Recommended 2026 weighting (with guardrail)
Anchor the win forecast on the **market win total**; use SP+ for per-game shape only (as the model already does); do NOT weight Collin or TARP into the win projection on this evidence. *Guardrail:* this governs WIN-TOTAL FORECASTING — the draft decision still runs through A-rating × S-depth = anchor premium and the tier-asymmetry doctrine, which this backtest does not touch.

## Reproduce
`export CFBD_KEY=...` then `python3 scripts/backtest_predictors.py` from repo root (`--offline` skips CFBD for a pipeline check; CCG NOT stripped in that mode). CCG list is printed for eyeball verification; `CCG_OVERRIDE` in the script backstops any miss.

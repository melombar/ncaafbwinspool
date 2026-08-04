# Prediction Model — spec (P(≥N wins) per team)

> **Governed by `Pre_Pick_Doctrine.md` + backtest #22.** The market win total is the LEVEL (not beatable); SP+ sets the SHAPE only; posted lines override SP+ per game. This model RE-EXPRESSES the market as threshold probabilities and win-path shape for within-tier comparison — it does NOT claim to beat the market. One-shot pool: predict + freeze at draft, backtest next August, never revise mid-season.

## Why it exists
A single win total hides the SHAPE. Two 6.5-win teams differ: one clears 6 with two 45% coin-flips on top (real 8-win path), the other scrapes 5 with long-shot upside (likely 4–6). For a wins pool where 8 is the magic number, the shape is the within-tier edge. This model surfaces it.

## Per-game win probability — source hierarchy (highest first)
1. **Posted moneyline** → de-vig (remove the hold from both sides) → implied win prob. Cleanest; a moneyline IS a probability.
2. **Posted spread** → win prob via the historical spread→outcome curve. Fallback if only a spread exists.
3. **SP+ differential** (rating gap + home-field ~2.5) → win prob, **shrunk toward the market baseline** (see shrinkage). For games with no line (most of weeks 5–13).
4. **Tier default** — FCS opponent = 0.90; non-pool FBS with no SP+ = conference-tier default. Simple, documented, repeatable — do not chase obscure totals.

Source used is LOGGED per game (line-grounded vs SP+-shaped vs default) so confidence is transparent.

## The two constraints that keep it honest
- **Sum-to-market-total:** each team's per-game probabilities are rescaled so they SUM to its market win total. Market sets the level; SP+ can only redistribute shape, never move the level. This structurally prevents SP+ from smuggling in a market-beating claim.
- **SP+ shrinkage toward market:** backtest #22 says on divergence the market wins ~2:1. So SP+'s per-game probs are pulled toward the market-implied baseline, STRONGER the further SP+ strays (regression-to-market), NOT a flat haircut. Shrink strength is CALIBRATED on the moneyline overlap (measure SP+ vs market where both exist) and refined by next year's backtest. Reported, tunable.

## Roll-up
- **Poisson-binomial** distribution over the per-game probabilities (exact for summing unequal independent probs) → full win distribution → **P(≥8), P(≥6), expected wins, floor (P10) / ceiling (P90) shape.**
- **Independence caveat** (stated, not hidden): games treated as independent; real correlation (injuries, momentum) slightly overstates the tails. Variance calibrated against historical total-vs-actual spread (`sbd_preseason_2018_2025.json` + workbook actuals) absorbs some of this.

## Schedule-cost decomposition
Split expected wins into: baseline (market total) vs what the schedule STRUCTURE adds/subtracts vs a neutral slate. This is what lets the backtest validate the Layer A/B schedule signals specifically — not just "was the total right" but "did tough-road teams underperform as predicted."

## Frozen prediction file — `predictions_YYYY.json`
Per team: market total, per-game probs (+ source tag per game), P(≥8)/P(≥6)/E[wins]/floor/ceiling, schedule-cost. Per game, LOG situational covariates for future backtests: home/away, con/non-con (pool + real), rest days / short-week / bye-adjacent, close-game band (pred prob 40–60%), tough-road / cupcake flags. **Timestamped and frozen at draft** — the permanent record. A prediction not recorded before kickoff is not admissible as validation.

## Validation (retrospective only — one-shot pool)
- No in-season revision (can't act on it; the pool is locked at draft).
- Next August: `backtest_predictions.py` joins frozen predictions to actual results → scores model calibration AND situational signals.
- **Situational signals** (tough-road, con/non-con, rest, cupcake, home-close vs away-close): tested as actual−PREDICTED (not actual−raw), pre-registered with direction + mechanism, pooled, MULTI-YEAR, significance discounted for number of factors tested. A factor enters a future model only on multi-year mechanism-backed evidence — never one season, never post-hoc. Guards the 6-Win% single-year-variance trap.
- Survivors adjust future SP+ shrinkage / add win-prob nudges. Everything else stays out.

## Inputs (all in project unless noted)
- `claude_data_2026.json` — SP+ ratings (`sp_mar`), market totals (`mkt_win_total`)
- `pool_schedule_grid_2026.csv` — the game list
- `sbd_preseason_2018_2025.json` — historical totals for variance calibration
- VegasInsider moneylines/spreads — live browser pull (weeks ~1–4 this far out)

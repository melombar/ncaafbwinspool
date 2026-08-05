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

## The a+b synthesis (theoretical shape × empirical bands)

The model reports two layers per team. Neither alone is honest: **(a)** the per-game Poisson-binomial is internally exact but assumes independence, so its tails are too tight; **(b)** the empirical spread bands measure how far real teams actually deviate from their market total but say nothing about *this* team's schedule. The synthesis fuses them — (a) supplies the schedule-driven shape, (b) supplies the real-world width and the tier-directional asymmetry.

**a — per-game model (theoretical).** Everything above this section: hierarchy → sum-to-market → Poisson-binomial → `expected_wins`, `P_ge_8/6/10`, and *theoretical* `floor_p10`/`ceiling_p90`. These theoretical bands are known too tight (the independence caveat) and are kept only as the internal, pre-widening reference.

**b — empirical widening + tier bands** (from `build/spread_bands.json`, 343 team-seasons 2022–2025; see `Spread_Bands_Spec.md`). Two corrections:
- **Variance widening.** A season-level common factor (`season_sigma = 0.85`) is applied across a team's per-game probs before the roll-up, inflating the total-win SD from the independence-only theoretical value up to the empirical **sd 2.27**. This produces `floor_p10_widened`/`ceiling_p90_widened` — the schedule-driven bands, now realistically wide. This is the direct fix for the independence caveat: correlation (a good/bad season moves all games together) is injected as a shared factor rather than left implicit.
- **Empirical tier bands.** `floor_empirical`/`ceiling_empirical` = market total + the tier's measured floor/ceiling residual (≤4.5: −1.8/+4.3; 5–6.5: −3.5/+3.5; 7–8.5: −3.2/+2.0; 9+: −3.0/+2.5). Market-anchored, not schedule-derived — the honest "how far do teams in this price tier actually swing" band for the draft room.

**Tier tilt — shapes uncertainty, NOT expected value.** `tier_tilt` (≤4.5 +1.0 · 5–6.5 +0.33 · 7–8.5 −0.51 · 9+ −0.17, the tiers' mean residuals) is carried per team and used to skew the band asymmetry (fat upside tail for cheap teams, capped ceiling for the 7–8.5 trap). It is deliberately **not** added to expected wins: backtest #22 says the market total is the unbeatable level, so moving E[wins] off the market would be a market-beating claim. `expected_wins_widened` stays centered on the market total; only the *shape* around it tilts. This is what "honest vs market efficiency" means in the synthesis note.

**Fields produced (per team):** `expected_wins` (a) vs `expected_wins_widened` (a+b); `floor_p10`/`ceiling_p90` (a, theoretical) vs `floor_p10_widened`/`ceiling_p90_widened` (a+b, schedule bands) vs `floor_empirical`/`ceiling_empirical` (b, market-tier bands); `tier_tilt`. `meta.synthesis` records `season_sigma`, the `tier_tilt` map, and the method note.

**Draft-room read:** use the model's `P_ge_8` and per-game shape for *within-tier* ranking (a); use `floor_empirical`/`ceiling_empirical` + `tier_tilt` for the honest floor/ceiling and upside-asymmetry call (b). Never present the tilt as added expected value.

> **Implementation note:** step (a) is `scripts/build_predictions.py`. Step (b) is currently applied as a post-process that writes the widened/empirical/tilt fields and `meta.synthesis` onto `predictions_2026.json`; that post-processor is **not yet committed to `scripts/`** — commit it (e.g. `scripts/apply_synthesis.py`) before the next rebuild so the a+b layer is reproducible, not hand-applied.

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

# NCAA FB Wins Pool — System of Record

Data, models, and method for a 12-player, 10-conference NCAA "Wins Pool" snake draft.
Score = combined regular-season wins across one team per conference. Objective = **total wins** (target ~80).

This repo is the **single system of record**: persistent historical data, the analysis pipeline,
the governing strategy docs, and the year-by-year almanacs. Nothing here is ephemeral.

## Where things live

| Dir | What | Notes |
|---|---|---|
| `data/sp_plus/` | SP+ ratings | `sp_final_preseason_hist.json` = 4 yrs (2022-25) **August/final** SP+, pool names. 2025 also has avgw/sos_rk. |
| `data/lines/` | Game betting lines | CBS 2026 wk1-4; `cfbd_curve_data.csv` = 3476 games 2020-24 (lines + season-level SP+). |
| `data/records/` | Actual wins | `cfbd_records.csv` — from CFBD `/records`, **includes FCS games** (the game file undercounts by ~1). |
| `data/market_totals/` | Preseason win totals | SBD 2018-2025 (P4-heavy pre-2025). The projection **baseline**. |
| `data/edge/` | Edge signals | 6-Win%, etc. See caveat below. |
| `data/schedule/` | 2026 schedule facts | Full 138-team opponent grid + derived rest/road/bye/anchor-cap facts. |
| `data/data_2026.json` | Current-year Layer A | One row/team: market, SP+ (mar), RetProd, TARP, Collin, 6Win%, SOS. |
| `almanac/` | Current-year almanac + BBOC pod writeups | `almanac_2026.md` consolidates all 10 confs. `archive_2025/` = prior year. |
| `specs/` | Governing method + strategy docs | Read these first (see Start Here). |
| `scripts/` | The pipeline | Pull scripts (need CFBD key) + model builders. |
| `build/` | **Regenerable** model outputs | predictions, calibration, spread bands. Rebuildable from data+scripts. |
| `draftroom/` | Live draft-room HTML + Apps Script proxy | |
| `workbooks/` | Historical pool spreadsheets 2015-2025 | Archive; actual results + standings. |

## Start Here (read order)
1. `specs/Annual_Rebuild_Playbook.md` — the master pipeline (what to rebuild each year, in order).
2. `specs/Pre_Pick_Doctrine.md` — the anti-flattening decision rule (objective = total wins; everything else is a proxy).
3. `specs/winner_almanac.md` — 10 years of champions: the winning number (~80) and archetype.
4. `specs/Prediction_Model_Spec.md` + `specs/SP_Curve_Calibration.md` + `specs/Spread_Bands_Spec.md` — the model.

## Key locked findings (so we never re-derive or re-pull)
- **Market is efficient.** Opening lines predict actual wins near-perfectly across all bands. It's the baseline; nothing beats it.
- **SP+ does NOT predict wins beyond the market** (residual corr ~0; blend weight 0). SP+ is a **shape** tool (within sum-to-market), never a level tool, and not a within-tier win tiebreaker. (Confirmed on clean 4-yr data.)
- **SP+→win-prob curve = OUTCOME-CALIBRATED empirical buckets** (favorite win-rate by SP+ margin: 0.534/0.679/0.859/0.959, cfbd 3476 games), HFA 3.0. Predicts *outcomes* (the model builds a win distribution). The single-logistic scales are **retired**: ~14/19.8 mimic the market (wrong target; the model is already sum-constrained to market), ~9.4 was a market-fit single logistic. See `specs/SP_Curve_Calibration.md`.
- **Empirical spread bands** (`specs/Spread_Bands_Spec.md`): actual wins land ~±3 of market total (sd 2.27). **Tier asymmetry**: cheap ≤4.5 teams beat 58% w/ fat upside (+4.3 ceiling); **7-8.5 is a trap** (beat 38%, capped +2.0); elite 9+ hold. Upside grows as price falls.
- **CAUTION — circular metrics:** postseason SP+ and SP+ preseason→postseason *movement* correlate with beat/miss but are measured AFTER the season — **unusable at draft time.**
- **Vintage trap:** CFBD historical `/ratings/sp` is SEASON-LEVEL, not preseason. Don't mix vintages.

## Rebuild pipeline (annual)
```
1. pull market totals (SBD)        -> data/market_totals/
2. pull SP+ (ESPN articles)        -> data/sp_plus/           [March + August, keep separate]
3. pull schedule (ESPN site.api)   -> data/schedule/          [MIND the Week 0/15 trap]
4. pull lines (CBS + CFBD)         -> data/lines/
5. pull TARP / RetProd / 6Win%     -> data/edge/, data/tarp/
6. extract BBOC pods               -> almanac/
7. build predictions               -> scripts/build_predictions.py -> build/predictions_2026.json
8. (post-season) pull records      -> data/records/  and backtest
```

## Data gaps / provenance notes
- **TARP** (`data/tarp/`): 2022/2023/2026 files existed in prior sessions but are NOT yet committed here — re-add from Drive.
- Market totals **P4-heavy** before 2025 — G5/thin-conf tiers underrepresented in the spread-band sample.
- CFBD scripts need a free **CFBD API key** + `certifi` (macOS SSL). The container can't reach CFBD; run locally.
- **6-Win%** does not replicate as a beat-the-market edge (sign reverses 2022 vs 2025). Within-tier tool only; do not re-promote.

## Pool specifics
10 confs / 138 teams. Pool reassignments override real affiliation: Notre Dame & UConn = CUSA; Boston College & Syracuse = MWC; Michigan State, Purdue, Oklahoma State, Arkansas = Pac-12.

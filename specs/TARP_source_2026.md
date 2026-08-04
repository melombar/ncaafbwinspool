# TARP — source & methodology (Layer C — governance)

*Layer scheme: A = raw data (the numbers) · B = supplemental (pod writeups) · C = governance (this doc). TARP values live in Layer A (`data_2026.json`); this file is the governance/provenance for them.*

**TARP = Transfer Activity and Returning Production.** Collin Wilson / Three Straight. Created around the pandemic season to measure roster retention + incoming portal talent. It displays the delta between a team's end-of-2025 roster and its 2026 spring roster; projected rosters include the full transfer-portal window **Jan 2 – Jan 16**.

## Underlying data sources
- **PFF** (premium.pff.com) — basis for all 2025-season statistics.
- **247Sports** transfer-portal team rankings — tracking of the source and destination of portal players.

## Component weights
**Offense:** OL Snaps 40% · Receiving Yards 35% · Passing Yards 22% · Rushing Yards 3%
**Defense:** Defensive Snaps 66% · Defensive Tackles 19% · Stops (PFF) 5% · Pressures 5% · Passes Defensed 5%

## 2026 benchmarks (FBS averages)
- TARP **offense** returned **63%**; TARP **defense** returned **56%**.
- Raw category totals are collected per team (a team can exceed 100% — e.g. Oregon returns >100% of passing yards via Dante Moore + Dylan Raiola transfer).
- Offenses that beat the 2025 statistical benchmark: Oklahoma State, Wisconsin, Auburn, UCLA, Colorado, Nebraska.
- Defenses returning >90% of 2025 output: Nebraska, Syracuse, Ole Miss, Notre Dame.

## From raw % to the pool's TARP number (the two published sheets)
1. **Team Totals sheet** — raw 0–1 composites: `RP Offense`, `RP Defense` (weighted category returns).
2. **PR Adjustments sheet** — each team's offense is modified against the 63% offensive benchmark and its defense against the 56% defensive benchmark, producing **TARP O** and **TARP D** on the pool's ±scale (Off ≈ ±6, Def ≈ ±5) and **Net TARP = Off + Def**. These PR adjustments are what feed the next off-season step: **Win Totals**.

## Retrieval
Both sheets are published Google Sheets linked from
`projectthreestraight.com/2026-tarp-transfer-activity-returning-production/`.
JS-rendered → not web-fetchable; captured by rendering the published sheet in-browser (2026-08-04).
`data_2026.json` carries the **PR Adjustments** values (net/off/def) for 136 FBS teams; `src_2026/tarp_2026.txt` is the raw capture.

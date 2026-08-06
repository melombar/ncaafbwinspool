# PREFLIGHT — Empirical draft-history model → recalibrate the Monte Carlo opponents

## Session confirmation (required first output)
- **Repo in effect:** `/Users/mike/Downloads/ncaafbwinspool`. Read this session: `winner_almanac.md`,
  `Pre_Pick_Doctrine.md`, `Annual_Rebuild_Playbook.md`, `specs/PREFLIGHT.md`, workbook `DraftTracker`
  (2022–2025), `sbd_preseason_2018_2025.json`, `predictions_2026.json`, `bboc_2026_{mwc,pac12,sunbelt}.json`.

## Foundations reloaded and IN EFFECT (per PREFLIGHT.md ¶"Foundations to reload first")
**1 — Universal Meta Game Principles (all binding, in parallel):**
1. The asset list is the trigger. 2. Availability across the full scoring window is the dominant variable.
3. Historical evidence degrades — state the weight explicitly. 4. Most recent relevant performance first.
5. Weaknesses on primary demands are near-disqualifying. 6. Pre-commit your disqualification criteria.
7. External research pressure-tests conclusions; it doesn't generate them. 8. Track what the pool's best
performers select repeatedly. 9. Critical steps require visible output, not stated intention.
10. Process failures belong to the analyst, not the decision-maker.

**2 — PRIMARY ANCHOR (cross-conference replacement value):** value a pick by the drop-off to the next
usable anchor in that conference, not its raw number. This build measures that drop-off *empirically*
(when each conference's supply actually gets drawn).

**3 — S1–S5 × A1–A10 operating model (anchor premium):** anchor premium = A-rating (projected wins) ×
S-depth (conference scarcity). The MC's whole purpose is to price S-depth from real draft behavior
instead of an invented heuristic.

**4 — Pre-Pick Doctrine (anti-flattening):** the TRIAD (scarcity ∧ floor ∧ upside-availability) all hold
at once; the objective is expected TOTAL wins; no conditional heuristic promoted to an unconditional rule.

## Standing 0–15 checklist, answered for THIS task
0. **REPO-CHECK** — checked; `DraftTracker`/`sbd_preseason` already in repo, staged from device, not re-captured.
1. **OBJECTIVE** — replace the invented MC opponent model with one calibrated to real draft history.
2. **LAYER** — infra/structure (the sim's opponent engine), not a forecast or a team value.
3. **BENCHMARK** — the ACTUAL empirical round each win-total tier was drafted (absolute: 7.5→R4.6), not a comparison.
4. **ISOLATION** — the opponent model is tested IN COMBINATION (full draft+season sim); the round-by-tier curve is the sum-of-parts thesis.
5. **EVIDENCE IN HAND** — every curve point is sourced from `DraftTracker`×`sbd_preseason`; no asserted ratings.
6. **DATA-SEMANTICS** — opened the actual `DraftTracker` sheet (found `pick` is within-round, not global — corrected).
7. **OBJECTS** — exact paths: `workbooks/NCAA_Wins_Pool_20{22..25}.xlsx`, `data/market_totals/sbd_preseason_2018_2025.json`, `scripts/monte_carlo_draft.py`.
8. **WHAT WOULD FALSIFY** — if the recalibrated field fails to reproduce the empirical round-by-tier curve, the model is wrong (kill criterion, P5/P6/P9).
9. **CONDITIONAL SUBSET** — the cliff-topper (conf-#1) subset diverges (~1.6 rounds earlier) — logged as a named, pre-draft-identifiable finding, folded into the model as a measured bump.
10. **NO FABRICATION** — name-match misses gap-flagged (2022–24 ~55%), never guessed; recency weighting leans on cleaner recent years.
11. **CAUTION-RESOLUTION PAIRING** — flagged the ~0.9-round-early residual on 8–9.5 tiers WITH its scope (doesn't affect thin-conf/late-slot conclusions).
12. **YEAR PARTITION** — each workbook extracted as its own partition; pooling is only the final recency-weighted aggregate, weights stated.
13. **CONFORMANCE** — the model prices A-rating × S-depth from data; it does not reintroduce the discarded "grab thin conferences by label" philosophy.
14. **ANTI-FLATTENING** — conclusion stated conditionally: "thin-conf anchors survive to R4–6 GIVEN market-banking opponents"; not a blanket "scarcity doesn't matter."
15. **AUTO-PUSH** — all artifacts committed to the device repo with a push handoff.

## Recency weights (P3, stated out loud)
2024–2025 ×2, 2022–2023 ×1; pre-2022 excluded (realignment changed the pool).

## Plan
1. Extract `DraftTracker` 2022–25 → join `sbd_preseason` → `build/draft_history_2022_2025.json` (visible curve). ✅
2. Rewrite MC field to market-bank + measured topper bump + observed noise; **gate:** reproduce the empirical curve. ✅
3. Re-run tournament + late-slot; regenerate `battle_plan_2026.html`; update artifact in place. ✅

## Kill criterion (P5/P6/P9)
Reject any opponent model that does not reproduce the empirical round-by-tier curve within ~1 round on
the thin-conference tiers (7.5/6.5). Current model passes (7.5→R3.7 vs R4.6; 6.5→R6.0 vs R6.3).

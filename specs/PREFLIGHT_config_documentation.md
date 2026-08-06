# PREFLIGHT — Complete the Config Documentation + Name-Key Normalization

Closes out the 2026 conference/header rebuild: normalize every name-keyed file the rebuild missed,
fix the normalization map at its source, and write the whole config into governance. Binds the session.

## 0. Why
The rebuild normalized `data_2026.json` + 3 schedule files, but a repo-wide audit (2026-08) found stale
store spellings still in Layer B sources, the Layer A schedule-columns paste file, the frozen model
output, the draftroom's real-line name map, and the alias maps in scripts. Any one silently blanks a
name-keyed join (Meta Game Principle 9: a step without visible proof isn't done — the proof here is a
clean re-audit).

## 1. Canonical map (from `specs/Naming_Canon_2026.md`)
`Eastern Michigan→EMU · FIU→Florida Intl · Miami FL→Miami · Miami OH→Miami-OH · San Jose State→San José State ·
Southern Miss→Southern Mississippi · ULM→UL Monroe · UMass→UMASS · bare Louisiana→UL Lafayette`
(keep `Louisiana Tech`, `SE Louisiana`). Conf token `Big 10→Big Ten`.

## 2. Audit findings — real (normalize) vs benign (leave)
**Normalize:** `data/schedule/layerA_schedule_columns_2026.csv`, `almanac/bboc_2026_mwc.json`,
`almanac/bboc_2026_sunbelt.json`, `draftroom/mwc_layerB_rows.tsv`, `almanac/almanac_2026.md`,
`draftroom/wins_pool_2026_draftroom.html` (line-418 real-line name map), `build/predictions_2026.json`
(names only — frozen numbers preserved), `data/lines/cbs_lines_2026_wk1-4.json`, and the alias maps in
`scripts/build_predictions.py` + `backtest_predictors.py` + `replay_draft.py` + `join_layerb_2025.py`.
**Benign (do NOT touch):** `Naming_Canon_2026.md`, `PREFLIGHT_conf_rebuild.md`,
`Dashboard_LiveJoin_Formulas.md` (they document the wrong→right map / before-state); `SE Louisiana` +
`Louisiana Tech` in the grid/probs.

## 3. Execution
1. **Normalize structured name-keyed files** (csv/tsv/json) with the full map incl. bare-Louisiana.
2. **Normalize MD/HTML** with the multiword+token pairs only (skip bare-Louisiana in prose; hand-check residuals).
3. **`predictions_2026.json`** — names only; do NOT regenerate (frozen artifact); validate JSON parses.
4. **Fix alias maps at source** — `build_predictions.py` ALIAS targets → Brad-canonical + add store-spelling
   keys so a future regen is canonical; same for backtest/replay/join_layerb.
5. **Docs** — `Annual_Rebuild_Playbook.md` rewrite (conference source-of-truth, identical-header join,
   retire SWITCH/ARRAYFORMULA gotchas; project + repo); `Schedule_Extraction_Process.md` (canonical
   examples + emit-canonical rule); `DATA_INDEX.md` (register Master_Lookup, LayerA_AN, Naming_Canon, Import tabs).
6. **Deliver + commit** each; project_write the playbook.
7. **Verification gate** — re-run the repo audit → **0 real hits** (only the benign allowlist survives).

## 4. Decisions locked
- predictions: string-normalize names, not regenerate (frozen).
- Playbook: written to both Project and repo `specs/`.
- Scope: full (incl. lower-priority backtest scripts + cbs_lines).

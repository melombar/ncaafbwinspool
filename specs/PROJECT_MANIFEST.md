# Project Manifest — what stays in the Claude Project vs. the repo

The **repo is the system of record** (everything, permanent). The **Claude Project holds only the active working set** — the few files Claude must read in full every session. Claude Projects flip to fragment-retrieval (RAG) around ~13 files, losing cross-doc reasoning, so the project is kept deliberately small (~6-8 files). Everything else lives here in the repo and is pulled into the project temporarily only when working on that specific piece.

## Rule of thumb
- **In the project** if Claude needs it to answer a typical draft-prep question *without being told where to look*.
- **In the repo only** if it's reference-for-a-specific-task (pull it in when that task comes up).

## KEEP in the Claude Project (the lean active set)

| File | Repo path | Why in-context |
|---|---|---|
| `Pre_Pick_Doctrine.md` | specs/ | The decision rule; governs every pick/ranking. |
| `Annual_Rebuild_Playbook.md` | specs/ | Master pipeline; how everything fits + rebuild order. |
| `winner_almanac.md` | specs/ | The winning number (~80) + champion archetype. |
| `almanac_2026.md` | almanac/ | The current-year board — what you actually draft from. |
| `data_2026.json` | data/ | Current-year Layer A numbers (market, SP+, TARP, etc.). |
| `predictions_2026.json` | build/ | Model output: floor/ceiling, anchor-cap probs. |

**Optional (only if you want the full spec one glance away — otherwise covered by memory):**
- `Spread_Bands_Spec.md` (specs/) — empirical floor/ceiling + tier asymmetry
- `SP_Curve_Calibration.md` (specs/) — curve = ~14 August vintage; 9.4 retired

## REMOVE from the project (now lives in repo)
- All workbooks (`workbooks/NCAA_Wins_Pool_*.xlsx`) — archive
- All prior-year BBOC (`almanac/archive_2025/bboc_2025_*.json`)
- All scripts (`scripts/*.py`) — Claude runs these in the container, not from project knowledge
- Calibration/build JSONs (`build/*.json`, `data/records/`, `data/market_totals/`, `data/lines/`) — data, regenerable
- One-time prompts (`PROMPT_2025_BBOC_Extraction.md`) — done
- Task-specific method docs — pull in only when doing that task:
  `Prediction_Model_Spec.md`, `Schedule_Extraction_Process.md`, `Overperform_Tally_Spec.md`,
  `Upside_Flag_Spec.md`, `BBOC_Extraction_Template.md`, `TARP_source_2026.md`

## Annual roll-over
Each new season: swap the current-year files in the project (almanac_YYYY, data_YYYY, predictions_YYYY),
archive the prior year to the repo, and the 3 governing specs stay put. The project never grows past ~8.

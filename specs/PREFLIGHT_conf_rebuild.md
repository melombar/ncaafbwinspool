> **⚙ REQUIRED HEADER (retrofit to `specs/PREFLIGHT.md` standard).**
>
> **Session:** repo `/Users/mike/Downloads/ncaafbwinspool`; docs read per the plan below.
> **Foundations IN EFFECT:** **Universal Meta Game Principles** (1 asset-list-is-trigger · 2 availability-across-window-dominant · 3 evidence-degrades-state-weight · 4 most-recent-first · 5 weakness-on-primary-demand-near-DQ · 6 pre-commit-DQ-criteria · 7 external-pressure-tests-not-generates · 8 track-best-performers · 9 steps-need-visible-output · 10 process-failure-is-analyst's); **PRIMARY ANCHOR** (cross-conf replacement value); **S1–S5 × A1–A10** (anchor premium = A-rating × S-depth); **Pre-Pick Doctrine** (TRIAD scarcity∧floor∧upside-availability; objective = expected TOTAL wins; no heuristic promoted to a rule).
> **0–15 checklist:** applied for this task (see body); REPO-CHECK, NO-FABRICATION (`—`/gap-flag, never guess), YEAR-PARTITION, ANTI-FLATTENING, AUTO-PUSH all binding.
> ****KILL CRITERION:** any name-keyed join column that returns blank/mismatched for a team → reject the join; reconcile to 138 teams, 0 unmatched before shipping.**
> **Weights/caveats:** stated inline (P3/P10).

# PREFLIGHT — Brad-Sourced Conference + Identical-Header Rebuild

Standing checklist for the rebuild that removes hand-entered / positionally-pasted source data
from the join. Reference this file at the top of the executing thread; producing/reading it binds
the session to it. Supersedes the ad-hoc positional-reference join.

## 0. Why this exists (the failure being fixed)
Layer A's **Pool Conf** was hand-entered and the A+B join used **positional cell references**
(`='Layer A'!B4`) plus **renamed headers** (`Mkt` vs `Mkt O/U`, `Collin` vs `Collin Proj`).
Result: Notre Dame rendered as AAC and its market win total swapped with South Florida — a
draft-invalidating error that was invisible because the rename hid the mismatch. Meta Game
Principle 9 (critical steps need visible output) and Principle 10 (the process owns the failure,
not the drafter) govern the fix: every joined column must trace to an authoritative source by
**name-keyed lookup**, and the join must expose **identical header names** so a mismatch cannot hide.

## 1. Authoritative sources (validated 2026-08-06)
Two Brad-imported alignment tables, each an uneven-width conference grid, both covering all 138 teams:

- **Import_BradConference** → **pool** alignment (what you draft from). 10 conferences.
- **Import_ActualConferences** → **actual/real** alignment. 10 conferences + `zIndependents` (Notre Dame, UConn).

Validation (both parsed, `scripts`-free, in-session): 138 teams each, **identical rosters**, no orphans
in either direction, **8 reassignments** (pool ≠ actual) — matching the prior hardcoded SWITCH exactly:

| Team | Pool conf | Actual conf |
|---|---|---|
| Arkansas | Pac12 | SEC |
| Boston College | MWC | ACC |
| Michigan State | Pac12 | Big 10 |
| Notre Dame | CUSA | Independent |
| Oklahoma State | Pac12 | Big 12 |
| Purdue | Pac12 | Big 10 |
| Syracuse | MWC | ACC |
| UConn | CUSA | Independent |

`zIndependents` → canonical real-conf token **`Independent`**.

## 2. Target data flow
```
Import_BradConference ─┐                Import_ActualConferences ─┐
  team → pool_conf     │                  team → real_conf        │
        ▼              │                        ▼                 │
  Master_Lookup (new tab): one row per team, deduped, canonical conf tokens
        │  team · pool_conf · real_conf
        ▼
  Layer A — "Pool Conf" is a LOOKUP into Master (not hand-entered); real conf also sourced here
        │
  Layer A (numbers) ─┐
  Layer B (pod)      ─┼──►  A+B join  (headers IDENTICAL to source tabs, verbatim)
                             │  proxy serializes by header
                             ▼
                      draftroom HTML reads by those exact names
```

## 3. Canonical header rule (the core change)
One name per field, byte-identical across **Import → Master → Layer A → Layer B → A+B join →
proxy JSON → HTML → data_2026.json / bboc_*.json**. The join stops renaming.

**Q4 decision: Layer A human names are canonical.** Columns that currently rename in the join get
corrected to their source names:

| Join today | Canonical (source) name | Fix |
|---|---|---|
| `Mkt` | `Mkt O/U` | rename join header; HTML `d["Mkt"]`→`d["Mkt O/U"]` |
| `Collin` | `Collin Proj` | rename join header; HTML `d["Collin"]`→`d["Collin Proj"]` |
| `SP+ Rk`, `SP+ Rtg`, `RetProd%`, `TARP net`, `Proj−Mkt`, `Pool Conf` | identical | no change |
| `Real Conf` | `Real Conf` | now sourced from Master (Import_ActualConferences); retire the SWITCH |

**Layer B header contract (Q2, locked):**
`Team · QB status · New HC · New OC · New DC · Host Lean · Dark Horse · Fade · Split · Variance ·
Sched Tag · Key Avoids/Draws · Key Injury · BBOC Notes · mkt_pod`

Note the join today reads `d["Sched"]` and `d["QB status"]`, `d["Coaching"]`, `d["Flags"]` — these are
**join-composed** columns (Coaching = HC/OC/DC concatenated; Flags = DH/FADE/SPLIT/VAR; Sched =
Sched Tag). Under the identical-header rule the join may keep composed convenience columns, but each
must be clearly a *derived* column, not a rename of a single source column. Decision to confirm at
execution: keep `Coaching`/`Flags`/`Sched` as derived, or surface raw Layer B columns verbatim and
move composition into the HTML.

## 4. Formula convention (adopted everywhere — NO ARRAYFORMULA)
Per-row, filled down:
```
=VLOOKUP($A2, 'Layer A — raw data (SOURCED)'!$A:$Z, MATCH(A$1,'Layer A — raw data (SOURCED)'!$1:$1,0), 0)
```
`A$1` is the join column's own header, which now equals the source header, so `MATCH` resolves the
right column dynamically. Same shape for the Master lookup and the Layer A Pool Conf/Real Conf cells.
Trade-off accepted: filled-down formulas need the fill range extended when teams are added — record a
`_LASTROW` note in the governance doc and in Dashboard_LiveJoin_Formulas.md.

## 5. Execution order (each step gated by VISIBLE output)
1. **REPO-CHECK** — confirm full repo state (almanac/bboc_*.json, scripts, build) on the device;
   duplicate the current Dashboard tab as `Dashboard_BACKUP` before any rewrite (rollback).
2. **Master_Lookup tab** — build from the two imports: one row per team, `pool_conf` + `real_conf`,
   conf tokens normalized to Brad-canonical (`CUSA`,`MWC`,`Pac12`, `Independent`). *Visible: 138-team
   count + "0 unmatched" reconciliation between the two imports and Layer A's team list.*
3. **Layer A Pool Conf + Real Conf → lookups** into Master. *Visible: the 8 reassigned teams read
   correctly (ND pool CUSA / real Independent; Arkansas pool Pac12 / real SEC; etc.).*
4. **Rename join headers** to source-identical names (`Mkt O/U`, `Collin Proj`, …).
5. **Rewrite A+B join** as per-row VLOOKUP+MATCH (drop ARRAYFORMULA). *Visible: Notre Dame 11.5 /
   South Florida 8.5; spot-check 5 more against Layer A.*
6. **Update HTML** DATA mapping to canonical names (`d["Mkt O/U"]`, `d["Collin Proj"]`, real conf from
   the sourced column); re-deliver + commit. *Visible: draftroom board correct on the 8 + spot-checks.*
7. **Update JSON stores + capture scripts + specs** to the canonical name dictionary: data_2026.json,
   bboc_*.json, BBOC_Extraction_Template field contract, Dashboard_LiveJoin_Formulas.md (rewritten to
   this convention), PROJECT_MANIFEST. Add a Layer C name-dictionary (source↔canonical) doc.
8. **Full-column audit** — programmatically diff every Layer A Pool Conf / Real Conf against Master,
   and every join column against its source, for all 138 teams. *Visible: a pass/fail list; target 0 fails.*
9. **Commit + push** commands for each repo change (container cannot push; user pushes from device).

## 6. Rollback
`Dashboard_BACKUP` (step 1) is the revert target if the per-row rewrite misbehaves. No source tab is
edited destructively until its lookup replacement is verified.

## 7. Open confirmations before execute
- **§3 derived columns:** keep `Coaching`/`Flags`/`Sched` as join-derived, or raw + compose in HTML?
- **Master tab name:** `Master_Lookup` acceptable, or preferred name?
- **Real conf token:** `Independent` (singular) as canonical for the 2 independents — confirm.

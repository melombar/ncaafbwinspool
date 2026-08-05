# PREFLIGHT — run before every substantive NCAA Wins build

The standing operating checklist. Load and apply this at the top of any analysis, extraction, or build session (`load specs/PREFLIGHT.md and apply it`). A blank or generic answer to any step = **STOP and reread the task**. Producing/reading this binds only the session that has it in context — reference it every run.

**Foundations to reload first:** the Universal Meta Game Principles (project instructions), the PRIMARY ANCHOR (cross-conference replacement value), the S1–S5 × A1–A10 operating model (anchor premium), and the Pre-Pick Doctrine (anti-flattening).

**Layer scheme (2026):** A = raw data (the numbers, `data_YYYY.json`) · B = supplemental (pod writeups, `bboc_YYYY_CONF.json`) · C = governance (this file, the playbook, source docs).

0.  **REPO-CHECK** — before capturing ANY data, check `specs/DATA_INDEX.md`. Never re-capture data already in the repo.
1.  **OBJECTIVE** — state the task in one concrete sentence.
2.  **LAYER** — is this forecast (predict outcome), value, or infra/structure?
3.  **BENCHMARK** — the benchmark is the ACTUAL outcome / absolute number, never a comparison row. State the absolute first.
4.  **ISOLATION** — testing a piece ALONE or IN COMBINATION? A null in isolation is a lead, not a verdict. Sum-of-parts is the thesis; one-piece-at-a-time is the known failure.
5.  **EVIDENCE IN HAND** — is each claim sourced data or a repeated conclusion? Mark repeated conclusions `[VERIFY]`; never assert team ratings you have no data for.
6.  **DATA-SEMANTICS** — have you opened the actual column/sheet/transcript, or are you trusting a description? Open it.
7.  **OBJECTS** — reference exact project/repo paths, no search.
8.  **WHAT WOULD FALSIFY** — state it before running.
9.  **CONDITIONAL SUBSET** — did any conference/player/subset diverge sharply from pooled? Is it pre-draft-identifiable and logged as a named finding? Mechanism is not a verdict.
10. **NO FABRICATION** — never fabricate team quality/projections; they must be sourced (Vegas win totals per the Proj Log method) or supplied by the user. Use `—` for unknowns; flag rather than guess.
11. **CAUTION-RESOLUTION PAIRING** — if flagging a concern about a verified result, include the resolving test in the same output, or it's just gatekeeping.
12. **YEAR PARTITION** — each workbook/season is its own partition; never pool or conflate data across years in the model.
13. **CONFORMANCE** — before finalizing pick logic or a ranking, confirm it follows A-rating × S-depth = anchor premium and doesn't reintroduce a discarded philosophy. If it deviates, STOP and flag it explicitly.
14. **ANTI-FLATTENING** — before any strategy conclusion, check: am I promoting a conditional heuristic to an unconditional rule? State findings WITH their guardrails (round/price/scarcity). A clean directional slogan is the tell — restate it conditionally or STOP.
15. **AUTO-PUSH** — after producing any persistent data/spec/script/almanac, commit it toward the repo and give the push handoff; never leave durable work stranded in ephemeral output.

---

### Extraction-specific reminders (BBOC pod → Layer B)

- Pod writeup = **Layer B** (supplemental). Numeric fields (market/SP+/RetProd/TARP/Collin) **join from Layer A** (`data_YYYY.json`) — do NOT re-key them from the pod (step 0).
- **Pod-cited lines are never ignored, never overwritten:** a newer/moved SP+ or market number the hosts quote goes in `sp_pod` / `mkt_pod`; Layer A stays the anchor; the DELTA is the signal, recorded in `bboc_notes` (see `BBOC_Extraction_Template.md`).
- **QB (2026+):** enriched capture — enum + name + role/origin + class + experience + style + lead read + displaced-incumbent destination. 2025 frozen.
- **Division of labor:** pod = qualitative; official schedule = objective facts (game count, byes, non-con, road count). Source schedule facts from the schedule, not the pod.

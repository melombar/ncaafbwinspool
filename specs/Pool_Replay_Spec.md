# Pool Replay — spec & result (would the model have beaten our actual draft?)

> Replays past drafts: at each of our slots, substitute the replacement-value model's pick and re-score by actual wins. Governed by Pre_Pick_Doctrine + backtest #22/#27. Script `scripts/replay_draft.py`; result `build/replay_results_2022_2025.json`.

## Pick logic (Option A — doctrine-pure)
`V(t) = sbd_preseason` market total (LEVEL only). Tier tilt is used **only** to break near-equal premiums (prefer the fatter upside tail) and to report floor/ceiling — never added to the level (#22/#27). Pick = argmax **replacement premium** `V(t) − V(next-best available team in the same pool-conference)`, respecting one-team-per-pool-conference. This is A-rating × S-depth = anchor premium (the Memphis lesson: cost measured vs in-conference replacement, not zero).

## Counterfactual
Sequential draft in the actual order. Opponents take their historical team (fixed). At our slot the model picks the best-premium team still on the board (not yet taken) in a conference we haven't used; its pick leaves the board for later picks. Every player (incl. the model roster) is scored by the SAME actual-wins source (`cfbd_records`, regular season incl CCG), so the ranking is internally fair.

## Projection source (per the gate)
`sbd_preseason` is the ONLY projection used. The workbook **Proj Log fails the corruption gate** — MAE(ProjLog, actual wins) = **0.12 (2022) / 0.31 (2023)**, i.e. the "projections" are essentially the final results (leakage). It is discarded, so it cannot supplement sbd's thin G5 coverage.

## The coverage limitation (decisive — read before trusting any number)
sbd is **P4-heavy** except 2025. When sbd doesn't cover a conference, the model can't value that conference's teams and can't fill that slot. A season is a **fair test only if the model could fill every slot we did** (full coverage). Otherwise the model's total is short by *missing G5 projections*, not worse picks — an artifact, not a result. This is exactly the pre-registered "P4-heavy sbd → our scarce G5 anchors are unmodelable" caveat.

## Result (2022–2025)
| Season | Fair? | Our finish | Model finish | Our wins | Model wins | Slots filled | Δ |
|---|---|---|---|---|---|---|---|
| 2022 | coverage-limited | 2 | — | 71 | 49 | 7/10 | (invalid) |
| 2023 | coverage-limited | 5 | — | 68 | 47 | 5/10 | (invalid) |
| 2024 | coverage-limited | 7 | — | 64 | 50 | 6/10 | (invalid) |
| **2025** | **YES (sbd=133)** | **10** | **6** | **61** | **66** | **10/10** | **+5** |

## Verdict (with guardrail — anti-flattening)
**On the one fair season (2025), the replacement-value model beat our actual roster (+5 wins, 6th vs our actual 10th).** Edge is **SUGGESTED, not proven** — n=1 fair season. The 2022–2024 comparisons are **coverage artifacts** (model filled 5–7 of 10 slots because sbd was P4-only and the Proj Log is corrupted) and are **not** evidence the model is worse. *Guardrail:* do NOT read this as "the model wins" or as "the model loses 3 of 4" — both are wrong. The honest statement is: where we could test it fairly, it helped; we lack fair tests elsewhere.

## Resolving test (caution-resolution pairing)
To upgrade from suggested to proven: obtain **clean full-FBS preseason win totals** (not the corrupted Proj Log) for more seasons — 2025-style coverage — so 2022–2024 (and 2018/19/21) become fair tests. Alternatively, run an **override-only-where-covered** variant (model swaps our pick only in sbd-covered conferences, keeps our G5 picks) to isolate decision quality within the covered universe without the roster-size artifact. Until then, 2025 stands as the single fair data point.

## Not yet run
2018/19/21: sbd exists but is thin (35/85/80) → would also be coverage-limited; and pre-2022 actual wins need a workbook source (cfbd_records starts 2022). 2015–17, 2020: no sbd. Flagged, not fabricated.

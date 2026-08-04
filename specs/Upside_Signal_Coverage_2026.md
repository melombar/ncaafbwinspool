# Upside-signal coverage — empirical assessment (2026 Pac-12 + Sun Belt pods)


> **Governed by `Pre_Pick_Doctrine.md`** — objective = maximize total wins; every heuristic here is CONDITIONAL (round/price/scarcity); the triad (scarcity + floor + upside-availability) always holds together; never separate a finding from its guardrail. If this doc's contents ever read as a flat rule, re-read the doctrine.

*Re-parsed the existing BBOC extractions for the upside inputs (game count, non-con, bye/rest, home/away, conference draw). This is what the pod ACTUALLY captured vs. what must be sourced elsewhere. Raw transcripts are not retained in-project, so completeness is assessed against the extracted free-text, not the audio.*

## Verdict
The pod extraction is **faithful where the pod discussed a signal** — but the upside inputs are unevenly covered, for two structural reasons that re-listening would NOT fix:

1. **The 4 reassigned P4 teams (Oklahoma State, Arkansas, Michigan State, Purdue) have NO schedule signal** in the Pac-12 pod — correctly, because they play real Big 12 / SEC / Big Ten schedules. Their non-con, avoids/draws, and rest live in their REAL conference's pod (not yet extracted) + the official schedule. This is the pool-conf≠real-schedule rule in practice.
2. **Bye/rest is almost entirely absent** (only ODU) — pods mention a bye only when notable, so ~26 of 28 teams have none. **Bye/rest is an objective schedule fact and must come from the official schedule, not the pod.**

## Coverage by signal
| Signal | Coverage | Source going forward |
|---|---|---|
| **Game count** | Full — Pac-12 all "12+Wk13 flex" (book-dependent 11/12), Sun Belt all 12 | pod + official schedule; the flex "does it count" ambiguity is the live question |
| **Non-conference** | Good for 8 real Pac-12 teams; patchy Sun Belt (some in prose, not prefixed); BLANK for reassigned P4 | official schedule (objective) + real-conf pod for reassigned |
| **Bye / rest** | Absent (1 of 28) | **official schedule ONLY** — pod won't fill this |
| **Home/away split** | Good Sun Belt (division race), sparse Pac-12 (round-robin flattens) | pod for race-relevance + schedule for the raw H/A |
| **Conf draw (avoids)** | Full for both — round-robin (Pac-12 core) / partial w/ named avoids (Sun Belt) | pod (qualitative) + schedule; reassigned P4 = real-conf partial round-robin |

## Concrete gaps to fill (not from re-listening)
- **Reassigned P4 (OKST/ARK/MSU/PUR):** extract Big 12 / SEC / Big Ten pods when they drop; pull their real avoids/draws + non-con. Until then, flagged `sched_gap` in the data.
- **Bye/rest for all 28:** source from official conference schedule releases → populate `rest_edge`.
- **Sun Belt non-con:** re-scan `bboc_notes` (not just `key_avoids`) — several non-con opponents are described mid-sentence (e.g. JMU "opens Liberty + Wagner") and weren't caught by the prefixed-only parse.

## New structured fields written to Layer B
Added `upside_signals` object per team: `game_count`, `game_count_note`, `non_con`, `rest_edge`, `home_away`, `conf_draw`, `sched_gap`. These feed the Upside flag (Low/Med/High) directly, replacing prose-scraping. Gap-flagged entries are explicit (`[gap — source from official schedule]`), never guessed.

## Division of labor (the fix, going into the extraction template)
- **Pod = qualitative reads:** QB upgrade/downgrade, coaching-hire quality, dark-horse/fade lean, race-relevant home/away, which specific anchors a team is glad to avoid.
- **Official schedule = objective facts:** game count, bye timing, non-con opponent list + difficulty, road-game count, short weeks. These don't need the pod and shouldn't wait for it.
Conflating the two is why upside inputs were uneven. Separate them at extraction.

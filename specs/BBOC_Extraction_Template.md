# BBOC Extraction Template — reconstruction spec for ALL conferences

This is the standing spec for turning a Big Bets on Campus conference preview into a structured summary. Apply it identically to every conference, every year. Drop this in the project so it can be reconstructed on demand.

## Storage architecture (three layers — do not mix)

> **Layer scheme (relabeled 2026 — intuitive order):** **A = raw data** (the numbers) · **B = supplemental** (the pod writeups) · **C = governance** (provenance/rules). Earlier docs used the reverse (A=writeup, B=data); every current file uses the A=raw / B=supplemental / C=governance scheme below. **This spec governs Layer B.**

- **Layer A — Raw data store** (one `data_YYYY.json` per year, all conferences): market, SP+, Ret Prod, TARP (off/def/net), Collin proj, 6-Win%, SOS, Miles. New data releases (6-Win%, Collin, August SP+) go HERE, keyed on Brad-canonical name.
- **Layer B — Conference writeup** (`bboc_YYYY_CONF.json` + `.md`): pod-derived, team-specific content ONLY. This spec governs Layer B.
- **Layer C — Governance** (data dictionary): provenance of each measure (source, as-of date, quirks) + rules. Not the numbers.
- **Dashboard** = JOIN of A (raw) + B (writeup) on Brad-canonical name.

## Naming

- Roster + conference assignments = **current-year pool canon** (2026 = the locked 138-team / 10-conf list with reassignments).
- Spelling = **Brad's conventions** (EMU, UMASS, Miami-OH, Florida Intl, San José State). Brad's sheet structure is stable year-over-year; use it as the template.
- Every record keys on the Brad-canonical `Conf|Team` name so Layer A and B join.

## Per-team field contract

| Field | Type | Source | Notes |
|---|---|---|---|
| team | text | canon | Brad-canonical name |
| pool_conf | text | canon | current-year pool conference |
| real_conf | text | ref | real-world conference |
| **adj_conf** | text | derived | BLANK if pool==real; else `Pool (real: X)` e.g. `Pac12 (real: Mountain West)`. Fires for reassigned/holdover teams. |
| **games** | text/num | schedule | # regular-season games. Flag 13-game teams (Hawaii rule) and Pac-12 11-vs-12 flex ambiguity. |
| mkt_win_total | num | Layer A | market line (our sourced, dated snapshot — canonical anchor) |
| **mkt_pod** | num | **pod** | market win total AS CITED ON THE POD when it differs from Layer A — a later line move. Capture it; the DIFFERENCE vs `mkt_win_total` is the signal. `—` if not cited or same. |
| sp_mar / sp_rank | num | Layer A | Connelly March SP+ (our sourced, dated snapshot — canonical anchor) |
| **sp_pod** | num | **pod** | SP+ as cited on the pod — often a LATER refresh than March; the DIFFERENCE is the update-direction beat/miss signal |
| ret_prod | num | Layer A | ESPN returning production % |
| net_tarp / off_tarp / def_tarp | num | Layer A | always carry all THREE |
| collin_proj | num | pod/Layer A | Collin's projected wins (spoken on pod) |
| proj_minus_mkt | num | derived | collin_proj − market = edge magnitude |
| new_hc / new_oc / new_dc | name/blank | pod | blank = returning |
| qb_status | enum + battle detail | pod | **2026+: enriched capture — see "QB-status capture" below.** 2025 and earlier: FROZEN (enum + name only). |
| **host_lean** | enum | pod | `Hard Over / Lean Over / No Play / Lean Under / Hard Under` |
| dark_horse | flag | pod | "could win the conf / surprise people" |
| fade | flag | pod | hosts want to bet against |
| host_split | flag | pod | hosts disagree with EACH OTHER |
| variance | flag | pod | hosts call it high-variance / boom-bust |
| sched_tag | enum | pod | `Favorable / Neutral / Brutal` |
| **key_avoids** | text | pod/schedule | which conference anchors the team AVOIDS or DRAWS + confirmed head-to-heads. THE UNBALANCED-SCHEDULE SIGNAL. |
| sos_rank | num | Layer A | when cited |
| miles | num | Layer A | from xMiles Traveled tab |
| key_injury | text | pod | notable injury/health flag |
| bboc_notes | rich text | pod | paragraph-style qualitative take |

## Pod-cited lines (SP+ and market) — never ignore, never overwrite

Pods routinely cite a NEWER SP+ refresh or a MOVED market line than our Layer A snapshot. Capture both — do not drop the pod number, do not overwrite Layer A with it.

- Put the pod's number in `sp_pod` / `mkt_pod`; keep our sourced, dated Layer A values (`sp_mar`/`sp_rank`, `mkt_win_total`) as the canonical anchor and join key.
- Do NOT overwrite Layer A with a pod number — Layer A is a full-FBS, primary-sourced, dated snapshot; the pod is a single-book, per-team mention. Mixing them corrupts the join and the vintage.
- The DELTA is the signal: pod line above ours = market moved up since our pull (roster news / money on the over); an updated pod SP+ above ours = the model beat its preseason vintage. Record the delta direction in `bboc_notes`.
- A genuinely new full-FBS release (Connelly refresh, new market page) is a Layer A RE-CAPTURE from the primary source — never a pod copy.

## QB-status capture (enum + battle detail) — 2026 forward

From 2026 on, `qb_status` is not just enum + name — capture the battle: who, from where, and why it matters. **2025 and earlier are FROZEN** (enum + name only; do not backfill).

**Format:** `<Enum> — <Name> (<role/origin>, <class/eligibility>, <experience>, <style>) [lead read; displaced-incumbent destination]`

- **Enum:** Returning / Transfer / Battle / Freshman / Unsettled
- **role/origin:** incumbent · returning backup · transfer-from-X · JUCO · true/RS freshman · converted (e.g. WR→QB)
- **class/eligibility:** year + eligibility if stated
- **experience:** snaps/starts, prior production, injury history if relevant
- **style:** pocket / dual-threat / game-manager / gunslinger; mobility; arm
- **lead read:** who's favored to win a Battle, per the pod (`[lead: unsettled]` if genuinely unstated)
- **displaced-incumbent destination:** if a starter was beaten out or transferred, where they went

**Worked examples (2026):**
- `Battle — Haas Haney (transfer from Oklahoma State, ex-TCU 4-star, 4.45 speed, dual-threat) vs Darius Curry [lead: Haney expected to win the job]`
- `Transfer — Kayden Pinnock (from UC Davis, 2025 Big Sky Freshman of the Year, ~185 lbs, mobile scrambler)`
- `Returning — Maddox Madsen (incumbent; flagged — 54% comp / 7 INT when tied-or-trailing, over-reliant on the run) [held the job, no battle]`

If the pod doesn't give a field, use `—` (never invent).

## The unbalanced-schedule rule (applies to EVERY conference)

Teams in a conference do NOT all play each other (partial round-robins in SEC/B10/ACC/etc.). Two teams with the same win total can have very different paths — one drew the soft half, one the gauntlet. This is a pre-draftable edge (schedule known before the draft). For every team, capture in `key_avoids` and Notes: which conference anchors it avoids vs draws, and whether that moves its beat/miss likelihood vs the market. Confirmed official head-to-heads (anchor-on-anchor games cap combined anchor wins) go here too.

## Extraction procedure

1. Read the full transcript (store to disk/var; slice past display limits).
2. For each team, fill every field above. `—` = pod didn't say / not applicable (never invent).
3. Reassigned P4 teams: their BBOC notes come from their REAL-conference pod, not the bucket pod — mark `[BBOC pending — covered in X pod]` and keep edge-data reads only.
4. Distill schedule commentary to `sched_tag` + `key_avoids`; keep the narrative in Notes.
5. Write `bboc_YYYY_CONF.json` (with `field_contract`) + render the `.md`.

## Upside signals (structured — feed the Upside flag, not prose-scraped)
Add an `upside_signals` object per team so the Low/Med/High Upside flag scores fields, not free text:
- `game_count` (12 or 13) + `game_count_note` — a 13th regular-season game is an extra win chance (Hawaii rule / counted flex). Book-dependent flex → note it.
- `non_con` (opponent list) + difficulty read — soft (FCS/G5 home) vs body-bag P4 road trips.
- `rest_edge` — bye timing / extra rest / short weeks. **OBJECTIVE — source from the official schedule, NOT the pod** (pods only mention a bye when notable → patchy).
- `home_away` — race-relevant home/away split (esp. divisional).
- `conf_draw` — full round-robin (no avoids) vs partial (name the avoided/drawn anchors).
- `sched_gap` — for reassigned P4 teams, flag `plays real X schedule — source from real X pod + official schedule` (never apply the pool conf's schedule structure to them).

## Division of labor (why upside inputs came out uneven — separate these at extraction)
- **Pod = QUALITATIVE:** QB upgrade/downgrade, coaching-hire quality, dark-horse/fade lean, race-relevant H/A, which anchors a team is glad to avoid.
- **Official schedule = OBJECTIVE facts:** game count, bye timing, non-con list + difficulty, road-game count, short weeks. Don't wait for the pod on these — the pod won't reliably cover them.

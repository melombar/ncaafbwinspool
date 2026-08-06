# Schedule-fact extraction — annual process (preserve; re-run each preseason)

> **Governed by `Pre_Pick_Doctrine.md`.** This is the OBJECTIVE schedule layer (facts, not pod opinion). Pairs with the pod's qualitative layer per the division of labor in BBOC_Extraction_Template.md.

> **Naming (2026):** every emitted file (`schedule_facts`, `pool_schedule_grid`, `schedule_probs`, `layerA_schedule_columns`) must use **Brad-canonical** team names in both the Team column AND opponent references (`Naming_Canon_2026.md`) — the schedule tab and Overperform tally key on Team, so a drift (e.g. `App State`, `Miami FL`) silently blanks that team. Ship Layer A A–N + P→ as ONE aligned `LayerA_FULL_YYYY.tsv` so schedule facts can't misalign with the team column.

## Why this is a data requirement (not optional)
The schedule is MULTI-DIMENSIONAL — assess each team's full PATH to wins, not just caps. Anchor-on-anchor is ONE signal among several. The full profile per team:
- **Rest** — bye placement (before a tough game = edge), short weeks (<=5-day turnaround; strict — only ~3 teams league-wide).
- **Road/home structure** — road count, longest consecutive-road streak (road-heavy stretch = win drain), home clustering.
- **Non-con cupcakes** — soft non-con (FCS/weak G5) = near-certain win padding; brutal non-con (P4 road) = likely losses. Direct floor impact.
- **Schedule strength** — avg opponent quality. CAVEAT: SOS is PARTLY already priced into the team's own market line; the EDGE is schedule STRUCTURE (when hard games cluster, home/road split of the hard games, non-con specifically — memory #18), NOT raw SOS.
- **Anchor-on-anchor caps** — pairs of pool anchors that play each other (don't draft both). 2026 = 81.
- **Game count / bye** — objective ceiling signals the pods don't reliably carry.
- **Travel** — road-STRUCTURE only (road count, road streak). Raw 'Miles Traveled' is a DEAD metric (memory #19) — do NOT reintroduce without an explicit user call.

Produces intelligence nothing else in the pipeline does:
- **Anchor-on-anchor caps** — pairs of pool anchors that play each other. Directly changes picks: never draft both (one loss guaranteed). 2026 = 81 caps.
- **Pool-framed schedule for reassigned/independent teams** — their real-schedule games vs POOL anchors (any pool conf), the item-5 requirement. E.g. Michigan State plays Notre Dame + Oregon; UConn plays JMU + Old Dominion.
- **Game count / bye week** — objective ceiling signals the pods don't reliably carry (1 of 28 byes came from a pod).

## Source & method (the fragile parts — preserve exactly)
**Endpoint (works, no auth):**
`https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/{ESPN_ID}/schedule?season=YYYY&seasontype=2`
- `seasontype=2` = regular season. Without it, returns 0 events.
- 2026 schedules were live by Aug; run once when schedules post, re-run closer to draft (Pac-12/rebuild confs post late).

**CRITICAL: match opponents by ESPN TEAM ID, not name.** Name-matching mangles Texas→Texas State, Ohio State→Ohio, Miami FL→Miami OH. Build `espn_id -> pool_team` from the pool list's own IDs, then read each event's opponent `team.id` and look it up. (Cost me a live bug this session — the caps list had false pairs until switched to ID matching.)

**Bulk teams endpoint is BLOCKED** (`teams?limit=400` returns 0; `core.api` host trips the browser cookie filter). Do NOT rely on it. Use the maintained ID map instead (below).

**Run environment:** browser (Claude in Chrome) — the container egress can't reach espn.com. `site.api` per-team calls are reliable; wrap in a 3× retry (occasional transient fail). The proxy/`window.__` vars hold results; extract to disk in <4KB pipe-delimited slices (the JS console truncates long strings and trips a cookie filter on big JSON blobs — pipe-delimited plain text is safe).

**Derived fields (full profile per team):**
- `home / road / neutral` counts; `max_road_streak` / `max_home_streak` = longest consecutive run.
- `bye_week` = gap in the posted week numbers (weeks 1..max missing a number).
- `short_weeks` = games <=5 days after previous (STRICT — loose thresholds inflate; only ~3 teams qualify).
- `sos_proxy` = avg market O/U of pool opponents (flag coverage; partly redundant with the line — use structure not raw SOS).
- `cupcakes` = count of non-pool opponents (FCS/weak proxy).
- `game_count` / `game_delta` = +1 (13 games), -1 (11), 0 (12). Flag rebuild-conf counts PROVISIONAL until finalized.
- `anchor` = pool team with mkt ≥ 7.0 AND within 1.0 of its conference ceiling.
- `anchor_on_anchor` = games where both teams are anchors → the cap list (dedupe by sorted pair).

## ESPN team-ID map (2026 pool — maintain year-over-year, only roster swaps change)
Stored in `schedule_facts_YYYY.json` provenance. 134 of 138 were standard; 4 needed manual add: North Dakota State 2449, FIU 2229, UTEP 2638, Sacramento State 16. Full working map lives in the extraction script/session; regenerate the missing-check each year (`pool teams not in ESPN_ID`).


## WEEK 0 / WEEK 15 — validation caveats (LEARNED THE HARD WAY 2026)
ESPN's `week.number` does NOT map cleanly to a 0-13 grid. Two traps that corrupt bye/road/rest analysis if missed:

1. **WEEK 0 (late-August openers).** Teams playing a game before Sept 1 have a "Week 0" game that ESPN labels **week 1 with an August date** — same week number as their September opener. If you key cells by week number alone, the two games COLLAPSE into one cell: you drop a game AND hide a bye. 16 teams had a Week 0 game in 2026 (USC, TCU, Virginia, NC State, North Carolina, UNLV, Memphis, Stanford, Hawaii, NDSU, Jacksonville St, Eastern Michigan, San Jose St, New Mexico St, Sacramento St + Florida St). **FIX: split Week 0 by DATE** — a week-1-labeled game dated `< YYYY-09-01` goes in slot 0, not slot 1. A Week 0 team plays 12 games across 14 weeks → **TWO byes**, not one. (Caught only because a bye count disagreed with the schedule; USC showed 11 games + a phantom missing week until the collapse was found.)

2. **WEEK 15 (Army-Navy).** Army and Navy play their annual game the week AFTER championship weekend = ESPN `week.number` 15. It's a real regular-season game (their 13th). Keep a week-15 slot; only Army & Navy use it.

3. **RECONCILIATION IS MANDATORY before any grid is trusted.** For every team: filled-cell count MUST equal its known game_count (12 std; 13 for Pac-12 flex #27, Hawaii-rule teams, and Army/Navy). Two missing weeks with no Week-0 game = one real bye + one UNPOSTED game (flag, don't fabricate). Two missing weeks WITH a Week-0 game = two real byes (complete). A single snapshot showing 11 for a flex team = ESPN mid-population, override to 13 per #27.

## Grid build — validation gate
Before presenting any schedule grid or deriving any bye/road/rest metric: (1) split Week 0 by date; (2) keep Week 15 slot; (3) reconcile filled cells vs game_count per team; (4) confirm no known name-mangle pairs (ID-match); (5) flag TBD/unposted cells, never fill them. A grid that doesn't reconcile is not presented.

## Output
`schedule_facts_YYYY.json` — anchor_on_anchor_caps (all pairs) + per_team_verified (game_count, game_delta, bye_week, anchor_on_anchor). Join into Layer B `sched_facts` per team; feeds the Upside flag (game count) and the draft-room cap warnings.

# Overperform Tally — spec (repeatable, doctrine-governed)

> **Governed by `Pre_Pick_Doctrine.md`.** This is a TRANSPARENT COUNT of pre-draftable, team-specific reasons a team may beat/miss its market number — NOT a prediction, NOT a ranked score to draft down. The market total stays the baseline; round/price/scarcity judgment governs the pick. A high tally with a bad price is still a bad early pick.

## Why a tally, not a score
Backtest (memory #21/#22): AGGREGATE edge signals (SP+, TARP, RetProd, 6-Win%) do NOT predict beating the market — so they are EXCLUDED from the tally. What DOES identify overperformers is TEAM-SPECIFIC structural + pod knowledge (doctrine #24 key separation). The tally counts only those. Each point is a named reason you can see and overrule.

## Tailwinds (+) — pre-draftable reasons to beat the number
| Factor | Trigger | Source |
|---|---|---|
| Extra game | game_count = 13 (flex / Hawaii / Army-Navy) | schedule |
| Double bye | bye_count = 2 (extra rest across season) | schedule |
| Soft non-con | cupcakes ≥ 2 (win padding) | schedule |
| Home-leaning | home − road ≥ 2 | schedule |
| Favorable draw | pod sched_tag = Favorable | pod |
| QB upgrade | pod qb_status indicates upgrade/returning starter | pod |
| Dark horse | pod dark_horse flagged | pod |

## Headwinds (−) — pre-draftable reasons to miss
| Factor | Trigger | Source |
|---|---|---|
| Road-heavy stretch | max_road_streak ≥ 3 | schedule |
| Road-loaded | road ≥ 7 | schedule |
| Zero padding | cupcakes = 0 (no soft games) | schedule |
| Anchor gauntlet | ≥ 3 anchor-on-anchor games | schedule |
| Tough conference draw | pod sched_tag = Brutal, OR ≥2 anchor-on-anchor games vs same-conference anchors | pod + schedule (pool-relative draw, NOT raw SOS — SOS is already in the line) |
| Brutal draw | pod sched_tag = Brutal | pod |
| QB downgrade | pod qb_status indicates downgrade/loss | pod |
| Fade | pod fade flagged | pod |

## Upside thresholds — two levels (don't discard the soft leans)
- **Strong upside = net ≥ +2** — drives the Upside Availability heatmap COUNT and URGENCY color (fewer teams qualify = real scarcity pressure).
- **Soft upside = net ≥ +1** — still SHOWN in the heatmap cells (dimmed/italic), never discarded; a +1 lean is real, just weaker. Keeps the full supply visible.
- Urgency (need-filtered) keys on the STRONG count so it flags genuine drain, not every faint lean.

## Display rules (anti-flattening)
- Show the COUNT **with the reasons visible** — never the number alone.
- Net = tailwinds − headwinds, shown as "+3 / −1" NOT a single blended grade.
- Teams whose pod isn't loaded show `pod: pending` — their tally is SCHEDULE-ONLY and must be labeled so a thin count isn't misread as "no upside."
- Sort is allowed for scanning, but the header states this is NOT a draft order.
- SOS shown as context only (partly in the market line already — not a tally point).

## Repeatable pipeline (next year)
1. Schedule extraction (Schedule_Extraction_Process.md) → `layerA_schedule_columns_YYYY.csv`.
2. Paste/import those columns into the Layer A sheet tab (join key = Team).
3. Pod upside fields flow from `bboc_YYYY_CONF.json` as pods drop.
4. Frontend Overperform tab computes the tally LIVE from the published columns — no baked numbers, no per-year code changes. New data → tally recomputes automatically.

# Upside flag — Layer B derived signal (the price-equal tiebreaker)


> **Governed by `Pre_Pick_Doctrine.md`** — objective = maximize total wins; every heuristic here is CONDITIONAL (round/price/scarcity); the triad (scarcity + floor + upside-availability) always holds together; never separate a finding from its guardrail. If this doc's contents ever read as a flat rule, re-read the doctrine.

## What it is
A **Low / Med / High** read on a team's ROOM TO BEAT its projected win total — the secondary A-rating term that breaks ties between similarly-priced anchors. It is NOT a win projection and never overrides projected wins; it differentiates two anchors at the same price, weighted more heavily as round/price fall.

## Inputs (all already in Layer B)
| Signal | Source field | Upside contribution |
|---|---|---|
| Schedule softness | `sched_tag` (Favorable/Neutral/Brutal) | Favorable +, Brutal − |
| Anchor avoids | `key_avoids` — does it MISS the conference's top anchors? | avoids top anchors +; draws them / full round-robin − |
| Non-con cupcakes | `bboc_notes` / schedule | soft non-con + ; @P4 body-bag games − |
| QB | `qb_status` | returning starter / clear upgrade + ; unsettled battle / downgrade − |
| Rest / bye edges | `bboc_notes` | bye before rival, extra rest + |
| Host/pod signal | `host_lean`, `dark_horse`, `host_split` | dark_horse / lean-over + ; fade / lean-under − |
| Price headroom | `proj_minus_mkt`, tier | lower projected win total = more ceiling distance (structural, from the 453-anchor table) |
| **Game count** | `games` | a 13th regular-season game (Hawaii rule, counted flex) is an EXTRA win opportunity — pure ceiling, independent of per-game difficulty. 13 games > 12. Can outweigh schedule softness in a close call. |
| **Real-conf schedule (reassigned teams)** | real conference's pod + schedule | POOL CONFERENCE ≠ real schedule. Reassigned P4 teams (2026 pool Pac-12: Oklahoma State/Big 12, Arkansas/SEC, Michigan State+Purdue/Big Ten) play their REAL partial-round-robin schedules with real avoids/draws — big schedule-upside signal that lives in their REAL conference's pod, NOT the pool-conf pod. Never apply a pool conference's schedule structure to its reassigned members. |

## Scoring (transparent, not a black box)
Start Neutral (Med). Each signal nudges up or down. Net:
- **High** = multiple + signals, few/no − (soft slate + avoids anchors + returning QB, etc.)
- **Med** = mixed or neutral
- **Low** = capped: brutal slate OR draws all anchors OR QB downgrade with no offsetting +

## SCARCITY IS THE PRECONDITION (upside room operates WITHIN scarcity, never instead of it)
The upside-room strategy DEPENDS on scarcity timing — it does not loosen it:
- If the plan is "find an overperforming 5-6 win team," that team must still be ON THE BOARD at your pick. In a boat-anchor / bottom-heavy conference, the usable supply — anchors AND the upside-room mid-tiers — drains over the draft. You cannot punt a thin conference assuming you'll grab an overperformer later; the overperformer candidates won't survive to your next turn either.
- **S1-S5 scarcity tells you WHEN a conference's usable supply (anchors + upside mid-tiers) will be gone; the Upside flag tells you WHICH of the still-available same-priced teams to prefer.** Upside room refines the scarcity-timed pick; it never replaces it.
- Do NOT throw out the anchor-premium / scarcity doctrine (memory #2, #7). The upside finding refines it. Treating "chase upside" as a standalone rule is itself the flattening error (memory #24).

## Rules of use (from the winner almanac)
- **Round 1 / elite scarce anchor:** IGNORE upside — bank the wins. A 10.5 with "Low upside" is still the pick.
- **Similarly-priced fork:** upside breaks the tie. 5.5-High > 5.5-Low, decisively.
- **Weight grows as price/round fall.** By rounds 5-10 in capped conferences, it's the primary differentiator.
- **Flag informs, judgment decides.** The score surfaces the signals; the analyst confirms against the actual schedule and situation. Never auto-pick on the flag alone.

## Storage
Add `upside` (Low/Med/High) + `upside_why` (short reason string) to Layer B. Derived at extraction time from the fields above; re-derive if schedule/QB changes.

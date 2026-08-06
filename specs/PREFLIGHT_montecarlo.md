> **⚙ REQUIRED HEADER (retrofit to `specs/PREFLIGHT.md` standard).**
>
> **Session:** repo `/Users/mike/Downloads/ncaafbwinspool`; docs read per the plan below.
> **Foundations IN EFFECT:** **Universal Meta Game Principles** (1 asset-list-is-trigger · 2 availability-across-window-dominant · 3 evidence-degrades-state-weight · 4 most-recent-first · 5 weakness-on-primary-demand-near-DQ · 6 pre-commit-DQ-criteria · 7 external-pressure-tests-not-generates · 8 track-best-performers · 9 steps-need-visible-output · 10 process-failure-is-analyst's); **PRIMARY ANCHOR** (cross-conf replacement value); **S1–S5 × A1–A10** (anchor premium = A-rating × S-depth); **Pre-Pick Doctrine** (TRIAD scarcity∧floor∧upside-availability; objective = expected TOTAL wins; no heuristic promoted to a rule).
> **0–15 checklist:** applied for this task (see body); REPO-CHECK, NO-FABRICATION (`—`/gap-flag, never guess), YEAR-PARTITION, ANTI-FLATTENING, AUTO-PUSH all binding.
> ****KILL CRITERION:** the opponent model must reproduce the empirical draft-timing curve (thin-conf tiers within ~1 round) before any path number is trusted; season sim must be market-calibrated (no SP+-over-market bias).**
> **Weights/caveats:** stated inline (P3/P10).

# PREFLIGHT — Monte Carlo draft + season simulator ("5 paths to victory")

Binds the session. Builds the engine that produces **position-agnostic** draft strategies and answers the
live strategic questions (is Big Ten a target? which rounds decide it?) by simulating the whole pool —
draft *and* season — thousands of times.

## 0. Objective & doctrine
The pool is won by TOTAL actual wins across 10 anchors (one per conference). Champions draft to ~68
market and overperform to ~80 (`winner_almanac`); mean champion anchor projects to 6.8; the upside
tiebreaker weights later rounds. We don't know our draft slot until the night before — so the output is
NOT "do X at pick 7," it's **~5 strategy paths, each tagged with the slots + board conditions where it
wins** (Meta Game P2: availability across the scoring window dominates; P6: pre-commit disqualifiers).

## 1. What we simulate (one trial)
1. **Draw a slot** for us uniformly across the 12 seats (position-agnostic).
2. **Simulate the snake draft** — 12 players × 10 rounds, one-team-per-conference, scarcity-aware
   opponents; we pick by the candidate **strategy/policy** under test.
3. **Simulate the season** — every drafted team's regular-season wins from its per-game distribution,
   with anchor-on-anchor correlation; sum each of the 12 rosters → rank → did WE finish 1st / top-3?
Repeat N≈20–50k trials per policy.

## 2. Components
- **(a) Team season model** — per-game win probs from the sheet's Schedule Probs (the same `winDist`
  the F–C uses). Season wins = a Poisson-binomial draw (sample each game as Bernoulli).
  - **Anchor-on-anchor correlation:** when two POOL anchors play each other, one win = the other's loss.
    Use `schedule_facts_2026.json` `anchor_on_anchor` so rosters holding both don't double-count.
  - **Pac-12 flex ±1 game:** the 8 flex teams have 12 known games + 1 unknown conf game (schedule locks
    post-draft). Model the 13th as one extra Bernoulli at the team's computed flex-type win% (reuse the
    home/road SP+ vs cross-group average). Flagged assumption.
- **(b) Draft-flow sim — scarcity-aware opponents.** Opponents pick to maximize
  `value = market_line − λ·(depth penalty) + μ·(fills an unmet conference need)` — i.e. they grab thin-
  conference anchors early like real drafters, not pure market rank (your note). λ, μ tunable; add pick
  noise so the field isn't perfectly optimal.
- **(c) Candidate strategies (the paths under test)** — pick policies, e.g.: *elite-banking-first*,
  *thin-conference-sweep* (scarcity-first), *upside-mid-tier stack*, *balanced/adaptive*,
  *defer-deep-conferences*. Each is a scoring function over available teams given round + roster state
  (uses the dual-path Grade + Anchor Availability scarcity + upside tally). This is where **the Big Ten
  question is answered**: policies differ on whether to spend an early pick on a Big Ten elite vs defer —
  the sim tells us which wins more often, and at which slots.
- **(d) Scoring** — per trial, our total wins vs the 11 field rosters → finish rank → P(1st), P(top-3),
  mean finish, win-total distribution.
- **(e) Path selection** — run all candidate policies; keep the ~5 with the best P(1st) that are also
  *diverse* (don't keep 5 variants of the same idea). For each surviving path, report: P(1st) overall
  AND **conditioned on slot bucket** (early/mid/late), the round-by-round pick pattern, and primary +
  backup anchors per conference.

## 3. Key assumptions to CONFIRM before building
1. **Scoring = regular-season wins only, or include CCG wins?** (Backtest strips CCG; confirm the pool's rule.)
2. **Field strength:** how good are the 11 opponents — near-optimal scarcity-aware with light noise, or
   weaker/mixed? This calibrates P(1st) and matters a lot. Propose: scarcity-aware + moderate noise.
3. **Correlation scope:** model anchor-on-anchor only, or also within-conference schedule overlap? Propose: anchor-on-anchor only (the material one).
4. **Independence of team seasons** otherwise (different teams, different weeks) — propose treat as independent aside from anchor-on-anchor.
5. **N trials + runtime** — propose 20–50k/policy (seconds-to-minutes in Python).

## 4. Execution order (visible gate each step)
1. **Team season sampler** — validate: sampled mean wins ≈ `winDist.exp` per team; App State ~6.1, Boise ~8.3, ND ~11. *Visible: 10-team spot check.*
2. **Draft-flow sim** — validate: thin conferences (MWC/MAC/Pac12) empty of usable anchors earlier than deep (Big Ten/SEC); print the round each conference's supply cliffs. *Visible: scarcity curve.*
3. **Full trial loop** — one policy end-to-end; sanity P(1st) ≈ 1/12 for a naive policy. *Visible: baseline.*
4. **Policy tournament** — all candidate policies × slots; rank by P(1st). *Visible: policy leaderboard + Big Ten verdict.*
5. **Path synthesis** — cluster/select 5 diverse winners; per-path round pattern + backups + viable slots. *Visible: the 5 paths.*
6. **Deliverable** — `build/mc_paths_2026.json` + a rendered report (`almanac/battle_plan_2026.*`); optionally a draftroom "Battle Plan" tab later.

## 5. Where it runs
Python (`scripts/monte_carlo_draft.py`) in the container — heavy compute, not the HTML. Reads the repo's
schedule_probs + schedule_facts + data_2026 + Master. Outputs JSON + report; commit both. The draftroom
can surface the paths in a later pass.

## 6. Open decisions (answer to start)
- §3.1 CCG in scoring? · §3.2 field strength model? · N trials?
- Report format: markdown battle-plan doc, an HTML artifact, or a draftroom tab?

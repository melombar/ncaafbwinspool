# Wins Pool — Annual Rebuild Playbook (Layer C — governance)

> **START HERE.** This is the master doc. Open it each summer. It maps every file, defines the three-layer architecture, lists every data source (what/where/when/how), and gives the full rebuild order for the live draft pipeline. Work top to bottom.

## Start here — the 30-second orientation

1. **What is this?** A once-a-year rebuild spec for the NCAA Wins Pool draft tools: a 9-tab Google Sheet (data + live join + draft mechanics) and an HTML "draft room" that reads it live.
2. **The data model:** three layers — **A** = raw numbers (`data_YYYY.json`), **B** = pod writeups (`bboc_YYYY_CONF.json`), **C** = governance (this playbook + source docs). Dashboard = live JOIN(A,B).
3. **To rebuild for a new year:** collect Layer A + Layer B (Part I) → extract schedules + import schedule columns into Layer A → generate the 9-tab workbook → port to Sheets → rebuild the live join → deploy the proxy → regenerate the HTML (Part II).
4. **On draft day:** fill Draft_Order (roster + order), point Import_BradTracker at Brad's feed, open the HTML. Everything goes live.
5. **If something's broken:** check Part II → GOTCHAS first (they cover ~every failure we've hit).

## File map — what every file is, and which to keep active

> **Project hygiene (important):** Claude Projects flip from full-context reading to RAG/fragment retrieval at **~13 files**. Keep the ACTIVE project lean — ideally just the current-year almanac + this playbook + the two method docs. Everything else (historical years, raw JSON, scripts) archives to Drive and is pulled in on demand. **Regenerate JSON from MD when needed rather than storing both.**

### KEEP ACTIVE in the Claude Project (the lean core)

| File | Layer | Role |
|---|---|---|
| `Annual_Rebuild_Playbook.md` | C | **this file** — master governance + rebuild spec |
| `BBOC_Extraction_Template.md` | C | how to extract pod writeups into Layer B (year-agnostic method) |
| `TARP_source_2026.md` | C | TARP methodology/provenance (rename per year) |
| `almanac_YYYY.md` | B | the year's consolidated pod writeups, all 10 confs (one file/year) |

That's the target: **~4 files.** Everything below lives in Drive, not the active project.

### DATA FILES (archive to Drive; regenerate/re-upload on demand)

| File | Layer | Role |
|---|---|---|
| `data_YYYY.json` | A | the year's raw numbers (market, SP+, RetProd, TARP, Collin, 6-Win%, SOS), one row/team + Pool Conf |
| `bboc_YYYY_CONF.json` | B | per-conference pod writeup (source for almanac + Layer B tab) |
| `sp_YYYY_final.json`, `edge_YYYY.json`, `tarp_YYYY.json` etc. | A | raw source captures (kept for backtest/reprovenance) |

### BUILD ARTIFACTS (this cycle's outputs — Drive, not project)

| File | Role |
|---|---|
| `NCAA_Wins_Pool_YYYY_PREVIEW.xlsx` | the 9-tab workbook (ported to Google Sheets) |
| `Dashboard_LiveJoin_Formulas.md` | the live-join formulas to paste into the Sheet (regenerate per year) |
| `wins_pool_proxy.gs` | Apps Script data proxy (deploy once; reuse if sheet persists) |
| `Apps_Script_Setup.md` | proxy deployment steps |
| `wins_pool_YYYY_draftroom.html` | the HTML draft room (wired to the proxy `/exec` URL) |

### HISTORICAL (Drive archive — pull in only for backtest)

`NCAA_Wins_Pool_20NN.xlsx` (2015–prior years), prior almanacs, `NCAA_wins_pool_rules.pdf`, the GPT framework transcript. Never needed for a current-year build; each workbook is its own season (never pool across years).

### BLOAT TO RESOLVE (found 2026 — duplicate/stale files in the project)

- **`claude_*` duplicates** (`claude_bboc_*.json`, `claude_data_2026.json`, `claude_TARP_source_2026.md`) duplicate the non-prefixed versions — **keep one, delete the `claude_` copies.**
- **`.json` + `.md` pairs of the same content** (e.g. `bboc_2025_acc.json` + `.md`) — the almanac consolidates the MD; keep the JSON in Drive, drop loose per-conf MDs from the project.
- **Loose per-conference 2025 files** (`claude_bboc_2025_*.json` ×8) should be consolidated into `almanac_2025.md` and archived.
- **A decade of historical workbooks** in the project → move to Drive; they only matter for backtest and can be re-uploaded.
- Net: the project can drop from ~37 files to ~4 active without losing anything (all recoverable from Drive/regeneration).

---

> **Layer scheme (relabeled 2026 — intuitive order):**
> **A = raw data** (the numbers) · **B = supplemental data** (the pod writeups) · **C = governance** (this playbook + source/methodology docs).
> *Historical note: earlier docs briefly used the reverse (A=writeups, B=numbers). All current files use the A=raw / B=supplemental / C=governance scheme below.*

---

## The three layers (what goes where)

| Layer | What it holds | Files | Update cadence |
|---|---|---|---|
| **A — Raw data** | Every numeric measure, one row per team, keyed on Brad-canonical name (market, SP+, ret prod, TARP off/def/net, Collin proj, 6-Win%, SOS) | one `data_YYYY.json` (mirrors the Data sheet `Combined` tab) | Whenever a source releases/updates |
| **B — Supplemental data** | Pod-derived, team-specific content ONLY (QB, HC/OC/DC, host lean, dark horse/fade/split/variance, sched tag, key avoids/draws, key injury, notes) | `bboc_YYYY_CONF.json` + `.md`, one per conference | Once, as each conference's pod drops (July–Aug) |
| **C — Governance** | Provenance & rules: what each measure is, source, availability date, retrieval method, quirks, methodology docs | this playbook + source docs (e.g. `TARP_source_YYYY.md`) | Edit when a source changes |

**Dashboard = JOIN(A, B) on Brad-canonical name.** Update A once → every conference dashboard reflects it. Never put numbers in Layer B (the writeups); never put pod-qualitative content in Layer A (the data sheet).

---

## Naming (the join key)

- **Roster + conference** = current-year pool canon (the locked list; reassignments differ each year).
- **Spelling** = Brad's conventions (EMU, UMASS, Miami-OH, Florida Intl, San José State). Brad's sheet STRUCTURE is stable year-over-year — reuse the prior year's sheet as the template; only contents change.
- Everything keys on Brad-canonical `Conf|Team`. The normalization layer maps each source's names → Brad-canonical (each site names teams differently; this is now handled here, not in the sheet).

---

## ⭐ 2026 REBUILD — conference source-of-truth + identical-header join (SUPERSEDES the join/gotcha notes below)

The 2026 cycle replaced hand-entered conferences and the positional/ARRAYFORMULA join after a
draft-invalidating bug (Notre Dame rendered as AAC, swapped its win total with South Florida — hidden
because the old join *renamed* columns). New model:

- **Conference is SOURCED, not typed.** Brad imports two tabs — `Import_BradConference` (pool) and
  `Import_ActualConferences` (actual, incl. `zIndependents`). They feed **`Master_Lookup`**
  (Team · Pool Conf · Real Conf), pasted **static** from the repo-generated `data/Master_Lookup_YYYY.tsv`.
  Layer A `Pool Conf` and the join `Real Conf` are `VLOOKUP`s into Master. **The SWITCH is retired.**
- **The A+B join surfaces RAW columns with IDENTICAL headers** to the source tabs — no renamed or
  composed join columns. Per-row **`VLOOKUP(A2, range, MATCH(header,…), 0)`**, filled down.
  **No ARRAYFORMULA** in the join. `Coaching`/`Flags` no longer exist as join columns — the HTML
  composes them from raw `New HC/New OC/New DC` and `Dark Horse/Fade/Split/Variance`.
- **Layer A** is a static paste: A–N from `LayerA_AN_YYYY.tsv`, P→ schedule facts from
  `layerA_schedule_columns_YYYY.csv`. Ship them as ONE aligned block (`LayerA_FULL_YYYY.tsv`) so A and
  the schedule columns can't land in different row orders (that misalignment silently gives every team
  the wrong schedule facts). Only formulas in Layer A: **O** (Pool Conf VLOOKUP) and **Z**
  (`pod_upside_status` = live Layer-B coverage check).
- **Naming is the join key** — governed by **`specs/Naming_Canon_2026.md`**: 9 canonical team spellings
  (`EMU`, `Florida Intl`, `Miami`, `Miami-OH`, `San José State`, `Southern Mississippi`, `UL Lafayette`,
  `UL Monroe`, `UMASS`; plus `Appalachian State` not `App State`) and conf token **`Big Ten`** (not
  `Big 10`), `Independent` (not `zIndependents`). Normalization lives in **repo code** and is applied to
  every name-keyed file BEFORE the sheet sees it. A single drift blanks a name-keyed row.
- Formula set + column layout: **`draftroom/Dashboard_LiveJoin_Formulas.md`** (24 raw columns).
  Change record: **`specs/PREFLIGHT_conf_rebuild.md`**. Completion audit: **`specs/PREFLIGHT_config_documentation.md`**.

**Everything in "The Dashboard join (operating logic)", the GOTCHAS list, and the Dashboard column
layout below is the OLD (pre-2026) design — kept for history but SUPERSEDED by this section.**

---

## Data sources — the annual collection list

Work down this list. "When" = when it becomes available/final.

### Layer A — numeric sources (raw data)

| Source | Measure | Where | When available | Retrieval | Quirks |
|---|---|---|---|---|---|
| **Market win totals** | preseason O/U per team | DraftKings (via DK Network article) or SBD or Phil Steele | **May–July** | web_fetch the article (DK works via web_fetch even when browser-blocked) | SBD's later pages go P4-only some years — use full-FBS source. Confirm PRESEASON, not in-season. |
| **Historical preseason totals** | past-year O/U by team, for model variance calibration | `sbd_preseason_2018_2025.json` (SBD past-seasons page) | once (static); re-pull only to extend | Held in project. Schema: year→{team:total}. Coverage uneven (2018 thin=35, 2023/24 P4-heavy=69, 2025 full=133); no 2020 (COVID). Pair with workbook actuals to calibrate the win-distribution variance for P(≥N). | PRESEASON lines. Do NOT confuse with in-season/actuals. |
| **Game moneylines / spreads** | per-game lines for the prediction model | VegasInsider `/college-football/odds/las-vegas/` | Aug (weeks ~1–4 post); re-pull closer to draft as more post | Browser only (not container-reachable). Moneyline → de-vig → win prob (cleaner than spread). Coverage partial this far out (~4 of 12 games); rest fall back to SP+ shaping. | Real line beats SP+ per game. Use where posted; flag coverage. Feeds `predictions_YYYY.json`. |
| **SP+ (March)** | early ratings | ESPN (Connelly article) | **Feb–Mar** | ESPN article; ESPN+ paywalled but readable when logged in | Recruiting-heavy placeholder. |
| **SP+ (August)** | final-roster ratings | ESPN (Connelly article) | **Aug** | same | Connelly flags Aug as draft-relevant. **SP+ updates MULTIPLE times** — pods often cite a later refresh than our pull; capture pod SP+ separately (see Layer B). |
| **ESPN Returning Production %** | ret prod, off/def | ESPN article | **Spring–Summer** | ESPN | Overlaps SP+/TARP (returning-production family) — don't triple-count. |
| **ESPN 6-Win %** | P(≥6 wins) | ESPN returning-production article (SAME article family, distinct metric) | **Summer** | ESPN | The most DIFFERENTIATED family member (an outcome probability). 2025-only historically — check each year. |
| **Collin Wilson / Action projections** | full-model win projection | projectthreestraight.com (formerly Action Network) | **Jul** | web_fetch; also spoken on the pods | Treat Action + Collin as ONE source. |
| **TARP (off/def/net)** | transfer + returning production | Three Straight (Collin) — published Google Sheets linked from projectthreestraight.com/2026-tarp-transfer-activity-returning-production/ | **Jun** (post-spring portal) | Render the published sheet in-browser (JS-rendered, not web-fetchable). "PR Adjustments" sheet = ±scale net/off/def; "Team Totals" = raw 0–1. Underlying data PFF + 247Sports. See `TARP_source_YYYY.md`. | Off range ±6, Def ±5. Net = Off + Def. Overlaps SP+/ret prod. |
| **Official schedules (ESPN)** | opponents, home/away, bye week, game count → **anchor-on-anchor caps** + pool-framed reassigned-team schedules | ESPN `site.api` per team (see `Schedule_Extraction_Process.md`) | **When schedules post (~Jul–Aug); re-run near draft** | Browser only (container can't reach ESPN). **Match opponents by ESPN team ID, NOT name.** Bulk teams endpoint blocked — use maintained ID map. | Rebuild-conf (Pac-12) counts PROVISIONAL until finalized (see #27). **WEEK 0/15 TRAP:** split Week 0 (Aug openers ESPN labels wk1) by DATE or games collapse + byes hide; keep Week 15 (Army-Navy). RECONCILE filled cells vs game_count per team before trusting any grid. See Schedule_Extraction_Process.md validation gate. |
| **SOS Rank** | strength of schedule | SP+ article (SOS_RK col) or pod | with SP+ | — | — |

### Layer B — the pods (supplemental / qualitative)

| Source | What | Where | When | Retrieval |
|---|---|---|---|---|
| **Big Bets on Campus** conference previews | per-team QB/coaching/host-lean/schedule read | iHeart / project files | **Jul–Aug**, one per conference | get_page_text (browser) or project docx (plain-text). Extract per the BBOC Extraction Template. |

### Official schedules (feeds key_avoids + games count)

| Source | What | When | Quirk |
|---|---|---|---|
| Conference schedule releases | confirmed head-to-heads, round-robin structure, game count | **May–Jul** | Partial round-robins (SEC/B10/ACC) create "avoids" = the unbalanced-schedule signal. FULL round-robins (real Pac-12, 8 teams) have NO avoids. Flex/13th games create win-total (11-vs-12) ambiguity. Confirm per conference. |

---

## Build order (once per year)

1. **Roster/canon** — lock the year's pool conferences + reassignments; set Brad-canonical names. **(2026+)** Source conferences from Brad's two imports (`Import_BradConference` = pool, `Import_ActualConferences` = actual) → build `Master_Lookup` (normalize spelling per `Naming_Canon`, `Big 10→Big Ten`, `zIndependents→Independent`); reconcile to 138 teams, 0 unmatched. Don't hand-enter Pool Conf.
2. **Layer A numerics (raw data)** — collect each source above as it's available; normalize names; assemble `data_YYYY.json`.
3. **Layer B pods (supplemental)** — as each conference pod drops, extract to `bboc_YYYY_CONF.json` per the template.
4. **Schedules** — capture official releases; populate key_avoids + games count.
5. **Dashboard** — JOIN A+B on Brad-canonical name; build against prior year's sheet structure.
6. **Backtest / strategy docs** — once the historical layers are complete.

---

## Known cross-source notes (quirks that bite)

- **Returning-production family** (SP+, ESPN ret prod, TARP) are CORRELATED — don't count as 3 independent signals. 6-Win% is the differentiated one.
- **SP+ multiple updates** — the pod-vs-our-pull difference is itself a signal (update direction = beat/miss).
- **Preseason vs in-season** — always confirm a projection column is PRESEASON before using it in a backtest (workbook Proj Logs are corrupted-to-actuals).
- **Market G5 coverage** — some sources drop G5; use a full-FBS source.
- **Flex/13th games** — real Pac-12 Week-13 flex may not count; books differ. Hawaii-rule 13th games are extra win opportunities.

---

# Part II — The live draft pipeline (workbook → Google Sheet → HTML draft room)

*Everything below was built and validated in the 2026 cycle. It turns the static Layer-A/B data into a live draft-day tool. Rebuild once per year against the prior year's version.*

## The workbook (9 tabs)

Built as an `.xlsx` first (Claude generates it), then ported to Google Sheets. Three-layer model made literal:

| Tab | Rows | Role | Source |
|---|---|---|---|
| **ReadMe & Sources** | — | layer model + provenance front page | static |
| **Layer A — raw data (SOURCED)** | 138 | the numbers, one row/team + **Pool Conf** in last col | `data_YYYY.json` |
| **Layer B — pod writeups** | ~26→138 | pod content, one row per covered team (blank teams absent) | `bboc_YYYY_CONF.json` |
| **Dashboard (A+B join)** | 138 | **LEFT JOIN** of A+B — every team, Layer B blank where no pod | live formulas |
| **Import_BradTracker** | picks | the pick log — mirrors Brad's DraftTracker cols (`draft,rnd,pick,player,conf,team,…`); filter key = `team` | Brad's feed |
| **Draft_Order** | 12 slots | roster (12 blank yellow slots) + current round + snake gap math | manual, draft day |
| **Conferences_Needed** | 10×12 | player × conf NEED matrix; player cols reference Draft_Order roster | formulas |
| **Remaining_By_Conf** | — | auto-refresh depth board; teams drop to "—" when picked | formulas |
| **Following_Me** | 10 | in-gap demand + punt/grab reads (the neighbor-demand view) | formulas |

**Column layouts (the join keys off these — confirm before regenerating formulas):**
- **Layer A**: A=Team, B=Mkt O/U, C=SP+ Rk, D=SP+ Rtg, E=RetProd%, F=Ret Off%, G=Ret Def%, H=TARP net, I=TARP off, J=TARP def, K=Collin Proj, L=Proj−Mkt, M=6-Win%, N=SOS Rk, **O=Pool Conf**
- **Layer B**: A=Team, B=QB status, C=New HC, D=New OC, E=New DC, F=Host Lean, G=Dark Horse, H=Fade, I=Split, J=Variance, K=Sched Tag, L=Key Avoids/Draws, M=Key Injury, N=BBOC Notes
- **Dashboard** *(⚠️ SUPERSEDED 2026 — the join is now 24 RAW columns with identical source headers; see the 2026 REBUILD section + `Dashboard_LiveJoin_Formulas.md`)*: ~~A=Pool Conf, B=Team, C=Real Conf, D=Mkt, E=SP+ Rk, F=SP+ Rtg, G=RetProd%, H=TARP net, I=Collin, J=Proj−Mkt, K=QB status, L=Coaching, M=Host Lean, N=Sched, O=Flags, P=Key Avoids/Draws, Q=Notes~~

## The Dashboard join (operating logic)

The Dashboard is **not** static values — it's a live join so that editing Layer A or Layer B updates it automatically. Built as **one `ARRAYFORMULA` per column** in row 2 (spills down; auto-extends on new rows; no fill-down). The Team column (B) is the spine (pulls the Layer A team list); every other column is a `VLOOKUP` against that spine into Layer A or Layer B, wrapped `IFERROR(…,"")` so missing Layer B → blank (the left join).

- **Numbers** (Mkt, SP+, RetProd, TARP net, Collin, Proj−Mkt) → VLOOKUP into Layer A.
- **Pod fields** (QB, Host Lean, Sched, Key Avoids, Notes) → VLOOKUP into Layer B.
- **Coaching** = concatenated `"HC "&… "OC "&… "DC "&…` from Layer B cols C/D/E, `TRIM`-wrapped.
- **Flags** = concatenated `DH/FADE/SPLIT/VAR` from Layer B cols G/H/I/J (each ="Y").
- **Real Conf** = reassignment map lookup, else Pool Conf (see gotcha below).

The full formula set lives in `Dashboard_LiveJoin_Formulas.md` (regenerate per year — the tab names and column letters are baked in).

### GOTCHAS (each cost real time — do not rediscover)

1. **Paste flattens formulas to values.** Pasting an `.xlsx` (or paste-special values) into Google Sheets lands the *computed values*, NOT the formulas — so the "join" is a frozen snapshot that never updates. **Fix:** after porting, rebuild the Dashboard body as live formulas IN the sheet (delete row 2→bottom first, then paste the ARRAYFORMULAs). Symptom: "there are no lookups anywhere in A+B."
2. *(⚠️ SUPERSEDED 2026 — the SWITCH is retired; Real Conf is now a VLOOKUP into `Master_Lookup`. This gotcha no longer applies.)* **`SWITCH` is NOT array-aware inside `ARRAYFORMULA`.** It evaluates only the first row's branch; every other row falls through to the default. This silently broke Real Conf (all reassigned teams showed pool=real). **Fix:** use `VLOOKUP` into an inline array literal map instead — VLOOKUP *is* array-aware:
   `=ARRAYFORMULA(IF(A2:A="","",IFERROR(VLOOKUP(A2:A,{"Notre Dame","Independent"; "UConn","Independent"; …},2,FALSE),<pool conf vlookup>)))`
3. **`TEXTJOIN` didn't survive the paste** (blank Coaching/Flags) — same root as #1; rebuilding as live formulas fixes it.
4. **"Array result was not expanded, would overwrite C3"** — leftover static values below the ARRAYFORMULA cell block the spill. **Fix:** clear the target column from row 3 to ~1000 first, then the row-2 formula expands.
5. **App State vs Appalachian State** and similar — Layer B team names must match Layer A exactly or the VLOOKUP misses. Normalize on the way in.

## Publishing the sheet (for the HTML to read)

**Publish to web as CSV** — File → Share → Publish to web. Publishing is per-tab and tied to the document (not a version), so it auto-updates when the sheet changes. **Newly-added tabs are NOT auto-published** — after adding a tab (e.g. Layer B), re-open Publish settings and include it, or the HTML can't see it.

- `…/pub?output=csv` with **no gid** returns only the FIRST tab. Each tab needs `&gid=NNNN&single=true&output=csv`.
- Get gids: open the `…/pubhtml` version in-browser and scan for `gid=\d+`; map each by fetching its CSV and reading the header (reading tab NAMES requires DOM, not the HTML bootstrap).
- **CRITICAL:** the published CSV only fetches from JS **without credentials** — `fetch(url)` (no `credentials:'include'`). Google's `/pub` sends CORS headers for anonymous requests, blocks credentialed ones.

### But CSV-from-`file://` fails — use the Apps Script proxy instead

A plain HTML file opened via `file://` **cannot** reliably fetch the published CSVs — the browser enforces CORS strictly from a `file://` origin and Google's `/pub` exposes no allow-origin header. **Solution: a Google Apps Script web-app proxy** (`wins_pool_proxy.gs`). It reads the tabs and returns one JSON blob with CORS enabled. The HTML fetches ONE proxy URL and works from any origin, `file://` included, with no republish-timing issues.

**Deploy (once per year, or reuse if the sheet persists):**
1. Sheet → **Extensions → Apps Script**, paste `wins_pool_proxy.gs`, Save.
2. **Deploy → New deployment → Web app**, **Execute as: Me**, **Who has access: Anyone**, Deploy, authorize.
3. Copy the **`/exec` URL** → wire it into the HTML's `PROXY` const.
- The script references tabs by exact name (`Dashboard (A+B join)`, `Layer A — raw data (SOURCED)`, `Layer B — pod writeups`, `Import_BradTracker`, `Draft_Order`). Rename a tab → update the script. Editing the script requires re-deploying (Manage deployments → edit) for changes to take effect; the URL stays stable.
- "Who has access: Anyone" = read access to returned data via the random URL (same privacy as publish-to-web); does NOT expose edit access.

## The HTML draft room

Single self-contained file (`wins_pool_YYYY_draftroom.html`). Fetches the proxy `/exec` URL on load + every 60s (+ manual ↻). Joins Dashboard (spine + most fields) with Layer B (coaching/flags/injury read directly from Layer B for robustness — see gotcha #3, so the board is correct even if the sheet's TEXTJOIN columns break). Five views:

1. **Enriched Board** — all 138 teams, sortable/filterable; columns incl. QB, Coaching, Sched, Lean, Flags; notes cell leads with **Key Avoids** (the schedule edge) + Injury, then pod notes. Picked teams greyed. Click ⊕ to pick, or paste picks.
2. **Anchor Availability heat map** — usable anchors (≥6.0) per conference, brightness = O/U, draining as picked; count color-scaled red(0–1)→green(4+). This is the depth-countdown visualized; pre-draft it ranks the thin conferences (MWC/MAC/Pac12) red, deep (Big Ten/SEC) green — confirms the defer-deep strategy.
3. **My Needs** — my 10 conferences, green=filled / red=needed.
4. **Pool Needs** — 12 players × 10 conferences grid, ●filled/○needed, my column outlined.
5. **Setup & Picks** — roster/order input + pick entry (click or paste).

Data-source keys the HTML expects (must match Dashboard/Layer B headers): Dashboard `Pool Conf, Team, Real Conf, Mkt, SP+ Rk, SP+ Rtg, RetProd%, TARP net, Collin, Proj−Mkt, QB status, Coaching, Host Lean, Sched, Flags, Key Avoids/Draws, Notes`; Layer B `New HC/New OC/New DC, Dark Horse/Fade/Split/Variance, Key Injury`.

## Draft mechanics — the operating logic (Following Me / neighbor demand)

Operationalizes structural-scarcity-vs-actual-demand (the whole strategy). Lives in **Draft_Order** + **Following_Me**, roster-agnostic (12 fixed slots; names/order fill in on draft day).

- **Snake gap math** (Draft_Order): given my slot + current round, compute which players pick between my current pick and my next. Snake parity: odd rounds slot ascending (pick# = slot), even rounds descending (pick# = N+1−slot). A player is "in gap" if their pick# this round > my pick# this round, OR their pick# next round < my pick# next round. Near the ends of the order that's few players; mid-order it's many.
- **In-gap demand** (Following_Me): for each conference, count in-gap players who still NEED it (from Conferences_Needed × the gap flags). 
- **The read:** SCARCE (≤3 open) + nobody in gap needs it → **PUNT OK** (anchor likely returns). SCARCE + in-gap demand → **GRAB** (a neighbor takes it before it snakes back). This is the punt-vs-grab decision made mechanical.
- **Depth-countdown trigger** (not pick tempo): act when a conference you still need drops to ≤2–3 usable remaining. Deep conferences never trip it → defer.

## Annual pipeline rebuild — order of operations

1. Assemble `data_YYYY.json` (Layer A) + `bboc_YYYY_CONF.json` (Layer B) per Part I.
2. **Extract schedules → schedule columns.** Run the schedule extraction (see `Schedule_Extraction_Process.md`): pull all pool teams' real ESPN schedules, split Week 0 by date, keep Week 15, reconcile filled cells vs game_count. Produces `schedule_facts_YYYY.json` + `pool_schedule_grid_YYYY.csv` + `layerA_schedule_columns_YYYY.csv` (game_count, game_delta, bye_count, byes, home, road, max_road_streak, cupcakes, sos_proxy, anchor_on_anchor, pod_upside_status). **Import `layerA_schedule_columns_YYYY.csv` into the Layer A sheet tab (join key = Team)** — this feeds the Overperform tally + Upside Availability heatmap (per `Overperform_Tally_Spec.md`). Pod upside fields flow from Layer B as pods drop; teams without a pod carry `pod_upside_status = pending-pod`.
3. **Build the frozen prediction model** (`predictions_YYYY.json`). Per team, per-game win prob via the hierarchy: posted **moneyline** (de-vig) → posted **spread** → **SP+** differential (shrunk toward market, calibrated on the line overlap per backtest #22) → **tier default** (FCS 0.90, non-pool FBS by conf tier) — all **sum-constrained to the market win total** (market sets level, SP+ sets shape). Roll up via Poisson-binomial → **P(≥8), P(≥6), expected wins, floor/ceiling shape, schedule-cost decomposition.** Log per-game **situational covariates** (home/away, con/non-con, rest/short-week, close-game band, tough-road/cupcake) for future backtests. Calibrate the win-distribution variance from `sbd_preseason_2018_2025.json` + workbook actuals. **Freeze + timestamp** the file at draft — it's the permanent record for next year's backtest. Spec: `Prediction_Model_Spec.md`.
4. Generate the 9-tab `.xlsx` from those (Claude builds it; validate with recalc — 0 errors).
5. Port to Google Sheets (import/replace, keeping the same document so gids/publish persist if reusing).
6. **Rebuild the Dashboard as live formulas** in the sheet (regenerate `Dashboard_LiveJoin_Formulas.md` for the year; watch gotchas 1–4). Test: edit a Layer B cell → Dashboard changes.
7. Deploy/refresh the Apps Script proxy; grab the `/exec` URL.
8. Regenerate the HTML draft room with the year's proxy URL; validate against the live proxy (138 teams, coaching live, reassignments correct, schedule columns present so Overperform tab + Upside heatmap populate).
9. On draft day: fill Draft_Order (roster + order + round); point Import_BradTracker at Brad's live feed (or paste). Everything downstream goes live. **Freeze `predictions_YYYY.json` before the season starts.**
10. **Next August — retrospective backtest** (`backtest_predictions.py`): pull LAST year's frozen `predictions_(YYYY-1).json`, join to actual results, score the model (predicted vs actual, P(≥8) calibration) AND the situational signals (pooled, market-baselined, multi-year — do tough-road / con-non-con / rest / cupcake tags predict actual−predicted?). Feed verdicts into this year's SP+ shrinkage + signal weights. One season = one data point; revise only on multi-year evidence (guards the 6-Win% single-year-variance trap). This is the ONLY revision point — the pool is one-shot, no in-season changes.

## Validation checklist (run after rebuild)

- [ ] Dashboard = 138 rows, 0 formula errors, edits to Layer A/B propagate live
- [ ] Reassigned teams show correct Real Conf (Notre Dame→Independent, Oklahoma State→Big 12, etc. — now sourced from `Master_Lookup`, not the retired SWITCH)
- [ ] `Master_Lookup` + Layer A reconcile to 138 teams, 0 unmatched; all 9 canonical spellings + `Big Ten` token clean (grep the repo — see `PREFLIGHT_config_documentation.md`)
- [ ] Layer A A–N and P→ pasted from ONE aligned `LayerA_FULL` block (no A-vs-schedule row misalignment); spot-check James Madison shows its 3 anchor-on-anchor games
- [ ] Coaching + Flags populate (not blank — the paste/TEXTJOIN gotcha)
- [ ] Proxy `/exec` returns `ok:true`, all 5 tabs, correct row counts
- [ ] Layer A carries the 12 schedule columns (game_count … pod_upside_status); flex-8 = 13 games, Week-0 teams = 2 byes (spot-check USC bye_count 2, Boise game_count 13)
- [ ] HTML loads from `file://` (proxy, not CSV), all 5 views render, heat maps compute
- [ ] Overperform tab populates (tallies non-empty); Upside Availability heatmap colors urgency on needed conferences; pod-pending confs labeled
- [ ] Anchor Availability pre-draft ranks thin conferences red / deep green (sanity-checks the data)

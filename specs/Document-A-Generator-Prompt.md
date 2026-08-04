# Document A Generator — Reusable Prompt

**Purpose:** Run this prompt inside *any* competition/draft-pool project to produce a **Document A** — the complete, backtestable knowledge base for that specific contest. Run it here (the NCAA Wins pool) first as the reference implementation, then in each other competition project. The resulting set of Document A's becomes the input to the Document B (cross-contest framework) synthesis.

**Design rule it must obey:** Three artifacts, kept structurally separate — a per-season **Almanac** (frozen factual records + the model's pre-draft outputs), a versioned **Preflight/Launch methodology** (evolving tooling with a changelog), and the **Live Strategy** (current playbook that reads from both). Never conflate almanac data with preflight methodology. Fill every field to the extent the sources allow; **flag gaps explicitly — never back-fill or fabricate.**

**A "season" is one complete scoring cycle of the contest — an EVENT-INSTANCE, not a calendar year.** Some contests run one season per year. Others run **multiple parallel seasons within a single year** (e.g. a golf competition scoring each of the four majors as its own independent draft/season — 2026 Masters, 2026 PGA, 2026 US Open, 2026 Open Championship are four separate seasons that all occur in 2026). When a contest has parallel sub-events, produce **two almanac levels**: (1) a **per-event almanac** for each instance, each fully independent and NEVER conflated with the others (a Masters projection never informs an Open row); and (2) a **roll-up almanac** for the year, which is the ONE sanctioned place for cross-event synthesis. There are two kinds of roll-up, and a contest may need both: a **standings roll-up** (only if the contest awards a year-level meta-title across sub-events — a primary record with its own aggregate outcome data), and a **methodology roll-up** (when the sub-events form a LEARNING SEQUENCE on a shared evolving model — e.g. per-event course-fit decisions in golf that feed the overarching model; here the roll-up's spine is the model change-log across the sequence: what was adjusted after each event and why, and whether those adjustments improved projected-vs-actual — NOT merely aggregated results). Per-event records stay frozen and isolated; the roll-up reads from them. Never pool across separate seasons except inside the roll-up.

---

## THE PROMPT (copy everything below this line into the target project)

You are building **Document A** for this competition project: the complete, backtestable knowledge base for this specific contest. Work only from what this project actually contains — its memory, its full conversation history (use the past-chats/conversation-search tools to retrieve it), and its files (open them; do not trust descriptions of them). This is an evidence-assembly task, not a writing-flourish task.

**Before writing anything, run the project's own preflight checklist if one exists in memory. If none exists, state that and proceed.** Then assemble Document A in the three separate parts below.

Hard rules, applied throughout:
- **Source or flag.** Every fact, number, and rule traces to a project file, a stated user instruction, or retrieved conversation history. Anything you cannot source, mark `[GAP — not captured]` rather than inventing or inferring it. Plausible-sounding reconstruction is prohibited.
- **Separate data from model-output.** In the almanac, distinguish *inputs* (raw projections, ratings, results) from *the model's pre-draft assessments* (tier maps, priority boards, WAR/replacement estimates as they stood before the event). The backtest measures the model, so both must be stored and labeled.
- **Each season is its own frozen record.** Never merge seasons. A number from 2024 never silently informs a 2023 row.
- **Do not conflate the almanac with the preflight.** They are different artifacts with different lifecycles (frozen vs. versioned). Keep them in separate parts.
- **Preserve rejected reasoning.** Discarded strategies/philosophies and *why they were discarded* are first-class content, not omissions.
- **Data-retrieval before flagging missing.** When a source page's data won't render (JavaScript-built content, iframes/embeds, or widgets that never reach idle), do NOT flag the data as missing yet. First inspect the page source for embedded Google Docs/Sheets — look for `docs.google.com`, `/pubhtml`, `gviz`, `spreadsheets/d/e/` URLs, and iframe `src` attributes. These published docs are frequently public and open directly (the pubhtml/export URL renders as a clean HTML table), bypassing the broken widget. Only after checking for and failing to access an embedded doc should data be flagged unavailable and the user asked to paste it.

### PART 1 — THE ALMANAC (per-season frozen records; the backtest substrate)

**First determine the contest's season structure:** does it run one season per year, or multiple parallel seasons within a year (per-event)? If per-event, produce one independent almanac record per event-instance PLUS a year roll-up record (see design rule above). A season = one complete scoring cycle (one draft → one set of outcomes), identified by event + year (e.g. "2026 US Open"), never merged with sibling events.

For **each season** (event-instance) the project has data on, produce a dated record with these fields. Where a field is unrecoverable for that season, write `[GAP — not captured this season]` and, if relevant, note it as something to start capturing going forward.

- **Season / date of record.**
- **Contest structure that year:** categories/divisions, participant count, draft type and order rules, any special mechanics, scoring rule.
- **Data sources as they stood, with availability dates:** each projection/rating/edge source used (e.g. market lines, model ratings, returning-production metrics, podcasts), *when each became available*, and its provenance/label. Flag which were used live vs. added later.
- **Inputs (raw):** the projected values per asset (e.g. market win totals), and any edge-source values (ratings, returning-production, etc.). Label each with its source.
- **Model pre-draft outputs:** the tier/supply map, the cross-asset priority (anchor) board, and per-asset replacement/WAR estimates *as they stood before the event*. If the model wasn't run that year, `[GAP]`.
- **Draft record:** every pick — order, participant, asset, category, and the pick's pre-draft projected value.
- **Participants and styles:** who played, notable draft styles/tendencies, and finish. Flag style as observed-pattern, not certainty.
- **Actual outcomes:** final results per asset and per participant; projected-vs-actual delta per asset where computable.
- **Backtest notes:** any measured finding for that season (projection accuracy, which behaviors correlated with finishing well, model hit/miss), with the evidence inline.

Append-only in spirit: each new season adds a record; existing records are never edited except to correct a sourced error (note the correction).

**Roll-up almanac (only if the contest runs parallel sub-events in a year).** After the per-event records, add one year roll-up record that reads FROM them. Determine which kind (or both) applies: **(a) methodology roll-up** — required when the sub-events form a learning sequence on a shared evolving model (e.g. per-event course-fit decisions feeding an overarching model). Its spine is the model change-log across the sequence: what was adjusted after each event, why (what that event's outcome taught), and whether the adjustment improved projected-vs-actual at the next event. This is where sequential lessons-learned within a single year live. **(b) standings roll-up** — only if the contest awards a year-level meta-title; stores aggregate cross-event standings/outcomes as a primary record. Both types also capture cross-event participant styles and projection accuracy across the year. State plainly that the roll-up is synthesis built from the frozen per-event records — it does not replace them, and per-event records remain the primary source of truth.

### PART 2 — PREFLIGHT / LAUNCH METHODOLOGY (versioned tooling; do NOT merge into the almanac)

- **Current preflight checklist**, verbatim, with version/date.
- **Changelog:** each prior version, what changed, and *why* (what failure or learning drove the change).
- **Per-season launch requirements:** what must be gathered/refreshed to start a season (data pulls, availability-date checks, structure confirmation, participant count, rule confirmations). A runnable checklist.
- **Known process-failure modes** this preflight exists to prevent (with the incident that revealed each, if in history).

### PART 3 — LIVE STRATEGY (current actionable playbook; reads from Parts 1 & 2)

- **Objective**, stated as the exact win condition.
- **The operating model:** the core decision framework, in principle and in real-time (how a pick is actually made).
- **Backtested findings that are load-bearing:** the markers that separate winners from the field, each with its evidence from Part 1.
- **Discarded philosophies / things to avoid:** each rejected approach and the reason it was rejected. This section prevents drift.
- **Edge-source roles:** what each edge source is, when available, and how it refines (never overrides) the model. Stub any not yet characterized.
- **Open questions / next builds:** what's unresolved and what data is pending.

---

### Output format
Emit Document A as a single structured Markdown file with the three parts as top-level sections and each season's almanac record as its own subsection. Lead with a one-paragraph "state of knowledge" summary and a data-inventory table (source × season × have/gap). Keep the live strategy at the top of Part 3 so it's actionable at a glance; the almanac's depth sits below for retrieval.

### Self-check before returning
- Did you correctly identify the season structure (one-per-year vs. parallel per-event), and for per-event contests produce isolated per-event records PLUS a year roll-up — with no per-event data conflated across sibling events?
- Did every season record either carry sourced data or an explicit `[GAP]`? (No silent blanks, no back-fill.)
- Are almanac data and preflight methodology in separate parts, not blended?
- Is every discarded philosophy preserved with its reason?
- Are model pre-draft outputs distinguished from raw inputs, so the backtest can measure the model?
- Did you retrieve actual conversation history and open actual files, rather than working from memory summaries alone?

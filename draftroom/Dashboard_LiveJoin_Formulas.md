# Dashboard (A+B join) — rebuild spec (raw columns · identical headers · VLOOKUP+MATCH)

Supersedes the ARRAYFORMULA / positional-reference versions. The join now (1) surfaces **raw**
Layer A and Layer B columns with **byte-identical header names** to their source tabs — no renamed
or composed join columns — so a mismatch can't hide, and (2) uses per-row **VLOOKUP + MATCH** keyed
on team name, so row order never matters. Conference truth comes from `Master_Lookup`.

## Why (the failure this fixes)
Positional refs (`='Layer A'!B4`) + renamed headers (`Mkt` vs `Mkt O/U`) let Notre Dame render as
AAC and swap its win total with South Florida — invisibly. Rule now: **join header == source header**,
lookup by **name**, conference from a **sourced** master table.

## Universal formula (the only pattern used)
Per row, filled down. NO ARRAYFORMULA. `X$1` is the join column's own header, which equals the
source header, so `MATCH` finds the right column dynamically even if the source is reordered:
```
=VLOOKUP($A2, <SOURCE>!$A:$Z, MATCH(X$1, <SOURCE>!$1:$1, 0), 0)
```
Fill each column's row-2 formula down to the last team. When teams are added, extend the fill range
(there is no ARRAYFORMULA auto-spill — accepted trade-off). `_LASTROW` = last populated team row.

## Column layout — 24 columns, each header identical to its source

| Col | Header (VERBATIM) | Source tab | Notes |
|---|---|---|---|
| A | `Team` | Layer A | spine (see A2 below) |
| B | `Pool Conf` | Layer A col O | Layer A sources it from `Master_Lookup` |
| C | `Real Conf` | `Master_Lookup` | replaces the retired SWITCH |
| D | `Mkt O/U` | Layer A | |
| E | `SP+ Rk` | Layer A | |
| F | `SP+ Rtg` | Layer A | |
| G | `RetProd%` | Layer A | |
| H | `TARP net` | Layer A | |
| I | `Collin Proj` | Layer A | |
| J | `Proj−Mkt` | Layer A | `−` is U+2212, not a hyphen |
| K | `QB status` | Layer B | |
| L | `New HC` | Layer B | raw — HTML composes "Coaching" |
| M | `New OC` | Layer B | raw |
| N | `New DC` | Layer B | raw |
| O | `Host Lean` | Layer B | |
| P | `Dark Horse` | Layer B | raw Y/blank — HTML composes "Flags" |
| Q | `Fade` | Layer B | raw Y/blank |
| R | `Split` | Layer B | raw Y/blank |
| S | `Variance` | Layer B | raw Y/blank |
| T | `Sched Tag` | Layer B | |
| U | `Key Avoids/Draws` | Layer B | |
| V | `Key Injury` | Layer B | |
| W | `BBOC Notes` | Layer B | |
| X | `mkt_pod` | Layer B | pod-cited line; delta vs `Mkt O/U` is the signal |

Row 1 = these exact headers. Then:

**A2 — Team spine** (paste first; fill down)
```
=IF('Layer A — raw data (SOURCED)'!A2="","",'Layer A — raw data (SOURCED)'!A2)
```
**B2 — Pool Conf** (Layer A, which itself pulls Master)
```
=IF($A2="","",VLOOKUP($A2,'Layer A — raw data (SOURCED)'!$A:$Z,MATCH(B$1,'Layer A — raw data (SOURCED)'!$1:$1,0),0))
```
**C2 — Real Conf** (Master_Lookup)
```
=IF($A2="","",VLOOKUP($A2,Master_Lookup!$A:$C,MATCH(C$1,Master_Lookup!$A$1:$C$1,0),0))
```
**D2:J2 — Layer A columns** (same formula, copy across; MATCH auto-targets by header)
```
=IF($A2="","",VLOOKUP($A2,'Layer A — raw data (SOURCED)'!$A:$Z,MATCH(D$1,'Layer A — raw data (SOURCED)'!$1:$1,0),0))
```
**K2:X2 — Layer B columns** (same formula, copy across)
```
=IF($A2="","",VLOOKUP($A2,'Layer B — pod writeups'!$A:$Z,MATCH(K$1,'Layer B — pod writeups'!$1:$1,0),0))
```
Because `MATCH` reads each column's own header (`D$1`, `E$1`, … `X$1`), you paste ONE Layer A
formula in D2 and drag right through J2, and ONE Layer B formula in K2 and drag right through X2.
Then select D2:X2 and fill down to `_LASTROW`.

## Layer A — columns A–N pasted static; col O (Pool Conf) is the only formula
**Layer A cols A–N are a STATIC paste** of the repo-generated, normalized `LayerA_AN_YYYY.tsv`
(Team, Mkt O/U, SP+ Rk, SP+ Rtg, RetProd%, Ret Off%, Ret Def%, TARP net, TARP off, TARP def,
Collin Proj, Proj−Mkt, 6-Win%, SOS Rk) — **no formulas** in A–N. The team names there MUST be
Brad-canonical (`specs/Naming_Canon_2026.md`) or the col-O and join lookups miss (#N/A). Schedule
columns P→ are pasted from `layerA_schedule_columns_YYYY.csv`.

**Col O (`Pool Conf`) is the ONLY Layer A formula** — a per-row **VLOOKUP, filled down (NOT
ARRAYFORMULA)**. Cell **O2**:
```
=VLOOKUP($A2,Master_Lookup!$A:$C,MATCH(O$1,Master_Lookup!$A$1:$C$1,0),0)
```
`O1` must read exactly `Pool Conf`. (Real Conf is pulled straight from Master in the join; no need to
add it to Layer A.)

## Master_Lookup is a STATIC paste (decided 2026)
`Master_Lookup` (Team · Pool Conf · Real Conf) is pasted **static** from the repo-generated
`Master_Lookup_YYYY.tsv`. Normalization (spelling + `Big 10→Big Ten` + `zIndependents→Independent`)
happens upstream in repo code, so the sheet holds already-canonical values and cannot drift mid-draft.
A live-unpivot-from-the-Import-tabs version (FLATTEN/TOCOL/MAKEARRAY over the uneven conference grids)
was attempted and **abandoned** — brittle array behavior across Sheets versions, and it reintroduces
exactly the silent-drift risk this rebuild removed. Regenerate the TSV from the repo once a year.

## Critical: team-name spelling is the join key
Every tab that the join or the draftroom keys by team — **Layer A, Layer B, Master_Lookup, Import_*,
Import_BradTracker (picks), Draft_Order (roster)** — must use **Brad-canonical** spelling
(`EMU`, `Florida Intl`, `Miami`, `Miami-OH`, `San José State`, `Southern Mississippi`, `UL Lafayette`,
`UL Monroe`, `UMASS`) and the **system conf token** `Big Ten` (not `Big 10`). A single mismatch →
that column returns blank for that team. The repo's `data_2026.json` + schedule files were normalized
2026-08 for exactly this reason.

## Verify after building
- Notre Dame: Pool Conf `CUSA`, Real Conf `Independent`, `Mkt O/U` `11.5`.
- South Florida: `Mkt O/U` `8.5`.
- Edit any Layer B cell → the join row changes (confirms live, name-keyed, not static).
- `#N/A` in a column → the header text in row 1 doesn't byte-match the source header (check `−` vs `-`, `%`, spacing).

## HTML contract (draftroom)
The draftroom reads these exact Dashboard headers; Layer B fields are read from the `Layer B` tab by
the same names. `Coaching` and `Flags` no longer exist as join columns — the HTML composes them from
`New HC`/`New OC`/`New DC` and `Dark Horse`/`Fade`/`Split`/`Variance`.

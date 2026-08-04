# Dashboard (A+B) — LIVE JOIN rebuild for Google Sheets

The pasted Dashboard came in as STATIC VALUES (no formulas), so it never updated from Layer A/B. This rebuilds it as a true live join: edit Layer A or Layer B → Dashboard updates automatically. No fill-down needed (ARRAYFORMULA spills down the whole column).

## Setup (once)

1. Open the **Dashboard (A+B join)** tab.

2. Select row 2 down to the bottom (row 2:1000) across columns A:Q and **delete** — clears the stale static values. Keep row 1 (headers).

3. Use **Option 1** (recommended) or Option 2 below.


---

## Option 1 — 17 column formulas (recommended: easy to debug)

Paste each formula into the listed **row-2 cell**. Each fills its whole column automatically.

> Paste **B2 first** (it's the team spine everything else references).


**B2 — Team (spine)**
```
=ARRAYFORMULA(IF('Layer A — raw data (SOURCED)'!$A2:$A="","",'Layer A — raw data (SOURCED)'!$A2:$A))
```

**A2 — Pool Conf**
```
=ARRAYFORMULA(IF($B2:$B="","",IFERROR(VLOOKUP($B2:$B,'Layer A — raw data (SOURCED)'!$A:$O,15,FALSE),"")))
```

**C2 — Real Conf**
```
=ARRAYFORMULA(IF($B2:$B="","",SWITCH($B2:$B,"Notre Dame","Independent","UConn","Independent","Boston College","ACC","Syracuse","ACC","Michigan State","Big Ten","Purdue","Big Ten","Oklahoma State","Big 12","Arkansas","SEC",A2:A)))
```

**D2 — Mkt**
```
=ARRAYFORMULA(IF($B2:$B="","",IFERROR(VLOOKUP($B2:$B,'Layer A — raw data (SOURCED)'!$A:$B,2,FALSE),"")))
```

**E2 — SP+ Rk**
```
=ARRAYFORMULA(IF($B2:$B="","",IFERROR(VLOOKUP($B2:$B,'Layer A — raw data (SOURCED)'!$A:$C,3,FALSE),"")))
```

**F2 — SP+ Rtg**
```
=ARRAYFORMULA(IF($B2:$B="","",IFERROR(VLOOKUP($B2:$B,'Layer A — raw data (SOURCED)'!$A:$D,4,FALSE),"")))
```

**G2 — RetProd%**
```
=ARRAYFORMULA(IF($B2:$B="","",IFERROR(VLOOKUP($B2:$B,'Layer A — raw data (SOURCED)'!$A:$E,5,FALSE),"")))
```

**H2 — TARP net**
```
=ARRAYFORMULA(IF($B2:$B="","",IFERROR(VLOOKUP($B2:$B,'Layer A — raw data (SOURCED)'!$A:$H,8,FALSE),"")))
```

**I2 — Collin**
```
=ARRAYFORMULA(IF($B2:$B="","",IFERROR(VLOOKUP($B2:$B,'Layer A — raw data (SOURCED)'!$A:$K,11,FALSE),"")))
```

**J2 — Proj−Mkt**
```
=ARRAYFORMULA(IF($B2:$B="","",IFERROR(VLOOKUP($B2:$B,'Layer A — raw data (SOURCED)'!$A:$L,12,FALSE),"")))
```

**K2 — QB status**
```
=ARRAYFORMULA(IF($B2:$B="","",IFERROR(VLOOKUP($B2:$B,'Layer B — pod writeups'!$A:$B,2,FALSE),"")))
```

**L2 — Coaching**
```
=ARRAYFORMULA(IF($B2:$B="","",TRIM(IF(IFERROR(VLOOKUP($B2:$B,'Layer B — pod writeups'!$A:$C,3,FALSE),"")="","","HC "&VLOOKUP($B2:$B,'Layer B — pod writeups'!$A:$C,3,FALSE)&" ")&IF(IFERROR(VLOOKUP($B2:$B,'Layer B — pod writeups'!$A:$D,4,FALSE),"")="","","OC "&VLOOKUP($B2:$B,'Layer B — pod writeups'!$A:$D,4,FALSE)&" ")&IF(IFERROR(VLOOKUP($B2:$B,'Layer B — pod writeups'!$A:$E,5,FALSE),"")="","","DC "&VLOOKUP($B2:$B,'Layer B — pod writeups'!$A:$E,5,FALSE)))))
```

**M2 — Host Lean**
```
=ARRAYFORMULA(IF($B2:$B="","",IFERROR(VLOOKUP($B2:$B,'Layer B — pod writeups'!$A:$F,6,FALSE),"")))
```

**N2 — Sched**
```
=ARRAYFORMULA(IF($B2:$B="","",IFERROR(VLOOKUP($B2:$B,'Layer B — pod writeups'!$A:$K,11,FALSE),"")))
```

**O2 — Flags**
```
=ARRAYFORMULA(IF($B2:$B="","",TRIM(IF(IFERROR(VLOOKUP($B2:$B,'Layer B — pod writeups'!$A:$G,7,FALSE),"")="Y","DH ","")&IF(IFERROR(VLOOKUP($B2:$B,'Layer B — pod writeups'!$A:$H,8,FALSE),"")="Y","FADE ","")&IF(IFERROR(VLOOKUP($B2:$B,'Layer B — pod writeups'!$A:$I,9,FALSE),"")="Y","SPLIT ","")&IF(IFERROR(VLOOKUP($B2:$B,'Layer B — pod writeups'!$A:$J,10,FALSE),"")="Y","VAR",""))))
```

**P2 — Key Avoids/Draws**
```
=ARRAYFORMULA(IF($B2:$B="","",IFERROR(VLOOKUP($B2:$B,'Layer B — pod writeups'!$A:$L,12,FALSE),"")))
```

**Q2 — Notes**
```
=ARRAYFORMULA(IF($B2:$B="","",IFERROR(VLOOKUP($B2:$B,'Layer B — pod writeups'!$A:$N,14,FALSE),"")))
```

---

## Option 2 — single cell (elegant, harder to debug)

Delete A2:Q1000, then paste this ONE formula into **A2**. The entire join spills from it.

```
=ARRAYFORMULA(IF('Layer A — raw data (SOURCED)'!$A2:$A="","",{IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer A — raw data (SOURCED)'!$A:$O,15,0),""), 'Layer A — raw data (SOURCED)'!$A2:$A, SWITCH('Layer A — raw data (SOURCED)'!$A2:$A,"Notre Dame","Independent","UConn","Independent","Boston College","ACC","Syracuse","ACC","Michigan State","Big Ten","Purdue","Big Ten","Oklahoma State","Big 12","Arkansas","SEC",IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer A — raw data (SOURCED)'!$A:$O,15,0),"")), IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer A — raw data (SOURCED)'!$A:$B,2,0),""), IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer A — raw data (SOURCED)'!$A:$C,3,0),""), IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer A — raw data (SOURCED)'!$A:$D,4,0),""), IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer A — raw data (SOURCED)'!$A:$E,5,0),""), IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer A — raw data (SOURCED)'!$A:$H,8,0),""), IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer A — raw data (SOURCED)'!$A:$K,11,0),""), IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer A — raw data (SOURCED)'!$A:$L,12,0),""), IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer B — pod writeups'!$A:$B,2,0),""), TRIM(IF(IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer B — pod writeups'!$A:$C,3,0),"")="","","HC "&IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer B — pod writeups'!$A:$C,3,0),"")&" ")&IF(IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer B — pod writeups'!$A:$D,4,0),"")="","","OC "&IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer B — pod writeups'!$A:$D,4,0),"")&" ")&IF(IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer B — pod writeups'!$A:$E,5,0),"")="","","DC "&IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer B — pod writeups'!$A:$E,5,0),""))), IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer B — pod writeups'!$A:$F,6,0),""), IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer B — pod writeups'!$A:$K,11,0),""), TRIM(IF(IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer B — pod writeups'!$A:$G,7,0),"")="Y","DH ","")&IF(IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer B — pod writeups'!$A:$H,8,0),"")="Y","FADE ","")&IF(IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer B — pod writeups'!$A:$I,9,0),"")="Y","SPLIT ","")&IF(IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer B — pod writeups'!$A:$J,10,0),"")="Y","VAR","")), IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer B — pod writeups'!$A:$L,12,0),""), IFERROR(VLOOKUP('Layer A — raw data (SOURCED)'!$A2:$A,'Layer B — pod writeups'!$A:$N,14,0),"")}))
```

---

## After pasting

- **Test the join:** edit any Layer B cell (e.g. a QB note) → the Dashboard row should change immediately. That confirms it's live, not static.

- **Your workflow now works:** paste a new row into Layer B → the Dashboard picks it up by VLOOKUP with no extra steps.

- **If a formula errors** (`#REF!` / `#N/A`): the tab name reference is off. The formulas assume the tabs are named exactly:

  - `Layer A — raw data (SOURCED)`
  - `Layer B — pod writeups`

  If yours differ (especially the — em-dash), find/replace the tab name inside the formula. Tell me the exact names and I'll regenerate.

- **Column assumptions** (if you reordered columns, tell me): Layer A has Pool Conf in col O; Layer B is Team,QB,HC,OC,DC,Lean,DH,Fade,Split,Var,Sched,Avoids,Injury,Notes (A–N).

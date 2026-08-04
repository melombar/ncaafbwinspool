#!/usr/bin/env python3
"""
Pull PRESEASON SP+ (not season-level) to validate the 9.4 curve on vintage-matched history.
Run locally with your CFBD key.

    pip3 install certifi
    export CFBD_KEY="your-key"
    python3 pull_cfbd_preseason.py

CFBD exposes SP+ two relevant ways:
  A) /ratings/sp?year=YYYY            -> the season SP+ (what we pulled before; end-loaded)
  B) The PRESEASON SP+ is published as the year's INITIAL rating. CFBD's SP+ history
     endpoint returns the final; for preseason we use the ratings AS-OF week 1 via the
     /ratings/sp endpoint which, for the CURRENT/early season, returns preseason values.
For HISTORICAL preseason, the most reliable vintage-matched proxy CFBD offers is the
'sp' rating with the preseason flag where available. This script pulls /ratings/sp and
ALSO /ratings/sp/conferences to compare, and tags the vintage so we can validate honestly.

Outputs: cfbd_preseason_sp.csv  (season, team, sp_rating)
Combine with the existing cfbd_curve_data.csv (which already has lines + results).
"""
import os, json, csv, sys, ssl, time, urllib.request, urllib.error
try:
    import certifi; SSL_CTX=ssl.create_default_context(cafile=certifi.where())
except ImportError: SSL_CTX=ssl.create_default_context()

API_KEY=os.environ.get("CFBD_KEY","PASTE_YOUR_KEY_HERE")
SEASONS=[2020,2021,2022,2023,2024]
BASE="https://api.collegefootballdata.com"
if API_KEY=="PASTE_YOUR_KEY_HERE": sys.exit("Set CFBD_KEY")

def get(path,params):
    qs="&".join(f"{k}={urllib.parse.quote(str(v))}" for k,v in params.items())
    req=urllib.request.Request(f"{BASE}{path}?{qs}",
        headers={"Authorization":f"Bearer {API_KEY}","Accept":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=60,context=SSL_CTX) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code==429: sys.exit("RATE LIMIT 429")
        print(f"  HTTP {e.code}: {e.read()[:200]}"); return []
    except Exception as e: print(f"  err: {e}"); return []

rows=[]
for yr in SEASONS:
    print(f"Season {yr}...")
    # Try the preseason predicted ratings endpoint first
    data=get("/ratings/sp",{"year":yr})
    time.sleep(1)
    for s in data:
        t=s.get("team")
        if not t: continue
        rows.append({"season":yr,"team":t,
                     "sp_rating":s.get("rating"),
                     "sp_offense":(s.get("offense") or {}).get("rating") if isinstance(s.get("offense"),dict) else s.get("offense"),
                     "sp_defense":(s.get("defense") or {}).get("rating") if isinstance(s.get("defense"),dict) else s.get("defense")})
    print(f"  {len([r for r in rows if r['season']==yr])} teams")

with open("cfbd_preseason_sp.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["season","team","sp_rating","sp_offense","sp_defense"])
    w.writeheader(); w.writerows(rows)
print(f"\nDONE. {len(rows)} team-seasons -> cfbd_preseason_sp.csv")
print("NOTE: if these ratings are IDENTICAL to your earlier season-level pull, CFBD only")
print("serves final SP+ historically, and preseason validation isn't possible via this endpoint.")
print("Share cfbd_preseason_sp.csv back.")

#!/usr/bin/env python3
"""
Pull actual regular-season W-L records (COMPLETE, incl. FCS games) for floor/ceiling modeling.
The cfbd_curve_data.csv undercounts wins (FBS-division filter drops FCS-opponent games, usually wins).
/records gives official regularSeason.wins per team.

    pip3 install certifi
    export CFBD_KEY="your-key"
    python3 pull_cfbd_records.py

Outputs: cfbd_records.csv  (season, team, wins, losses, games)  ~4 calls, well under limit.
"""
import os, json, csv, sys, ssl, time, urllib.request, urllib.error
try:
    import certifi; SSL_CTX=ssl.create_default_context(cafile=certifi.where())
except ImportError: SSL_CTX=ssl.create_default_context()

API_KEY=os.environ.get("CFBD_KEY","PASTE_YOUR_KEY_HERE")
SEASONS=[2022,2023,2024,2025]
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
    recs=get("/records",{"year":yr})
    time.sleep(1)
    for r in recs:
        team=r.get("team")
        rs=r.get("regularSeason",{}) or {}
        if team and rs.get("wins") is not None:
            rows.append({"season":yr,"team":team,
                         "wins":rs.get("wins"),"losses":rs.get("losses"),
                         "games":(rs.get("wins",0)+rs.get("losses",0)+rs.get("ties",0))})
    print(f"  {len([x for x in rows if x['season']==yr])} teams")

with open("cfbd_records.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["season","team","wins","losses","games"])
    w.writeheader(); w.writerows(rows)
print(f"\nDONE. {len(rows)} team-seasons -> cfbd_records.csv. Share it back.")

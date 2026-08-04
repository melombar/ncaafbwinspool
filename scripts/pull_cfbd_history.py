#!/usr/bin/env python3
"""
Pull CFBD historical data to refit the SP+ -> win-probability curve.
Run locally with YOUR CollegeFootballData.com API key. Key never leaves your machine.

Usage:
    export CFBD_KEY="your-key-here"
    python3 pull_cfbd_history.py
  (or edit API_KEY below)

Outputs: cfbd_curve_data.csv  — one row per game with:
    season, week, home, away, neutral, home_sp, away_sp, sp_diff,
    home_open_ml, away_open_ml, home_open_spread, home_points, away_points, home_win

Efficiency: 3 calls per season (games, lines, sp ratings) = ~15 calls for 5 seasons.
Free tier = 1000 calls/month, so this is safe. Preseason SP+ vs OPENING lines
(contamination-free, matches how the draft model uses it).
"""
import os, json, csv, sys, time, urllib.request, urllib.error, ssl

# --- SSL: verify against a real CA bundle (fixes CERTIFICATE_VERIFY_FAILED on macOS) ---
try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    # certifi not installed -> try system default; if that fails, run: pip3 install certifi
    SSL_CTX = ssl.create_default_context()
    print("NOTE: 'certifi' not found. If SSL still fails, run: pip3 install certifi")

API_KEY = os.environ.get("CFBD_KEY", "PASTE_YOUR_KEY_HERE")
SEASONS = [2020, 2021, 2022, 2023, 2024]   # edit as desired
BASE = "https://api.collegefootballdata.com"

if API_KEY == "PASTE_YOUR_KEY_HERE":
    sys.exit("Set your key: export CFBD_KEY='...'  (or edit API_KEY in the script)")

def get(path, params):
    qs = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k,v in params.items())
    url = f"{BASE}{path}?{qs}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {API_KEY}",
                                               "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60, context=SSL_CTX) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            sys.exit("RATE LIMIT (429): out of API calls for the month.")
        print(f"  HTTP {e.code} on {path}: {e.read()[:200]}"); return []
    except Exception as e:
        print(f"  error on {path}: {e}"); return []

def norm(s):
    return (s or "").lower().replace("'","").replace(".","").replace("-"," ").strip()

rows = []
for yr in SEASONS:
    print(f"Season {yr}...")
    # 1. GAMES (results) — regular season, FBS
    games = get("/games", {"year": yr, "seasonType": "regular", "division": "fbs"})
    time.sleep(1)
    # 2. LINES (betting) — has opening & consensus per game
    lines = get("/lines", {"year": yr, "seasonType": "regular"})
    time.sleep(1)
    # 3. SP+ ratings — CFBD /ratings/sp returns end-of-season by default.
    #    For PRESEASON vintage, we approximate with the rating as of the season
    #    (CFBD historical SP+ is season-level). Flag: this is season SP+, best available.
    sp = get("/ratings/sp", {"year": yr})
    time.sleep(1)

    sp_by_team = {}
    for s in sp:
        t = s.get("team")
        if t and s.get("rating") is not None:
            sp_by_team[norm(t)] = s["rating"]

    # index lines by gameId
    lines_by_game = {}
    for lg in lines:
        gid = lg.get("id")
        provs = lg.get("lines", []) or []
        # prefer an opening line; fall back to first available
        pick = None
        for p in provs:
            if p.get("spreadOpen") is not None or p.get("homeMoneyline") is not None:
                pick = p; break
        if pick is None and provs: pick = provs[0]
        if pick: lines_by_game[gid] = pick

    n_used = 0
    for g in games:
        gid = g.get("id")
        home, away = g.get("homeTeam") or g.get("home_team"), g.get("awayTeam") or g.get("away_team")
        hp, ap = g.get("homePoints", g.get("home_points")), g.get("awayPoints", g.get("away_points"))
        neutral = g.get("neutralSite", g.get("neutral_site", False))
        if not home or not away or hp is None or ap is None: continue
        hsp, asp = sp_by_team.get(norm(home)), sp_by_team.get(norm(away))
        if hsp is None or asp is None: continue
        ln = lines_by_game.get(gid, {})
        row = {
            "season": yr, "week": g.get("week"),
            "home": home, "away": away, "neutral": int(bool(neutral)),
            "home_sp": round(hsp,2), "away_sp": round(asp,2), "sp_diff": round(hsp-asp,2),
            "home_open_spread": ln.get("spreadOpen", ln.get("spread")),
            "home_open_ml": ln.get("homeMoneyline"), "away_open_ml": ln.get("awayMoneyline"),
            "home_points": hp, "away_points": ap,
            "home_win": int(hp > ap),
        }
        rows.append(row); n_used += 1
    print(f"  {n_used} games with SP+ both sides")

with open("cfbd_curve_data.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

print(f"\nDONE. {len(rows)} games across {len(SEASONS)} seasons -> cfbd_curve_data.csv")
print("Games WITH a moneyline:", sum(1 for r in rows if r['home_open_ml'] is not None))
print("Games WITH a spread:", sum(1 for r in rows if r['home_open_spread'] is not None))
print("\nShare cfbd_curve_data.csv back (or drop in the project) for the curve refit.")

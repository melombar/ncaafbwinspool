#!/usr/bin/env python3
"""
Predictor-accuracy backtest — how well does each PRESEASON predictor forecast
ACTUAL regular-season wins (CCG stripped, bowls/playoff excluded)?

Governed by Prediction_Model_Spec.md + Pre_Pick_Doctrine.md + backtest #22.
Ground truth = CFBD regular-season wins MINUS conference-championship-game wins.

WHY CFBD IS PULLED HERE:
  data/records/cfbd_records.csv holds CFBD `regularSeason.wins`, which INCLUDES the
  CCG (Georgia 2022 = 13 = 12 reg + SEC CCG). The brief wants CCGs excluded. There is
  no CCG flag in the csv, so we pull the CFBD /games endpoint (seasonType=postseason),
  detect the conference-title games (both teams same conference), and dock the WINNER
  -1. That is a real lookup, not imputation.

USAGE:
    export CFBD_KEY="your-key"
    python3 scripts/backtest_predictors.py            # pulls CFBD, writes results
    python3 scripts/backtest_predictors.py --offline  # skip CFBD (pipeline check only;
                                                       # CCG NOT stripped -> NOT the final numbers)

Run from the repo root. Outputs:
    build/backtest_predictors_2022_2025.json   (all metrics)
    build/ccg_winners_2022_2025.json           (the detected CCG winners, for audit)
  and prints the summary table.

Dependency: numpy (standard). `pip3 install numpy certifi` if missing.
"""
import os, sys, json, csv, ssl, time, math, urllib.request, urllib.parse, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)

SEASONS = [2022, 2023, 2024, 2025]
OFFLINE = '--offline' in sys.argv

try:
    import numpy as np
except ImportError:
    sys.exit("numpy required: pip3 install numpy")

try:
    import certifi; SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()

# ---- predictor pool-name -> CFBD/records name -------------------------------
ALIAS = {
    'Appalachian State': 'App State', 'FIU': 'Florida International',
    'Hawaii': "Hawai'i", 'Miami FL': 'Miami', 'Miami OH': 'Miami (OH)',
    'San Jose State': 'San José State', 'ULM': 'UL Monroe',
    'UMass': 'Massachusetts', 'Missouri St.': 'Missouri State',
}
def rn(pool_name):  # -> records/CFBD canonical name
    return ALIAS.get(pool_name, pool_name)

# ---- CFBD -------------------------------------------------------------------
def cfbd_get(path, params):
    key = os.environ.get("CFBD_KEY")
    if not key:
        sys.exit("Set CFBD_KEY (export CFBD_KEY=...), or run with --offline for a pipeline check.")
    qs = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
    req = urllib.request.Request(f"https://api.collegefootballdata.com{path}?{qs}",
        headers={"Authorization": f"Bearer {key}", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60, context=SSL_CTX) as r:
        return json.load(r)

def ccg_winners_for(year):
    """Detect conference-championship-game winners = postseason games whose two
    teams share a conference. Returns {records_team_name: 1}. Prints each for audit."""
    games = cfbd_get("/games", {"year": year, "seasonType": "postseason"})
    time.sleep(1)
    winners = {}
    detected = []
    for g in games:
        hc, ac = g.get("home_conference"), g.get("away_conference")
        ht, at = g.get("home_team"), g.get("away_team")
        hp, ap = g.get("home_points"), g.get("away_points")
        if hc and ac and hc == ac and hp is not None and ap is not None:
            win = ht if hp > ap else at
            winners[win] = 1
            detected.append({"conf": hc, "winner": win, "loser": at if win == ht else ht,
                             "score": f"{hp}-{ap}", "week": g.get("week")})
    print(f"  {year}: detected {len(detected)} CCGs:")
    for d in sorted(detected, key=lambda x: x["conf"]):
        print(f"     {d['conf']:<20} {d['winner']}  (beat {d['loser']} {d['score']})")
    return winners, detected

# ---- load repo predictors + base wins ---------------------------------------
def load_base_wins():
    rows = list(csv.DictReader(open(P('data', 'records', 'cfbd_records.csv'))))
    w = {}
    for x in rows:
        w.setdefault(x['season'], {})[x['team']] = int(x['wins'])  # regularSeason incl CCG
    return w

def load_market():
    m = json.load(open(P('data', 'market_totals', 'sbd_preseason_2018_2025.json')))
    return {y: {rn(t): float(v) for t, v in m.get(str(y), {}).items()} for y in SEASONS}

def load_sp():
    sp = json.load(open(P('data', 'sp_plus', 'sp_final_preseason_hist.json')))['ratings']
    def rating(v):  # entries are dicts {sp_final, avgw, ...}; use the raw rating only
        return float(v['sp_final']) if isinstance(v, dict) else float(v)
    return {y: {rn(t): rating(v) for t, v in sp.get(str(y), {}).items()
                if (not isinstance(v, dict)) or v.get('sp_final') is not None}
            for y in SEASONS}

def load_edge_2025():
    e = json.load(open(P('data', 'edge', 'edge2025.json')))['teams']
    collin = {rn(t): float(v['collin']) for t, v in e.items() if v.get('collin') is not None}
    tarp = {rn(t): float(v['net_tarp']) for t, v in e.items() if v.get('net_tarp') is not None}
    return collin, tarp

# ---- metrics ----------------------------------------------------------------
def mae_rmse(pred, actual, keys):
    r = [pred[k] - actual[k] for k in keys]
    n = len(r)
    mae = sum(abs(x) for x in r) / n
    rmse = math.sqrt(sum(x * x for x in r) / n)
    return {"n": n, "mae": round(mae, 3), "rmse": round(rmse, 3),
            "bias": round(sum(r) / n, 3)}  # bias = mean(pred-actual)

def ols_fit(X, y):
    X = np.asarray(X, float); y = np.asarray(y, float)
    X1 = np.column_stack([np.ones(len(X)), X])
    beta, *_ = np.linalg.lstsq(X1, y, rcond=None)
    return beta  # [intercept, coef...]

def ols_pred(beta, X):
    X = np.asarray(X, float)
    return beta[0] + X @ np.asarray(beta[1:], float)

def loyo_regression(feature_maps, actual, label):
    """Leave-one-year-out OLS of actual ~ features. feature_maps: list of {year:{team:val}}.
    Returns per-year OOS metrics + pooled, computed on teams present in ALL feature maps
    and actual for that year. OOS = fit on other years, predict held-out year."""
    per_year = {}
    pooled_res = []
    for test in SEASONS:
        train_years = [y for y in SEASONS if y != test]
        # build training rows
        def rows_for(y):
            keys = set(actual.get(y, {}))
            for fm in feature_maps: keys &= set(fm.get(y, {}))
            keys = sorted(keys)
            X = [[fm[y][k] for fm in feature_maps] for k in keys]
            yv = [actual[y][k] for k in keys]
            return keys, X, yv
        Xtr, ytr = [], []
        for y in train_years:
            _, X, yv = rows_for(y)
            Xtr += X; ytr += yv
        if len(Xtr) < len(feature_maps) + 2:
            continue
        beta = ols_fit(Xtr, ytr)
        keys, Xte, yte = rows_for(test)
        if not keys:
            continue
        preds = ols_pred(beta, Xte)
        res = [float(preds[i] - yte[i]) for i in range(len(keys))]
        n = len(res)
        per_year[str(test)] = {"n": n,
            "mae": round(sum(abs(x) for x in res) / n, 3),
            "rmse": round(math.sqrt(sum(x * x for x in res) / n), 3),
            "bias": round(sum(res) / n, 3),
            "beta": [round(float(b), 4) for b in beta]}
        pooled_res += res
    n = len(pooled_res)
    pooled = {"n": n, "mae": round(sum(abs(x) for x in pooled_res) / n, 3),
              "rmse": round(math.sqrt(sum(x * x for x in pooled_res) / n), 3),
              "bias": round(sum(pooled_res) / n, 3)}
    return {"label": label, "per_year": per_year, "pooled": pooled}

def pearson(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3: return None
    return round(float(np.corrcoef(a, b)[0, 1]), 3)

# ---- main -------------------------------------------------------------------
def main():
    base = load_base_wins()
    market = load_market()
    sp = load_sp()
    collin, tarp = load_edge_2025()

    # --- clean actuals: base regularSeason wins minus CCG win ---
    print("Building CCG-stripped actuals" + (" [OFFLINE: CCG NOT stripped]" if OFFLINE else ""))
    ccg_all = {}
    actual = {}
    for y in SEASONS:
        winners = {}
        if not OFFLINE:
            winners, det = ccg_winners_for(y)
            ccg_all[str(y)] = det
        actual[y] = {t: base[str(y)][t] - (1 if t in winners else 0)
                     for t in base[str(y)]}

    results = {"meta": {
        "objective": "MAE/RMSE of each preseason predictor vs actual regular-season wins (CCG stripped)",
        "ground_truth": "CFBD regularSeason.wins minus conference-championship-game win",
        "offline_ccg_not_stripped": OFFLINE,
        "seasons": SEASONS,
        "coverage_note": "market 2023/24 P4-heavy (~69 teams); Collin/TARP 2025 only; 2022/23 TARP unrecoverable (excluded).",
    }, "market": {"per_year": {}, "note": "raw market total as the prediction (blind forecast, no fit)"}}

    # --- 1. MARKET raw (blind) ---
    mkt_pooled = []
    for y in SEASONS:
        keys = sorted(set(market[y]) & set(actual[y]))
        results["market"]["per_year"][str(y)] = mae_rmse(market[y], actual[y], keys)
        mkt_pooled += [market[y][k] - actual[y][k] for k in keys]
    n = len(mkt_pooled)
    results["market"]["pooled"] = {"n": n,
        "mae": round(sum(abs(x) for x in mkt_pooled) / n, 3),
        "rmse": round(math.sqrt(sum(x * x for x in mkt_pooled) / n), 3),
        "bias": round(sum(mkt_pooled) / n, 3)}

    # --- 2. SP+ standalone via LOYO regression (no fixed curve) ---
    results["sp_plus_loyo"] = loyo_regression([sp], actual,
        "SP+ rating -> wins, leave-one-year-out OLS (empirical slope, NOT a fixed curve)")

    # --- 3. Does a signal ADD value over market? apples-to-apples LOYO on shared teams ---
    # market-fit (actual~market) vs market+sp (actual~market+sp), same intersection.
    results["market_fit_loyo"] = loyo_regression([market], actual, "actual ~ market (LOYO)")
    results["market_plus_sp_loyo"] = loyo_regression([market, sp], actual, "actual ~ market + SP+ (LOYO)")

    # --- 4. Collin (2025 only) ---
    y = 2025
    ck = sorted(set(collin) & set(actual[y]) & set(market[y]))
    results["collin_2025"] = {
        "collin_alone": mae_rmse(collin, actual[y], ck),
        "market_same_teams": mae_rmse(market[y], actual[y], ck),
        "corr_collin_vs_market_residual": pearson(
            [collin[k] for k in ck], [actual[y][k] - market[y][k] for k in ck]),
        "note": "single year (2025) -> high variance, not multi-year evidence (decay + year-partition).",
    }

    # --- 5. TARP (2025 only) — not in win units; test vs market residual ---
    tk = sorted(set(tarp) & set(actual[y]) & set(market[y]))
    results["tarp_2025"] = {
        "corr_net_tarp_vs_market_residual": pearson(
            [tarp[k] for k in tk], [actual[y][k] - market[y][k] for k in tk]),
        "n": len(tk),
        "note": "net_tarp is a +/- adjustment, not a wins forecast; a ~0 corr = adds nothing to market. Single year.",
    }

    # --- write + print ---
    os.makedirs(P('build'), exist_ok=True)
    json.dump(results, open(P('build', 'backtest_predictors_2022_2025.json'), 'w'), indent=1)
    if not OFFLINE:
        json.dump(ccg_all, open(P('build', 'ccg_winners_2022_2025.json'), 'w'), indent=1)

    def line(lbl, d): print(f"  {lbl:<34} n={d['n']:<4} MAE={d['mae']:<6} RMSE={d['rmse']:<6} bias={d['bias']:+.2f}")
    print("\n===== PREDICTOR ACCURACY vs actual regular-season wins =====")
    print("MARKET (raw blind forecast):")
    for y in SEASONS: line(f"  {y}", results["market"]["per_year"][str(y)])
    line("  POOLED", results["market"]["pooled"])
    print("SP+ (LOYO regression, out-of-sample):")
    for y in SEASONS:
        if str(y) in results["sp_plus_loyo"]["per_year"]:
            line(f"  {y}", results["sp_plus_loyo"]["per_year"][str(y)])
    line("  POOLED", results["sp_plus_loyo"]["pooled"])
    print("ADD-VALUE TEST (same teams, LOYO OOS):")
    line("  market-fit", results["market_fit_loyo"]["pooled"])
    line("  market + SP+", results["market_plus_sp_loyo"]["pooled"])
    print("COLLIN 2025:")
    line("  collin alone", results["collin_2025"]["collin_alone"])
    line("  market (same teams)", results["collin_2025"]["market_same_teams"])
    print(f"  corr(collin, actual-market) = {results['collin_2025']['corr_collin_vs_market_residual']}")
    print(f"TARP 2025: corr(net_tarp, actual-market) = {results['tarp_2025']['corr_net_tarp_vs_market_residual']}  (n={results['tarp_2025']['n']})")
    print("\nWrote build/backtest_predictors_2022_2025.json" + ("" if OFFLINE else " + build/ccg_winners_2022_2025.json"))
    print("VERDICT RULE: if market-raw RMSE <= market+SP+ RMSE, SP+ adds no forecasting value over market.")

if __name__ == '__main__':
    main()

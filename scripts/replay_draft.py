#!/usr/bin/env python3
"""
Historical pool replay — would the replacement-value model have beaten our actual draft?
Option A (doctrine-pure): V(t) = sbd market total (level). Tier tilt is used ONLY to break
near-equal premiums (prefer fatter upside tail) and to report floor/ceiling. Governed by
Pre_Pick_Doctrine + backtest #22/#27.

Counterfactual: opponents' picks fixed to history. At each of OUR slots the model picks the
best replacement-premium team from teams our opponents did NOT take (undrafted ∪ our own
actual picks), respecting one-team-per-pool-conference. Scored by ACTUAL wins (cfbd_records,
regular season incl CCG — same source for every player, so ranking is internally fair).

Run from repo root:  python3 scripts/replay_draft.py
"""
import json, csv, math, openpyxl, unicodedata

SEASONS = [2022, 2023, 2024, 2025]  # clean cfbd actuals; sbd present
SBD = json.load(open('data/market_totals/sbd_preseason_2018_2025.json'))
BANDS = json.load(open('build/spread_bands.json'))['tiers']

def tilt(total):
    if total is None: return -0.51
    if total <= 4.5: return BANDS['le4.5']['mean']
    if total <= 6.5: return BANDS['5-6.5']['mean']
    if total <= 8.5: return BANDS['7-8.5']['mean']
    return BANDS['9+']['mean']

def norm(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode()
    return s.lower().replace('.', '').replace("'", '').replace('-', ' ').replace('  ', ' ').strip()

# DraftTracker / sbd pool name -> cfbd_records name (for actual wins)
TO_CFBD = {'appalachian state': 'App State', 'fiu': 'Florida International', 'hawaii': "Hawai'i",
    'miami fl': 'Miami', 'miami florida': 'Miami', 'miami oh': 'Miami (OH)', 'miami ohio': 'Miami (OH)',
    'san jose state': 'San José State', 'ulm': 'UL Monroe', 'ul monroe': 'UL Monroe',
    'ul lafayette': 'Louisiana', 'louisiana lafayette': 'Louisiana', 'umass': 'Massachusetts',
    'massachusetts': 'Massachusetts', 'southern miss': 'Southern Miss', 'southern mississippi': 'Southern Miss', 'emu': 'Eastern Michigan', 'wku': 'Western Kentucky', 'fau': 'Florida Atlantic'}
# DraftTracker pool name -> sbd key (sbd uses pool-canonical; a few differ)
TO_SBD_ALIAS = {'ul lafayette': 'Louisiana', 'louisiana lafayette': 'Louisiana',
    'miami florida': 'Miami FL', 'miami ohio': 'Miami OH', 'ul monroe': 'ULM'}

def load_actual_wins(year):
    rows = list(csv.DictReader(open('data/records/cfbd_records.csv')))
    return {r['team']: int(r['wins']) for r in rows if r['season'] == str(year)}

def load_tracker(year):
    wb = openpyxl.load_workbook(f'workbooks/NCAA_Wins_Pool_{year}.xlsx', read_only=True, data_only=True)
    ws = wb['DraftTracker']
    picks = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or row[3] is None or row[5] is None: continue
        picks.append({'player': str(row[3]).strip(), 'conf': str(row[4]).strip() if row[4] else '?',
                      'team': str(row[5]).strip()})
    wb.close()
    return picks

def load_conf_full(year):
    """Full pool team->conference map from the Teams-Conference sheet (cols A,B)."""
    wb = openpyxl.load_workbook(f'workbooks/NCAA_Wins_Pool_{year}.xlsx', read_only=True, data_only=True)
    cf = {}
    if 'Teams-Conference' in wb.sheetnames:
        for row in wb['Teams-Conference'].iter_rows(min_row=2, values_only=True):
            if row and row[0] and row[1] and len(str(row[1])) <= 14:
                cf.setdefault(str(row[0]).strip(), str(row[1]).strip())
    wb.close()
    return cf

def sbd_lookup(year, team):
    yb = SBD.get(str(year), {})
    if team in yb: return yb[team]
    n = norm(team)
    for k, v in yb.items():
        if norm(k) == n: return v
    a = TO_SBD_ALIAS.get(n)
    if a and a in yb: return yb[a]
    return None

def cfbd_lookup(wins, team):
    if team in wins: return wins[team]
    n = norm(team)
    a = TO_CFBD.get(n)
    if a and a in wins: return wins[a]
    for k, v in wins.items():
        if norm(k) == n: return v
    return None

def replay(year, us_name):
    picks = load_tracker(year)
    wins = load_actual_wins(year)
    players = []
    for p in picks:
        if p['player'] not in players: players.append(p['player'])
    us = [p for p in players if us_name.lower() in p.lower()]
    us = us[0] if us else None
    # rosters (actual)
    rosters = {pl: [pk['team'] for pk in picks if pk['player'] == pl] for pl in players}
    our_actual = rosters[us]
    n_slots = len(our_actual)

    # FULL pool conference map (Teams-Conference sheet, all teams incl undrafted)
    conf_of = load_conf_full(year)
    for pk in picks: conf_of.setdefault(pk['team'], pk['conf'])  # fallback from tracker

    # candidate universe = every team with an sbd value + a pool conference.
    # (Proj Log is NOT used to supplement: it fails the corruption gate — MAE-to-actual ~0.1-0.3.)
    candidates = {}
    for t, c in conf_of.items():
        v = sbd_lookup(year, t)
        if v is None: continue           # no market value -> unmodelable (P4-heavy sbd coverage gap)
        candidates[t] = {'V': v, 'conf': c, 'tilt': tilt(v)}

    # SEQUENTIAL replay in actual draft order. Opponents take their historical team; at OUR
    # slot the model picks best replacement-premium from teams still on the board (not yet taken),
    # in a conference we haven't used. Model's pick becomes unavailable to later picks.
    taken, used_conf, model_roster = set(), set(), []
    for pk in picks:
        if pk['player'] == us:
            avail = {t: d for t, d in candidates.items()
                     if t not in taken and t not in model_roster and d['conf'] not in used_conf}
            if not avail: continue
            byconf = {}
            for t, d in avail.items(): byconf.setdefault(d['conf'], []).append((t, d))
            best = None
            for c, lst in byconf.items():
                lst.sort(key=lambda x: -x[1]['V'])
                anchor, ad = lst[0]
                repl = lst[1][1]['V'] if len(lst) > 1 else 0.0
                cand = (ad['V'] - repl, ad['tilt'], ad['V'], anchor, c)
                if best is None or cand[:3] > best[:3]:  # premium, then tilt, then V
                    best = cand
            model_roster.append(best[3]); used_conf.add(best[4]); taken.add(best[3])
        else:
            taken.add(pk['team'])   # opponent's historical pick leaves the board

    def score(roster):
        tot, miss = 0, []
        for t in roster:
            w = cfbd_lookup(wins, t)
            if w is None: miss.append(t)
            else: tot += w
        return tot, miss

    model_tot, model_miss = score(model_roster)
    our_tot, our_miss = score(our_actual)
    # rank all players by cfbd-scored total (fair, same source); then slot the model total in
    totals = {pl: score(rosters[pl])[0] for pl in players}
    field = sorted(totals.values(), reverse=True)
    winner_tot = field[0]
    our_rank = sorted(totals, key=lambda p: -totals[p]).index(us) + 1
    # model finish: replace our total with model total, re-rank
    others = [totals[pl] for pl in players if pl != us]
    model_rank = 1 + sum(1 for x in others if x > model_tot)
    return {'year': year, 'us': us, 'n_players': len(players), 'n_slots': n_slots,
            'model_picks': len(model_roster),
            'our_total': our_tot, 'model_total': model_tot, 'winner_total': winner_tot,
            'our_rank': our_rank, 'model_rank': model_rank,
            'model_roster': model_roster, 'our_roster': our_actual,
            'model_beats_us': model_tot > our_tot, 'delta': model_tot - our_tot,
            'coverage': {'model_unscored': model_miss, 'our_unscored': our_miss,
                         'candidates': len(candidates), 'slots_filled': f"{len(model_roster)}/{n_slots}"}}

def main():
    US = {2018: 'Janice/Mike', 2019: 'Janice/Mike', 2021: 'Janice/Mike',
          2022: 'Janice/Mike', 2023: 'Janice/Mike', 2024: 'Mike', 2025: 'Mike'}
    results = []
    for y in SEASONS:
        results.append(replay(y, US[y]))
    # A season is a FAIR test only if the model could fill every slot we did (full sbd coverage).
    for r in results:
        r['fair'] = (r['model_picks'] == r['n_slots'])
    fair = [r for r in results if r['fair']]
    fair_wins = sum(1 for r in fair if r['model_beats_us'])
    print(f"{'YR':<6}{'fair?':>6}{'us_fin':>8}{'mdl_fin':>8}{'our_w':>7}{'mdl_w':>7}{'win':>6}{'slots':>7}{'Δ':>6}")
    for r in results:
        print(f"{r['year']:<6}{('YES' if r['fair'] else 'cov-lim'):>6}{r['our_rank']:>8}{r['model_rank']:>8}"
              f"{r['our_total']:>7}{r['model_total']:>7}{r['winner_total']:>6}{r['coverage']['slots_filled']:>7}{r['delta']:>+6}")
    print(f"\nFair (full-coverage) seasons: {len(fair)} of {len(results)}. Model beat us in {fair_wins}/{len(fair)} of them.")
    if not fair:
        print("VERDICT: inconclusive — no season had full sbd coverage for a fair test.")
    elif fair_wins > len(fair) / 2:
        print("VERDICT: on fair seasons the model beat our actual roster — edge SUGGESTED (small n; see caveats).")
    else:
        print("VERDICT: on fair seasons the model did NOT beat us — edge unproven.")
    print("Coverage-limited seasons (model filled < our slots because sbd was P4-only) are NOT a valid")
    print("head-to-head — the shortfall is missing G5 projections, not worse picks. Proj Log can't fill")
    print("the gap (fails corruption gate, MAE-to-actual ~0.1-0.3). This is the P4-heavy-sbd limitation.")
    json.dump(results, open('build/replay_results_2022_2025.json', 'w'), indent=1)
    print("\nWrote build/replay_results_2022_2025.json")

if __name__ == '__main__':
    main()

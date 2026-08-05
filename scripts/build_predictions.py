"""Stage 1 prediction model v2 — now with real CBS moneylines (wk1-4).
Hierarchy per game: de-vigged moneyline -> spread -> shrunk SP+ -> tier default. Sum-constrained to market total."""
import json, csv, math, datetime
from collections import defaultdict
PROJ='/mnt/project/'

d=json.load(open('data/data_2026.json')); teams=d.get('teams',d)
teams=teams if isinstance(teams,list) else list(teams.values())
SP={t['team']:t.get('sp_mar') for t in teams}
MKT={t['team']:t.get('mkt_win_total') for t in teams}
SPCAL=json.load(open('build/sp_calibration_2026.json'))
SP_SCALE=SPCAL['sp_scale']; SP_HFA=SPCAL['sp_hfa']
grid=list(csv.DictReader(open('data/schedule/pool_schedule_grid_2026.csv')))
POOL={r['Team'] for r in grid}
CONF_G={r['Team']:r['Conf'] for r in grid}

# --- name normalization: CBS abbreviations -> pool names ---
def norm(s): return s.lower().replace("'","").replace('.','').replace('-',' ').replace('(fla)','').replace('  ',' ').strip()
POOL_N={norm(t):t for t in POOL}
# manual CBS->pool aliases
ALIAS={'san jose st':'San Jose State','n dakota st':'North Dakota State','e michigan':'Eastern Michigan',
'new mexico st':'New Mexico State','jacksonville st':'Jacksonville State','sacramento st':'Sacramento State',
'miami (fla)':'Miami FL','miami fla':'Miami FL','miami oh':'Miami OH','so miss':'Southern Miss',
'app st':'Appalachian State','ga southern':'Georgia Southern','c carolina':'Coastal Carolina',
'w kentucky':'Western Kentucky','w michigan':'Western Michigan','n illinois':'Northern Illinois',
'c michigan':'Central Michigan','fresno st':'Fresno State','boise st':'Boise State','texas st':'Texas State',
'oregon st':'Oregon State','washington st':'Washington State','colorado st':'Colorado State','utah st':'Utah State',
'arkansas st':'Arkansas State','georgia st':'Georgia State','kennesaw st':'Kennesaw State','middle tenn':'Middle Tennessee',
'ul monroe':'ULM','fau':'Florida Atlantic','fiu':'FIU','uconn':'UConn','miss state':'Mississippi State',
'louisiana tech':'Louisiana Tech','s dakota st':'South Dakota State'}
def to_pool(cbs):
    n=norm(cbs)
    if n in ALIAS: return ALIAS[n]
    if n in POOL_N: return POOL_N[n]
    if ALIAS.get(n) in POOL: return ALIAS[n]
    # try alias-normalized
    for k,v in ALIAS.items():
        if norm(v)==n: return v
    return None  # non-pool (FCS/other) — fine, we only need pool teams matched

# --- de-vig moneyline -> win prob ---
def ml_to_prob(ml):
    if ml is None: return None
    return (100/(ml+100)) if ml>0 else ((-ml)/((-ml)+100))
def devig(p_home,p_away):
    s=p_home+p_away
    return (p_home/s, p_away/s) if s>0 else (p_home,p_away)

# --- load CBS lines: key by (pool_home, pool_away) -> home_winprob ---
LINE_WP={}   # (home,away) -> P(home win)
SPREAD={}    # (home,away) -> home spread
for line in open('data/lines/cbs_lines_2026.txt'):
    p=line.strip().split('~')
    if len(p)<7: continue
    wk,a,asp,aml,h,hsp,hml=p
    ph=to_pool(h); pa=to_pool(a)
    if not ph and not pa: continue
    # moneyline path
    try:
        hml_v=None if hml=='null' else int(hml); aml_v=None if aml=='null' else int(aml)
    except: hml_v=aml_v=None
    if hml_v is not None and aml_v is not None:
        phw,paw=devig(ml_to_prob(hml_v),ml_to_prob(aml_v))
        LINE_WP[(ph,pa)]=('ml',phw)
    else:
        try: hsp_v=float(hsp)
        except: hsp_v=None
        if hsp_v is not None: SPREAD[(ph,pa)]=hsp_v

print(f"CBS lines loaded: {len(LINE_WP)} moneyline games, {len(SPREAD)} spread-only games")

HFA=SP_HFA; SHRINK=0.10  # shrink small — curve is OUTCOME-calibrated (empirical buckets)
# OUTCOME-calibrated empirical SP+ curve: favorite win-rate by SP+ margin, from
# data/lines/cfbd_curve_data.csv (3476 games). Control points = (mean |margin|,
# empirical P(favorite wins)); monotonic piecewise-linear. Replaces the single-logistic
# scale. ~14 was market-mimic (wrong target for a distribution model); this predicts
# ACTUAL outcomes. VINTAGE: control games are season-level SP+; model uses preseason SP+,
# so exact values shift, but the ~8-9 outcome regime is correct either way (see SP_Curve_Calibration.md).
SP_CURVE=[(0.0,0.500),(1.5,0.534),(6.4,0.679),(14.7,0.859),(27.6,0.959),(45.0,0.990)]
def _curve(d):
    a=abs(d)
    if a>=SP_CURVE[-1][0]: p=SP_CURVE[-1][1]
    else:
        p=SP_CURVE[-1][1]
        for i in range(1,len(SP_CURVE)):
            if a<=SP_CURVE[i][0]:
                (x0,y0),(x1,y1)=SP_CURVE[i-1],SP_CURVE[i]
                p=y0+(y1-y0)*(a-x0)/(x1-x0); break
    return p if d>=0 else 1.0-p
def spread_to_wp(sp): return 1.0/(1.0+math.exp(sp/6.5))
def sp_to_wp(rt,ro,home):
    if rt is None or ro is None: return None
    diff=rt-ro+(HFA if home else -HFA); return _curve(diff)

WK=['W0','W1','W2','W3','W4','W5','W6','W7','W8','W9','W10','W11','W12','W13','W15']
def opp_of(cell):
    c=(cell or '').strip()
    if not c: return None,None
    away=c.startswith('@'); name=c[1:].strip() if away else (c[3:].strip() if c.startswith('vs ') else c)
    return name,(not away)

games_by_team=defaultdict(list)
for r in grid:
    for w in WK:
        opp,home=opp_of(r.get(w,''))
        if opp: games_by_team[r['Team']].append((w,opp,home))

# per-game wp with hierarchy
def game_wp(team,opp,home):
    # 1. moneyline (either orientation)
    if home and (team,opp) in LINE_WP: return LINE_WP[(team,opp)][1],'ml'
    if (not home) and (opp,team) in LINE_WP: return 1-LINE_WP[(opp,team)][1],'ml'
    # 2. spread
    if home and (team,opp) in SPREAD: return spread_to_wp(SPREAD[(team,opp)]),'spread'
    if (not home) and (opp,team) in SPREAD: return spread_to_wp(-SPREAD[(opp,team)]),'spread'
    # 3. shrunk SP+
    if opp in SP and SP.get(opp) is not None and SP.get(team) is not None:
        swp=sp_to_wp(SP[team],SP[opp],home)
        if swp is not None: return swp+SHRINK*(0.5-swp),'sp+'
    # 4. tier default
    if opp not in POOL: return (0.90 if home else 0.85),'default-fcs'
    return 0.5,'default-pool'

# calibration on overlap (line vs SP+)
overlap=[]
for team in games_by_team:
    for (w,opp,home) in games_by_team[team]:
        po=to_pool(opp) or opp
        wp,src=game_wp(team,po,home)
        if src in ('ml','spread') and po in SP and SP.get(po) is not None and SP.get(team) is not None:
            swp=sp_to_wp(SP[team],SP[po],home)
            if swp is not None: overlap.append((swp,wp))
if overlap:
    n=len(overlap); bias=sum(a-b for a,b in overlap)/n; mae=sum(abs(a-b) for a,b in overlap)/n
    print(f"CALIBRATION: {n} overlap games · SP+ bias {bias:+.3f} · MAE {mae:.3f}")
json.dump({'overlap_n':len(overlap),'sp_bias':round(bias,4) if overlap else None,'mae':round(mae,4) if overlap else None,'shrink':SHRINK,'cbs_ml_games':len(LINE_WP),'cbs_spread_games':len(SPREAD)},open('build/calibration_2026.json','w'),indent=1)

def poisson_binomial(probs):
    dist=[1.0]
    for p in probs:
        p=min(max(p,1e-6),1-1e-6); nd=[0.0]*(len(dist)+1)
        for k,v in enumerate(dist): nd[k]+=v*(1-p); nd[k+1]+=v*p
        dist=nd
    return dist
def rescale(probs,target):
    if target is None or not probs: return probs
    lo,hi=-6,6
    for _ in range(50):
        mid=(lo+hi)/2
        s=sum(1.0/(1.0+math.exp(-(math.log(min(max(p,1e-6),1-1e-6)/(1-min(max(p,1e-6),1-1e-6)))+mid))) for p in probs)
        if s<target: lo=mid
        else: hi=mid
    dlt=(lo+hi)/2
    return [1.0/(1.0+math.exp(-(math.log(min(max(p,1e-6),1-1e-6)/(1-min(max(p,1e-6),1-1e-6)))+dlt))) for p in probs]

preds={}; src_counts=defaultdict(int)
for team in sorted(games_by_team):
    raw=[]; covs=[]
    for (w,opp,home) in games_by_team[team]:
        po=to_pool(opp) or opp
        wp,src=game_wp(team,po,home); raw.append(wp); src_counts[src]+=1
        covs.append({'wk':w,'opp':po,'home':home,'conf_game':CONF_G.get(po)==CONF_G.get(team),'src':src})
    tgt=MKT.get(team); adj=rescale(raw,tgt); dist=poisson_binomial(adj)
    Pge=lambda n: sum(dist[n:]) if n<len(dist) else 0.0
    ew=sum(k*v for k,v in enumerate(dist))
    cum=0;p10=p90=None
    for k,v in enumerate(dist):
        cum+=v
        if p10 is None and cum>=.10:p10=k
        if p90 is None and cum>=.90:p90=k
    preds[team]={'conf':CONF_G.get(team),'market_total':tgt,'sp_plus':SP.get(team),
        'expected_wins':round(ew,2),'P_ge_8':round(Pge(8),3),'P_ge_6':round(Pge(6),3),'P_ge_10':round(Pge(10),3),
        'floor_p10':p10,'ceiling_p90':p90,'n_line_games':sum(1 for c in covs if c['src'] in('ml','spread')),
        'per_game':[{**covs[i],'wp':round(adj[i],3)} for i in range(len(adj))]}

meta={'model':'stage1 v4 — CBS moneylines(wk1-4) + OUTCOME-CALIBRATED empirical SP+ bucket curve (cfbd 3476g, ~8-9 regime; scale 14 retired) + tier default, sum-to-market','built':datetime.datetime.now().isoformat(),
      'frozen':False,'calibration':json.load(open('build/calibration_2026.json')),'source_counts':dict(src_counts),
      'note':'P(>=N) re-expresses market as threshold probs. market=level, SP+=shape, real lines override. Not market-beating. FREEZE at draft.'}
json.dump({'meta':meta,'predictions':preds},open('build/predictions_2026.json','w'),indent=1)
print("source counts:",dict(src_counts)); print("teams:",len(preds))

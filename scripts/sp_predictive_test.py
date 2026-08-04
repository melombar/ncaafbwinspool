#!/usr/bin/env python3
"""
Does preseason/postseason SP+ predict ACTUAL WINS beyond the market total?
Residual-signal test on clean 4-year data (2022-2025). Doctrine-safe: benchmark = actual wins (absolute),
market total = baseline, SP+ factors tested INDIVIDUALLY and IN COMBINATION (preflight #4).

REQUIRES clean actual wins: cfbd_records.csv (from pull_cfbd_records.py) — the CFBD game file
undercounts wins (drops FCS games). DO NOT run on game-derived wins.

Factors tested (each vs actual wins, controlling for market total):
  - preseason(final/Aug) SP+ rating
  - preseason SP+ rank
  - SP+ avgw (SP+'s own win projection) [2025 only]
  - postseason(season-level) SP+ rating   [from cfbd_curve_data]
  - SP+ MOVEMENT preseason->postseason     [the tracked-delta hypothesis]
Output: for each factor, does it reduce MAE / add R^2 beyond the market total alone?
"""
import json, csv, math, os
from collections import defaultdict

REC='cfbd_records.csv'
if not os.path.exists(REC):
    print("BLOCKED: need cfbd_records.csv (run pull_cfbd_records.py). Not using game-derived wins (undercounts).")
    raise SystemExit

def norm(s): return (s or '').lower().replace("'","").replace('.','').replace('-',' ').replace(' st ',' state ').strip()

# actual wins (clean)
actual={}
for r in csv.DictReader(open(REC)):
    actual[(r['season'],norm(r['team']))]=int(r['wins'])

# preseason final SP+
hist=json.load(open('sp_final_preseason_hist.json'))['ratings']
pre_sp={}; pre_rank={}; pre_avgw={}
for y in hist:
    for t,v in hist[y].items():
        pre_sp[(y,norm(t))]=v['sp_final']; pre_rank[(y,norm(t))]=v['sp_final_rank']
        if v.get('avgw') is not None: pre_avgw[(y,norm(t))]=v['avgw']

# postseason (season-level) SP+ from cfbd_curve_data (one rating per team-season)
post_sp={}
for r in csv.DictReader(open('/mnt/user-data/uploads/cfbd_curve_data.csv')):
    for side in ['home','away']:
        k=(r['season'],norm(r[side]))
        post_sp[k]=float(r[f'{side}_sp'])

# preseason market totals (SBD) — P4-heavy
sbd=json.load(open('/mnt/project/sbd_preseason_2018_2025.json'))
mkt={}
for y in sbd:
    for t,tot in sbd[y].items():
        try: mkt[(y,norm(t))]=float(tot)
        except: pass

# build joined table
rows=[]
for k in actual:
    y,t=k
    if k in pre_sp and k in mkt:
        rows.append({'y':y,'t':t,'actual':actual[k],'mkt':mkt[k],'pre_sp':pre_sp[k],
                     'pre_rank':pre_rank.get(k),'post_sp':post_sp.get(k),
                     'avgw':pre_avgw.get(k),
                     'sp_move':(post_sp[k]-pre_sp[k]) if k in post_sp else None})
print(f"Joined {len(rows)} team-seasons with actual wins + market total + preseason SP+\n")

def mae(pred,act): return sum(abs(p-a) for p,a in zip(pred,act))/len(act)
def corr(x,y):
    n=len(x); mx=sum(x)/n; my=sum(y)/n
    cov=sum((a-mx)*(b-my) for a,b in zip(x,y))
    sx=math.sqrt(sum((a-mx)**2 for a in x)); sy=math.sqrt(sum((b-my)**2 for b in y))
    return cov/(sx*sy) if sx*sy else 0

act=[r['actual'] for r in rows]

# BASELINE: market total alone
print("=== BASELINE: market total vs actual wins ===")
print(f"  MAE(market -> actual) = {mae([r['mkt'] for r in rows],act):.3f}")
print(f"  corr(market, actual) = {corr([r['mkt'] for r in rows],act):.3f}")

# Does each factor correlate with the RESIDUAL (actual - market)?  <- the key test
resid=[r['actual']-r['mkt'] for r in rows]
print("\n=== RESIDUAL SIGNAL: does factor X predict (actual - market)? ===")
print("  (corr near 0 = market already priced it; nonzero = factor adds info)")
for name,key in [('preseason SP+ rating','pre_sp'),('preseason SP+ rank','pre_rank'),
                 ('postseason SP+ rating','post_sp'),('SP+ movement pre->post','sp_move')]:
    sub=[(r[key],rr) for r,rr in zip(rows,resid) if r.get(key) is not None]
    if len(sub)>10:
        c=corr([s[0] for s in sub],[s[1] for s in sub])
        print(f"  {name:26} corr with residual = {c:+.3f}  (n={len(sub)})")

# avgw (2025) — does SP+'s own win projection beat the market?
av=[r for r in rows if r.get('avgw') is not None]
if len(av)>10:
    print(f"\n=== SP+ avgw (its own win projection) vs market, {len(av)} teams (2025) ===")
    print(f"  MAE(avgw -> actual)   = {mae([r['avgw'] for r in av],[r['actual'] for r in av]):.3f}")
    print(f"  MAE(market -> actual) = {mae([r['mkt'] for r in av],[r['actual'] for r in av]):.3f}")

# COMBINATION: does market + SP+ together beat market alone? (simple 2-var blend)
print("\n=== COMBINATION: blend market + preseason SP+ (grid search weight) ===")
best=None
# scale SP+ to win-ish units via /14 curve is complex; instead z-blend: pred = mkt + w*(pre_sp - mean_sp)*k
msp=sum(r['pre_sp'] for r in rows)/len(rows)
for w in [x/100 for x in range(0,60,2)]:
    pred=[r['mkt']+w*(r['pre_sp']-msp)/10 for r in rows]  # /10 rough SP+->win
    m=mae(pred,act)
    if best is None or m<best[0]: best=(m,w)
print(f"  best blend MAE {best[0]:.3f} at weight {best[1]} (baseline market MAE {mae([r['mkt'] for r in rows],act):.3f})")
print(f"  -> if best-blend MAE < baseline, SP+ adds; if ~equal, market already efficient (confirms #22)")

json.dump({'n':len(rows),'baseline_mkt_mae':round(mae([r['mkt'] for r in rows],act),3),
           'note':'residual-signal test, clean wins'}, open('sp_predictive_result.json','w'),indent=1)
print("\nwrote sp_predictive_result.json")

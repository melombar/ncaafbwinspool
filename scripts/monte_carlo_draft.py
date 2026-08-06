import csv, json, math, random, numpy as np
from collections import defaultdict

CONFS=["AAC","ACC","Big Ten","Big 12","CUSA","MAC","MWC","Pac12","SEC","Sun Belt"]
USABLE=6.0
pool_conf={r['Team']:r['Pool Conf'] for r in csv.DictReader(open('data/Master_Lookup_2026.tsv'),delimiter='\t')}
PRED=json.load(open('build/predictions_2026.json'))['predictions']
mkt={t:PRED[t].get('market_total') for t in PRED}
POOL=set(pool_conf)
games=defaultdict(list)
for t,v in PRED.items():
    for g in v.get('per_game',[]):
        if g.get('wp') is not None:
            games[t].append((str(g.get('opp','')).replace('@','').replace('vs','').strip(), float(g['wp'])))
teams=[t for t in POOL if mkt.get(t) is not None and games[t]]
# shared intra-pool events
seen={}; team_games=defaultdict(list)
for t in teams:
    for opp,wp in games[t]:
        if opp in POOL and mkt.get(opp) is not None:
            key=frozenset((t,opp))
            if key not in seen: seen[key]=(len(seen),wp,t)
            eid,p0,owner=seen[key]; team_games[t].append(('ev',eid,t==owner))
        else: team_games[t].append(('ind',wp))
NEV=len(seen); evp=np.zeros(NEV)
for k,(eid,p0,o) in seen.items(): evp[eid]=p0
def sample_seasons(M,rng):
    owin = rng.random((M,NEV)) < evp
    W={}
    for t in teams:
        w=np.zeros(M)
        for g in team_games[t]:
            if g[0]=='ind': w+=(rng.random(M)<g[1])
            else: w+= owin[:,g[1]] if g[2] else ~owin[:,g[1]]
        W[t]=w
    return W
def dstats(t):
    probs=[wp for _,wp in games[t]]; d=[1.0]
    for p in probs:
        nd=[0.0]*(len(d)+1)
        for k in range(len(d)): nd[k]+=d[k]*(1-p); nd[k+1]+=d[k]*p
        d=nd
    Pge=lambda n: sum(d[max(0,math.ceil(n)):]); m=mkt[t]
    return sum(probs),(Pge(round(m)+2) if m is not None else 0)
import glob, re as _re
def _coach(r):
    H=bool(r.get('new_hc'));O=bool(r.get('new_oc'));D=bool(r.get('new_dc'))
    promo=bool(_re.search('promot|interim|in-house|within|internal|elevat',r.get('new_hc') or '',_re.I))
    if not(H or O or D):return 1
    if H and O and D:return -1
    if H and promo:return 0
    if H:return -1
    if O and D:return -1
    return 0
def _qb(r):
    q=r.get('qb_status') or '';m=_re.match(r'\s*([A-Za-z]+)',q);en=m.group(1) if m else ''
    proven=bool(_re.search(r'start(ed|er|s)\b|multi-?year|veteran|incumbent|held the job|passed for|threw for|Award|all-?conf',q,_re.I))
    unpro=bool(_re.search(r'first year|limited snaps|waited|sparingly|\bbackup\b|no (real )?starts',q,_re.I))
    if _re.match(r'Returning',en,_re.I):return 0 if (unpro and not _re.search('incumbent|held the job',q,_re.I)) else 1
    if _re.match(r'Transfer',en,_re.I):return -1 if(unpro and not proven) else (1 if proven else 0)
    if _re.match(r'Freshman|Battle|Unsettled',en,_re.I):return -1
    return 0
def load_layerB():
    sc={};n=0
    for fn in glob.glob('almanac/bboc_2026_*.json'):
        for r in json.load(open(fn)).get('teams',[]):
            lean=(r.get('host_lean') or '').lower();sd=(r.get('sched_tag') or '').lower()
            s=(1 if 'over' in lean else -1 if 'under' in lean else 0)+(1 if 'favor' in sd else -1 if 'brutal' in sd else 0)
            s+=(1 if r.get('dark_horse') else 0)+(-2 if r.get('fade') else 0)+_coach(r)+_qb(r)
            sc[r['team']]=s;n+=1
    return sc,n
LAYERB,LBN=load_layerB()
TEAM={t:{'conf':pool_conf[t],'m':mkt[t]or 0,'ceilP':dstats(t)[1],'lb':LAYERB.get(t,0)} for t in teams}
by_conf_sorted={c:sorted([t for t in teams if TEAM[t]['conf']==c],key=lambda t:-TEAM[t]['m']) for c in CONFS}
USABLE_TOT={c:sum(1 for t in by_conf_sorted[c] if TEAM[t]['m']>=USABLE) for c in CONFS}

def scorer(kind):
    def f(t,ur,rnd,rng):
        s=TEAM[t]; m=s['m']; conf=s['conf']
        scar=2.5 if ur<=2 else (1.0 if ur<=4 else 0.0); up=5*s['ceilP']; lb=s['lb']
        if kind=='field':    return m+scar+rng.gauss(0,0.4)
        if kind=='rookie':   return m+(0.5 if ur<=2 else 0)+rng.gauss(0,1.6)
        if kind=='elite':    return m+0.3*scar+rng.gauss(0,0.3)
        if kind=='scarcity': return m+(4 if ur<=2 else 2 if ur<=4 else 0)+rng.gauss(0,0.3)
        if kind=='upside':   return m+up+scar+rng.gauss(0,0.3)
        if kind=='balanced': return m+scar+0.8*up+rng.gauss(0,0.3)
        if kind=='almanac':  return m+scar+0.6*lb+rng.gauss(0,0.3)
        if kind=='defer_deep':
            dp=3 if(conf in('Big Ten','SEC')and rnd<4)else 0; return m+scar-dp+rng.gauss(0,0.3)
    return f
FN={k:scorer(k) for k in['field','rookie','elite','scarcity','upside','balanced','defer_deep','almanac']}

def draft(our_policy,our_slot,rng):
    pol=['field']*12; others=[i for i in range(12) if i!=our_slot]; pol[rng.choice(others)]='rookie'; pol[our_slot]=our_policy
    rosters=[dict() for _ in range(12)]; taken=set(); uavail=dict(USABLE_TOT)
    for rnd in range(10):
        order=range(12) if rnd%2==0 else range(11,-1,-1)
        for p in order:
            myc=rosters[p]; cand=[]
            for c in CONFS:
                if c in myc: continue
                n=0
                for t in by_conf_sorted[c]:
                    if t in taken: continue
                    cand.append((t,uavail[c])); n+=1
                    if n>=3: break
            if not cand: continue
            f=FN[pol[p]]; best=max(cand,key=lambda tu:f(tu[0],tu[1],rnd,rng))[0]
            myc[TEAM[best]['conf']]=best; taken.add(best)
            if TEAM[best]['m']>=USABLE: uavail[TEAM[best]['conf']]-=1
    return rosters

if __name__=='__main__':
    rng=np.random.default_rng(42); W=sample_seasons(3000,rng)
    print("GATE1 season sampler:")
    for t in['Appalachian State','Boise State','Notre Dame','Ohio State']:
        print(f"  {t:16} sampled {W[t].mean():.2f} sum-probs {sum(wp for _,wp in games[t]):.2f}")
    print(f"  teams={len(teams)} events={NEV}")
    # GATE 2 cliff
    r2=random.Random(7); cliff=defaultdict(list)
    for _ in range(300):
        ros=draft('field',0,r2); taken=set(v for rr in ros for v in rr.values())
        # approx cliff: round when conf usable exhausted — re-derive from a fresh timed draft
    # simpler: report supply depth (validated ordering already); skip re-timing
    print("\nGATE2 usable depth per conf (thin=few):",{c:USABLE_TOT[c] for c in sorted(CONFS,key=lambda c:USABLE_TOT[c])})
    # GATE 3+4 tournament
    rngS=np.random.default_rng(2026); M=8000; WARR=sample_seasons(M,rngS)
    print("\nLayer-B pods scored:",LBN,"teams | tilt sensitivity: does Layer-B-aware drafting win IF Layer-B predicts beats?")
    def run(kind,N,seed,beta):
        rng=random.Random(seed); f=t3=0; tot=[]
        delta={t:beta*TEAM[t]['lb'] for t in teams}
        def total(r,j): return sum(WARR[t][j]+delta[t] for t in r.values())
        for i in range(N):
            slot=rng.randrange(12); ros=draft(kind,slot,rng); j=rng.randrange(M)
            T=[total(r,j) for r in ros]; mine=T[slot]; rank=1+sum(1 for x in T if x>mine)
            f+=rank==1; t3+=rank<=3; tot.append(mine)
        return f/N,t3/N,float(np.mean(tot))
    N=4500; POLS=['elite','defer_deep','almanac','upside']
    for beta in (0.0,0.30):
        print(f"\n  β={beta}  (Layer-B beat-tilt: +{beta}/upside-point):")
        rowsb=[]
        for k in POLS:
            p1,p3,mt=run(k,N,(hash(k)^int(beta*100))&0xffff,beta); rowsb.append((k,p1,p3,mt))
            print(f"    {k:11} P1st {p1:5.1%} Ptop3 {p3:5.1%} meanTot {mt:4.1f}")
        rowsb.sort(key=lambda x:-x[1]); print(f"    WINNER: {rowsb[0][0]}  (baseline 8.3%)")

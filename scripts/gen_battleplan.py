import json, csv
r=json.load(open('build/mc_paths_2026.json'))
P=r['paths']; S=r['sensitivity']; cliff=r['cliff']; N=r['meta']['N']; nb=r['meta']['layerB_pods_teams']
CONFS=["MWC","Sun Belt","MAC","Pac12","AAC","CUSA","Big 12","ACC","SEC","Big Ten"]
# market + usable-anchor counts (sub-floor <6.0 must never be shown as a recommendation)
USABLE=6.0
pred=json.load(open('build/predictions_2026.json'))['predictions']
MKT={t:(pred[t].get('market_total') or 0) for t in pred}
pc={row['Team']:row['Pool Conf'] for row in csv.DictReader(open('data/Master_Lookup_2026.tsv'),delimiter='\t')}
usable_ct={c:sum(1 for t in pc if pc[t]==c and MKT.get(t,0)>=USABLE) for c in CONFS}
def board_cells(c,b):
    # keep ONLY usable teams from what the policy drafted; sub-floor forced-fills are not recommendations
    us=[x for x in b['top'] if MKT.get(x['team'],0)>=USABLE]
    thin = usable_ct.get(c,99)<=5
    if not us:
        prim=f'<span style="color:#e0664d">⚠ no usable anchor — often forced to a sub-floor fill</span>'; backs=''
    else:
        prim=f"{us[0]['team']} <span class='pct'>{us[0]['pct']}%</span> <span class='mk'>({MKT.get(us[0]['team'])})</span>"
        backs=', '.join(f"{x['team']} ({MKT.get(x['team'])})" for x in us[1:]) or '<span style="color:#8aa0b4">— (only 1 usable drafted)</span>'
    warn=f'  <span class="thin" title="only {usable_ct[c]} usable anchors in this conference">⚠ {usable_ct[c]} usable — secure early</span>' if thin else ''
    return prim, backs, warn
board=P['almanac']['board']
order=sorted(board.items(),key=lambda kv:kv[1]['avg_round'])
betas=sorted(S.keys(),key=float)
paths_order=['almanac','defer_deep','elite','scarcity','balanced']
def bar(pct,color,w=180):
    return f'<div style="background:#1a2735;border-radius:3px;width:{w}px;display:inline-block;vertical-align:middle"><div style="background:{color};height:12px;border-radius:3px;width:{max(2,pct*w/0.25):.0f}px"></div></div>'
def cliffrow(c):
    d=cliff[c]; tag=("GRAB EARLY" if d<=5 else "defer OK" if d>=10 else "mid")
    col="#e0664d" if d<=5 else "#6ede9a" if d>=10 else "#e0b24a"
    return f'<tr><td>{c}</td><td style="text-align:center">{d}</td><td>{bar(min(0.25,d/13*0.25),col,120)} <span style="color:{col};font-size:11px;font-weight:600">{tag}</span></td></tr>'
sens_rows=""
for k in paths_order:
    cells="".join(f'<td style="text-align:center;{ "background:#12492a;color:#7be0a0;font-weight:700" if S[b][k]==max(S[b].values()) else ""}">{S[b][k]:.0%}</td>' for b in betas)
    sens_rows+=f"<tr><td>{P[k]['name']}</td>{cells}</tr>"
def slotbest(p):
    bs=p['byslot']; b=max(bs,key=bs.get); return f"{b} ({bs[b]:.0%})"
NOTE={'almanac':'Bank market early, break same-price ties by Layer-B upside (returning QB, soft non-con, favorable draw, no fade). THE bet if you trust the pod read.',
'defer_deep':'Take highest-market anchors; skip Big Ten/SEC early (bank their elites late). The robust floor that wins even if Layer-B is noise.',
'elite':'Pure highest-market. Simple, banks wins, no upside read. Middle of the pack.',
'scarcity':'Grab thin-conference elites in rounds 1-2 above all. Underperforms — scarcity timing alone is not the edge.',
'balanced':'Blend of everything. Jack of all trades, master of none here.'}
cards="".join(f'''<div class="card {'win' if k=='almanac' else ''}">
  <div class="pn">{P[k]['name']}{' ★' if k=='almanac' else ''}</div>
  <div class="p1">{P[k]['p1']:.0%}<span class="lbl"> P(win) @β=0.25</span></div>
  <div class="meta">top-3 {P[k]['p3']:.0%} · mean {P[k]['mean_total']} · best slot {slotbest(P[k])}</div>
  <div class="desc">{NOTE[k]}</div></div>''' for k in paths_order)
def seqrow(i,c,b):
    prim,backs,warn=board_cells(c,b)
    tag='grab early' if cliff[c]<=5 else 'defer OK' if cliff[c]>=10 else 'mid'
    tcls='ge' if cliff[c]<=5 else 'df' if cliff[c]>=10 else 'md'
    return (f'<tr><td style="text-align:center;color:#8aa0b4">{i+1}</td><td><b>{c}</b>{warn}</td>'
            f'<td style="text-align:center">R{b["avg_round"]}</td><td>{prim}</td><td class="bk">{backs}</td>'
            f'<td><span class="tag {tcls}">{tag}</span></td></tr>')
seq="".join(seqrow(i,c,b) for i,(c,b) in enumerate(order))
html=f'''<!doctype html><meta charset=utf-8><title>Wins Pool 2026 — Battle Plan</title>
<style>
body{{background:#0d1520;color:#e8eef5;font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;padding:22px;max-width:1000px}}
h1{{font-size:20px;margin:0 0 2px}} h2{{font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:#9fb2c6;margin:26px 0 8px;border-bottom:1px solid #22303f;padding-bottom:5px}}
.sub{{color:#9fb2c6;margin:0 0 4px}} .verdict{{background:#12212e;border:1px solid #294056;border-radius:8px;padding:12px 16px;margin:14px 0;font-size:15px}}
.verdict b{{color:#7be0a0}} table{{border-collapse:collapse;width:100%;font-size:13px}} th,td{{border:1px solid #22303f;padding:6px 10px;text-align:left}}
th{{color:#9fb2c6;font-weight:600;font-size:11px;text-transform:uppercase}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:10px;margin-top:8px}}
.card{{background:#131e2b;border:1px solid #22303f;border-radius:8px;padding:12px}} .card.win{{border-color:#c79a3a;box-shadow:0 0 0 1px #c79a3a55}}
.pn{{font-weight:700;font-size:14px;color:#cfe0f0}} .p1{{font-size:26px;font-weight:800;color:#7be0a0;margin:4px 0}} .p1 .lbl{{font-size:11px;font-weight:400;color:#9fb2c6}}
.card .meta{{font-size:11px;color:#8aa0b4;font-family:monospace}} .desc{{font-size:12px;color:#c3d0dd;margin-top:6px}}
.pct{{color:#7bd6ff;font-size:11px;font-weight:600}} .bk{{color:#8aa0b4;font-size:12px}} .mk{{color:#6d8199;font-size:10px}}
.thin{{background:#3a1e14;color:#f0a068;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;margin-left:5px;white-space:nowrap}}
.tag{{font-size:10px;font-weight:700;padding:1px 7px;border-radius:3px}} .tag.ge{{background:#3a1e14;color:#f0a068}} .tag.df{{background:#12331f;color:#6ede9a}} .tag.md{{background:#2a2f3a;color:#c8b060}}
.foot{{color:#6d8199;font-size:11px;margin-top:22px;border-top:1px solid #22303f;padding-top:10px}}
</style>
<h1>Wins Pool 2026 — Battle Plan</h1>
<p class="sub">Monte Carlo of the full pool (draft + season) across all 12 slots · {N:,} trials/policy · market-calibrated · {nb} pod teams scored so far</p>

<div class="verdict">The pool turns on one question: <b>does team-specific Layer-B knowledge (returning QB, soft non-con, favorable draw, avoid fades) actually tilt beats?</b> The champions' 78% beat-rate says yes. If it does, the <b>Almanac Upside</b> path nearly doubles your win odds. If it's noise, fall back to <b>Defer-Deep Banking</b>. Either way: <b>grab MWC & Sun Belt in rounds 1–2, defer Big Ten/SEC to the back third.</b></div>

<h2>The 5 paths (win probability at β=0.25)</h2>
<div class="grid">{cards}</div>

<h2>The number that decides it — β (does Layer-B predict beats?)</h2>
<p class="sub">P(win) by path as the Layer-B beat-tilt grows. Crossover ≈ β 0.12: above it, Almanac wins; below, bank/defer. Champion beat-rate implies β&gt;0.</p>
<table><tr><th>Path</th>{"".join(f'<th style="text-align:center">β={b}</th>' for b in betas)}</tr>{sens_rows}</table>

<h2>Ideal draft — the Almanac path, round by round</h2>
<p class="sub">Average pick round + primary / backups per conference. Position-agnostic (holds across slots); on the night, take the primary if there, else a backup, honoring the grab-early tags.</p>
<table><tr><th>#</th><th>Conf</th><th>Avg round</th><th>Primary</th><th>Backups</th><th>Timing</th></tr>{seq}</table>

<h2>Scarcity clock — usable anchors (≥6.0) per conference</h2>
<p class="sub">Thin conferences dry up first (MWC cliffs ~round 2). This sets the grab-vs-defer order above.</p>
<table><tr><th>Conf</th><th>Usable</th><th></th></tr>{"".join(cliffrow(c) for c in sorted(CONFS,key=lambda c:cliff[c]))}</table>

<div class="foot">Reusable: re-run <code>scripts/monte_carlo_draft.py</code> as more BBOC pods load (only {nb} teams scored now — non-pod conferences pick on market alone, so their primaries will sharpen). Caveats: opponents modeled as near-optimal scarcity-aware + one rookie; Pac-12 flex teams carry a ±1-game uncertainty (schedule locks post-draft); β is an assumed edge, not proven by the sim — the champion beat-rate is the external evidence for β&gt;0.</div>
'''
open('almanac/battle_plan_2026.html','w').write(html)
print("wrote almanac/battle_plan_2026.html",len(html),"bytes")

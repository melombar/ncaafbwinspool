import json

edge=json.load(open('edge2025.json'))['teams']       # full names: "Air Force"
sp=json.load(open('sp2025_final.json'))['ratings']    # abbrev: "Ohio St."

# Brad-canonical -> edge2025 name (mostly identical; handle exceptions)
def edge_lookup(team):
    aliases={'Miami':'Miami','NC State':'NC State','Florida Atlantic':'Florida Atlantic',
      'UConn':'Connecticut','Florida Intl':'Florida International','EMU':'Eastern Michigan',
      'UMASS':'Massachusetts','Miami-OH':'Miami (OH)','San José State':'San Jose State',
      'Sam Houston':'Sam Houston State','Southern Miss':'Southern Mississippi',
      'Louisiana':'Louisiana','ULM':'Louisiana Monroe','App State':'Appalachian State'}
    for n in [team, aliases.get(team,team), team.replace('State','St.'), team.replace(' St.',' State')]:
        if n in edge: return edge[n]
    return None

# Brad-canonical -> sp2025 abbreviated name
def sp_lookup(team):
    m={'Ohio State':'Ohio St.','Penn State':'Penn St.','Michigan State':'Michigan St.',
      'Iowa State':'Iowa St.','Oklahoma State':'Oklahoma St.','Kansas State':'Kansas St.',
      'Arizona State':'Arizona St.','Mississippi State':'Mississippi St.','Boise State':'Boise St.',
      'Fresno State':'Fresno St.','San Diego State':'San Diego St.','San José State':'San Jose St.',
      'Colorado State':'Colorado St.','Utah State':'Utah St.','Washington State':'Washington St.',
      'Oregon State':'Oregon St.','Florida State':'Florida St.','NC State':'NC State',
      'Texas State':'Texas St.','Appalachian State':'Appalachian St.','App State':'Appalachian St.',
      'Arkansas State':'Arkansas St.','Georgia State':'Georgia St.','Ball State':'Ball St.',
      'Kent State':'Kent St.','Jacksonville State':'Jacksonville St.','New Mexico State':'New Mexico St.',
      'Sam Houston':'Sam Houston St.','Missouri State':'Missouri St.','Kennesaw State':'Kennesaw St.',
      'UConn':'Connecticut','Florida Intl':'Florida Intl','EMU':'Eastern Michigan',
      'UMASS':'Massachusetts','Miami-OH':'Miami (OH)','Miami':'Miami','Southern Miss':'Southern Miss',
      'Middle Tennessee':'Middle Tennessee','Western Kentucky':'Western Kentucky','ULM':'UL Monroe',
      'Louisiana':'Louisiana','Georgia Southern':'Georgia Southern','Coastal Carolina':'Coastal Carolina'}
    for n in [m.get(team), team, team.replace('State','St.'), team.replace(' St.',' State')]:
        if n and n in sp: return sp[n]
    return None

def join_file(path):
    d=json.load(open(path)); hits=0; misses=[]
    for r in d['teams']:
        t=r['team']
        e=edge_lookup(t); s=sp_lookup(t)
        if e:
            hits+=1
            # market: prefer VI consensus (canonical), keep pod value in notes if diverges
            if e.get('vi') is not None: r['mkt_win_total']=e['vi']
            if e.get('collin') is not None: r['collin_proj']=e['collin']
            r['ret_prod']=e.get('overall_ret')
            r['net_tarp']=e.get('net_tarp'); r['off_tarp']=e.get('off_tarp'); r['def_tarp']=e.get('def_tarp')
            r['six_win_pct']=e.get('six_win_pct')
        else:
            misses.append(t); r['six_win_pct']=r.get('six_win_pct')
        if s:
            r['sp_mar']=s.get('sp'); r['sp_rank']=s.get('rank')
        # recompute proj-mkt
        if r.get('collin_proj') is not None and r.get('mkt_win_total') is not None:
            r['proj_minus_mkt']=round(r['collin_proj']-r['mkt_win_total'],1)
    # add six_win_pct to contract if not there
    if 'six_win_pct' not in d['field_contract']:
        d['field_contract']=d['field_contract'].replace('proj_minus_mkt','proj_minus_mkt,six_win_pct')
    json.dump(d, open(path,'w'), indent=1)
    return hits, misses, len(d['teams'])

for f in ['bboc_2025_aac.json','bboc_2025_acc.json']:
    h,m,tot=join_file(f)
    print(f"{f}: joined {h}/{tot}  misses: {m}")

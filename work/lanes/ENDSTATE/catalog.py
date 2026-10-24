from native import *
from distance_catalog import compute
NAMES={'abstract_opt11':'abstract_staticA_h2_opt_w011','abstract_opt10':'abstract_staticA_h2_opt_w010','abstract_opt08':'abstract_staticA_h2_opt_w008','legacy_opt48':'legacy_staticA_h2_opt_w048','legacy_opt46':'legacy_staticA_h2_opt_w046','legacy_depth':'legacy_depth_h2_opt_w001','helper_shared_best':'shared_helper_h2_opt_w028','helper_shared_opt14':'shared_helper_h2_opt_w014'}
rows=[]
for name,source in NAMES.items():
 x=json.loads((H/(source+'.schedule.json')).read_text());meta=json.loads((H/(name+'.json')).read_text());plan=json.loads((H/(name+'.plan.json')).read_text());ops=plan['ops'];per=collections.defaultdict(list)
 for o in ops:
  for q in S.Unit(o['lines']).qs:per[q].append(o)
 timeline=[];exposure=0
 for q,seq in per.items():
  seq=sorted(seq,key=lambda o:o['t']);start=0
  for j,o in enumerate(seq):
   last=j==len(seq)-1;resetnext=not last and S.Unit(seq[j+1]['lines']).name in('RESET','RX')
   if last or resetnext:
    part=seq[start:j+1];anc=part[0].get('region')in('prep_init','teleports');busy={p['t']for p in part};first=part[0]['t'];end=part[-1]['t']+1
    idle=[t for t in range(first,min(end,meta['R']))if t not in busy]if anc else[];exposure+=len(idle);timeline.append(dict(cell=q,start=first,end=end,ancilla=anc,pre_round_idle=len(idle),operations=part));start=j+1
 initial={k:[x['tokens'][f'{k}{j}']['pos'][0]for j in x['permutations'][k]]for k in'abc'};final=x['endpoints'];counts={k:sum(o.get('tag')=='encoder_'+k for o in ops)for k in'abc'};entry=dict(name=name,initial=initial,final=final,prep_cx=counts,block_moves={k:sum(sum(x['tokens'][f'{k}{i}']['moves'])for i in range(7))for k in'abc'},data_hops=meta['data_hops'],native_R=meta['R'],ancilla_idle_ticks=exposure,secondary_measured=exposure+meta['block_teleports']+2*meta['data_hops'],earliest_R_scope='minimum for the final fixed physical wire order; not global across layouts',model_R=x['R'])
 entry['helpers']=x.get('helpers',{})
 (H/(name+'.catalog.json')).write_text(json.dumps(entry,indent=2));(H/(name+'.timeline.json')).write_text(json.dumps(timeline,indent=1));compute(H/(name+'.catalog'))
 try:entry['screen']=json.loads((H/(name+('.wide_screen.json'if x.get('helpers')else'.screen.json'))).read_text())
 except FileNotFoundError:pass
 rows.append(entry)
(H/'catalog.json').write_text(json.dumps(sorted(rows,key=lambda r:r.get('screen',{}).get('total',1)),indent=2));print([(r['name'],r['native_R'],r['ancilla_idle_ticks'])for r in rows])

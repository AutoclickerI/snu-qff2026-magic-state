import json,re
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn'); OUT=ROOT/'work/lanes/PRE3'; SRC=ROOT/'work/lanes/MAIN/spec/v16e.qasm'
D=[0,3,4,7,8,15,20]; N=lambda q:[x for x in (q-6,q+6,q-1,q+1) if 0<=x<36 and (x//6==q//6 or x%6==q%6)]
lines=SRC.read_text().splitlines(); layers=[];cur=[]
for l in lines:
 if l.startswith('// region round'):break
 if l.startswith('barrier'):layers.append(cur);cur=[]
 elif l.strip() and not l.startswith(('OPENQASM','include','qreg','creg','//')):cur.append(l)
layers=layers[:33]
last_gate={}; last_cx={}; last_any={}; gates={}; touched=set()
for t,ops in enumerate(layers):
 for op in ops:
  qs=[int(x) for x in re.findall(r'q\[(\d+)\]',op)]; touched.update(qs)
  is_measure=op.startswith('measure ')
  for q in qs:
   last_any[q]=t
   if not is_measure: last_gate[q]=t; gates.setdefault(q,[]).append((t,op))
   if op.startswith('cx '): last_cx[q]=t
neighbor_union=sorted(set().union(*(set(N(d)) for d in D))-set(D))
never=sorted(set(range(36))-touched)
# baseline all terminal measurements remain at t32; release at next step
base_rel={q:(0 if q in never else 33) for q in range(36)}
for q in (19,13):base_rel[q]=33
variants={
 'base':base_rel,
 'q13_19':{**base_rel,13:20},
 'q19_13_prompt':{**base_rel,19:16,13:20},
 'q19_11':{**base_rel,19:12},
}
rows=[]
for d in D:
 rows.append({'data':d,'last_gate':last_gate[d],'neighbors':N(d),'neighbor_release':{str(q):variants['q19_13_prompt'][q] for q in N(d) if q not in D}})
obj={'prefix_nominal_steps':33,'touched':sorted(touched),'never_touched':never,'data_last_gate':{str(q):last_gate[q] for q in D},'neighbor_union':neighbor_union,'neighbor_last_gate':{str(q):last_gate.get(q) for q in neighbor_union},'neighbor_last_cx':{str(q):last_cx.get(q) for q in neighbor_union},'neighbor_gates':{str(q):gates.get(q,[]) for q in neighbor_union},'release_variants':variants,'data_rows':rows}
(OUT/'release_schedule.json').write_text(json.dumps(obj,indent=2)+'\n')
print('data last gates',obj['data_last_gate']);print('neighbor union',neighbor_union);print('last gates',obj['neighbor_last_gate']);
for name,r in variants.items():
 for t in (33,34,35):
  free=set(q for q,s in r.items() if s<=t); per={str(d):sorted(set(N(d))&free-set(D)) for d in D}; distinct=sorted(set().union(*(set(v) for v in per.values())))
  print(name,t,'distinct',len(distinct),'per',per)
# Static one-hop movement screen: after last earlier interaction, destination must be adjacent to each later partner.
# Later final partner steps are read from prefix CXs; destinations are untouched neighbors of data.
move={}
for d in [0,3,4,15,20]:
 ds=[]
 # candidate destination is a never-touched adjacent cell, excluding data cells
 for dst in N(d):
  if dst not in never:continue
  # all CX partners after each possible idle gap; choose latest pre-move CX and inspect later
  cx=[(t, sorted(set(map(int,re.findall(r'q\[(\d+)\]',op))))) for t,ops in enumerate(layers) for op in ops if op.startswith('cx ') and d in map(int,re.findall(r'q\[(\d+)\]',op))]
  for t,partner in cx:
   later=[(tt,pp) for tt,pp in cx if tt>t]
   # destination must touch the other endpoint of all later CXs; T/tdg is okay
   req=[next(q for q in pp if q!=d) for _,pp in later]
   ok=all(x in N(dst) for x in req)
   ds.append({'after_step':t,'dst':dst,'later_partners':req,'adjacent_to_all_later':ok})
 move[str(d)]={'candidates':ds,'reason':'A one-hop move is useful only if destination touches every later partner; a moved partner would require a second coupled move.'}
(OUT/'movement_screen.json').write_text(json.dumps(move,indent=2)+'\n')
for d,v in move.items(): print('move',d,[(x['dst'],x['after_step'],x['later_partners'],x['adjacent_to_all_later']) for x in v['candidates']])

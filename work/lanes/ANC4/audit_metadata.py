import sys,json,re,itertools
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'upstream/snu-qff2026-problem'))
import tprep.qasm as tq,tprep.noise as tn
out=[]
for p in sorted(HERE.glob('grid_*.qasm')):
 j=json.loads(p.with_suffix('.json').read_text());text=p.read_text();st,lab,errs=tq.convert(text);assert not errs,errs
 prog,steps,gaps=tn.schedule(st);events=[]
 for ins,ss in zip(prog,steps):
  for qs,t in ss:
   events.append((t,ins.name,list(qs)))
 B=j['layout']['b'];D=j['data_qubits'];A=j['layout']['a'];couples=[];aa=[];exp=[]
 for b,d,a in zip(B,D,A):
  tb=max(t for t,n,qs in events if n=='CX' and qs==[b,d]);couples.append(tb)
  aa.append(max(t for t,n,qs in events if n=='CX' and qs==[d,a]))
  prev=max(t for t,n,qs in events if n=='CX' and b in qs and t<tb)
  exp.append(tb-prev-1)
 j.update(cx=text.count('\ncx '),R=min(aa),A_round=aa,B_round=couples,readout_end=max(t for t,n,qs in events),B_last_touch_exposure=exp)
 p.with_suffix('.json').write_text(json.dumps(j,indent=2)+'\n');out.append(dict(name=p.stem,R=j['R'],B_round=couples,end=j['readout_end'],exposure=exp,cx=j['cx']))
(HERE/'grid_timing_audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
for fn in ['layout_enumeration_autos','layout_tele_enumeration_autos']:
 v=json.loads((HERE/(fn+'.json')).read_text())[0];A=v['a'];H=v['hA'];nb=lambda q:{u for u in range(36) if abs(u//6-q//6)+abs(u%6-q%6)==1}
 for k in range(len(H)+1):
  good=None
  for h in itertools.combinations(H,k):
   qs=set(A)|set(h);s={A[0]}
   while True:
    nxt=s|set().union(*(nb(q) for q in s))&qs
    if nxt==s:break
    s=nxt
   if s==qs:good=list(h);break
  if good is not None:break
 v['minimum_A_helpers']=k;v['minimum_A_helper_witness']=good;(HERE/(fn+'_best.json')).write_text(json.dumps(v,indent=2)+'\n');print(fn,'distance',v['distance'],'min A helpers',k)

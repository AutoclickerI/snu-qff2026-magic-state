"""Rebuild six D4 classes with current prefix dependencies and joint82 blocks."""
from core import *
import argparse,concurrent.futures,subprocess
import co_design as CD
def prefix():
 c=provenance(read(BASE));pre=[u for u,tag in zip(c['u'],c['tags'])if tag!='suffix']
 bits={int(b)for u in pre for l in u.lines for b in re.findall(r'c\[(\d+)\]',l)}
 det=[l for l in c['tail']if set(map(int,re.findall(r'c\[(\d+)\]',l)))<=bits]
 return pre,det
CD.prefix=prefix
def solve(row,col,auto=False):
 name=f'embed_r{row}c{col}'+('_auto'if auto else'')
 a=argparse.Namespace(out=name,sym=0,row=row,col=col,option='l5_11',dhops=3,bhops=0,horizon=60,seconds=90,workers=1,seed=0,fixed_endpoints=False,hint=None,joint=True,calibration=None,early_a=False,automorphisms=auto,alap_tie=True)
 CD.solve(a)
 if not (OUT/name).with_suffix('.qasm').exists():return []
 meta=json.loads((OUT/name).with_suffix('.json').read_text())
 raw=read(OUT/name);x=meta['solver'];ends={k:v['pos'][-1]for k,v in x['tokens'].items()};perm=x['permutations']
 roundpairs=[(ends[f'd{i}'],ends[f'a{perm["a"][i]}'])for i in range(7)]+[(ends[f'b{perm["b"][i]}'],ends[f'c{perm["c"][i]}'])for i in range(7)]
 rt=[max(t for u,t in zip(raw['u'],raw['t'])if u.lines==[f'cx q[{s}],q[{tgt}];'])for s,tgt in roundpairs]
 assert len(set(rt))==1,rt
 meta['R']=rt[0];meta['round_native_audited']=rt;meta['change']=f'current-prefix joint82 full rebuild in D4 class r{row}c{col}; code automorphisms {auto}'
 (OUT/name).with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
 # Apply first-use measure-inits and the two known suffix re-encodings by
 # code index in the new layout, whenever their physical adjacency permits.
 c=read(OUT/name);us=c['u'];ts=c['t'];tail=c['tail'];R=meta['R'];bit=180;seen=set()
 for i,u in enumerate(us):
  if u.name=='RESET' and u.qs[0]not in seen:
   q=u.qs[0];us[i]=Unit([f'measure q[{q}] -> c[{bit}];']);tail.append(f'// DETECTOR c[{bit}]');bit+=1
  seen.update(u.qs)
 x=meta['solver'];T=x['tokens'];ends={k:v['pos'][-1]for k,v in T.items()}
 for sk,tk in [('c3','a5'),('c2','c1')]:
  s,t=ends[sk],ends[tk]
  if abs(s//6-t//6)+abs(s%6-t%6)!=1:continue
  si=next(i for i,u in enumerate(us)if u.name=='MEASURE'and u.qs==(s,)and ts[i]>=R+1)
  ti=next(i for i,u in enumerate(us)if u.name=='MEASURE'and u.qs==(t,)and ts[i]>=R+1)
  sb=int(re.search(r'c\[(\d+)\]',us[si].lines[0])[1]);tb=int(re.search(r'c\[(\d+)\]',us[ti].lines[0])[1])
  ts[si]=ts[ti]=R+2;us.append(Unit([f'cx q[{s}],q[{t}];']));ts.append(R+1)
  tail[:]=[l+f' c[{sb}]'if re.search(r'c\['+str(tb)+r'\]',l)else l for l in tail]
 # Timing is still the solved native schedule; score its real costs.
 c['h']=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];','creg c[256];']
 text=textof(c);h,r,t=S.qasm_ops(text);un=S.fold_units(r);nt=native_times(text,un)
 expected=[(S.compress(ts)[i],us[i].lines)for i in sorted(range(len(us)),key=lambda i:(ts[i],i))]
 actual=list(zip(nt,[u.lines for u in un]))
 if expected!=actual:
  (OUT/(name+'_timing_debug.json')).write_text(json.dumps(dict(expected=expected,actual=actual),indent=2))
  raise ValueError(('native emission changed',name,max(nt),max(ts),[(a,b)for a,b in zip(expected,actual)if a!=b][:5]))
 name2=name+'_minit_re';(OUT/name2).with_suffix('.qasm').write_text(text)
 meta2=dict(meta,cx=sum(u.name=='CX'for u in un),change=meta['change']+'; first-use measurement and legal C3→A5/C2→C1 re-encodings')
 (OUT/name2).with_suffix('.json').write_text(json.dumps(meta2,indent=2)+'\n')
 return [dict(stem=str(OUT/name),change=meta['change']),dict(stem=str(OUT/name2),change=meta2['change'])]
if __name__=='__main__':
 jobs=[]
 for row in range(3):
  for col in range(2):jobs+=solve(row,col)
 jobs+=solve(0,0,True)
 (OUT/'embeddings_manifest.json').write_text(json.dumps(jobs,indent=2)+'\n')

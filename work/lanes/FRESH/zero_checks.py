"""Insert actual noisy checks of factorized zero states in the BC resource."""
from common import *
import argparse,collections

def opportunities(c):
 ops=c['ops'];bcset=set(B+C);state={q:0 for q in bcset};seen=set();degree=0;out=[]
 init={q:int(c['meta']['init_times'][str(q)]) for q in bcset}
 R=c['meta']['R'];by=collections.defaultdict(list)
 for o in ops:by[o['t']].append(o)
 for t in range(R+1):
  busy=set()
  for o in by[t]:
   u=unit(o);busy.update(u.qs)
   if not set(u.qs)<=bcset or any(t<init[q] for q in u.qs):continue
   if u.name in ('RESET','RX') or (u.name in ('MEASURE','MX') and t==init[u.qs[0]]):
    q=u.qs[0];seen.add(q);state[q]=0
    if u.name in ('RX','MX'):state[q]=1<<degree;degree+=1
   elif u.name=='CX':
    a,b=map(int,S.QRE.findall(u.lines[0]));state[b]^=state[a]
  for q in sorted(seen-busy):
   if state[q]==0 and t<R and any(q in unit(o).qs for o in ops if t<o['t']<=R):out.append((q,t))
 return out

def add_checks(c,sites):
 c=copy.deepcopy(c);nb=max(map(int,re.findall(r'c\[(\d+)\]','\n'.join(s for o in c['ops'] for s in o['lines']))))+1
 for q,t in sites:
  c['ops'].append(dict(lines=[f'measure q[{q}] -> c[{nb}];'],t=t,id=len(c['ops'])))
  c['tail'].append(f'// DETECTOR c[{nb}]');nb+=1
 c['h']=[re.sub(r'creg c\[\d+\]',f'creg c[{nb}]',s) for s in c['h']]
 c['meta']['fresh_zero_checks']=sites
 return c

def run(stem):
 base=read(stem);ops=opportunities(base);name=Path(stem).stem
 (H/(name+'.zero_sites.json')).write_text(json.dumps(ops))
 print(name,'sites',len(ops),ops,flush=True)
 choices=[('all',ops)]
 # Individual checks and one check at each zero interval's final available step.
 latest={}
 for q,t in ops:latest[q]=max(t,latest.get(q,-1))
 choices.append(('last',list(latest.items())))
 choices += [(f'q{q}t{t}',[(q,t)]) for q,t in ops]
 ranked=[]
 for label,sites in choices:
  try:
   d=add_checks(base,sites);out=save(d,name+'_z'+label);r=score(out)
   append_result(out.name,r,'Deterministic-zero BC checks in available native slots; sites '+repr(sites));print(label,r,flush=True)
   if 'total' in r:ranked.append((r['total'],out.name,r))
  except Exception as e:append_result(name+'_z'+label,dict(error=repr(e)),'Zero-check construction error');print(label,repr(e),flush=True)
 ranked.sort();(H/(name+'.zero_rank.json')).write_text(json.dumps(ranked,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stems',nargs='+');a=p.parse_args()
 for s in a.stems:run(s)

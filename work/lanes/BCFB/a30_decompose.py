"""A attribution: unchanged exact2 API, including normalized third order."""
from a30_common import *
import argparse,collections,time,math,numpy as np
import exact2
from moments_batch import evaluate
p=argparse.ArgumentParser();p.add_argument('--procs',type=int,default=8);p.add_argument('--fast-only',action='store_true');p.add_argument('--case');a=p.parse_args()
text,md,h,us,ts,tail,init,owned,_=source();ev=exact2.Eval(text,DATA);R=md['R'];qmap=S.native_qasm_index(text);raw_to_unit={k:i for i,u in enumerate(us) for k in u.raw_indices}
bcinit={int(q):t for q,t in md['init_times'].items()};release={q:max(t for u,t in zip(us,ts) if q in u.qs and t<R and u.name in ('CX','RX','RESET','MEASURE','MX')) for q in DATA}
labels=[];units=[]
for ch in ev.m.chans:
 ins=ev.m.prog[ch['ins']];lab=ev.m.labels[ins.line_no-1];mt=re.match(r'instruction (\d+)',lab);i=raw_to_unit.get(qmap.get(int(mt[1]))) if mt else None;units.append(i);qs=set(ch['qubits']);t=ts[i] if i is not None else 99
 if ch['gap'] is not None:
  q,first,n=ch['gap']
  if q in A and first>ts[init[q]]:name='A_idle_prep' if first+n<=R else 'A_idle_post'
  elif q in DATA and first>release[q] and first<R:name='data_wait'
  elif q in B+C and first>bcinit[q]:name='BC_idle'
  else:name='pre_idle'
 elif i in owned:name='A_CX' if us[i].name=='CX' else ('A_init' if i in init.values() else 'A_check')
 elif t==R and qs&set(A) and qs&set(DATA):name='A_couple_data'
 elif t>=R and qs&set(A):name='A_couple_C' if us[i].name=='CX' else 'A_readout'
 elif t<R and qs<=set(B+C) and all(t>=bcinit[q] for q in qs):name='BC_prep'
 elif t>=R:name='round_other'
 else:name='pre_gate'
 labels.append(name)
fl=np.array([labels[c] for c in ev.fch]);fp=ev.fp.copy();AA={l for l in labels if l.startswith('A_')};PRE={'pre_idle','pre_gate'}
sets={'base':set(),'no_A_CX':{'A_CX'},'no_A_init_checks':{'A_init','A_check'},'no_A_encoder':{'A_init','A_check','A_CX'},'no_A_idle':{'A_idle_prep','A_idle_post'},'no_A_coupling':{'A_couple_data','A_couple_C'},'no_A_readout':{'A_readout'},'no_A_all':AA,'no_data_wait':{'data_wait'},'no_pre_stage':PRE,'no_A_all_data_wait':AA|{'data_wait'},'no_A_all_pre_stage':AA|PRE,'no_A_CX_data_wait':{'A_CX','data_wait'},'no_A_CX_pre_stage':{'A_CX'}|PRE}
exposure={}
for q in A:
 active=[(t,u.name,u.lines) for i,(u,t) in enumerate(zip(us,ts)) if q in u.qs and i in owned];gaps=[dict(first=c['gap'][1],steps=c['gap'][2]) for c,l in zip(ev.m.chans,labels) if c['gap'] is not None and c['gap'][0]==q and l=='A_idle_prep']
 exposure[q]=dict(init=ts[init[q]],coupling=R,live_steps=R-ts[init[q]],gates=active,idle_gaps=gaps,idle_steps=sum(g['steps'] for g in gaps))
out=dict(source='v30f',A=A,init_indices=init,owned_indices=sorted(owned),data_release=release,exposure=exposure,channels=[dict(family=l,unit=i,**ev.chan_label(c)) for c,(l,i) in enumerate(zip(labels,units))],counterfactuals={},scope='A coupling includes entire joint noise channels; ablation differences overlap. pre-stage excludes post-release data waiting and block preparation.')
def save():
 path=D/'runs'/('decomp_'+a.case+'.json') if a.case else D/'decomposition_screen.json'
 path.write_text(json.dumps(out,indent=2))
for name,off in sets.items():
 if a.case and name!=a.case:continue
 ev.fp=fp.copy();ev.fp[np.isin(fl,list(off))]=0;fast=evaluate(ev);r=dict(fast,removed_families=sorted(off),reference_verified=False)
 if not a.fast_only:
  z=exact2.run(ev,a.procs,keep_thr=1e-18 if name=='base' else 1,log=lambda *args:None,third=True);v,big=exact2.third_order(ev,a.procs);total=z['loss']+z['t3bc']+v;assert abs(total-fast['total'])<1e-14,(name,total,fast['total']);r.update(reference_verified=True,reference_second=z['loss'],reference_third=z['t3bc']+v,reference_total=total)
  if name=='base':
   pairs=collections.defaultdict(float)
   for val,i,j,*_ in z['big']:pairs[' x '.join(sorted([str(fl[i]),str(fl[j])]))]+=val
   out['pair_families']=dict(sorted(pairs.items(),key=lambda x:-x[1]));out['top_A_pairs']=[dict(loss=val,families=[str(fl[i]),str(fl[j])],faults=[ev.fault_label(i),ev.fault_label(j)]) for val,i,j,*_ in sorted(z['big'],reverse=True) if str(fl[i]).startswith('A_') or str(fl[j]).startswith('A_')][:80]
 out['counterfactuals'][name]=r;save();print(json.dumps(dict(case=name,**r)),flush=True)
f=out['counterfactuals'];out['cross_terms']={}
for x,xtag in [('A_all','no_A_all'),('A_CX','no_A_CX')]:
 for y,ytag in [('data_wait','no_data_wait'),('pre_stage','no_pre_stage')]:
  both='no_'+x+'_'+y
  if not all(k in f for k in ['base',xtag,ytag,both]):continue
  out['cross_terms'][x+' x '+y]={k:f['base'][k]-f[xtag][k]-f[ytag][k]+f[both][k] for k in ['second','third','total']}
save()

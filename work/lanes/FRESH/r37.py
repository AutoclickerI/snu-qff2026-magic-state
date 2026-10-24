"""FRESH v36b experiments with lane-local output and exact gates."""
from round35 import *
from general_atoms import analyze
import round35 as base
D=HERE/'r37';D.mkdir(exist_ok=True)
base.D=D;base.sw.__file__=str(D/'sparse_local.py');base.CACHE=D/'.xtim_cache';base.CACHE.mkdir(exist_ok=True);base.xtim.cache_dir=str(base.CACHE)
base.BASE=ROOT/'work/lanes/MAIN/v36b';BASE=base.BASE
ACC_FLOOR=.5002

def emit37(name,ops,dets,md,recipe):
 used_times=sorted({o.time for o in ops});tm={t:i for i,t in enumerate(used_times)}
 oldR=md.get('R',44);md=copy.deepcopy(md);md['R']=tm.get(oldR,oldR)
 oo=copy.deepcopy(ops)
 for o in oo:o.time=tm[o.time]
 return base.emit(name,oo,dets,md,{'base':'MAIN/v36b',**recipe})

def audit(stem):
 r=dict(stem=str(stem));
 try:
  r['ideal']=certify(stem,singles=False)
  ops,dets,md=load(stem);f.DATA=md['data_qubits'];m=f.make_model(ops,dets);e=f.Engine(m);c1=0;harm=[]
  for fault in m.faults:
   a,n=e.ntable(fault['s'],fault['d']);v=0 if n is None else fault['p']*n[fault['e']];c1+=v
   if v>1e-15:harm.append(dict(weight=float(v),label=fault['label']))
  r['c1']=float(c1);r['harmful_single_count']=len(harm);r['harmful_singles']=harm;r['static']=analyze(stem,True)
 except Exception as ex:r.update(error=repr(ex),trace=traceback.format_exc())
 Path(str(stem)+'.audit.json').write_text(json.dumps(r,indent=2));return r

def build_deferred():
 ops,dets,md=load(BASE);stems=[]
 for name,drop in [('drop_mx8',{7}),('drop_mx2',{10}),('drop_mx8_mx2',{7,10})]:
  oo=[copy.deepcopy(o) for o in ops if o.bit not in drop];dd=[]
  for row in dets:
   rr=row-drop
   if rr and rr not in dd:dd.append(rr)
  s=emit37(name,oo,dd,md,dict(drop_records=sorted(drop),mechanism='Test later-record recovery of the cultivation flag; no noiseless or single-fault test is relaxed'))
  r=audit(s);print(json.dumps({k:v for k,v in r.items() if k not in ('ideal','static','harmful_singles','trace')}),flush=True);print('STATIC',r.get('static',{}).get('prediction'),flush=True)
  if r.get('c1',1)>1e-12:print('HARM',r['harmful_singles'][:3],flush=True)
  stems.append(str(s))
 (D/'deferred_stems.json').write_text(json.dumps(stems,indent=2))

if __name__=='__main__':build_deferred()

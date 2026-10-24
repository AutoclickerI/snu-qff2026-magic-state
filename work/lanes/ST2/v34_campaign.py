"""v34m campaign configuration and complete physical-element pricing."""
import sys,json,math,random,itertools
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import acceptance as a
C=a.C;d=a.d;H=a.H;V=H/'v34'

def configure():
 a.OUT=V;a.BASE_LOSS=4.6629334817191845e-5;a.BASE_ACC=.5012004436526478
 if not getattr(d,'_v34_configured',False):
  old=d.normalize
  def norm(c):
   c=old(c);c['meta']={k:c['meta'][k]for k in ('data_qubits','cx','native_depth','round_range')};c['meta']['R']=max(c['meta']['round_range']);c['meta']['source']='MAIN/v34m campaign';return c
  d.normalize=norm;d._v34_configured=True
configure()

def physical():
 c=d.normalize(C.read(V/'base'));opts=list(a.pricing(c));oldrows={p.stem.replace('.score',''):json.loads(p.read_text())for p in (H/'knapsack/prices').glob('*.score.json')}
 # The full detector-only ledger is done in a shared exact contraction.
 # These independent reruns audit an ordinary row, the transformed row,
 # the new A flag and an echo detector.
 audit={3,17,57,64};prior=[];later=[]
 for n,x,r in opts:
  if r['family']=='base':continue
  if r['family']=='detector_only':
   if r['row']in audit:prior.append((n,x,dict(r,audit=True)))
   continue
  if r['family']=='known_measurement':
   b=r['bit'];other=f'meas_{b}_'+('reset'if r['form']=='omit'else'omit');old=oldrows.get(n);alt=oldrows.get(other)
   # Omit dominated alternate forms from the initial physical sweep. Every
   # measurement is still priced; late A/prep choices retain both forms.
   if r['time']<28 and old and alt and alt.get('ok')and old.get('ok'):
    if alt['loss']<old['loss']-1e-13 and alt['acceptance']>=old['acceptance']:continue
    if abs(alt['loss']-old['loss'])<=1e-13 and r['form']=='reset':continue
   later.append((n,x,r))
  else:prior.append((n,x,r))
 yield from prior
 # Rank old marginal efficiency only to choose launch order, never new rank.
 later.sort(key=lambda z:oldrows.get(z[0],{}).get('delta_loss',1))
 yield from later

def additions():
 import additional_prices
 yield from additional_prices.proposals()

def early_exchange():
 import knapsack_select as k
 base=d.normalize(C.read(V/'base'))
 for drop in [270,269,None]:
  for mz in [(5,),(5,12),(11,5,12)]:
   x=a.drop_echo(base,next(e for e in a.ECHO if e[-1]==drop))if drop else C.clone(base)
   for q in mz:
    i=max((i for i,(u,t)in enumerate(zip(x['u'],x['t']))if u.lines==[f'reset q[{q}];']and t>=30),key=lambda i:x['t'][i]);b=C.bit(x);x['u'][i]=C.Unit([f'measure q[{q}] -> c[{b}];']);x['tail'].append(f'// DETECTOR c[{b}]')
   yield f'exchange_{drop}_mz'+'_'.join(map(str,mz)),x,dict(family='knapsack_exchange',drop_echo=drop,mz=mz,budget_screen=True)

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('mode');p.add_argument('--workers',type=int,default=14);args=p.parse_args()
 if args.mode=='physical':a.batch(physical(),'physical',args.workers)
 elif args.mode=='additions':a.batch(additions(),'additional',args.workers)
 elif args.mode=='exchange':a.batch(early_exchange(),'exchange',args.workers)

"""Disjoint physical-tick provenance for the v36a all-orders ledger."""
from core import *
import collections
REGIONS=['prefix_ops','prefix_idles','data_hops','waiting_data','A_preparation','A_decoder','BC_resource','round','readout']
c=base();R=c['meta']['R'];ops=c['ops'];OWNER={};ASTART={};BCSTART={};HOP={};WAIT={};GUARD_WINDOWS=[]
source={1:64,8:54,9:56,15:57,16:55}
for q in A:
 enc=[o for o in ops if o.get('tag')=='encoder_a'and q in unit(o).qs and not any(f'c[{b}]'in' '.join(o['lines'])for b in(54,55))]
 first=min(o['t']for o in enc)
 # Source-zero records directly reused as Z inputs start a live A input.
 if q in source and not any(unit(o).name in('RESET','RX')and o['t']<first for o in enc):
  first=min(first,next(o['t']+1 for o in ops if f'measure q[{q}] -> c[{source[q]}];'in o['lines']))
 ASTART[q]=first
for q in B+C:BCSTART[q]=min(o['t']for o in ops if o.get('tag')=='encoder_bc'and q in unit(o).qs)
for q in range(36):
 hh=[o for o in ops if (o.get('tag')=='data_hops'or any(f'c[{b}]'in' '.join(o['lines'])for b in(54,55,56,57)))and q in unit(o).qs]
 if hh:HOP[q]=(min(o['t']for o in hh),max(o['t']for o in hh)+1)
for q,h in [(0,6),(20,19),(7,13),(10,11),(4,5)]:
 gg=[o['t']for o in ops if o.get('tag')=='wait_guard'and unit(o).name=='CX'and set(unit(o).qs)=={q,h}];assert len(gg)==2;GUARD_WINDOWS.append((q,min(gg),max(gg)+1))
# Last non-guard prefix/transfer operation on each final data wire; terminal
# T/Tdag may move within a storage interval, so do not define its start.
COUPLE={}
for q,a in zip(D,A):
 COUPLE[q]=max(o['t']for o in ops if o['lines']==[f'cx q[{q}],q[{a}];'])
 old=[o for o in ops if q in unit(o).qs and o.get('tag')in('prefix','data_hops')and unit(o).name not in('T','TDG')]
 WAIT[q]=max(o['t']for o in old)+1
for o in ops:
 u=unit(o);tag=o.get('tag','prefix');txt=' '.join(o['lines']);qs=tuple(sorted(u.qs));t=o['t']
 if tag=='wait_guard':reg='waiting_data'
 elif any(f'-> c[{b}];'in txt for b in(54,55,56,57)):reg='data_hops'
 elif tag=='data_hops':reg='data_hops'
 elif tag=='encoder_a':reg='A_preparation'
 elif tag=='encoder_bc':reg='BC_resource'
 elif tag=='decoder'or(t>=R and'measure q[8] -> c[16];'in o['lines']):reg='A_decoder'
 elif tag=='round':
  pair=tuple(map(int,S.QRE.findall(o['lines'][0])))if u.name=='CX'else None
  reg='round'if pair in list(zip(D,A))+list(zip(B,C))+list(zip(B,D))else'readout'
 else:reg='prefix_ops'
 assert(t,qs)not in OWNER;(OWNER.__setitem__((t,qs),reg))
def region(qs,t,idle=False):
 qs=tuple(sorted(qs))
 if not idle:return OWNER[(t,qs)]
 assert len(qs)==1;q=qs[0]
 if q in D and t>=COUPLE[q]:return 'round'
 if q in D and WAIT[q]<=t<COUPLE[q]:return 'waiting_data'
 if any(q==a and lo<=t<hi for a,lo,hi in GUARD_WINDOWS):return 'waiting_data'
 if q in A and t>=ASTART[q]:
  if t<R:return 'A_preparation'
  return'A_decoder'if q in(8,9,15)else'readout'
 if q in BCSTART and t>=BCSTART[q]:return'BC_resource'if t<R else'readout'
 if q in HOP and HOP[q][0]<=t<HOP[q][1]:return'data_hops'
 if t>=R:return'readout'
 return'prefix_idles'
def manifest():return dict(regions=REGIONS,A_start=ASTART,BC_start=BCSTART,data_hop_intervals=HOP,waiting_data_after=WAIT,guard_windows=GUARD_WINDOWS,data_couplings=COUPLE,R=R,definition='Operations use exact plan provenance. Source checks54..57 belong to data hops. Waiting-data includes guard operations, protected storage windows, and final-data idle time after its last non-guard prefix/transfer operation, excluding movable T/Tdag. Other idle ticks follow A/BC preparation ownership or prefix-idles. Final data idle noise is round; terminal readout/copy gates are readout; two A decoder CXs and flag MX8 are A_decoder. Mixed idle gaps are recomposed exactly when masking.')

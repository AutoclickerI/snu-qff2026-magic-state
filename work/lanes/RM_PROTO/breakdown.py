import sys,os,json
sys.dont_write_bytecode=True
from score import *
from tprep.parse import parse

def main2():
 stem=Path(sys.argv[1]);q=stem.with_suffix('.qasm').read_text();j=json.loads(stem.with_suffix('.json').read_text());ev=exact2.Eval(q,j['data_qubits'])
 last={d:max(i for i,ins in enumerate(ev.m.prog) if d in ins.qubits) for d in j['data_qubits']}
 mask=np.array([any(d in ch['qubits'] and ch['ins']==last[d] and ch['when']=='after' for d in j['data_qubits']) for ch in ev.m.chans])
 # Tail includes noise after the final data operation (the entire final CX channel,
 # including the partner's Pauli) and each terminal data idle gap.
 out={'definition':'last data-operation noise (entire CX channel) plus terminal data idle gaps; all other channels rest','tail_channels':[dict(channel=i,**ev.chan_label(i)) for i in np.flatnonzero(mask)]}
 orig=ev.fp.copy()
 for name,select in [('all',np.ones(len(mask),bool)),('tail',mask),('rest',~mask)]:
  ev.fp=orig*select[ev.fch];r=exact2.run(ev,procs=1)
  out[name]={k:float(r[k]) for k in ['loss1','loss2','loss','A1','acc2']};print(name,out[name],flush=True)
 out['cross2']=out['all']['loss2']-out['tail']['loss2']-out['rest']['loss2']
 out['fraction2_tail_including_half_cross']=(out['tail']['loss2']+.5*out['cross2'])/out['all']['loss2']
 stem.with_name(stem.name+'_breakdown').with_suffix('.json').write_text(json.dumps(out,indent=2,default=int)+'\n')
 print('cross2',out['cross2'],flush=True)
if __name__=='__main__':main2()

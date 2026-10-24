"""Exact fault-pair classification and third-order noiseless-region ablations."""
from mbp import *
import numpy as np
import fast_third

def main(a):
    stem=OUT/a.stem;text=stem.with_suffix('.qasm').read_text();meta=json.loads(stem.with_suffix('.json').read_text())
    if meta.get('grid_free'):relax(meta['n_qubits'])
    else:physical()
    nd=stim_verify(text,meta['n_qubits']);ch=check(text,meta['data_qubits'],meta['n_qubits']);assert ch['correct'],ch
    ev=exact2.Eval(text,meta['data_qubits']);assert abs(ev.fp@ev.n_single)<1e-12
    roles=[];data=set(meta['data_qubits'])
    for i,channel in enumerate(ev.m.chans):
        lab=ev.chan_label(i);region=meta['line_regions'].get(str(lab['line']),'other')
        if region in 'ABC' and any(q>=36 for q in channel['qubits']):region+=' ancilla'
        elif region in 'ABC':region+=' block'
        if lab['kind']=='idle' and set(channel['qubits'])<=data:
            region='data tail' if int(lab['steps'].split('..')[0])>=meta['R'] else 'data pre-round'
        roles.append(region)
    r=exact2.run(ev,a.procs,third=True,keep_thr=1e-18);pair={};top={}
    for loss,i,j,*_ in r['big']:
        k=' × '.join(sorted([roles[ev.fch[i]],roles[ev.fch[j]]]))
        pair[k]=pair.get(k,0)+loss
        if k not in top or loss>top[k]['loss']:top[k]=dict(loss=loss,faults=[ev.fault_label(i),ev.fault_label(j)])
    assert abs(sum(pair.values())-r['loss2'])<1e-13,(sum(pair.values()),r['loss2'])
    rows=[];original=ev.fp.copy()
    for name,remove in [('all',set()),('no A',{'A ancilla','A block'}),('no B',{'B ancilla','B block'}),('no C',{'C ancilla','C block'}),('no preparation ancillas',{'A ancilla','B ancilla','C ancilla'}),('no data pre-round',{'data pre-round'})]:
        ev.fp=original*np.array([roles[c] not in remove for c in ev.fch])
        rr=exact2.run(ev,a.procs,third=True,keep_thr=1)
        third=fast_third.third_order(ev,a.procs)[0]+rr['t3bc']
        row=dict(name=name,second=rr['loss2'],third=third,total=rr['loss']+third,expA1=math.exp(-rr['A1']));rows.append(row);print(json.dumps(row),flush=True)
    result=dict(stem=a.stem,stim_detectors=nd,check=ch,pairs=pair,top_pair_per_class=top,ablations=rows)
    stem.with_suffix('.analysis.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--procs',type=int,default=4);main(p.parse_args())

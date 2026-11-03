"""One-tick-shorter terminal product measurements without the final B read.

Reconstruct deterministic affine record checks exactly after changing bases.
This deliberately tests a different terminal contract, with noiseless validity,
single-fault screening and full noisy prices kept separate.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse, copy, json, random, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/tools'))
sys.path.insert(0,str(ROOT/'work/lanes/REBUILD20261027'))
sys.path.insert(0,str(ROOT/'work/lanes/END2_20261027'))
from qtools import price, write_stem
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from record_contract import model, complete, singles
from joint import emit

BASE=ROOT/'work/lanes/MAIN/v37j'
A_READS=[0,1,14,7,13,21,15,9,8]
B_READS=[12,26,25,11,3,28,17]
DATA=[6,20,19,10,2,22,16]


def build(mask):
    ops,ds=f.parse_current(BASE.with_suffix('.qasm').read_text())
    changed={o.bit for o in ops if o.time>=47 and o.kind in ('M','MX') and o.qs[0] in A_READS+B_READS}
    keep=[o for o in ops if not(o.time==48 and o.qs[0] in B_READS)
          and not(o.kind=='CX' and o.qs==(9,8) and o.time==47)]
    for o in keep:
        if o.time>=47 and o.kind in ('M','MX') and o.qs[0] in A_READS:
            o.time=47
            o.kind='MX' if mask>>A_READS.index(o.qs[0])&1 else 'M'
    ds=[r for r in ds if not(r&changed)]
    text=emit(keep,ds)
    m,_=model(text,DATA)
    rec=complete(m,ds)
    extras=[r for r in rec['missing'] if set(r['bits'])&changed]
    if any(r['reference'] for r in extras):
        raise ValueError('Nonzero-reference detector requires generalized emitter')
    ds += [set(r['bits']) for r in extras]
    text=emit(keep,ds)
    raw=raw_check(text,DATA)
    stem=write_stem(text,DATA,HERE/'short_tail_cand',f'short_{mask:03x}',
                    source={'source':str(BASE.relative_to(ROOT)),
                            'x_measurement_qubits':[q for i,q in enumerate(A_READS) if mask>>i&1],
                            'removed_final_B_reads':B_READS})
    return stem,text,raw


def run(count,finalists):
    # Include both homogeneous bases, the old product bases with its final
    # decoder removed, and all Hamming-distance-one/two repairs of that basis.
    oldmask=sum(1<<A_READS.index(q) for q in [0,1,9])
    masks=[511,0,oldmask]
    masks += [oldmask^(1<<i) for i in range(9)]
    masks += [oldmask^(1<<i)^(1<<j) for i in range(9) for j in range(i+1,9)]
    rng=random.Random(0)
    rest=list(set(range(512))-set(masks));rng.shuffle(rest)
    masks=list(dict.fromkeys(masks))+rest
    results=[]
    for mask in masks[:count]:
        stem,text,raw=build(mask)
        row=dict(mask=mask,stem=str(stem.relative_to(ROOT)),raw=raw)
        if raw['ok']:
            m,_=model(text,DATA);audit=singles(m)
            row['c1']=audit['c1'];row['harmful_single_components']=len(audit['harmful_faults'])
        results.append(row)
        print('screen',mask,raw['ok'],row.get('c1'),flush=True)
        (HERE/'short_tail_results.json').write_text(json.dumps(results,indent=2)+'\n')
    front=sorted((r for r in results if r['raw']['ok']),key=lambda r:(r['c1'],r['harmful_single_components']))
    for row in front[:finalists]:
        r=price(ROOT/row['stem'],1);row['price']=r
        print('price',row['mask'],r['loss'],r['acceptance'],flush=True)
        (HERE/'short_tail_results.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--count',type=int,default=64)
    ap.add_argument('--finalists',type=int,default=12);a=ap.parse_args();run(a.count,a.finalists)

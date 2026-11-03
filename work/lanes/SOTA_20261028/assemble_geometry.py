"""Assemble actual source, native A and B/C modules and price the full circuit.

All measurement outcomes are retained; the magic-state record quotient derives
the complete noiselessly deterministic acceptance contract, including measured
helper byproducts. No preparation or transport noise is suppressed.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse, copy, hashlib, json, sys, time
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'work/tools'),str(ROOT/'work/lanes/END2_20261027'),
             str(ROOT/'work/lanes/REBUILD20261027')]
from qtools import write_stem, price
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from joint import emit
from partial_contract import terminal
import record_contract


def assemble(source, a_file, bc_file, index=0, bc_shift=0, name=None, evaluate=True):
    began=time.perf_counter()
    source_doc=json.loads(Path(source).read_text())
    base=Path(source_doc['stem'])
    # Saved receipts retain their original absolute path. A new checkout uses
    # the same repository-relative artifact when that original path is absent.
    if not base.with_suffix('.qasm').exists() and '/work/lanes/' in str(base):
        base=ROOT/'work/lanes'/str(base).split('/work/lanes/',1)[1]
    roles=source_doc['roles']; data=roles['D']
    ops,dets=f.parse_current(base.with_suffix('.qasm').read_text())
    ops=copy.deepcopy(ops); dets=copy.deepcopy(dets)
    if a_file=='-':
        aa=dict(operations=[])
    else:
        a_doc=json.loads(Path(a_file).read_text())
        aa=a_doc['candidates'][index]
        assert aa['A']==roles['A']
    bc=json.loads(Path(bc_file).read_text())
    assert bc['roles']==roles
    bit=max(o.bit or 0 for o in ops)+1
    modules=[]
    for label,module,shift in [('A',aa,0),('BC',bc,bc_shift)]:
        added=[]
        for row in module['operations']:
            kind=row['kind']; qs=tuple(row['qs']); t=int(row['time'])+shift
            record=bit if kind in ('M','MX') else None
            if record is not None: bit+=1
            op=f.Op(kind,qs,t,record); ops.append(op); added.append(op)
        modules.append((label,added))
    # A/BC module reads may share the first terminal clock if they only touch
    # released helpers. A resource qubit must finish its preparation first.
    resource=set(roles['A']+roles['B']+roles['C'])
    tail=max(o.time+1 for o in ops if set(o.qs)&(resource|set(data)))
    if any(o.time>tail for o in ops): tail=max(o.time for o in ops)
    first_terminal_bit=bit
    for kind,qs,t,record in terminal(roles,source_doc['square_mask']):
        ops.append(f.Op(kind,tuple(qs),tail+t,None if record is None else first_terminal_bit+record))
    ops.sort(key=lambda o:(o.time,o.kind,o.qs))
    occupied={}
    for o in ops:
        if o.kind=='CX':
            a,b=o.qs
            assert abs(a//6-b//6)+abs(a%6-b%6)==1,o
        for q in o.qs:
            key=(o.time,q)
            assert key not in occupied,(o,occupied.get(key))
            occupied[key]=o
    f.DATA=data
    contract=record_contract.complete(f.make_model(ops,dets),dets)
    assert not any(row['reference'] for row in contract['missing']),contract
    dets += [set(row['bits']) for row in contract['missing']]
    text=emit(ops,dets)
    info=dict(source=str(source),a_file=str(a_file),a_index=index,
              bc_file=str(bc_file),bc_shift=bc_shift,roles=roles,
              square_mask=source_doc['square_mask'],tail=tail,
              cx=sum(o.kind=='CX' for o in ops),ticks=max(o.time for o in ops)+1,
              detectors=len(dets),record_contract=contract,
              qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),
              raw=raw_check(text,data))
    stem=write_stem(text,data,HERE/'geometry_cand',name or f'geometry_a{index}_{Path(bc_file).stem}',source=info)
    info['stem']=str(stem)
    print(json.dumps({k:info[k] for k in ('stem','cx','ticks','tail','raw')}),flush=True)
    if info['raw']['ok']:
        f.DATA=data
        info['singles']=record_contract.singles(f.make_model(*f.parse_current(text)))
        print('SINGLES',info['singles']['c1'],len(info['singles']['harmful_faults']),flush=True)
        if evaluate:
            info['exact']=price(stem,processes=1)
            print('EXACT',info['exact']['loss'],info['exact']['acceptance'],flush=True)
    info['seconds']=time.perf_counter()-began
    stem.with_suffix('.result.json').write_text(json.dumps(info,indent=2)+'\n')
    return info


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('source');ap.add_argument('a_file');ap.add_argument('bc_file')
    ap.add_argument('--a-index',type=int,default=0)
    ap.add_argument('--bc-shift',type=int,default=0)
    ap.add_argument('--name');ap.add_argument('--no-price',action='store_true')
    args=ap.parse_args()
    assemble(args.source,args.a_file,args.bc_file,args.a_index,args.bc_shift,args.name,not args.no_price)

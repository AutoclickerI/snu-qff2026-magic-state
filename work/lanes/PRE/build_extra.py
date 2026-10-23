from common import *
assert emit(OPS,TIMES,DETS,22)==(ROOT/'work/submissions/v12_L5lns12.qasm').read_text(), 'baseline schedule does not reconstruct'
save('v12_reference',OPS,TIMES,DETS,22,NPRE,'Unchanged v12; saved schedule reproduced byte-for-byte')
chunk=cp.extract_chunk('make_chunk_d3_double_cat_check',cp.UP+'_cultivation_stage.py')
for extra in (1,2):
    c=cp.build(stages=('inject','check'),s_to='Tswap')
    for _ in range(extra):cp.run_chunk(c,chunk,s_to='Tswap')
    pre=list(c.sops)
    last={q:i for i,(k,qs,b) in enumerate(pre) if k=='MX' for q in qs}
    for q in (13,1,9):
        i=last[q];k,qs,b=pre[i];pre[i]=('MX_KEEP',qs,b)
    sh=c.nbits-14
    suffix=[(k,qs,b+sh if b is not None else None) for k,qs,b in OPS[NPRE:]]
    dets=c.detectors+[[b+sh for b in d] for d in DETS[17:]]
    ops=pre+suffix
    for seed in (0,1,4,8):
        times=pack(ops,TIMES[NPRE:],len(pre),seed)
        name=f'extra{extra}_s{seed}'
        save(name,ops,times,dets,c.nbits+8,len(pre),f'{extra} additional upstream double-cat H_XY checks; fixed v12 suffix; ALAP seed {seed}')
        validate(name,10000)

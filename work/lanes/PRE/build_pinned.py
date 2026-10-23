from common import *
# Insert an extra check before v12's existing last check and pin that last check
# and all final-cycle nodes to their original relative schedule. This isolates
# the effect of additional cultivation from last-check scheduling differences.
chunk=cp.extract_chunk('make_chunk_d3_double_cat_check',cp.UP+'_cultivation_stage.py')
for extra in (1,2):
    c=cp.build(stages=('inject',),s_to='Tswap')
    for _ in range(extra):cp.run_chunk(c,chunk,s_to='Tswap')
    pre=[('MX_KEEP' if b==6 else k,qs,b) for k,qs,b in c.sops]
    sh=7*extra
    tail=[(k,qs,b+sh if b is not None and b>=7 else b) for k,qs,b in OPS[85:]]
    dets=c.detectors+[[b+sh if b>=7 else b for b in d] for d in DETS[7:]]
    for seed in (0,4):
        ops=pre+tail;times=pack(ops,TIMES[85:],len(pre),seed)
        name=f'extra{extra}_pinned_s{seed}'
        save(name,ops,times,dets,22+sh,len(pre)+NPRE-85,f'{extra} extra check; original v12 last check and suffix timing pinned; seed{seed}')
        validate(name,10000)
# Central repeat replacing reset is a drop-in one-node change at the same time.
ops=list(OPS);ops[110]=('MX_KEEP',OPS[110][1],7);ops[111]=('MX_KEEP',OPS[111][1],22)
save('central_retain_pinned',ops,TIMES,DETS+[[7,22]],23,NPRE,'Replace central RX by repeated native MX, retain central X state; original timing fixed')
validate('central_retain_pinned',10000)

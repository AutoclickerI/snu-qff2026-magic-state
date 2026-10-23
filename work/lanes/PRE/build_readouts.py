from common import *

for mode in ('central_verify','central_retain','late_verify','all_verify'):
    pre=[];dets=copy.deepcopy(DETS);nextbit=22
    for i,(k,qs,b) in enumerate(OPS[:NPRE]):
        chosen=(b==7 and mode in ('central_verify','central_retain','all_verify')) or (b in (8,9,10,11,12,13) and mode in ('late_verify','all_verify'))
        if chosen:
            pre.append(('MX_KEEP',qs,b))
            pre.append(('MX_KEEP',qs,nextbit))
            dets.append([b,nextbit]);nextbit+=1
        elif mode=='central_retain' and i==111:
            # A verified +X central outcome supplies the state formerly reset to +X.
            continue
        else:pre.append((k,qs,b))
    ops=pre+OPS[NPRE:]
    for seed in (0,4):
        times=pack(ops,TIMES[NPRE:],len(pre),seed)
        name=f'{mode}_s{seed}'
        save(name,ops,times,dets,nextbit,len(pre),f'{mode}, repeated native X readout with parity detector, fixed v12 suffix, seed{seed}')
        validate(name,10000)

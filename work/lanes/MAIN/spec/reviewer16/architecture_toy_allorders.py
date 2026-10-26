"""Exact finite-p distribution for architecture_probe's relaxed encoded tails.

The noiseless boundary state is U^{-1}(|T_L>_D |0_L>_E |+_L>_2 |+_L>_3).
It is supplied perfectly; no claim of realizable inexpensive preparation.
All gates, idles and final measurement flips in the three tail ticks are noisy.
"""
import contextlib,io,json,runpy
import numpy as np

with contextlib.redirect_stdout(io.StringIO()):a=runpy.run_path('architecture_probe.py')
rows=a['rows'];final=a['final'];cxprop=a['cxprop']
p=.001

def calc(layers):
    # Per index: output X,Z and record-2,record-3 flip bits.
    channels=[]
    def propagated(x,z,suffix):
        for layer in suffix:
            for aa,b in layer:x,z=cxprop(x,z,aa,b)
        return (x&1)|((z&1)<<1)|(((z>>2)&1)<<2)|(((z>>3)&1)<<3)
    for t,layer in enumerate(layers):
        used={v for e in layer for v in e}
        for aa,b in layer:
            ch=np.zeros(16);ch[0]=1-p
            for pa in range(4):
                for pb in range(4):
                    if pa==pb==0:continue
                    x=((pa&1)<<aa)|((pb&1)<<b)
                    z=(((pa>>1)&1)<<aa)|(((pb>>1)&1)<<b)
                    ch[propagated(x,z,layers[t+1:])]+=p/15
            channels.append(ch)
        for qubit in range(4):
            if qubit in used or (t==len(layers)-1 and qubit in (2,3)):continue
            ch=np.zeros(16);ch[0]=1-p
            for pa in (1,2,3):
                ch[propagated((pa&1)<<qubit,((pa>>1)&1)<<qubit,layers[t+1:])]+=p/3
            channels.append(ch)
    for record_bit in (4,8):
        ch=np.zeros(16);ch[0]=1-p;ch[record_bit]=p;channels.append(ch)
    local=np.zeros(16);local[0]=1;idx=np.arange(16)
    for ch in channels:
        local=sum(ch[k]*local[idx^k] for k in range(16))
    dist=np.zeros(1<<16);dist[0]=1;idx=np.arange(1<<16)
    for coordinate in range(1,8):
        col=coordinate|8
        masks=[sum((col<<(4*b)) for b in range(4) if val>>b&1) for val in range(16)]
        dist=sum(local[v]*dist[idx^mask] for v,mask in enumerate(masks))
    # Zero record Hamming syndromes AND zero logical-X read parity.
    accepted=dist[:256];A=float(accepted.sum());N=0
    for v,pv in enumerate(accepted):
        sx=v&15;sz=v>>4
        lx=((sx>>3)^bool(sx&7))&1;lz=((sz>>3)^bool(sz&7))&1
        loss=(.5 if lx else 1.) if lz else (.5 if lx else 0.)
        N+=float(pv)*loss
    assert abs(float(dist.sum())-1)<1e-12
    return dict(L=N/A,A=A,N=N)

r=rows[0]
out={key:calc([tuple(map(tuple,r[key]['l0'])),tuple(map(tuple,r[key]['l1'])),final]) for key in ('greedy','joint')}
out['scope']='Exact three-tick perfect-boundary toy; physical preparation and real-prefix compatibility excluded.'
print(json.dumps(out,indent=2))

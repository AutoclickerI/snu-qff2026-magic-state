"""Independent terminal-channel certificate. No reviewer code imported."""
import itertools, json
from pathlib import Path
import numpy as np

OUT = Path(__file__).resolve().parent
P = .001
IDX = np.arange(256)

def signature(q, pauli):
    x, z = pauli in 'XY', pauli in 'YZ'
    return ((q + 1) if x else 0) ^ (((q + 1) << 3) if z else 0) ^ (int(x) << 6) ^ (int(z) << 7)

def channel(qs, probability):
    vals = list(itertools.product('IXYZ', repeat=len(qs)))
    return [(sum_signature(qs, ps), 1-probability if k == 0 else probability/(len(vals)-1)) for k, ps in enumerate(vals)]

def sum_signature(qs, ps):
    s = 0
    for q,p in zip(qs,ps): s ^= signature(q,p)
    return s

def distribution(channels):
    v = np.zeros(256); v[0] = 1
    for ch in channels:
        w = np.zeros(256)
        for s,p in ch: w += p * v[IDX ^ s]
        v = w
    return v

def spectrum(v):
    sx, sz = IDX & 7, (IDX >> 3) & 7
    px, pz = (IDX >> 6) & 1, (IDX >> 7) & 1
    ax=[]; ay=[]
    for a in range(64):
        x, z = a & 7, a >> 3
        ex = pz ^ ((sz ^ z) != 0)
        ey = px ^ pz ^ ((sx ^ x) != 0) ^ ((sz ^ z) != 0)
        ax.append(float(v @ (1 - 2*ex.astype(int))))
        ay.append(float(v @ (1 - 2*ey.astype(int))))
    norms=np.sqrt((np.array(ax)**2 + np.array(ay)**2)/2)
    k=int(np.argmax(norms))
    return dict(minimum_loss=(1-float(norms[k]))/2, best_syndrome=k,
                perfect_T_loss=(2-ax[0]-ay[0])/4, ax0=ax[0], ay0=ay[0], total=float(v.sum()))

def matchings(qs):
    if not qs: yield []; return
    q,*others=qs
    for rest in matchings(others): yield [(q,)]+rest
    for k,r in enumerate(others):
        for rest in matchings(others[:k]+others[k+1:]): yield [(q,r)]+rest

def main():
    rows=[]
    for m in matchings(list(range(7))):
        ch=[channel(qs,P if len(qs)==2 else 4*P/5) for qs in m]
        rows.append(dict(matching=m,**spectrum(distribution(ch))))
    summary={str(n):min((r for r in rows if sum(len(q)==2 for q in r['matching'])==n),key=lambda r:r['minimum_loss']) for n in range(4)}
    cases={}
    for label,probs in [('one_idle',[P]),('one_terminal_helper',[4*P/5]),
                        ('two_idle',[P,P]),('idle_then_helper',[P,4*P/5]),
                        ('two_inverse_CX_helpers',[.75*(1-(1-16*P/15)**2)]),
                        ('measured_CX_then_idle',[2*P/(5-8*P/3),P])]:
        cases[label]=spectrum(distribution([channel((q,),p) for p in probs for q in range(7)]))
    result=dict(origin='independent, before reviewer18 read', all_terminal_matchings=len(rows), minima_by_output_pairs=summary,idealized_cases=cases)
    (OUT/'experiments/independent_spectrum.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__': main()

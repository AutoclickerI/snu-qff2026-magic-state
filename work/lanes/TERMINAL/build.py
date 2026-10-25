"""Grid-free, legal-gate terminal witnesses. Preparation noise is selected by price.py."""
import json
from pathlib import Path
from build_rounds_source import Circuit,D,A,B,C
H=Path(__file__).resolve().parent
F=list(range(28,35))

def build(name,helper=None,square=False,cut=7,earlier=False):
    c=Circuit();c.magic()
    c.prep(A,3,True);c.prep(B,3,False);c.prep(C,3,square)
    for d,a,b,k in zip(D,A,B,C):
        c.cx(7,d,a);c.cx(7,b,k);c.cx(8,b,d)
        if square:c.cx(8,k,a)
    c.readblock(9 if square else 8,A)
    c.readblock(9,B,True)
    c.readblock(9 if square else 8,C,square,True)
    if helper:
        for f,d in zip(F,D):
            if helper=='measX':
                bit=c.read(8,f);c.dets.append([bit])
            else:c.reset(8,f,helper=='resetZ')
            c.cx(9,d,f) if helper=='resetZ' else c.cx(9,f,d)
    c.save(name,noise_start=cut,round_start=7,helper=helper,
           scope='two-check round' if cut==7 else 'last check, helper preparation, and reads',
           interpretation='earlier last check / concurrent read and helper CX' if earlier else 'replace read-tick idle')

if __name__=='__main__':
    for cut in (7,8):
        build(f'class_cut{cut}',cut=cut)
        build(f'square_cut{cut}',square=True,cut=cut)
        for h in ('resetX','resetZ','measX'):
            build(f'a_{h}_cut{cut}',h,cut=cut)
            build(f'b_{h}_cut{cut}',h,cut=cut,earlier=True)
    for checker in ('A','C'):
        for cut in (7,8):
            c=Circuit();c.magic();c.prep(A,3,True);c.prep(B,3,False);c.prep(C,3,False)
            for d,a,b,k,f in zip(D,A,B,C,F):
                c.cx(7,d,a);c.cx(7,b,k);c.reset(7,f)
                c.cx(8,b,d);c.cx(8,f,a if checker=='A' else k);c.cx(9,f,d)
            c.readblock(9 if checker=='A' else 8,A)
            c.readblock(9,B,True)
            c.readblock(9 if checker=='C' else 8,C,False,True)
            c.save(f'ab_checked{checker}_cut{cut}',noise_start=cut,round_start=7,
                   helper='reset then verified by an existing readout',checker=checker)
    build('e_zero_syndrome_check',cut=7)
    meta=json.loads((H/'builds/v37b.json').read_text())
    for cut in (46,47,48):
        name=f'v37b_timecut{cut}'
        (H/'builds'/f'{name}.qasm').write_bytes((H/'builds/v37b.qasm').read_bytes())
        (H/'builds'/f'{name}.json').write_text(json.dumps(dict(meta,noise_start=cut)))

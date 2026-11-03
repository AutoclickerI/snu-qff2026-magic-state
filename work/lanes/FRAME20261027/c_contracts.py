from frame_tools import *
from teleport_b import build,D,B,C,A
import itertools,traceback

def xor(rows):
    result=set()
    for row in rows:result^=row
    return result

def variant(base,name,checks,fx=set(),fz=set()):
    ops,dets,md=load(base)
    cr=[]
    for j in range(7):
        candidates=[row for row in dets if 337+j in row]
        assert len(candidates)==1,candidates
        cr.append(candidates[0])
    dd=[row for row in dets if not any(337<=b<=343 for b in row)]
    dd += [xor([cr[j] for j in check]) for check in checks]
    oldframes=parse_frames(base.with_suffix('.qasm').read_text())
    frames={P:(oldframes[P][0],oldframes[P][1]^xor([cr[j] for j in bits])) for P,bits in [('X',fx),('Z',fz)]}
    return emit(name,ops,dd,md['data_qubits'],frames,{'architecture':'B-output teleport; relaxed C detector contract','checks':[sorted(r) for r in checks]})

if __name__=='__main__':
    base=OUT/'btele_fresh'
    if not base.with_suffix('.qasm').exists():build('btele_fresh')
    variants=[('csyndrome',list(f.SUPPORTS)),('ccode',list(f.SUPPORTS)+[set(range(7))]),
              ('cparity',[set(range(7))])]
    for j in range(7):
        variants.append((f'cdrop{j}',[{i} for i in range(7) if i!=j]))
    for name,checks in variants:
        s=variant(base,name,checks)
        try: print(json.dumps(price(s)),flush=True)
        except Exception:traceback.print_exc()


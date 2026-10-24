import sys, json, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from abl import Ctx, ALL
import chan
R = chan.ROLES
D, A, B, C = set(R['D']), set(R['A']), set(R['B']), set(R['C'])

def comp(f, q):
    """Pauli letter of fault f on qubit q ('I' if absent)."""
    if q not in f['qs']:
        return 'I'
    return f['pauli'][list(f['qs']).index(q)]

def specs():
    s = {}
    s['base'] = ALL
    # 1. data idles at 44 forced by the A decoder's early coupling
    s['d1021_idle44'] = lambda md, f: 0. if (md['kind'] == 'idle' and md['qs'][0] in (10, 21) and md['t0'] == 44) else 1.
    # 2. data waiting idles (after prefix, before D->A), split by Pauli type
    wait = lambda md: md['kind'] == 'idle' and md['qs'][0] in D and md['t0'] >= 30 and md['t0'] + md['n'] - 1 <= 43
    s['wait_all'] = lambda md, f: 0. if wait(md) else 1.
    s['wait_X'] = lambda md, f: 0. if (wait(md) and f['pauli'] in 'XY') else 1.
    s['wait_Z'] = lambda md, f: 0. if (wait(md) and f['pauli'] in 'ZY') else 1.
    # 3. masking agents on A: X-type components on A cells during A's role (t>=36), incl. readout flips
    def a_x(md, f):
        if md['t0'] < 36: return 1.
        qa = [q for q in md['qs'] if q in A]
        if not qa: return 1.
        if md['kind'] == 'mflip': return 0. if md['qs'][0] in A else 1.
        return 0. if any(comp(f, q) in 'XY' for q in qa) and all(comp(f, q) in 'IXY' for q in md['qs'] if q not in A or True) and not any((q in D and comp(f, q) != 'I') for q in md['qs']) else 1.
    s['A_Xtype'] = a_x
    def a_z(md, f):
        if md['t0'] < 36 or md['kind'] == 'mflip': return 1.
        qa = [q for q in md['qs'] if q in A]
        if not qa: return 1.
        return 0. if any(comp(f, q) in 'ZY' for q in qa) and not any((q not in A and comp(f, q) != 'I') for q in md['qs']) else 1.
    s['A_Ztype'] = a_z
    s['A_all36'] = lambda md, f: 0. if (md['t0'] >= 36 and all(q in A for q in md['qs'])) else 1.
    # 4. masking agents on B: Z-type components on B cells (t>=32) excluding data partner components, incl. B readout flips
    def b_z(md, f):
        if md['t0'] < 32: return 1.
        qb = [q for q in md['qs'] if q in B]
        if not qb: return 1.
        if md['kind'] == 'mflip': return 0.
        return 0. if any(comp(f, q) in 'ZY' for q in qb) and not any((q not in B and comp(f, q) != 'I') for q in md['qs']) else 1.
    s['B_Ztype'] = b_z
    def b_x(md, f):
        if md['t0'] < 32 or md['kind'] == 'mflip': return 1.
        qb = [q for q in md['qs'] if q in B]
        if not qb: return 1.
        return 0. if any(comp(f, q) in 'XY' for q in qb) and not any((q in D and comp(f, q) != 'I') for q in md['qs']) else 1.
    s['B_Xtype'] = b_x
    s['BC_all32'] = lambda md, f: 0. if (md['t0'] >= 32 and all(q in B | C for q in md['qs']) and not (md['t0'] == 44 and md['kind'] == 'g2')) else 1.
    # 5. readout flips by role (t>=36)
    for r, S in (('A', A), ('B', B), ('C', C)):
        s[f'mflip_{r}'] = (lambda S: lambda md, f: 0. if (md['kind'] == 'mflip' and md['t0'] >= 36 and md['qs'][0] in S) else 1.)(S)
    # 6. helpers outside A,B,C,D roles after t>=17 (guards, echoes, copies)
    s['helpers'] = lambda md, f: 0. if (md['t0'] >= 17 and all(q not in (A | B | C | D) for q in md['qs'])) else 1.
    return s

if __name__ == '__main__':
    t = time.time()
    ctx = Ctx(sys.argv[1])
    res = ctx.many(specs())
    b = res['base']
    for n, r in res.items():
        print(f"{n:16s} loss {r['loss']:.6e}  gain {b['loss']-r['loss']:+.3e} ({100*(b['loss']-r['loss'])/b['loss']:+.2f}%)  acc {r['acceptance']:.5f} ({r['acceptance']-b['acceptance']:+.5f})")
    Path(sys.argv[2]).write_text(json.dumps(res, indent=1))
    print(time.time() - t)

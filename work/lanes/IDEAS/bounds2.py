import sys, json, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from abl import Ctx, ALL
from bounds1 import comp, A, B, C, D
def specs():
    s = {'base': ALL}
    # B X-type split: round B->C CX (t44) vs resource (t<44)
    def bx(lo, hi):
        def f(md, fl):
            if not (lo <= md['t0'] <= hi) or md['kind'] == 'mflip': return 1.
            qb = [q for q in md['qs'] if q in B]
            if not qb: return 1.
            return 0. if any(comp(fl, q) in 'XY' for q in qb) and not any((q in D and comp(fl, q) != 'I') for q in md['qs']) else 1.
        return f
    s['BX_round44'] = bx(44, 44)
    s['BX_res32_43'] = bx(32, 43)
    # C Z-type (masking via B at B->C) and C X-type (masks B X; rejection)
    def cz(md, fl):
        if md['t0'] < 32 or md['t0'] > 44: return 1.
        qc = [q for q in md['qs'] if q in C]
        if not qc: return 1.
        return 0. if any(comp(fl, q) in 'ZY' for q in qc) and all(comp(fl, q) == 'I' for q in md['qs'] if q not in C) else 1.
    s['C_Ztype'] = cz
    def cx_(md, fl):
        if md['t0'] < 32: return 1.
        qc = [q for q in md['qs'] if q in C]
        if not qc: return 1.
        if md['kind'] == 'mflip': return 0.
        return 0. if any(comp(fl, q) in 'XY' for q in qc) and all(comp(fl, q) == 'I' for q in md['qs'] if q not in C) else 1.
    s['C_Xtype'] = cx_
    # all Z-type masking for the B syndrome: B and C Z-type (C before 44) + B mflip
    s['mask_Zsyn'] = lambda md, fl: min(cz(md, fl), (0. if (md['kind'] == 'mflip' and md['qs'][0] in B and md['t0'] >= 32) else 1.),
                                        (0. if (md['t0'] >= 32 and md['kind'] != 'mflip' and any(q in B for q in md['qs']) and any(comp(fl, q) in 'ZY' for q in md['qs'] if q in B) and all(comp(fl, q) == 'I' for q in md['qs'] if q not in B)) else 1.))
    # prefix periods: all noise with t0 < 13; 13..30; 31..37 on non-A/B/C role qubits
    s['pre_0_12'] = lambda md, fl: 0. if md['t0'] <= 12 else 1.
    s['pre_13_30'] = lambda md, fl: 0. if (13 <= md['t0'] <= 30 and not (md['kind'] == 'idle' and md['t0'] + md['n'] - 1 > 30)) else 1.
    # data idles at the final tick ideal for reference (TERM's floor component)
    s['final_idle'] = lambda md, fl: 0. if (md['kind'] == 'idle' and md['t0'] == 46) else 1.
    # A encoder only (36..43, A-only channels), X-type vs Z-type components
    def aenc(t):
        def f(md, fl):
            if not (36 <= md['t0'] <= 43) or not all(q in A for q in md['qs']) or md['kind'] == 'mflip': return 1.
            return 0. if any(comp(fl, q) in t for q in md['qs']) else 1.
        return f
    s['Aenc_X'] = aenc('XY'); s['Aenc_Z'] = aenc('ZY')
    # round D->A CX data-side X/Y components with A-side I/Z (unflagged), and B->D data-side
    def comp_ideal(kind_pred, side_q, side_pauli, other_q, other_pauli):
        return None
    s['DA_unflaggedX'] = lambda md, fl: 0. if (md['kind'] == 'g2' and md['t0'] in (43, 44) and md['qs'][0] in D and md['qs'][1] in A and comp(fl, md['qs'][0]) in 'XY' and comp(fl, md['qs'][1]) in 'IZ') else 1.
    s['BC44_unflaggedX'] = lambda md, fl: 0. if (md['kind'] == 'g2' and md['t0'] == 44 and md['qs'][0] in B and md['qs'][1] in C and comp(fl, md['qs'][0]) in 'XY' and comp(fl, md['qs'][1]) in 'IZ') else 1.
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

import sys, json, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from abl import Ctx, ALL
from bounds1 import comp, A, B, C, D
FLAG = {8, 9, 15}
def specs():
    s = {'base': ALL}
    # flag masking: Z-type components on flag-support qubits from t>=43 (incl. MX8 flip), no data component
    def fm(md, fl):
        if md['t0'] < 43: return 1.
        if md['kind'] == 'mflip': return 0. if md['qs'][0] == 8 else 1.
        qa = [q for q in md['qs'] if q in FLAG]
        if not qa: return 1.
        return 0. if any(comp(fl, q) in 'ZY' for q in qa) and all(comp(fl, q) == 'I' for q in md['qs'] if q in D) else 1.
    s['flag_mask'] = fm
    s['mflip_A8'] = lambda md, fl: 0. if (md['kind'] == 'mflip' and md['qs'][0] == 8 and md['t0'] == 46) else 1.
    # decoder CX noise ideal (9->15 @44, 8->9 @45)
    s['dec_cx'] = lambda md, fl: 0. if (md['kind'] == 'g2' and set(md['qs']) in ({9, 15}, {8, 9}) and md['t0'] in (44, 45)) else 1.
    # readout edges 14->15, 17->16 @45 ideal
    s['edges45'] = lambda md, fl: 0. if (md['kind'] == 'g2' and set(md['qs']) in ({14, 15}, {16, 17}) and md['t0'] == 45) else 1.
    # C copies (CX c->h @45) ideal + helper noise
    s['copies'] = lambda md, fl: 0. if ((md['kind'] == 'g2' and md['t0'] == 45 and any(q in (18, 31, 34, 35) for q in md['qs'])) or all(q in (18, 31, 34, 35) for q in md['qs'])) else 1.
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

"""Channel metadata for the sparse/adjoint model: kind, qubits, tick, idle run, role."""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import frontend as fa
from judge_subset.noise import noise_blocks, schedule

ROLES = dict(D=[0, 20, 7, 10, 3, 22, 21], A=[1, 14, 8, 9, 2, 16, 15], B=[6, 26, 13, 11, 4, 23, 27], C=[12, 25, 19, 17, 5, 29, 28])


def classify(m):
    """List (per channel id) of dicts: kind in init/mflip/mafter/reset/g1/g2/idle, qs, t0, n, line, op."""
    text = m.native
    prog, blocks = noise_blocks(text, .001)
    _, steps, gaps = schedule(text)
    gaps_by_ins = {}
    for g in gaps:
        gaps_by_ins.setdefault(g[0], []).append(g)
    out = []
    for c in m.chans:
        ii, jl = c['ins'], c['jl']
        block = blocks[ii]
        ins = prog[ii]
        k = block.index(ins.text)
        nidle = len(gaps_by_ins.get(ii, []))
        lab = m.labels[ii]
        t = lab.time
        d = dict(qs=tuple(c['qs']), line=lab.line, op=lab.kind, t0=t, n=1, p=c['p'])
        if jl >= len(block) - nidle:
            g = gaps_by_ins[ii][jl - (len(block) - nidle)]
            d.update(kind='idle', t0=g[2], n=g[3])
        elif jl < k:
            d['kind'] = 'mflip' if (block[jl].startswith(('X_ERROR', 'Z_ERROR')) and ins.name in ('M', 'MX') and jl == k - 1) else 'init'
        else:
            nm = block[jl].split('(')[0]
            if ins.name in ('M', 'MX'):
                d['kind'] = 'mafter'
            elif ins.name in ('R', 'RX'):
                d['kind'] = 'reset'
            elif nm == 'DEPOLARIZE2':
                d['kind'] = 'g2'
            else:
                d['kind'] = 'g1'
        out.append(d)
    return out


def role(q):
    for r, qs in ROLES.items():
        if q in qs:
            return r
    return 'H'

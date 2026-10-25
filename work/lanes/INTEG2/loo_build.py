"""Leave-one-out circuits on a base plan (default i2_v36f): every INTEG/PRECELL/BFLAG gadget of v36f removed in turn.
usage: loo_build.py [base] -> c/<base>__L_<element>, list in loo_<base>.list"""
from elements import *

base = sys.argv[1] if len(sys.argv) > 1 else 'i2_v36f'
c0 = read(C / base)
S1 = singles(c0)


def rmcx(t, a, b):
    return ('rm', t, (a, b), 'CX')


def mbit(t, q):
    return bits_of(find(c0, t, q, 'MEASURE' if any(unit(o).name == 'MEASURE' for o in c0['ops'] if o['t'] == t and q in unit(o).qs) else 'MX'))[0]


def session(h, cxs, tm, mname, init=None, extra=()):
    """remove CX list [(t,a,b)], the measurement of h at tm (+ its singleton detector) and the init (t, name)."""
    b = bits_of(find(c0, tm, h, mname))[0]
    ed = [rmcx(*x) for x in cxs] + [('rm', tm, h, mname), ('rmdet', b)]
    if init:
        ed.append(('rm', init[0], h, init[1]))
    return ed + list(extra)


E = {}
# live CX pairs (INTEG) and r3's cancelling pairs
for a, b, t in [(0, 6, 15), (3, 4, 20), (3, 4, 22), (3, 4, 24), (3, 4, 26), (4, 10, 10), (4, 5, 14), (6, 7, 21), (9, 10, 21),
                (9, 10, 24), (9, 10, 26), (11, 10, 30), (14, 20, 19), (14, 13, 21), (14, 15, 23), (15, 16, 15), (15, 14, 26),
                (20, 21, 22), (20, 21, 24), (20, 21, 26), (20, 14, 40), (4, 5, 38), (4, 5, 41)]:
    E[f'pair_{a}_{b}_{t}'] = [rmcx(t, a, b), rmcx(t + 1, a, b)]
# INTEG echoes
E['echoX_15_h21_4_11'] = session(21, [(4, 21, 15), (11, 21, 15)], 12, 'MX', (3, 'RX'))
E['echoX_15_h21_14_17'] = [rmcx(14, 21, 15), rmcx(17, 21, 15)]  # keep RX13/MX18 (guard h22 sits on q21 at 15-16)
E['echoX_15_h21_14_17+g22'] = session(21, [(14, 21, 15), (17, 21, 15)], 18, 'MX', (13, 'RX')) + \
    session(22, [(15, 22, 21), (16, 22, 21)], 17, 'MEASURE', (14, 'RESET'))
E['echoX_20_h26_11_13'] = [rmcx(11, 26, 20), rmcx(13, 26, 20)]
E['echoZ_6_h12_19_24'] = session(12, [(19, 6, 12), (24, 6, 12)], 25, 'MEASURE', (18, 'RESET'))
E['echoX_13_h12_28_30'] = [rmcx(28, 12, 13), rmcx(30, 12, 13)]
E['ext_pre_13_h12_6'] = [rmcx(27, 6, 12)]
E['echoX_13_h12_28_30+ext'] = session(12, [(27, 6, 12), (28, 12, 13), (30, 12, 13)], 31, 'MX', (26, 'RX'))
E['echoX_15_h16_21_28'] = [rmcx(21, 16, 15), rmcx(28, 16, 15)]
E['ext_pre_15_h16_10'] = [rmcx(20, 10, 16)]
E['echoX_15_h16_21_28+ext'] = session(16, [(20, 10, 16), (21, 16, 15), (28, 16, 15)], 29, 'MX', (19, 'RX'))
E['echoX_21_h22_21_30'] = session(22, [(21, 22, 21), (30, 22, 21)], 31, 'MX', (20, 'RX'))
E['echoX_19_h25_19_30'] = session(25, [(19, 25, 19), (30, 25, 19)], 31, 'MX', (18, 'RX'))
E['echoX_0_h6_7_10'] = session(6, [(7, 6, 0), (10, 6, 0)], 11, 'MX', (6, 'RX'))
E['pguard16_10'] = [rmcx(39, 10, 16), ('move', 38, 16, 'RX', 39)]
# PRECELL
q6 = {e['name']: e['edits'] for e in q6_elements(c0)}
E.update(q6)
E['q13guard_7'] = [rmcx(34, 13, 7), rmcx(35, 13, 7), rmcx(36, 13, 7)]
E['q14echo_end36'] = [rmcx(36, 14, 20), ('add', 35, ['cx q[14],q[20];'])]
E['q21echo_end35'] = [rmcx(35, 20, 21), ('add', 34, ['cx q[20],q[21];'])]
E['q14q21_ends'] = [rmcx(36, 14, 20), ('add', 35, ['cx q[14],q[20];']), rmcx(35, 20, 21), ('add', 34, ['cx q[20],q[21];'])]
E['g32_26'] = session(32, [(40, 32, 26), (41, 32, 26)], 42, 'MEASURE', (39, 'RESET'))
E['g33_27'] = session(33, [(42, 33, 27)], 43, 'MEASURE', (41, 'RESET'))
E['g24_25'] = session(24, [(41, 24, 25)], 42, 'MEASURE', (40, 'RESET'))
E['g18_12'] = session(18, [(41, 18, 12)], 42, 'MEASURE', (40, 'RESET'))
E['g22_21'] = session(22, [(15, 22, 21), (16, 22, 21)], 17, 'MEASURE', (14, 'RESET'))

if __name__ == '__main__':
    names = []
    for k, ed in E.items():
        n = f'{base}__L_{k}'
        try:
            save(strip(c0, ed), n, dict(kind='loo', base=base, element=k))
            names.append(n)
        except Exception as e:
            print('fail', k, repr(e)[:200])
    (H / f'loo_{base}.list').write_text(' '.join(names))
    print(len(names), 'of', len(E))
    specs_json()


def specs_json():
    sp = {f'{base}__L_{k}': dict(family='loo', element=k, edits=ed) for k, ed in E.items()}
    names = set((H / f'loo_{base}.list').read_text().split())
    (H / f'loo_{base}.json').write_text(json.dumps({k: v for k, v in sp.items() if k in names}))

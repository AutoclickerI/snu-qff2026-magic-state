"""BUNDLE edit menu on a plan (ACCBUY/INTEG plan machinery, copied into this lane).

An edit is a JSON dict {id, fam, ...}. Families:
  rm      remove a gadget/element: list of primitive edits `ed` (elements.strip format)
  rmcx    remove one CX (t, a, b)
  trade   singleton check `bit` -> mode detector|omit|reset (INTEG2 trades)
  shift   move the unit at tick t on qubits qs (name) to tick nt, per-qubit order kept
  pd      delay a prep (reset/RX) to just before its checking measurement (INTEG prep_delay)
  cx      add one CX a->b at tick t (validity left to the evaluator: deterministic detectors, correct output)
  pair    add a cancelling CX pair a->b at t, t+1 (INTEG live-live pair)
  echo    add an echoed parity check (q, h, axis, t1, t2) (INTEG)
  guard   add a continuous guard (h, seq) (PRECELL)
Bundles are applied all-or-nothing on the un-normalized plan in canonical family order (removals, trades, shifts,
additions), then normalized once; any failure raises Invalid for the whole bundle.
"""
import sys, os, json, copy, collections, re, hashlib
from pathlib import Path
for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[k] = '1'
H = Path(__file__).resolve().parent
sys.path.insert(0, str(H))
from elements import *  # noqa: F401,F403  (lib, gadgets: read, status, seq, unit, cx_qs, add_ops, normalized, ...)
import joint as J

ROOTQ = H.parents[2]
V36H = H / 'c/baseline'
ORDER = {'rm': 0, 'rmcx': 1, 'trade': 2, 'mi':2.1,'fuse':2.2,'rev':2.3,'pd': 3, 'shift': 4, 'ajoint': 4.5, 'polishguard': 4.75, 'cx': 5, 'pair': 6, 'echo': 7, 'guard': 8, 'global': 9}
ADDF = ('cx', 'pair', 'echo', 'guard')


class Invalid(Exception):
    pass


# ---------------------------------------------------------------- primitive application (no normalization)
def _find(c, t, q, name):
    try:
        return find(c, t, tuple(q) if isinstance(q, (list, tuple)) else q, name)
    except KeyError:
        raise Invalid(('missing op', t, q, name))


def ops_on(c, q):
    return sorted((o for o in c['ops'] if q in unit(o).qs), key=lambda o: o['t'])


def free_at(c, q, t):
    return not any(o['t'] == t and q in unit(o).qs for o in c['ops'])


def apply_edit(c, e):
    """Mutates and returns c (callers deep-copy once per bundle)."""
    f = e['fam']
    if f=='mi':
        from measured_init import convert_init
        o=_find(c,e['t'],e['q'],e['name']);i=c['ops'].index(o);result=convert_init(c,i)
        if result is None:raise Invalid('measured source output byproduct changed')
        return result[0]
    if f=='fuse':
        o=_find(c,e['t'],e['q'],e['name']);m=op_of_bit(c,e['bit'])
        if m['t']!=e['mt']:raise Invalid('fused source timing changed')
        m['t']=o['t'];c['ops'].remove(o)
        if not in_span(c,e['bit']):c['tail'].append(f"// DETECTOR c[{e['bit']}]")
        return c
    if f=='rev':
        o=_find(c,e['t'],[e['a'],e['b']],'CX');o['lines']=[f"cx q[{e['b']}],q[{e['a']}];"];return c
    if f == 'polishguard':
        if e.get('remove28',True):c=apply_edit(c,dict(fam='rmcx',a=28,b=22,t=29))
        c=apply_edit(c,dict(fam='shift',name='RESET',qs=[23],t=29,nt=28))
        c=apply_edit(c,dict(fam='cx',a=23,b=22,t=29))
        if e['switch21']:
            c=apply_edit(c,dict(fam='rmcx',a=21,b=20,t=30))
            c=apply_edit(c,dict(fam='cx',a=21,b=22,t=30))
        return c
    if f == 'ajoint':
        o = _find(c,37,9,'MEASURE')
        if bits_of(o)!=[321] or not free_at(c,9,38) or not free_at(c,10,37):
            raise Invalid('AJOINT interface changed')
        o['t']=38
        c['ops'].append(dict(t=37,lines=['cx q[9],q[10];']))
        return c
    if f == 'global':
        m = bit(c)
        if e['kind'] == 'source6':
            o = _find(c, 12, 6, 'RX')
            o['lines'] = ['h q[6];', f'measure q[6] -> c[{m}];', 'h q[6];']
        elif e['kind'] == 'row5':
            items = [(t, [f'cx q[31],q[32];']) for t in (30,31,34,35,38,39)]
            items += [(33, ['reset q[31];']), (36, [f'measure q[31] -> c[{m}];'])]
            for t,lines in items:
                for q in unit(dict(t=t,lines=lines)).qs:
                    if not free_at(c,q,t): raise Invalid(('global row5 collision',q,t))
            c['ops'] += [dict(t=t,lines=lines) for t,lines in items]
        else: raise Invalid(('unknown GLOBAL macro',e))
        c['tail'].append(f'// DETECTOR c[{m}]')
        return c
    if f == 'rm':
        for p in e['ed']:
            if p[0] == 'rm':
                c['ops'].remove(_find(c, p[1], p[2], p[3]))
            elif p[0] == 'add':
                c['ops'].append(dict(t=p[1], lines=list(p[2])))
            elif p[0] == 'rmdet':
                line = f'// DETECTOR c[{p[1]}]'
                if line not in c['tail']:
                    raise Invalid(('not a singleton detector', p[1]))
                c['tail'].remove(line)
            elif p[0] == 'move':
                o = _find(c, p[1], p[2], p[3])
                o['t'] = p[4]
            else:
                raise ValueError(p)
        return c
    if f == 'rmcx':
        c['ops'].remove(_find(c, e['t'], [e['a'], e['b']], 'CX'))
        return c
    if f == 'trade':
        try:
            c2 = remove_check(c, e['bit'], e['mode'])
        except Exception as ex:
            raise Invalid(('trade', repr(ex)[:80]))
        return c2
    if f in ('shift', 'pd'):
        if e['name'] == 'CX':
            # qs identifies the unit's footprint, not control/target order.
            matches=[o for o in c['ops'] if o['t']==e['t'] and unit(o).name=='CX'
                     and set(unit(o).qs)==set(e['qs'])]
            if len(matches)!=1:raise Invalid(('missing CX unit',e['t'],e['qs']))
            o=matches[0]
        else:
            o = _find(c, e['t'], e['qs'][0], e['name'])
        nt = e['nt']
        for q in e['qs']:
            s = ops_on(c, q)
            k = next(i for i, x in enumerate(s) if x is o)
            lo = s[k - 1]['t'] if k > 0 else -1
            hi = s[k + 1]['t'] if k + 1 < len(s) else 10 ** 6
            if not (lo < nt < hi):
                raise Invalid(('order', q, nt))
        o['t'] = nt
        return c
    if f == 'cx':
        a, b, t = e['a'], e['b'], e['t']
        if not (free_at(c, a, t) and free_at(c, b, t)):
            raise Invalid(('cx busy', a, b, t))
        if t > max(o['t'] for o in c['ops']):
            raise Invalid('cx past end')
        c['ops'].append(dict(t=t, lines=[f'cx q[{a}],q[{b}];']))
        return c
    if f in ('pair', 'echo'):
        g = e['g']
        if not J.valid(c, g):
            raise Invalid(f)
        try:
            return J.apply(c, g)
        except AssertionError:
            raise Invalid(f + ' apply')
    if f == 'guard':
        g = e['g']
        st = status(c)
        h, sq = g['h'], g['seq']
        FREE = ('dead', 'pre', 'prem')
        if not (all(st[h][t] in FREE for t in range(sq[0][0] - 1, sq[-1][0] + 2)) and all(st[q][t] == 'live' for t, q in sq)):
            raise Invalid('guard')
        m = bit(c)
        items = [(sq[0][0] - 1, [f'reset q[{h}];'])] + [(t, [f'cx q[{h}],q[{q}];']) for t, q in sq] + \
                [(sq[-1][0] + 1, [f'measure q[{h}] -> c[{m}];'])]
        c = add_ops(c, items)
        c['tail'].append(f'// DETECTOR c[{m}]')
        return c
    raise ValueError(f)


def canon(bundle):
    return sorted(bundle, key=lambda e: (ORDER[e['fam']], e['id']))


def apply_bundle(base, bundle):
    """All-or-nothing: returns (plan, qasm text) or raises Invalid."""
    c = copy.deepcopy(base)
    for e in canon(bundle):
        c = apply_edit(c, e)
    c = fix(c)
    try:
        c2, txt = normalized(c)
    except Exception as ex:
        raise Invalid(('normalize', repr(ex)[:100]))
    return c2, txt


# ---------------------------------------------------------------- menu generation
def eid(e):
    f = e['fam']
    if f=='mi':return f"mi:{e['name']}{e['q']}@{e['t']}"
    if f=='fuse':return f"fuse:{e['name']}{e['q']}@{e['t']}:M{e['bit']}@{e['mt']}"
    if f=='rev':return f"rev:{e['a']}_{e['b']}@{e['t']}"
    if f == 'polishguard':return 'polishguard:R45_switch21='+str(int(e['switch21']))+'_remove28='+str(int(e.get('remove28',True)))
    if f == 'ajoint': return 'ajoint:M321_37>38+CX9_10@37'
    if f == 'global': return 'global:' + e['kind']
    if f == 'rm':
        return 'rm:' + e['name']
    if f == 'rmcx':
        return f"rmcx:{e['a']}_{e['b']}@{e['t']}"
    if f == 'trade':
        return f"trade:{e['bit']}:{e['mode']}"
    if f in ('shift', 'pd'):
        return f"{f}:{e['name']}{'_'.join(map(str, e['qs']))}@{e['t']}>{e['nt']}"
    if f == 'cx':
        return f"cx:{e['a']}_{e['b']}@{e['t']}"
    if f == 'pair':
        g = e['g']
        return f"pair:{g['a']}_{g['b']}@{g['t']}"
    if f == 'echo':
        g = e['g']
        return f"echo{g['axis']}:{g['q']}_h{g['h']}@{g['t1']}-{g['t2']}"
    if f == 'guard':
        g = e['g']
        return f"guard:h{g['h']}:" + ','.join(f'{q}@{t}' for t, q in g['seq'])
    raise ValueError(f)


def mk(**kw):
    kw['id'] = eid(kw)
    return kw


def removals(c):
    out = []
    for el in elements(c) + q6_elements(c):
        out.append(mk(fam='rm', name=el['name'], ed=[list(p) if not isinstance(p, list) else p for p in el['edits']]))
    for o in c['ops']:
        if unit(o).name == 'CX':
            a, b = cx_qs(o)
            out.append(mk(fam='rmcx', a=a, b=b, t=o['t']))
    return out


def trades(c):
    out = []
    for b in sorted(singles(c)):
        for mode in ('detector', 'omit', 'reset'):
            out.append(mk(fam='trade', bit=b, mode=mode))
    return out


def shifts(c, maxd=3):
    T = depth(c)
    occ = busy(c)
    out = []
    for o in c['ops']:
        u = unit(o)
        qs = list(u.qs)
        lo, hi = -1, T
        for q in qs:
            s = ops_on(c, q)
            k = next(i for i, x in enumerate(s) if x is o)
            if k > 0:
                lo = max(lo, s[k - 1]['t'])
            if k + 1 < len(s):
                hi = min(hi, s[k + 1]['t'])
        cand = set(range(o['t'] - maxd, o['t'] + maxd + 1))
        if u.name in ('RESET', 'RX'):
            cand |= set(range(lo + 1, o['t']))          # inits: any earlier tick in their dead window
        for nt in sorted(cand):
            if nt == o['t'] or nt <= lo or nt >= hi or nt < 0 or nt >= T:
                continue
            if any(q in occ[nt] for q in qs):
                continue
            out.append(mk(fam='shift', t=o['t'], qs=qs, name=u.name, nt=nt))
    for r in prep_options(c):
        o = next(o for o in c['ops'] if o['t'] == r['old'] and o['lines'] == r['lines'])
        out.append(mk(fam='pd', t=r['old'], qs=[r['q']], name=unit(o).name, nt=r['new']))
    # pd duplicates a shift when the delay is within maxd: keep one id per (t, qs, nt)
    seen, res = set(), []
    for e in out:
        k = (e['t'], tuple(e['qs']), e['nt'])
        if k in seen:
            continue
        seen.add(k)
        res.append(e)
    return res


def cx_adds(c, st=None, only=None):
    """Single CX a->b at t with both qubits free at t, neither dead, at least one live. `only`: set of (a,b,t) to keep."""
    st = st or status(c)
    T = depth(c)
    out = []
    for t in range(T - 1):
        for a in range(36):
            if st[a][t] in ('busy', 'dead'):
                continue
            for b in ADJ[a]:
                if st[b][t] in ('busy', 'dead'):
                    continue
                if 'live' not in (st[a][t], st[b][t]):
                    continue
                if only is not None and (a, b, t) not in only:
                    continue
                out.append(mk(fam='cx', a=a, b=b, t=t))
    return out


def gadget_adds(c, st=None):
    """INTEG pairs (one per constant-status run, middle tick; data-data excluded), maximal INTEG echoes, PRECELL guards."""
    st = st or status(c)
    out = []
    by = collections.defaultdict(list)
    for e in echoes(c, st):
        by[(e['q'], e['h'], e['axis'])].append(e)
    for v in by.values():
        for e in v:
            if not any(f is not e and f['t1'] <= e['t1'] and f['t2'] >= e['t2'] for f in v):
                g = {k: e[k] for k in ('kind', 'q', 'h', 'axis', 't1', 't2')}
                out.append(mk(fam='echo', g=g))
    runs = collections.defaultdict(list)
    for p in pairs(c, st):
        if p['a'] in D and p['b'] in D:
            continue
        runs[(p['a'], p['b'])].append(p)
    for v in runs.values():
        v.sort(key=lambda p: p['t'])
        groups = [[v[0]]]
        for p in v[1:]:
            if p['t'] == groups[-1][-1]['t'] + 1 and p['sa'] == groups[-1][-1]['sa'] and p['sb'] == groups[-1][-1]['sb']:
                groups[-1].append(p)
            else:
                groups.append([p])
        for g in groups:
            p = g[len(g) // 2]
            out.append(mk(fam='pair', g=dict(kind='pair', a=p['a'], b=p['b'], t=p['t'])))
    for g in guard_menu(c, st):
        out.append(mk(fam='guard', g=g))
    return out


def guard_menu(c, st):
    """PRECELL guards_pc.menu (copied): single-target runs, split runs, multi-target."""
    T = len(st[0])
    FREE = ('dead', 'pre', 'prem')
    gs = []
    for h in range(36):
        wins, cur = [], None
        for t, s in enumerate(st[h]):
            if s in FREE:
                cur = [t, t] if cur is None else [cur[0], t]
            else:
                if cur:
                    wins.append(tuple(cur))
                cur = None
        if cur:
            wins.append(tuple(cur))
        for lo, hi in wins:
            per = {}
            for q in ADJ[h]:
                ts = [t for t in range(lo + 1, min(hi, T - 1)) if st[q][t] == 'live']
                if ts:
                    per[q] = ts
                    gs.append(dict(h=h, seq=[(t, q) for t in ts]))
                    runs = [[ts[0]]]
                    for t in ts[1:]:
                        if t == runs[-1][-1] + 1:
                            runs[-1].append(t)
                        else:
                            runs.append([t])
                    if len(runs) > 1:
                        for r in runs:
                            gs.append(dict(h=h, seq=[(t, q) for t in r]))
            if len(per) > 1:
                ticks = sorted({t for ts in per.values() for t in ts})
                sq = []
                for t in ticks:
                    qs = [q for q in per if t in per[q]]
                    qs.sort(key=lambda q: (q not in D, q))
                    sq.append((t, qs[0]))
                gs.append(dict(h=h, seq=sq))
    seen, out = set(), []
    for g in gs:
        g = dict(h=g['h'], seq=[list(x) for x in g['seq']])
        k = json.dumps(g)
        if k not in seen:
            seen.add(k)
            out.append(g)
    return out


# ---------------------------------------------------------------- footprints (on the base plan)
def touched(c, e):
    """(qubit, tick) cells an edit removes, adds or moves, in base-plan ticks."""
    f = e['fam']
    if f=='mi':return [(e['q'],e['t'])]
    if f=='fuse':return [(e['q'],e['t']),(e['q'],e['mt'])]
    if f=='rev':return [(e['a'],e['t']),(e['b'],e['t'])]
    if f == 'polishguard':return [(28,29),(22,29),(23,28),(23,29)]+([(21,30),(20,30),(22,30)] if e['switch21'] else [])
    if f == 'ajoint':return [(9,37),(9,38),(10,37)]
    cells = []
    if f == 'rm':
        for p in e['ed']:
            if p[0] in ('rm', 'move'):
                qs = p[2] if isinstance(p[2], (list, tuple)) else [p[2]]
                cells += [(q, p[1]) for q in qs]
                if p[0] == 'move':
                    cells += [(q, p[4]) for q in qs]
            elif p[0] == 'add':
                for l in p[2]:
                    cells += [(int(q), p[1]) for q in re.findall(r'q\[(\d+)\]', l)]
            elif p[0] == 'rmdet':
                try:
                    o = op_of_bit(c, p[1])
                    cells += [(q, o['t']) for q in unit(o).qs]
                except StopIteration:
                    pass
    elif f == 'rmcx' or f == 'cx':
        cells = [(e['a'], e['t']), (e['b'], e['t'])]
    elif f == 'trade':
        o = op_of_bit(c, e['bit'])
        cells = [(q, o['t']) for q in unit(o).qs]
    elif f in ('shift', 'pd'):
        cells = [(q, e['t']) for q in e['qs']] + [(q, e['nt']) for q in e['qs']]
    elif f == 'pair':
        g = e['g']
        cells = [(g['a'], g['t']), (g['b'], g['t']), (g['a'], g['t'] + 1), (g['b'], g['t'] + 1)]
    elif f == 'echo':
        g = e['g']
        cells = [(g['h'], t) for t in range(g['t1'] - 1, g['t2'] + 2)] + [(g['q'], g['t1']), (g['q'], g['t2'])]
    elif f == 'guard':
        g = e['g']
        sq = g['seq']
        cells = [(g['h'], t) for t in range(sq[0][0] - 1, sq[-1][0] + 2)] + [(q, t) for t, q in sq]
    return cells


def footprint(c, e, seqs=None):
    """qubit -> (lo, hi): the base-plan op interval enclosing every touched cell on that qubit (previous op .. next op)."""
    seqs = seqs or {q: [o['t'] for o in ops_on(c, q)] for q in range(36)}
    T = depth(c)
    fp = {}
    for q, t in touched(c, e):
        ts = seqs[q]
        lo = max([x for x in ts if x < t], default=0)
        hi = min([x for x in ts if x > t], default=T)
        a, b = fp.get(q, (lo, hi))
        fp[q] = (min(a, lo), max(b, hi))
    return fp


def connected(fa, fb):
    for q, (a, b) in fa.items():
        if q in fb:
            c, d = fb[q]
            if a <= d and c <= b:
                return True
    return False


def base_plan():
    return read(V36H)

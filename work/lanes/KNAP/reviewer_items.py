"""Rebuild reviewer-3 item 2 on the v23 MX-initialized base and port item 1.
All generated files stay in KNAP.  The verified-init gadget replaces an MX
initialization by RX on the output, prepares an adjacent RX helper, couples
helper->output, and measures the helper in X in the same native tick as the
output's first post-init operation.  The old MX frame record is substituted
by the helper record in every detector that used it.
"""
from core import *
from ortools.sat.python import cp_model
import json, re, copy, shutil

V23 = OUT / 'inputs/v23h_c2c9'
# MX initializations in fb_s401_0035 (the v23 base).  Feasible adjacent fresh
# helpers are found from the actual lifetime; q18 is shared by q12/q19, so
# those two are mutually exclusive.
CAND = {26: 32, 12: 18, 19: 18}
BITS = {26: 47, 12: 49, 19: 50, 17: 51}

def retime(c, deps):
    old = list(c['t']); us = c['u']; horizon = max(old) + 20
    m = cp_model.CpModel(); ts = [m.new_int_var(0, horizon, f't{i}') for i in range(len(us))]
    per = {}
    for i, u in enumerate(us):
        for q in u.qs: per.setdefault(q, []).append(i)
    for seq in per.values():
        for a, b in zip(seq, seq[1:]): m.add(ts[b] > ts[a])
    end = m.new_int_var(0, horizon, 'end'); m.add_max_equality(end, ts)
    for a, b in deps: m.add(ts[a] == ts[b])
    dev = []
    for i, t in enumerate(ts):
        d = m.new_int_var(0, horizon, f'd{i}'); m.add_abs_equality(d, t-old[i]); dev.append(d)
    m.minimize(10000 * end + sum(dev))
    s = cp_model.CpSolver(); s.parameters.num_workers = 1; s.parameters.max_time_in_seconds = 30
    st = s.solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): raise RuntimeError(s.status_name(st))
    c['t'] = [s.value(t) for t in ts]
    c['meta']['schedule_objective'] = dict(mode='reviewer2-helper', makespan=s.value(end)+1,
                                            status=s.status_name(st), deps=deps)
    return c

def build_init(qs, name):
    c = provenance(read(V23))
    # Current base has MX units at t=33; check the exact source before editing.
    edits=[]; deps=[]
    for q in qs:
        h = CAND[q]; oldbit = BITS[q];
        hits = [i for i,u in enumerate(c['u']) if u.name == 'MX' and u.qs == (q,) and c['t'][i] < 33 and i < 160]
        if len(hits) != 1: raise ValueError((q, hits))
        i = hits[0]
        # Helper must be fresh at the gadget time, except q16 which was read
        # at t=32 and is deliberately reset before reuse.
        if any(h in u.qs and c['t'][j] >= c['t'][i] for j,u in enumerate(c['u']) if j != i):
            raise ValueError(f'helper {h} is live at/after init for q{q}')
        init_t = c['t'][i]
        newbit = 180 + q
        # Replace q's random MX frame preparation with RX.  The helper's X
        # result carries exactly the old frame bit into the same detectors.
        c['u'][i] = Unit([f'reset q[{q}];', f'h q[{q}];'])
        # Find q's first later operation; helper MX must share that tick.
        first = next((j for j in range(i+1, len(c['u'])) if q in c['u'][j].qs), None)
        if first is None: raise ValueError(f'no first op for q{q}')
        # Insert helper RX, then output RX, helper->output CX, helper MX.
        c['u'].insert(i, Unit([f'reset q[{h}];', f'h q[{h}];']))
        c['t'].insert(i, init_t); c['tags'].insert(i, 'check_extra')
        i += 1; first += 1
        cx_i = i + 1; mx_i = i + 2
        c['u'].insert(cx_i, Unit([f'cx q[{h}],q[{q}];']))
        c['t'].insert(cx_i, init_t + 1); c['tags'].insert(cx_i, 'check_extra')
        c['u'].insert(mx_i, Unit([f'h q[{h}];', f'measure q[{h}] -> c[{newbit}];', f'h q[{h}];']))
        c['t'].insert(mx_i, init_t + 2); c['tags'].insert(mx_i, 'check_extra')
        # q's first later op index moved by the three inserted units.
        first += 3
        deps.append((first, mx_i))
        edits.append(dict(q=q, helper=h, old_bit=oldbit, new_bit=newbit, first_unit=first, helper_measure=mx_i))
        # Substitute the new helper record for the old MX frame bit.
        for k,l in enumerate(c['tail']):
            if l.startswith('// DETECTOR'):
                c['tail'][k] = re.sub(rf'c\[{oldbit}\]', f'c[{newbit}]', l)
    c['meta']['source'] = str(V23)
    c['meta']['method'] = 'reviewer3 item 2 helper verified MX re-derivation'
    c['meta']['reviewer_helper_edits'] = edits
    c = retime(c, deps)
    save(c, name, dict(kind='reviewer3_item2', edits=edits, deps=deps, source=str(V23)))

def copy4(src, out, startbit=230):
    """Port the audited item-1 terminal copy to a circuit with the same suffix."""
    L = Path(src).with_suffix('.qasm').read_text().splitlines()
    # Work from the last final-stage CX 19->25.  Remove it; copies replace it.
    hits=[i for i,l in enumerate(L) if l.strip()=='cx q[19],q[25];']
    if not hits: raise ValueError('no CX 19->25')
    old = hits[-1]
    # The barrier immediately following this final CX block is the insertion point.
    b = next((j for j in range(old+1,len(L)) if L[j].startswith('barrier')), None)
    if b is None: raise ValueError('no final barrier')
    # Reset helpers in the preceding barrier block, as in the audited circuit.
    prev = max((j for j in range(0,old) if L[j].startswith('barrier')), default=None)
    if prev is None: raise ValueError('no preceding barrier')
    helper_bar = 'barrier q[' + '],q['.join(map(str,range(36))) + '];'
    reset_lines=[f'reset q[{q}];' for q in (18,31,35,34)]
    L[prev:prev+1] = reset_lines + [helper_bar]
    # indices shifted by four lines if old follows prev.
    old += 4; b += 4
    L[old] = None
    copies=[f'cx q[19],q[18];', f'cx q[25],q[31];', f'cx q[29],q[35];', f'cx q[28],q[34];']
    L[b:b] = copies; b += len(copies)
    L=[x for x in L if x is not None]
    # Helper measurements share the original final measurement tick.  Add H
    # after each terminal MX because the audited circuit preserves the native
    # MX frame when the readout block is extended.
    measure_insert = None
    for i,l in enumerate(L):
        if l == 'h q[6];':
            # Only the terminal h immediately followed by measure gets a pair.
            if i+1 < len(L) and L[i+1].startswith('measure q[6]'):
                L.insert(i+2, 'h q[6];')
        if l.startswith('measure q[25] ->'):
            measure_insert = i+1
    for q in (26,13,11,4,23,27):
        for i,l in enumerate(L):
            if l == f'h q[{q}];' and i+1 < len(L) and L[i+1].startswith(f'measure q[{q}]'):
                L.insert(i+2, f'h q[{q}];'); break
    # H insertions above can shift the saved index; locate the final q25 read again.
    measure_insert = next((i+1 for i,l in enumerate(L) if l.startswith('measure q[25] ->')), None)
    if measure_insert is None: raise ValueError('no final q25 measurement')
    helper=[f'measure q[{q}] -> c[{startbit+k}];' for k,q in enumerate((18,31,35,34))]
    L[measure_insert:measure_insert]=helper
    # The old 19->25 coupling contributed q19 to two detector parities.  This
    # is exactly the audited re-encoding; append equality detectors for copies.
    for i,l in enumerate(L):
        if l == '// DETECTOR c[22] c[26] c[27]': L[i]='// DETECTOR c[22] c[23] c[26] c[27]'
        elif l == '// DETECTOR c[21] c[22] c[24] c[25] c[26] c[27]':
            L[i]='// DETECTOR c[21] c[22] c[23] c[24] c[25] c[26] c[27]'
    L += [f'// DETECTOR c[{23}] c[{startbit}]', f'// DETECTOR c[{22}] c[{startbit+1}]',
          f'// DETECTOR c[{26}] c[{startbit+2}]', f'// DETECTOR c[{27}] c[{startbit+3}]']
    Path(out).with_suffix('.qasm').write_text('\n'.join(L)+'\n')
    meta=json.loads(Path(src).with_suffix('.json').read_text()); meta['source']=str(src); meta['method']='reviewer3 item 1 readout copy4'; meta['cx']=int(meta.get('cx',0))+3; meta['reviewer_copy_bits']=list(range(startbit,startbit+4))
    Path(out).with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('mode',choices=['init','copy']); ap.add_argument('--qs',default='26'); ap.add_argument('--src',default=str(OUT/'base')); ap.add_argument('--out',required=True); a=ap.parse_args()
    if a.mode=='init': build_init([int(x) for x in a.qs.split(',')], a.out)
    else: copy4(a.src, a.out)

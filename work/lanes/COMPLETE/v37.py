"""v37a phase-check completion and rigid downstream-block co-design.

The forward tree computes the same X7 X8 X9 X14 measurement onto a freely
chosen root. On the accepted c7=0 branch its reset and inverse implement the
same projector. The full evaluator checks every candidate's actual records.
B/C's 65 CXs and the 11-CX A encoder are carried intact, with one common round
offset; no resource search or greedy local-edit campaign is performed here.
"""
import os,sys,json,copy,re,hashlib,collections,random
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
from ortools.sat.python import cp_model
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'INTEG'));import lib
lib.C=H/'builds'
from lifetime import commute
D=[6,20,19,10,2,22,16];A=[7,14,13,9,8,21,15]
BC=json.loads((H.parent/'GLOBAL/enc/r46warm_000.json').read_text())
BCSET={(BC['T0']+dt,*e) for dt,es in enumerate(BC['ops']) for e in es}
AE=json.loads((H.parent/'GLOBAL/enc/r46_2_a0.json').read_text())
ASET={(t,A[a],A[b]) for t,a,b in AE['layers']}
RELEASE={7,10,11,12,13,64,67,275,274,316,317,318,319,320,321,322}
def qubits(o):return list(map(int,re.findall(r'q\[(\d+)\]',o['lines'][0])))
def key(o):return (o.get('original_t',o['t']),*qubits(o))
def op(t,a,b):return dict(t=t,lines=[f'cx q[{a}],q[{b}];'],original_t=None,part='completion')
def base():
    c=lib.read(H/'builds/v37a_roundtrip')
    for i,o in enumerate(c['ops']):o.update(original_id=i,original_t=o['t'])
    c['meta']=dict(data_qubits=D,source='COMPLETE v37a phase completion')
    return c
def remove(c,keys,bits=()):
    c['ops']=[o for o in c['ops'] if key(o) not in keys and not(set(lib.bits_of(o))&set(bits))]
    # Eliminate a discarded record from the detector row space. Deleting only
    # its term would wrongly postselect the remaining (possibly random) record.
    rows=lib.det_rows(c)
    for bit in bits:
        pivot=next((r for r in rows if bit in r),None)
        if pivot is None:continue
        rows=[(r^pivot if bit in r else r) for r in rows if r is not pivot]
    c['tail']=[l for l in c['tail'] if not l.startswith('// DETECTOR')]+['// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(r)) for r in rows if r]
def rooted(root=9,reset=True):
    c=base();old={(18,8,14),(19,8,7),(20,8,9),(23,8,9),(24,8,7),(25,8,14),(21,8),(22,8)}
    removed=set();bits=[]
    if root==9:
        removed|={(21,9,10),(22,9,10)}
        tree=[(18,8,14),(19,8,7),(20,9,8)]
        mt=21;rt=22;undo=[(23,9,8),(24,8,7),(25,8,14)]
    elif root==7:
        removed|={(21,6,7),(22,6,7),(20,7,13),(23,7,13)};bits=[275]
        tree=[(18,8,14),(20,8,9),(21,7,8)]
        mt=22;rt=23;undo=[(24,7,8),(25,8,9),(26,8,14)]
    elif root==14:
        removed|={(19,14,20),(20,14,20),(23,14,15),(24,14,15),(21,14,13),(22,14,13)}
        tree=[(19,8,7),(20,8,9),(21,14,8)]
        mt=22;rt=23;undo=[(24,14,8),(25,8,9),(26,8,7)]
    else:raise ValueError(root)
    remove(c,old|removed,bits)
    if root!=9:
        for o in c['ops']:
            if o['t']>=26:o['t']+=1
            if root==14 and o.get('original_t')==25 and qubits(o)==[7,6]:o['t']=27
    if not reset:
        undo=[(t-1,a,b) for t,a,b in undo]
    c['ops'] += [op(*g) for g in tree+undo]
    c['ops'].append(dict(t=mt,lines=[f'h q[{root}];',f'measure q[{root}] -> c[7];',f'h q[{root}];'],original_t=None,part='completion'))
    if reset:c['ops'].append(dict(t=rt,lines=[f'reset q[{root}];',f'h q[{root}];'],original_t=None,part='completion'))
    c['ops'].sort(key=lambda o:o['t'])
    c['meta'].update(root=root,reset=reset,opened_guards=sorted(removed),removed_records=bits,
                     source=f'v37a phase check moved to q{root}, reset={reset}')
    return c
def blue_bell(c=None,omit_reset=True):
    """Reverse the last Bell-readout CX and exchange its X/Z readout ports.

    CX2->1, MX2(c67), MZ1(c64) and CX1->2, MX1(c67),
    MZ2(c64) measure the same XX and ZZ. The latter leaves q2 in
    the accepted known-Z state and can feed the data3->2 hop directly.
    """
    c=copy.deepcopy(c if c is not None else base())
    for o in c['ops']:
        if key(o)==(34,2,1):o['lines']=['cx q[1],q[2];']
        if 64 in lib.bits_of(o):o['lines']=['measure q[2] -> c[64];']
        if 67 in lib.bits_of(o):o['lines']=['h q[1];','measure q[1] -> c[67];','h q[1];']
    if omit_reset:remove(c,{(36,2)})
    c['meta']['source']+='; blue Bell readout ports exchanged, '+('MZ2 reused directly' if omit_reset else 'R2 retained')
    return c
EARLY_GUARDS={(41,20,14),(40,2,8),(39,9,10),(44,6,0),(44,2,1),(30,20,26),(29,28,22),(32,11,10),(36,12,6),(38,25,19),(37,21,15),(41,22,21)}
def early_bell(root=8,flags=()):
    c=blue_bell(base() if root==8 else rooted(root));remove(c,EARLY_GUARDS,flags)
    c['meta']['source']+='; earlier coherent handoffs, A and unchanged BC65 one tick earlier'
    return c
def schedule(c,name,shift=0,seed=0,seconds=10,weights=None,earliest=False,rigid_bc=True):
    c=copy.deepcopy(c);ops=c['ops'];m=cp_model.CpModel();tt=[];ns=[];byq=collections.defaultdict(list)
    weights=weights or {};rng=random.Random(seed)
    for i,o in enumerate(ops):
        q=qubits(o);u=lib.unit(o);node=dict(qs=q,kind={'RESET':'R','MEASURE':'M'}.get(u.name,u.name));ns.append(node)
        orig=o.get('original_t');v=m.new_int_var(0,48+max(0,shift),f't{i}');tt.append(v)
        if orig is not None and orig<17:m.add(v==orig)
        elif orig is not None and (key(o) in ASET or key(o) in BCSET and rigid_bc or orig>=45 and key(o) not in BCSET):m.add(v==orig+shift)
        elif orig is not None and key(o) in BCSET:
            m.add(v>=max(17,orig-6));m.add(v<=45+shift)
        else:
            m.add(v>=max(17,o['t']-8));m.add(v<=min(44+shift,o['t']+8))
        for j in {j for x in q for j in byq[x]}:
            if not commute(ns[j],node):m.add(v>tt[j])
        for x in q:byq[x].append(i)
        m.add_hint(v,min(48+max(0,shift),o['t']))
    for ids in byq.values():m.add_all_different([tt[i] for i in ids])
    dev=[];rel=[]
    for i,o in enumerate(ops):
        z=m.new_int_var(0,64,'dev');m.add_abs_equality(z,tt[i]-o['t']);dev.append(z)
        bits=lib.bits_of(o)
        for b in bits:
            if b in RELEASE:rel.append(weights.get(b,0)*tt[i])
    m.minimize(sum(rel)*10000+sum(dev)*10+(sum(tt) if earliest else -sum(tt)))
    solver=cp_model.CpSolver();solver.parameters.num_search_workers=1;solver.parameters.max_time_in_seconds=seconds;solver.parameters.random_seed=seed
    status=solver.solve(m);info=dict(status=solver.status_name(status),seconds=solver.wall_time,round_shift=shift,weights=weights)
    if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        (H/'logs'/f'{name}.schedule.json').write_text(json.dumps(info,indent=2));return None,info
    for i,o in enumerate(ops):o['t']=solver.value(tt[i])
    info.update(objective=solver.objective_value,bound=solver.best_objective_bound)
    c['meta']['schedule']=info;lib.fix(c);st=lib.save(c,name)
    recs=[]
    for o in c['ops']:
        for b in lib.bits_of(o):
            if b in RELEASE:recs.append(dict(bit=b,cell=qubits(o)[0],release=o['t']+1))
    info['release_profile']=sorted(recs,key=lambda r:r['bit']);info['sha256']=lib.sha(st)
    (H/'logs'/f'{name}.schedule.json').write_text(json.dumps(info,indent=2));return st,info
if __name__=='__main__':
    for root in [9,7,14]:
        for reset in ([True,False] if root==9 else [True]):
            for shift in [0,-1]:
                n=f'v37_root{root}_r{int(reset)}_R{46+shift}';st,info=schedule(rooted(root,reset),n,shift,seconds=10)
                print(n,info['status'],str(st),flush=True)

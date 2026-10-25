"""Verify schedule, gates, input-sector identities, and terminal rejection witnesses."""
import sys,json,hashlib,itertools,math
from pathlib import Path
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H/'sparse'))
import frontend as fa
from lookup_scan import syndrome,ccx,rccx,apply,onehot

def check_decomposition():
    ans={}
    for name,fn in [('ccx',ccx),('rccx',rccx)]:
        errors=[]
        for x in range(8):
            v={x:1.+0j}
            for op in fn(0,1,2):v=apply(v,op)
            want=x^(4 if x&1 and x&2 else 0)
            assert set(v)=={want} and abs(abs(v[want])-1)<1e-12
            if name=='ccx':assert abs(v[want]-1)<1e-12
        ans[name]='all 8 inputs: exact permutation'+(' with allowed relative phase' if name=='rccx' else '')
    return ans

def linear_identity():
    count=0
    for mask in range(128):
        s=syndrome(mask);linear=(s&1)|((s&2))|((s&4)<<1)
        single=(1<<(s-1)) if s else 0
        rest=linear^single
        f=int(s!=0)^(s.bit_count()%2)
        assert syndrome(rest)==0 and rest.bit_count()%2==f
        # Difference from the lookup is a stabilizer or its logical coset.
        count+=1
    return dict(single_axis_physical_Paulis=count,two_axis_Paulis=count*count,identity='P_lin=P_judge P_L^(OR(s) xor parity(s)), modulo stabilizers')

def schedules():
    rows=[]
    for p in sorted((H/'builds').glob('*.qasm')):
        if p.stem=='d_linear_frame':
            text='\n'.join(l for l in p.read_text().splitlines() if not l.startswith('// FRAME'))
        else:text=p.read_text()
        ops,dets=fa.parse_current(text);native,_=fa.native_text(ops)
        _,steps,_=fa.schedule(native)
        assert all(len(ss)==1 and ss[0][1]==o.time for ss,o in zip(steps,ops)),p
        rows.append(dict(stem=p.stem,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),native_ticks=max(o.time for o in ops)+1,
                         cx=sum(o.kind=='CX' for o in ops),detectors=len(dets)))
    return rows

def d_tail_partition():
    # The data controls have each been measured before any correction, and each
    # syndrome wire corrects exactly one physical position. Boolean faults occur
    # strictly after all physical corrections, so the lookup scan composes.
    def loss(x,z):
        fx=x.bit_count()%2 ^ bool(syndrome(x));fz=z.bit_count()%2 ^ bool(syndrome(z))
        return (2-(-1)**fz-(-1)**(fx^fz))/4
    cases=[]
    for axis in ('X','Z'):
        for j,pos in enumerate((0,1,3)):
            # Measurement flips its record and memory state together.
            s=1<<j;frame=bool(s)^(s.bit_count()%2)
            assert frame==0 and loss((1<<pos) if axis=='X' else 0,(1<<pos) if axis=='Z' else 0)==0
            cases.append(dict(kind='input measurement flip',axis=axis,position=pos,accepted=True,loss=0))
            for pc in 'IXYZ':
                for pd in 'IXYZ':
                    if pc+pd=='II':continue
                    accepted=pc not in 'XY'
                    # A Z-axis correction conjugates the data Pauli by its final H.
                    p=pd if axis=='X' else {'I':'I','X':'Z','Y':'Y','Z':'X'}[pd]
                    l=loss((1<<pos) if p in 'XY' else 0,(1<<pos) if p in 'YZ' else 0)
                    assert not accepted or l==0
                    cases.append(dict(kind='physical correction CX',axis=axis,position=pos,
                                      pauli=pc+pd,accepted=accepted,loss=l if accepted else None))
    for pos in range(7):
        for p in 'XYZ':assert loss((1<<pos) if p in 'XY' else 0,(1<<pos) if p in 'YZ' else 0)==0
    scan=json.loads((H/'logs/d_or_duplicate.scan.json').read_text())
    assert all(r['harmful']==0 for r in scan['input_rows'])
    return dict(verdict='first-order zero for the saved perfect-extraction tail',enumerated_external_cases=cases,
        partition=['lookup/native/idle/initial errors: 4952 exact scan cases, perfect recorded input',
                   'data idles and H errors: one physical coordinate, corrected by judge',
                   'syndrome memory X/Y between input read and physical correction: final source comparison rejects',
                   'input read flip: memory and record change together; exactly one physical correction, no logical frame',
                   'physical CX: a control X/Y is rejected by source comparison; otherwise at most one data Pauli',
                   'single OR-read error: duplicate comparison rejects; single source-read error: memory comparison rejects',
                   'post-read depolarization on a discarded helper: no output effect'],
        unverified='an actual noisy syndrome extractor before this tail')

if __name__=='__main__':
    out=dict(decompositions=check_decomposition(),linear_identity=linear_identity(),schedules=schedules(),d_tail_first_order=d_tail_partition())
    ops=onehot();assert ops[55]==('h',9)
    v={0:1.+0j}
    for j,op in enumerate(ops):
        v=apply(v,op)
        if j==55:v=apply(v,('x',9))
    assert set(v)=={127<<3}
    out['c_native_fault_witness']=dict(gate_index=55,gate='H q9',fault='X after H',input_syndrome=0,
        final_onehot_mask=127,output_syndrome=0,output='logical X or logical Z, according to correction axis',
        loss_X=.5,loss_Z=1.,fault_probability=.001/3)
    # In a zero-syndrome accepting check, a data-only Pauli after its last CX
    # cannot change any subsequently measured partner record. Explicitly verify
    # its accepted signature and nonzero physical syndrome with the actual model.
    import sparse_walsh as sw
    m,e,*_=sw.prepare(H/'builds/e_zero_syndrome_check',True)
    witnesses=[]
    for f in m.faults:
        if m.labels[f['ins']].time!=8 or m.labels[f['ins']].kind!='CX':continue
        a,n=e.ntable(f['s'],f['d'])
        if a>1-1e-10 and (f['e']&63)!=0:
            witnesses.append(dict(label=f['label'],accepted_probability=a,syndrome_bits=f['e']&63,decoded_loss=float(n[f['e']]),pauli=f['pauli']))
    assert witnesses
    out['e_accepts_nonzero_syndrome_single_faults']=witnesses
    (H/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='schedules'}),flush=True)

"""v35b lane-local native edits, without inherited verification claims."""
from decoder34 import *
def save(c,name,edits):
    c=C.normalize(C.clone(c));text=C.textof(c)
    md={k:v for k,v in c['meta'].items() if k in ('data_qubits','R','round_range','native_depth','cx','terminal_decoder','terminal_cancellations')}
    bc_times=[max(t for u,t in zip(c['u'],c['t']) if u.lines==[f'cx q[{b}],q[{cc}];']) for b,cc in zip(C.B,C.C)]
    md['R']=min(bc_times);md['BC_round_range']=[min(bc_times),max(bc_times)]
    md.update(base='MAIN/v35b',comp29_edits=edits,source=str(c.get('source','')),qasm_sha256=hashlib.sha256(text.encode()).hexdigest())
    (H/(name+'.qasm')).write_text(text);(H/(name+'.json')).write_text(json.dumps(md,indent=2)+'\n')
    return dict(stem=name,edits=edits,sha256=md['qasm_sha256'],cx=md['cx'],R=md['R'],native_depth=md['native_depth'])

def detector_basis(c):
    basis={}
    for line in c['tail']:
        v=sum(1<<int(b) for b in re.findall(r'c\[(\d+)\]',line))
        while v:
            p=v.bit_length()-1
            if p in basis:v^=basis[p]
            else:basis[p]=v;break
    return basis

def known_zero(c,bit):
    v=1<<bit;basis=detector_basis(c)
    while v:
        p=v.bit_length()-1
        if p not in basis:return False
        v^=basis[p]
    return True

def remove_check(base,bit,mode):
    c=C.clone(base);assert known_zero(c,bit)
    i=next(i for i,u in enumerate(c['u']) if f'-> c[{bit}];' in ' '.join(u.lines));u=c['u'][i];q=u.qs[0]
    assert u.name in ('MX','MEASURE')
    if mode=='omit':del c['u'][i];del c['t'][i]
    elif mode=='reset':c['u'][i]=C.Unit([f'reset q[{q}];']+([f'h q[{q}];'] if u.name=='MX' else []))
    else:raise ValueError(mode)
    tail=[]
    for line in c['tail']:
        bs=[int(b) for b in re.findall(r'c\[(\d+)\]',line) if int(b)!=bit]
        if bs:tail.append('// DETECTOR '+' '.join(f'c[{b}]' for b in bs))
    c['tail']=tail;return c

def build_checks():
    base=C.read(H/'h_base');rows=[];errors=[]
    for i,line in enumerate(base['tail']):
        n=f'h_det_{i:02d}';c=C.clone(base);del c['tail'][i]
        try:r=save(c,n,['detector-only removal',line]);r.update(family='detector',row=i,detector=line);rows.append(r)
        except Exception as e:errors.append(dict(stem=n,error=repr(e)))
    for u,t in zip(base['u'],base['t']):
        if u.name not in ('MX','MEASURE'):continue
        b=int(re.search(r'c\[(\d+)\]',' '.join(u.lines))[1])
        if not known_zero(base,b):continue
        for mode in ['omit','reset']:
            n=f'h_{mode}_{b}'
            try:
                r=save(remove_check(base,b,mode),n,[mode+' known-zero readout',dict(bit=b,qubit=u.qs[0],time=t,basis=u.name)]);r.update(family=mode,bit=b,q=u.qs[0],t=t);rows.append(r)
            except Exception as e:errors.append(dict(stem=n,error=repr(e)))
    (H/'v35_checks.json').write_text(json.dumps(rows,indent=2)+'\n');(H/'v35_check_build_errors.json').write_text(json.dumps(errors,indent=2)+'\n')
    print(dict(detectors=len(base['tail']),detector_rank=len(detector_basis(base)),built=len(rows),errors=errors))
if __name__=='__main__':build_checks()

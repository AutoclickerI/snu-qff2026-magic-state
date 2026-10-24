"""Port the clean BCFB preparations as full rank-6 endpoint replacements.

The v29c endpoint is rank 5, so the entire B+C prep through the B->C
boundary is replaced. Exterior gates are retained and frames reconstructed
by ST1's builder. The different rank is validated by the full judge.
"""
from common import *
import traceback
BC=module('comp29_bc_build','work/lanes/ST1/bc_build.py')

def source(kind='policy',value=9,base=None):
    assert kind=='endpoint'
    c=C.read(base);md,head,us,ts,tail=c['meta'],c['h'],c['u'],c['t'],c['tail'];R=md['R']
    init={q:max(i for i,u in enumerate(us) if u.qs==(q,) and ts[i]<R and u.name in ('RESET','RX','MEASURE','MX')) for q in C.B+C.C}
    rem=set(init.values())|{i for i,u in enumerate(us) if ts[i]<=R and u.name=='CX' and set(u.qs)<=set(C.B+C.C) and all(i>init[q] for q in u.qs)}
    assert sum(us[i].name=='CX' for i in rem)==sum(map(len,md['prep']['ops']))
    mxold={BC.bit(us[i]) for i in init.values() if us[i].name=='MX'}
    zold={BC.bit(us[i]) for i in init.values() if us[i].name=='MEASURE'}
    clean=[]
    for line in tail:
        if line.startswith('// DETECTOR'):
            bs=set(map(int,BC.BITS.findall(line)))
            if bs&zold:
                assert len(bs)==1,line
                continue
            bs-=mxold;assert bs,line
            line='// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(bs))
        else:assert not set(map(int,BC.BITS.findall(line)))&(mxold|zold)
        clean.append(line)
    return md,head,us,ts,clean,init,rem
BC.source=source

if __name__=='__main__':
    tags=['blue_d15_c90_s712_00007','v26n_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1','v26n_fast_d15_c105_s526_00356_preserve_rt1','v26n_fast_d15_c105_s526_00331_preserve_rt1','v26n_ic_fast_d15_c105_s526_00356_11_19_reset_rt1','v26n_fb_d14_c98_s517_00020_preserve','blue_d15_c90_s704_00057','v26n_fb_d15_c105_s506_00008_preserve_rt1','v26n_fb_d14_c98_s517_00020_reset']
    rows=[]
    for k,tag in enumerate(tags):
        try:
            orig=json.loads((ROOT/'work/lanes/BCFB/blue/finalists'/f'{tag}.json').read_text())
            d=copy.deepcopy(orig['prep']);d['ops'].append([list(e) for e in zip(C.B,C.C)]);d.update(kind='endpoint',value=0,endpoint_rank=6)
            opts=dict(orig['options'],base=str(ROOT/'work/lanes/MAIN/v29c'),retime_window=12)
            opts.pop('context',None)
            text,md=BC.build(d,opts)
            name=f'bc{k:02d}'
            (H/(name+'.qasm')).write_text(text);(H/(name+'.json')).write_text(json.dumps(md,indent=2)+'\n')
            c=C.read(H/name)
            # Preserve requested known-plus checks on the new preparation.
            checks=orig['options'].get('init_checks',[])
            if checks:
                for q in checks:
                    ids=[max(i for i,u in enumerate(c['u']) if u.name in ('RX','RESET','MEASURE','MX') and u.qs==(q,) and c['t'][i]<48)]
                    for i in reversed(ids):
                        u=c['u'][i];b=C.bit(c);plus=u.name in ('RX','MX')
                        lines=([f'h q[{q}];'] if plus else [])+[f'measure q[{q}] -> c[{b}];']+([f'h q[{q}];'] if plus else [])
                        bs=[b]+([BC.bit(u)] if u.name in ('MX','MEASURE') else [])
                        c['u'].insert(i+1,C.Unit(lines));c['t'].insert(i+1,c['t'][i]+1);c['tail'].append('// DETECTOR '+' '.join(f'c[{z}]' for z in bs))
                c=C.retime(c,round_fixed=True)
                assert c is not None,'init-check schedule infeasible'
            row=save(c,name,['bcfb:'+tag]);row.update(screen(name));rows.append(row)
        except Exception as e:rows.append(dict(source=tag,error=repr(e),traceback=traceback.format_exc()))
        print(json.dumps(rows[-1]),flush=True)
    (H/'bcfb_ports.json').write_text(json.dumps(rows,indent=2)+'\n')

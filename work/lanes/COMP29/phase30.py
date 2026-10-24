"""Port diagonal phases through the verified coherent data transfers."""
from build30 import *
if __name__=='__main__':
    base=C.read(H/'f_timing_best_r2');rows=[]
    for mask in (1,2,3):
        c=C.clone(base);desc=[]
        for k,(src,dst) in enumerate([(16,22),(8,21)]):
            if not(mask>>k&1):continue
            i=next(i for i,u in enumerate(c['u']) if u.lines==[f'tdg q[{src}];'])
            c['u'][i]=C.Unit([f'tdg q[{dst}];']);c['t'][i]=47;desc.append(f'Tdag{src}_to_{dst}')
        name='f_phase_'+str(mask)
        try:
            c=finish(c);row=save(c,name,['f_timing_best_r2']+desc);row.update(screen(name));rows.append(row);print(name,row['total'],row['exp_minus_A1'],flush=True)
        except Exception as e:rows.append(dict(stem=name,error=repr(e)));print(name,repr(e),flush=True)
    (H/'v30_phase.json').write_text(json.dumps(rows,indent=2)+'\n')

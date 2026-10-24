"""Revisit Z readout encodings and fresh preparation measurements."""
import os,sys,json,re,argparse,itertools
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(OUT),str(OUT/'inputs'),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from schedules import placement,write
from util import native_times
from exact2 import Eval
from ortools.sat.python import cp_model

REFERENCE={};TERMINAL=set();FIRST={};HORIZON=0

def toggle_tail(tail,sub):
    out=[]
    for l in tail:
        if l.startswith('// DETECTOR'):
            bits=set()
            for b in map(int,re.findall(r'c\[(\d+)\]',l)):
                bits^={b}
                if b in sub:bits^={sub[b]}
            l='// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(bits))
        out.append(l)
    return out

def check_write(src,name,us,h,tail,meta):
    m=cp_model.CpModel();tv=[m.new_int_var(0,HORIZON+3,f't{i}')for i in range(len(us))];last={}
    for i,u in enumerate(us):
        if id(u)in REFERENCE and id(u)not in TERMINAL:m.add(tv[i]==REFERENCE[id(u)])
        if u.name=='RESET'and len(u.qs)==1 and u.qs[0]not in last and id(u)not in REFERENCE:m.add(tv[i]==FIRST[u.qs[0]])
        for q in u.qs:
            if q in last:m.add(tv[i]>tv[last[q]])
            last[q]=i
    end=m.new_int_var(0,HORIZON+3,'end');m.add_max_equality(end,tv);dev=[]
    for i,u in enumerate(us):
        if id(u)in REFERENCE:
            d=m.new_int_var(0,HORIZON+3,f'd{i}');m.add_abs_equality(d,tv[i]-REFERENCE[id(u)]);dev.append(d)
    m.minimize(end*100000+sum(dev)*100+sum(tv));s=cp_model.CpSolver();s.parameters.num_search_workers=1
    status=s.solve(m);assert status in(cp_model.OPTIMAL,cp_model.FEASIBLE),(name,s.status_name(status))
    stem=write(src,name,[s.value(v)for v in tv],us,h,tail,meta)
    try:
        ev=Eval(stem.with_suffix('.qasm').read_text(),meta['data_qubits']);row=dict(correct=True,c1=float(ev.fp@ev.n_single))
    except Exception as ex:row=dict(correct=False,error=str(ex))
    stem.with_suffix('.build.json').write_text(json.dumps(row,indent=2)+'\n');print(name,row,flush=True)

def main(src):
    global REFERENCE,TERMINAL,FIRST,HORIZON
    stem=OUT/src;text=stem.with_suffix('.qasm').read_text();meta=json.loads(stem.with_suffix('.json').read_text());h,r,tail=S.qasm_ops(text);us=S.fold_units(r);ts=native_times(text,us)
    lastm={}
    for i,u in enumerate(us):
        if u.name=='MEASURE':lastm[u.qs[0]]=(i,int(re.findall(r'c\[(\d+)\]',u.lines[-1])[0]))
    REFERENCE={id(u):t for u,t in zip(us,ts)};TERMINAL={id(us[i])for i,b in lastm.values()};HORIZON=max(ts)
    for u,t in zip(us,ts):
        for q in u.qs:FIRST.setdefault(q,t)
    existing=[];remove=set();sub={}
    for c,t in [(17,16),(19,25)]:
        assert abs(c//6-t//6)+abs(c%6-t%6)==1
        ci,cb=lastm[c];ti,tb=lastm[t]
        j=max(i for i,u in enumerate(us)if i<min(ci,ti)and u.lines==[f'cx q[{c}],q[{t}];'])
        assert not any(c in u.qs or t in u.qs for u in us[j+1:min(ci,ti)])
        existing.append(dict(edge=[c,t],native_step=ts[j],readout_steps=[ts[ci],ts[ti]]));remove.add(j);sub[tb]=cb
    (OUT/(src+'.readout_edges.json')).write_text(json.dumps(existing,indent=2)+'\n')
    plain=[u for i,u in enumerate(us)if i not in remove];ptail=toggle_tail(tail,sub)
    for pairs in [[],[(17,16)],[(19,25)],[(17,16),(19,25)],[(17,16),(19,25),(14,8)],[(17,16),(19,25),(14,15)]]:
        nu=plain[:];ntail=ptail[:];sub={}
        for c,t in pairs:
            mi={u.qs[0]:(i,int(re.findall(r'c\[(\d+)\]',u.lines[-1])[0]))for i,u in enumerate(nu)if u.name=='MEASURE'}
            ci,cb=mi[c];ti,tb=mi[t];j=min(ci,ti);nu.insert(j,S.Unit([f'cx q[{c}],q[{t}];'],[]));sub[tb]=cb
        ntail=toggle_tail(ntail,sub);name=src+'_re_'+('_'.join(f'{c}-{t}'for c,t in pairs)or'none')
        check_write(src,name,nu,h,ntail,meta)
    # Fresh Z resets can use measurement initialization without any frame.
    seen=set();eligible=[]
    for i,u in enumerate(us):
        if not any(q in seen for q in u.qs)and u.name=='RESET':eligible.append((i,u.qs[0]))
        seen.update(u.qs)
    for subset in [[x]for x in eligible]+([eligible]if len(eligible)>1 else[]):
        nu=us[:];ntail=tail[:];nh=h[:];idx=max(map(int,re.findall(r'c\[(\d+)\]',text)))+1
        for i,q in subset:
            nu[i]=S.Unit([f'measure q[{q}] -> c[{idx}];'],[]);ntail.append(f'// DETECTOR c[{idx}]');idx+=1
        nh=[re.sub(r'creg c\[\d+\]',f'creg c[{idx}]',l)for l in nh]
        check_write(src,src+'_mi_'+('_'.join(str(q)for i,q in subset)),nu,nh,ntail,meta)
    (OUT/(src+'.minit_inventory.json')).write_text(json.dumps(dict(fresh_Z_resets=eligible),indent=2)+'\n')
    seen=set();measured=[]
    for i,u in enumerate(us):
        if not any(q in seen for q in u.qs)and u.name=='MEASURE':measured.append((i,u.qs[0],int(re.findall(r'c\[(\d+)\]',u.lines[0])[0])))
        seen.update(u.qs)
    for subset in [[x]for x in measured]+[measured]:
        nu=us[:];removebits={b for i,q,b in subset};ntail=[]
        for i,q,b in subset:nu[i]=S.Unit([f'reset q[{q}];'],[])
        for l in tail:
            if l.startswith('// DETECTOR'):
                bs=[int(b)for b in re.findall(r'c\[(\d+)\]',l)if int(b)not in removebits]
                if not bs:continue
                l='// DETECTOR '+' '.join(f'c[{b}]'for b in bs)
            ntail.append(l)
        check_write(src,src+'_reset_'+('_'.join(str(q)for i,q,b in subset)),nu,h,ntail,meta)

if __name__=='__main__':main(sys.argv[1])

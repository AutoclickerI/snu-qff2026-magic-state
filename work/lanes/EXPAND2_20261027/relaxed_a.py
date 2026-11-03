"""Test larger A X-spaces, trading final checks against resource error costs.

All results are complete native circuits and are raw/single/pair screened.
No lower-noise score is inferred solely from a cheaper state preparation.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import copy,contextlib,io,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/tools'))
sys.path.insert(0,str(ROOT/'work/lanes/NATIVE2_20261027'))
sys.path.insert(0,str(ROOT/'work/lanes/PREFIX2_20261027'))
from measured_assemble import assemble
from pairs import audit
from qtools import price


def span(rows):
    piv={}
    for row in rows:
        while row:
            j=row.bit_length()-1
            if j in piv:row^=piv[j]
            else:piv[j]=row;break
    for j in sorted(piv):
        for k in sorted(piv):
            if k>j and piv[k]>>j&1:piv[k]^=piv[j]
    return tuple(piv[k] for k in sorted(piv))


def main():
    native=ROOT/'work/lanes/NATIVE2_20261027'
    base=json.loads((native/'old_footprint_a_s1.json').read_text())
    a=base['candidates'][0];assert a['direct']
    bc=json.loads((native/'old_b_module.json').read_text())
    release={int(q):v for q,v in json.loads((native/'prefix_release.json').read_text())['release'].items()}
    states={r['q']:r for r in json.loads((native/'prefix_product_states.json').read_text())['cells']}
    original_plus=set(a['plus_inputs']);zero=sorted(set(a['A'])-original_plus)
    gates=[tuple(o['qs']) for o in a['operations'] if o['kind']=='CX']
    folder=HERE/'relaxed_a';folder.mkdir(exist_ok=True)
    results=[]
    for mask in range(1,1<<len(zero)):
        plus=original_plus|{q for i,q in enumerate(zero) if mask>>i&1}
        state=span(1<<q for q in plus);kept=[]
        for u,v in gates:
            new=span(row^(1<<v) if row>>u&1 else row for row in state)
            if new!=state:kept.append((u,v));state=new
        product_plus={q for q in a['A'] if len(span([*state,1<<q]))==len(state)}
        active=set(a['A'])-product_plus
        used=active|{q for edge in kept for q in edge}
        known=lambda q:states[q].get('product_axis')==('X' if q in plus else 'Z') and not states[q].get('phase_xor') and not states[q].get('phase_constant')
        ready={q:release[q]+int(not known(q)) for q in used};scheduled=[]
        for u,v in kept:
            t=max(ready[u],ready[v]);scheduled.append(dict(kind='CX',qs=[u,v],time=t));ready[u]=ready[v]=t+1
        first={q:min((o['time'] for o in scheduled if q in o['qs']),default=release[q]+1) for q in used}
        operations=list(scheduled)
        for q in used:
            if first[q]==release[q] and known(q):continue
            operations.append(dict(kind='RX' if q in plus else 'R',qs=[q],time=first[q]-1))
        module=dict(operations=sorted(operations,key=lambda o:(o['time'],o['kind'],o['qs'])),A=a['A'],cx=len(kept),
                    extra_plus_inputs=sorted(plus-original_plus),product_plus_outputs=sorted(product_plus),
                    target='X-space containing encoded plusL; fewer final data-X checks',
                    x_stabilizers=list(state))
        adoc=dict(prefix_stem=base['prefix_stem'],candidates=[module])
        bdoc=copy.deepcopy(bc)
        bdoc['terminal_operations']=[o for o in bdoc['terminal_operations']
                                    if not (o[0]=='CX' and o[1][1] in product_plus)
                                    and not (o[0]=='M' and o[1][0] in product_plus)]
        apath=folder/f'a_{mask}.json';bpath=folder/f'b_{mask}.json'
        apath.write_text(json.dumps(adoc,indent=2)+'\n');bpath.write_text(json.dumps(bdoc,indent=2)+'\n')
        with contextlib.redirect_stdout(io.StringIO()):
            result=assemble(apath,bpath,0,0,f'relaxed_a_{mask}',do_singles=True)
        row=dict(mask=mask,stem=result['stem'],raw=result['raw'],cx=result['cx'],ticks=result['ticks'],
                 extra_plus_inputs=module['extra_plus_inputs'],product_plus_outputs=sorted(product_plus),
                 c1=result.get('singles',{}).get('c1'))
        if result['raw']['ok'] and row['c1']<1e-10:
            with contextlib.redirect_stdout(io.StringIO()):
                pairs=audit(result['stem'],folder/f'pairs_{mask}.json')
            row['c2']=pairs['c2']
            if row['c2']<38:
                row['exact']=price(result['stem'],1)
        results.append(row)
        (HERE/'relaxed_a_results.json').write_text(json.dumps(results,indent=2)+'\n')
        print(json.dumps(row),flush=True)


if __name__=='__main__':main()

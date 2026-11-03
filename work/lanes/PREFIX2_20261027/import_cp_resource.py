"""Rebuild the connected B descriptor from an END2 strict CP witness."""
import argparse,json
from pathlib import Path
from b_resource import contract
from resource_pauli_audit import audit
from measured_resource import ROOT,HERE,canonical


def rebuild(solution,a_module,output):
    pc=contract(True);source=Path(solution);x=json.loads(source.read_text())
    assert x['status'] in ('FEASIBLE','OPTIMAL') and not x['direct_plus']
    assert list(x['A'])==pc.B
    used={q for o in x['operations'] if o['kind']=='CX' for q in o['qs']}
    ops=[o for o in x['operations'] if o['kind']!='H' and set(o['qs'])&used]
    initial={q:0 for q in pc.COLS};initial.update({int(q):v for q,v in x['initial_rows'].items()});final=initial.copy()
    for o in ops:
        if o['kind']=='CX':
            a,b=o['qs'];assert abs(a//6-b//6)+abs(a%6-b%6)==1
            final[b]^=final[a]
    helpers=sorted(used-set(pc.B));assert all(not final[q] for q in helpers)
    assert canonical({q:final[q] for q in pc.B},3)==canonical({q:pc.COLS[q] for q in pc.B},3)
    assert sum(bool(v) for v in initial.values())==3
    touched=set()
    for o in ops:
        for q in o['qs']:
            key=o['time'],q
            assert key not in touched,('Physical collision',key)
            touched.add(key)
    m=dict(operations=ops,cx=x['cx'],helpers=helpers,helper_byproducts=[],initial_rows=initial,final_rows=final,
           target_columns=pc.COLS,resource_rank=3,dual_a=False,reused_inputs=x['reused_inputs'],plus_inputs=x['plus_inputs'],
           resource_ready=max(o['time']+1 for o in ops if set(o['qs'])&set(pc.B)),module_end=max(o['time'] for o in ops)+1)
    result=audit(pc,m,True);m['resource_c1']=result['resource_c1'];assert result['resource_c1']<1e-12,result
    base=json.loads(Path(a_module).read_text())
    out=dict(prefix_stem=base['prefix_stem'],roles=base['roles'],square_mask=0,terminal_operations=pc.terminal(),
             b_only=True,swapped=True,candidates=[m],audit=result,
             provenance=dict(cp_solution=str(source),a_module=str(a_module),removed='Final all-A Hadamards and disconnected dummy heralds'))
    Path(output).write_text(json.dumps(out,indent=2)+'\n')
    return out


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--solution',default=str(ROOT/'work/lanes/END2_20261027/sol/a_flag_dual_R50_h0_1.json'))
    ap.add_argument('--a-module',default=str(ROOT/'work/lanes/NATIVE2_20261027/dual_old_a_module.json'))
    ap.add_argument('--output',default=str(HERE/'b_connected_cp18.json'));args=ap.parse_args()
    out=rebuild(args.solution,args.a_module,args.output);m=out['candidates'][0]
    print(json.dumps({k:m[k] for k in ('cx','resource_ready','module_end','resource_c1')},indent=2))

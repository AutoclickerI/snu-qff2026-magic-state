"""A complete 48-tick instrument with a real data pulse slot between checks.

Use END2's all-A-ready44 resource, tap D into A at44, and keep B-to-D at46.
The A phase readout still finishes at47. The empty data slots45 and47 permit
Clifford echoes which rotate the second checked syndrome relative to the first.
All native operations and their noise are retained.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import contextlib,copy,io,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/lanes/NATIVE2_20261027'))
sys.path.insert(0,str(ROOT/'work/lanes/PREFIX2_20261027'))
from measured_assemble import assemble
from pairs import audit


def build():
    solution_path=ROOT/'work/lanes/END2_20261027/sol/a_herald_R44_all_strong_h82.json'
    solution=json.loads(solution_path.read_text())
    bpath=ROOT/'work/lanes/NATIVE2_20261027/strong48_a9_m9_source_b_module.json'
    bdoc=json.loads(bpath.read_text())
    A,D=(bdoc['roles'][k] for k in ('A','D'))
    assert solution['A']==A and solution['a_ready']==44
    assert solution['logical_x_herald']==[8,14,15]
    aops=copy.deepcopy(solution['operations'])
    assert all(o['time']<44 for o in aops)
    aops += [dict(kind='CX',qs=[d,a],time=44) for d,a in zip(D,A)]
    aops += [dict(kind='CX',qs=[14,8],time=45),dict(kind='CX',qs=[15,14],time=46)]
    aops += [dict(kind='M',qs=[q],time=45) for q in (7,13,9,21)]
    aops += [dict(kind='M',qs=[8],time=46),dict(kind='M',qs=[14],time=47),dict(kind='MX',qs=[15],time=47)]
    # The actual selected prefix is replayed by the assembler. This copy keeps
    # all old B preparations, heralds, and its two physical acceptance modes.
    adoc=dict(prefix_stem=bdoc['prefix_stem'],source_solution=str(solution_path),
              candidates=[dict(A=A,operations=aops)],logical_x_herald=[8,14,15],
              scope='All A taps at44, B taps46, readout47; native data pulse slot45.')
    folder=HERE/'between_checks';folder.mkdir(exist_ok=True)
    apath=folder/'a_module.json';bp=folder/'b_module.json'
    apath.write_text(json.dumps(adoc,indent=2)+'\n');bp.write_text(json.dumps(bdoc,indent=2)+'\n')
    with contextlib.redirect_stdout(io.StringIO()):
        result=assemble(apath,bp,0,0,'between_checks_control',terminal_start=46,do_singles=True)
        if result['raw']['ok'] and result['singles']['c1']<1e-10:
            pair=audit(result['stem'],folder/'control_pairs.json')
            result['c2']=pair['c2']
    (folder/'control.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result.get(k) for k in ('stem','raw','cx','ticks','singles','c2')}),flush=True)
    return result


if __name__=='__main__':build()

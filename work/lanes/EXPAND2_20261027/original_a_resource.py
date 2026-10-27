"""Isolate the incumbent's A preparation/readout from its idle parking gates."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import contextlib,copy,io,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/tools'))
sys.path.insert(0,str(ROOT/'work/lanes/NATIVE2_20261027'))
sys.path.insert(0,str(ROOT/'work/lanes/PREFIX2_20261027'))
from measured_assemble import assemble
from pairs import audit
from park_data import make as park


def main():
    native=ROOT/'work/lanes/NATIVE2_20261027'
    old=json.loads((native/'old_a_instrument.json').read_text())
    bc=json.loads((native/'old_b_module.json').read_text())
    A=bc['roles']['A'];B=bc['roles']['B'];D=bc['roles']['D']
    operations=[copy.deepcopy(o) for o in old['candidates'][0]['operations']
                if (o['kind']=='CX' and set(o['qs'])<=set(A) and o['time']<=45)
                or (o['kind']=='RX' and o['qs'][0] in (8,9,21))
                or (o['kind']=='MX' and o['qs']==[8] and o['time']==38)]
    assert sum(o['kind']=='CX' for o in operations)==11
    operations += [dict(kind='CX',qs=[D[i],A[i]],time=45 if i in (0,4) else 46) for i in range(7)]
    operations += [dict(kind='CX',qs=[8,7],time=46),dict(kind='CX',qs=[9,8],time=47)]
    operations += [dict(kind='M',qs=[q],time=47) for q in (7,14,13,21,15)]
    operations += [dict(kind='M',qs=[8],time=48),dict(kind='MX',qs=[9],time=48)]
    adoc=dict(prefix_stem=bc['prefix_stem'],candidates=[dict(A=A,operations=operations)],
              scope='Original11CX A preparation and2CX logical-X readout; independent idle parking omitted.')
    bc['terminal_operations']=[['CX',[b,d],0,None] for b,d in zip(B,D)]+[['MX',[b],1,None] for b in B]
    folder=HERE/'original_a';folder.mkdir(exist_ok=True)
    apath=folder/'a.json';bpath=folder/'b.json'
    apath.write_text(json.dumps(adoc,indent=2)+'\n');bpath.write_text(json.dumps(bc,indent=2)+'\n')
    with contextlib.redirect_stdout(io.StringIO()):
        result=assemble(apath,bpath,0,0,'original_a_no_parking',terminal_start=47,do_singles=True)
        pair=audit(result['stem'],folder/'base_pairs.json')
    row=dict(stem=result['stem'],raw=result['raw'],c1=result['singles']['c1'],c2=pair['c2'],cx=result['cx'],ticks=result['ticks'])
    rows=[row];print(json.dumps(row),flush=True)
    for which,link in [(3,False),(3,True)]:
        r=park(result['stem'],link,which);rows.append(r);print(json.dumps(r),flush=True)
    (HERE/'original_a_results.json').write_text(json.dumps(rows,indent=2)+'\n')


if __name__=='__main__':main()

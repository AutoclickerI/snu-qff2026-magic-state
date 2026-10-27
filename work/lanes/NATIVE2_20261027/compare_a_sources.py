"""Replay the same measured-A map against independently certified prefixes."""
import contextlib,io,json,random,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
import boundary_product,a_factory as af,a_measured,a_factory_verify

def main():
    seed=json.loads((HERE/'a_measured.json').read_text())['candidates'][2]
    af.A=seed['A'];af.TARGET={q:af.A.index(q)+1 if q in af.A else 0 for q in af.CELLS}
    gates=[tuple(o['qs']) for o in seed['operations'] if o['kind']=='CX']
    initial={int(q):v for q,v in seed['initial_rows'].items()};final={int(q):v for q,v in seed['final_rows'].items()};out=[]
    for tag in ('pairs_fixed','original_asap_jit'):
        boundary_path=ROOT/'work/lanes/EXPAND2_20261027/source_variants'/tag/'release.json'
        states_path=HERE/f'{tag}_product_states.json'
        with contextlib.redirect_stdout(io.StringIO()):cert=boundary_product.certify(boundary_path,states_path)
        boundary=json.loads(boundary_path.read_text());release={int(q):v for q,v in boundary['release'].items()};states={r['q']:r for r in cert['cells']}
        row=a_measured.schedule(initial,gates,final,release,states,random.Random(1))
        path=HERE/f'a_measured_{tag}.json';path.write_text(json.dumps(dict(prefix_stem=boundary['stem'],boundary_file=str(boundary_path),states_file=str(states_path),candidates=[row]),indent=2)+'\n')
        with contextlib.redirect_stdout(io.StringIO()):check=a_factory_verify.verify(path)
        result=dict(source=tag,source_cx=boundary['cx'],source_ticks=boundary['source_ticks'],
            a_ready=row['a_ready'],resource_cx=row['cx'],helper_release=row['helper_release'],resource_ok=check['resource_ok'],
            raw=check['raw'],stem=check['stem'],module=str(path.relative_to(ROOT)))
        out.append(result);print(json.dumps(result),flush=True)
    (HERE/'a_source_comparison.json').write_text(json.dumps(out,indent=2)+'\n')

if __name__=='__main__':main()

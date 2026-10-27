"""Remove state identities from native resource witnesses while retaining F1."""
import argparse,json,sys,time
from pathlib import Path
from joint_resource_beam import finish,safe
import partial_contract as pc
HERE=Path(__file__).resolve().parent


def rank(rows):
    b={}
    for x in rows:
        while x:
            h=x.bit_length()-1
            if h not in b:b[h]=x;break
            x^=b[h]
    return len(b)


def bad_count(cells,gates):
    x={q:pc.fault_signature(q,'X',pc.HELPERS if len(cells)>21 else []) for q in cells}
    z={q:pc.fault_signature(q,'Z',pc.HELPERS if len(cells)>21 else []) for q in cells}
    n=0
    for a,b in reversed(gates):
        n+=int(not safe(x[a]^x[b]))+int(not safe(z[a]^z[b]))
        x[a]^=x[b];z[b]^=z[a]
    return n


def run(path):
    source_path=Path(path).resolve()
    start=time.perf_counter();rec=json.loads(source_path.read_text());cells=rec['cells']
    initial=dict(zip(cells,rec['initial_rows']))
    gates=[tuple(v) for v in reversed(rec['backward_path'])]
    before=len(gates);bad=bad_count(cells,gates)
    assert bad==rec['unsafe_cx_axis_checks'],(bad,rec['unsafe_cx_axis_checks'])
    changed=True
    while changed:
        changed=False;rows=dict(initial);i=0
        while i<len(gates):
            a,b=gates[i]
            identity=rows[a]==0 or rank([v for q,v in rows.items() if q!=b])<11
            if identity:
                alt=gates[:i]+gates[i+1:];nb=bad_count(cells,alt)
                if nb<=bad:gates=alt;bad=nb;changed=True;continue
            rows[b]^=rows[a];i+=1
        for i,(a,b) in enumerate(gates):
            removed=False
            for j in range(i+1,len(gates)):
                c,d=gates[j]
                if (a,b)==(c,d):
                    alt=gates[:i]+gates[i+1:j]+gates[j+1:]
                    nb=bad_count(cells,alt)
                    if nb<=bad:gates=alt;bad=nb;changed=True;removed=True
                    break
                if a==d or b==c:break
            if removed:break
    rows=[pc.COLS[q] for q in cells]
    xs=[pc.fault_signature(q,'X',pc.HELPERS if len(cells)>21 else []) for q in cells]
    zs=[pc.fault_signature(q,'Z',pc.HELPERS if len(cells)>21 else []) for q in cells]
    path=[]
    for a,b in reversed(gates):
        i,j=cells.index(a),cells.index(b);path.append((i,j))
        rows[j]^=rows[i];xs[i]^=xs[j];zs[j]^=zs[i]
    # Reversing the shortened circuit may choose a different free basis but
    # must still end on the same product |+>/|0> initialization pattern.
    assert [q for q,v in zip(cells,rows) if v]==rec['initial_plus_qubits']
    out=finish(cells,(tuple(rows),tuple(xs),tuple(zs)),path,2000+rec['seed'],bad==0,time.perf_counter()-start)
    out.update(parent=str(source_path),original_cx=before,
               unsafe_cx_axis_checks=bad,method='CSS state-identity and commuting-pair pruning')
    target=HERE/'joint_resource'/f'pruned_s{rec["seed"]}.json'
    target.write_text(json.dumps(out,indent=2)+'\n')
    print('PRUNED',target,before,len(gates),out['depth'],bad,flush=True)
    return out


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('paths',nargs='+');args=ap.parse_args()
    for p in args.paths:run(p)

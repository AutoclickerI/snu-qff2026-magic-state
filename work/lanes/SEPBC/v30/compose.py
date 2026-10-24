from retime import *
source=ROOT/'work/lanes/COMP29/best'
c=annotate(read(source));out,r=solve(c,27,40,1)
assert out is not None,r
st=save(out,'v30/critical_comp29');r['screen']=score(st);r['source']=str(source);r['source_sha256']=hashlib.sha256(source.with_suffix('.qasm').read_bytes()).hexdigest();st.with_suffix('.build.json').write_text(json.dumps(r,indent=2));append_result('critical_comp29',r,'Apply the commuting critical-tail shortening to COMP29 verified composition; full noise repriced.');print(json.dumps(r),flush=True)

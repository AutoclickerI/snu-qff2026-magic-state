import sys,json,collections
from pathlib import Path
from build import H,S,native_times,source

def canonical(text):
 h,r,tail=S.qasm_ops(text);u=S.fold_units(r);t=native_times(text,u);return u,t
base_text=(H/'inputs/v23h_c2c9.qasm').read_text();bu,bt=canonical(base_text)
for stem in sys.argv[1:]:
 p=H/'finalists'/stem;md=json.loads(p.with_suffix('.json').read_text());u,t=canonical(p.with_suffix('.qasm').read_text());B,C=collections.Counter(),collections.Counter()
 for x,tt in zip(bu,bt):B[(tt,tuple(x.lines))]+=1
 for x,tt in zip(u,t):C[(tt,tuple(x.lines))]+=1
 minus=[dict(time=tt,lines=ls,count=n) for (tt,ls),n in (B-C).items()];plus=[dict(time=tt,lines=ls,count=n) for (tt,ls),n in (C-B).items()]
 r=dict(stem=stem,base='v23h_c2c9',removed=minus,added=plus,options=md.get('options'),retained_previous_X_states=md.get('retained_previous_X_states'),unfolded_previous_MX=md.get('unfolded_previous_MX'),non_BC_time_changes=md.get('non_BC_time_changes'))
 p.with_suffix('.diff.json').write_text(json.dumps(r,indent=2));print(stem,'removed',len(minus),'added',len(plus),'CX',md['CX'],'piv',md['prep']['pivots'])

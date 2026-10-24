import json,time
from pathlib import Path
from build import build
from retime import run as retime
from reuse_A import reuse
from synth_resource import configure,F,endpoint
H=Path(__file__).resolve().parent
out=[]
for i,seed in [(117,3),(564,4),(2,5),(1162,6)]:
 p=H/f'r{i}_d11_s{seed}.prep.json';d=json.loads(p.read_text());configure(d['B'],d['C']);v=F.verify(d,clean=True);e=endpoint(d,d['B'],d['C']);assert v['target_ok']and not v['bad'];p.with_suffix('.recovered.json').write_text(json.dumps(dict(status='SAT witness independently revalidated',verification=v,endpoint=e,note='Original SAT process wrote this valid witness, then failed receipt hashing because FRESH source was absent remotely; this is witness recovery, not a successful original process exit.'),indent=2))
 stem=build(p,f'region{i}_d11');retime(stem,stem.name+'_alap');reuse(stem,stem.name+'_reuseA');out += [stem.name+'_alap',stem.name+'_reuseA']
(H/'batch_stems.json').write_text(json.dumps(out,indent=2))

from build import *
import numpy as np
import exact2,model
from fast_third import third_order
sys.path.insert(0,str(ROOT/'work/lanes/MAIN'))
import regions
name=sys.argv[1] if len(sys.argv)>1 else 'tdg_0';stem=OUT/name;text=stem.with_suffix('.qasm').read_text();h,u,ts,tail,meta=read(stem);meta['_stem']=str(stem)
reg=regions.unit_regions(u,ts,meta);qmap=S.native_qasm_index(text);raw_to_unit={j:i for i,x in enumerate(u)for j in x.raw_indices}
ev=exact2.Eval(text,meta['data_qubits']);r=exact2.run(ev,1,keep_thr=1e-15,third=True);tri,big3=third_order(ev,1)
def region(fi):
 ch=ev.m.chans[ev.fch[fi]];lab=ev.m.labels[ev.m.prog[ch['ins']].line_no-1];mt=re.match(r'instruction (\d+)',lab)
 return reg[raw_to_unit[qmap[int(mt.group(1))]]] if mt else 'other'
pairs={};hpair=[];htri=[]
for c,i,j,n,a in r['big']:
 key=' x '.join(sorted([region(i),region(j)]));pairs[key]=pairs.get(key,0)+c
 if 'hop' in (region(i),region(j)):hpair.append(dict(value=c,faults=[ev.fault_label(k)for k in(i,j)],regions=[region(k)for k in(i,j)]))
for c,i,j,k in big3:
 if 'hop' in (region(i),region(j),region(k)):htri.append(dict(value=c,faults=[ev.fault_label(a)for a in(i,j,k)],regions=[region(a)for a in(i,j,k)]))
out=dict(name=name,second=r['loss2'],third=tri+r['t3bc'],total=r['loss']+tri+r['t3bc'],pair_threshold=1e-15,triple_threshold=3e-13,pairs=pairs,hop_pairs=sorted(hpair,key=lambda x:-x['value'])[:60],hop_triples=sorted(htri,key=lambda x:-x['value'])[:60])
stem.with_suffix('.attribution.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)

"""Ablate the joint-search gain: delay tile-0 Bell preparation into its unused slot."""
from search_v10 import *
raw,data,ops,times,npre=base()
labels=[]
for parent in ('v10_reference','boundary_cm0_s5','lns1_0013'):
    meta=json.loads((HERE/(parent+'.json')).read_text());ts=list(meta['schedule']['times'])
    assert tuple(ops[144][1])==(1,2) and ops[144][0]=='cx'
    ts[144]+=1
    label='bell0_delay_'+parent
    save(label,raw,data,ops,ts,npre,{'change':'Delay only tile-0 Bell CX (1,2) by one layer; reset placement follows it lazily','parent':parent,'changed_op':144})
    labels.append(label)
(HERE/'bell_manifest.json').write_text(json.dumps(labels,indent=2)+'\n')

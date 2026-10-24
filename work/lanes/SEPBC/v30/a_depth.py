from retime import *
c=annotate(read(H/'inputs/v30f'))
d=json.loads((ROOT/'work/lanes/EXENC/prepA_L5_exact_stats.json').read_text())['depth_optimal']
old=[o for o in c['ops']if o['tag']=='encoder_a'and unit(o).name=='CX'];assert len(old)==11,len(old)
new=[]
for t,layer in enumerate(d['ops']):
 for a,b in layer:new.append(dict(lines=[f'cx q[{a}],q[{b}];'],t=43+t,tag='encoder_a',origin_t=43+t))
rest=[o for o in c['ops']if o not in old];c['ops']=[o for o in rest if o['t']<48]+new+[o for o in rest if o['t']>=48]
for i,o in enumerate(c['ops']):o['id']=i
out,r=solve(c,27,30,1)
assert out is not None,r
st=save(out,'v30/a_depth5');r['screen']=score(st);r['A_recipe']=d;st.with_suffix('.build.json').write_text(json.dumps(r,indent=2));append_result('a_depth5',r,'EXENC depth-optimal 11-CX A, same pivots and cells, followed by commuting-tail scheduling.');print(json.dumps(r),flush=True)

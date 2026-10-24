from core import *
sys.path.insert(0,str(H/'v34'));from assemble_layers import assemble,fit
root=ROOT/'work/lanes/BCFB';srcs=list((root/'a35/candidates').glob('frontier_*.json'))+list((root/'a35/candidates').glob('enc_*.json'))
srcs+=[root/'a34/candidates'/f'{s}.json'for s in['encoders_00013','encoders_00014','zreuse_00006']]
seen=set();rows=[]
for src in sorted(srcs):
 md=json.loads(src.read_text());opt=md.get('options',{});e=opt.get('enc',opt.get('parent_options',{}).get('enc'))
 if not e:continue
 layers=e['ops'];flat=layers if layers and isinstance(layers[0][0],int)else[g for layer in layers for g in layer];key=(tuple(e['pivots']),tuple(map(tuple,flat)))
 if key in seen:continue
 seen.add(key)
 # Free cell-specific start times; order from the delivered native path.
 # Re-derive on v36a's actual release graph with explicit reset inputs.
 for check16 in[False,True]:
  rec=dict(mode=2,R=44,pivots=e['pivots'],ops=[[36+i//2,u,v]for i,(u,v)in enumerate(flat)])
  c=assemble(base(),rec)
  if check16 and 16 in e['pivots']:
   b=bit(c);rx=next(o for o in c['ops']if o['lines']==['reset q[16];','h q[16];']and o.get('tag')=='encoder_a');idx=c['ops'].index(rx);c['ops'].insert(idx+1,dict(t=rx['t']+1,lines=['h q[16];',f'measure q[16] -> c[{b}];','h q[16];'],tag='encoder_a'));c['tail'].append(f'// DETECTOR c[{b}]');c['h']=[re.sub(r'creg c\[\d+\]',f'creg c[{b+1}]',l)for l in c['h']]
  elif check16:continue
  name=f'bcfb_{len(rows):03d}';d,r=fit(c,4,cut=0,phases=True);row=dict(stem=name,source=str(src.relative_to(ROOT)),source_options=opt,check16=check16,schedule=r)
  if d:
   try:st,z=write(d,name,dict(family='BCFB_encoder_port',source=str(src.relative_to(ROOT)),pivots=e['pivots'],check16=check16));row['screen']=z
   except Exception as ex:row['error']=repr(ex);print(name,repr(ex),flush=True)
  else:print(name,r,flush=True)
  rows.append(row);(V/'bcfb_builds.json').write_text(json.dumps(rows,indent=2))
print('distinct encoders',len(seen),'attempted variants',len(rows),flush=True)

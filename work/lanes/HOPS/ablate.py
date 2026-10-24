from build import *
import exact2,model
from fast_third import third_order
sys.path.insert(0,str(ROOT/'work/lanes/MAIN'));import regions
stem=OUT/'tdg_0';text=stem.with_suffix('.qasm').read_text();h,u,ts,tail,meta=read(stem);meta['_stem']=str(stem);reg=regions.unit_regions(u,ts,meta)
qmap=S.native_qasm_index(text);raw_to_unit={j:i for i,x in enumerate(u)for j in x.raw_indices};converted,labels,errs=model.convert(text,36,model.STANDARD);orig=model.noise_blocks
rows=[]
for mode in ['gate','idle','all']:
 def nb(stim,p,noise,first_order=False):
  prog,blocks=orig(stim,p,noise,first_order);_,_,gaps=model.schedule(stim)
  for i,ins in enumerate(prog):
   mt=re.match(r'instruction (\d+)',labels[ins.line_no-1]);owner=reg[raw_to_unit[qmap[int(mt.group(1))]]] if mt and int(mt.group(1))in qmap else 'other'
   if owner!='hop':continue
   n=sum(g[0]==i for g in gaps)
   for j,line in enumerate(blocks[i]):
    isidle=n>0 and j>=len(blocks[i])-n
    if ((isidle and mode in['idle','all'])or (not isidle and mode in['gate','all'])) and line.startswith('DEPOLARIZE'):
     blocks[i][j]=re.sub(r'\(([^)]*)\)','(0)',line,count=1)
  return prog,blocks
 model.noise_blocks=nb
 try:
  ev=exact2.Eval(text,meta['data_qubits']);r=exact2.run(ev,1,keep_thr=1,third=True,log=lambda*a:None);t=third_order(ev,1)[0]+r['t3bc'];row=dict(no_hop=mode,c1p=r['loss1'],second=r['loss2'],third=t,total=r['loss']+t,exp_minus_A1=float(exact2.np.exp(-r['A1'])));rows.append(row);print(row,flush=True);(OUT/'hop_ablation.json').write_text(json.dumps(rows,indent=2)+'\n')
 finally:model.noise_blocks=orig

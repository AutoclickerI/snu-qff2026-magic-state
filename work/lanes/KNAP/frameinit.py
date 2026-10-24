"""Native measure-inits with propagated detector records, no standalone detector.

Only a Pauli that does not flip a subsequent non-Clifford rotation can be
propagated this way. The full judge still decides correctness for every record.
"""
from search import *

def main():
 source='final_m2c_l2';c=loadc(OUT/source);text=(OUT/source).with_suffix('.qasm').read_text();ev=exact2.Eval(text,c['meta']['data_qubits']);jobs=[];mapping=[]
 # The converter places each detector immediately after its last record. Its
 # model ordering therefore differs from the declaration order in the QASM tail.
 detorder=[int(re.fullmatch(r'DETECTOR line (\d+)',ev.m.labels[ins.line_no-1])[1])-1 for ins in ev.m.prog if ins.name=='DETECTOR']
 for i,u in enumerate(c['u']):
  if u.name not in('RX','RESET'):continue
  q=u.qs[0];chs=[k for k,ch in enumerate(ev.m.chans)if ch['kind']=='flip'and ch['when']=='after'and ch['qubits']==[q]and ev.chan_label(k)['steps']==str(c['t'][i])]
  if len(chs)!=1:mapping.append(dict(unit=i,error='channel match',matches=chs));continue
  f=next(f for f in ev.m.faults if f['chan']==chs[0]);mapping.append(dict(unit=i,lines=u.lines,s=f['s'],d=f['d'],e=f['e']))
  if f['s']:continue
  v=copy.deepcopy(c);v['u'][i]=Unit(([f'h q[{q}];']if u.name=='RX'else[])+[f'measure q[{q}] -> c[230];']+([f'h q[{q}];']if u.name=='RX'else[]))
  flipped={detorder[d]for d in range(len(detorder))if f['d']>>d&1};d=0
  for j,line in enumerate(v['tail']):
   if line.startswith('// DETECTOR'):
    if d in flipped:v['tail'][j]=line+' c[230]'
    d+=1
  try:jobs.append(write(v,f'frame2_u{i}',dict(kind='frame_init',source=source,unit=i,q=q,axis='X'if u.name=='RX'else'Z',detector_mask=f['d'],declaration_indices=sorted(flipped),output_signature=f['e'])))
  except Exception as e:print(i,repr(e),flush=True)
 (OUT/'frame2_mapping.json').write_text(json.dumps(mapping,indent=2)+'\n');(OUT/'frame2_manifest.json').write_text(json.dumps(jobs,indent=2)+'\n');print('frame inits',len(jobs),flush=True)

if __name__=='__main__':main()

from round35 import *

def alternate(stem,name):
 ops,dets,md=load(stem)
 for o in ops:
  if o.kind=='CX' and o.qs==(8,9) and o.time==45:o.qs=(9,8)
  if o.time==46 and o.qs==(8,) and o.kind=='MX':o.kind='M'
  if o.time==46 and o.qs==(9,) and o.kind=='M':o.kind='MX'
 dets=[{17 if b==16 else 16 if b==17 else b for b in row} for row in dets]
 return emit(name,ops,dets,md,dict(flag_qubit=9,readout_network=[[9,15,44],[9,8,45]],input=str(stem)))

def comp_edge():
 ops,dets,md=load(BASE);bits={267,268}
 ops=[o for o in ops if not ((o.kind=='R' and o.qs[0] in (34,35) and o.time==44) or (o.kind=='CX' and o.qs in ((29,35),(28,34)) and o.time==45) or o.bit in bits)]
 dets=[row for row in dets if not row&bits]
 for row in dets:
  if 26 in row:row.symmetric_difference_update({27})
 ops.append(f.Op('CX',(28,29),45))
 return emit('comp_edge28_29_dropcopies',ops,dets,md,dict(imported_edge='COMP29/g_edge_28_29',removed_copies=[28,29]))

if __name__=='__main__':
 stems=[alternate(BASE,'flag9'),alternate(D/'sx_full','sx_flag9'),comp_edge()]
 (D/'flags_stems.json').write_text(json.dumps(list(map(str,stems)),indent=2))
 for stem in stems:
  try:print(stem.name,certify(stem),speed(stem,5000),flush=True)
  except Exception as e:print('ERROR',stem.name,repr(e),flush=True)

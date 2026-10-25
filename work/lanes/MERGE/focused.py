from campaign import *
from merge_build import menu
def main():
 base=M.read(H/'builds/CPGcore_read');tasks=[]
 def keep(c,n,why):
  st=save(c,n,why);tasks.append(dict(stem=str(st.relative_to(H)),why=why))
 # Save the failed restoration constraints rather than silently moving a readout.
 failures=[]
 for name,moves in [('P',[(38,39,[16,15]),(37,38,[15,16])]),('G',[(22,21,[16,15]),(23,22,[16,17])])]:
  try:
   v=copy.deepcopy(base)
   for old,new,qs in moves:v=M.apply_edit(v,M.mk(fam='shift',t=old,nt=new,qs=qs,name='CX'))
  except Exception as ex:failures.append(dict(lane=name,error=repr(ex),attempted=moves))
 write(H/'res/slot_restoration_failures.json',failures)
 # Test ancillary GLOBAL repairs on the complete three-way merge.
 dg=delta(M.read(H/'builds/A'),M.read(H/'builds/G'))
 source={k:[o for o in dg[k] if set(M.unit(o).qs)=={6}] for k in ['remove','add']}
 source.update(tail_remove=[],tail_add=['// DETECTOR c[356]'])
 guard=dict(remove=[],add=[dict(t=o['t']-1,lines=o['lines']) for o in dg['add'] if 31 in M.unit(o).qs],tail_remove=[],tail_add=['// DETECTOR c[357]'])
 for name,c in [('base',base)]:
  for tag,d in [('src6',source),('row5',guard)]:
   v=apply_delta(c,d);keep(v,'cpg_'+name+'_'+tag,'port GLOBAL '+tag+' on '+name)
  v=apply_delta(apply_delta(c,source),guard);keep(v,'cpg_'+name+'_allg','port GLOBAL source6 and row5 on '+name)
 write(H/'res/focused_tasks.json',tasks)
 print('focused',len(tasks),flush=True)
if __name__=='__main__':main()

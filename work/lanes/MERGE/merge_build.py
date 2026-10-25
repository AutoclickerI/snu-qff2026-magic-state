from campaign import *
def menu(c):
 st=M.status(c)
 es=M.removals(c)+M.trades(c)+M.shifts(c)+M.cx_adds(c,st)+M.gadget_adds(c,st)
 return {e['id']:e for e in es}
def build_ports():
 a=M.read(H/'builds/A');p=M.read(H/'builds/P');g=M.read(H/'builds/G');c=M.read(H/'builds/C')
 dp=delta(a,p);dg=delta(a,g);tasks=[];audit=[]
 def keep(c,name,why):
  st=save(c,name,why);tasks.append(dict(stem=str(st.relative_to(H)),why=why));return c
 # Keep COMPLETE's native timing; re-apply the exact ported menu edits.
 orig=json.loads((H.parent/'POLISH/res/base_menu.json').read_text())
 ids=['rm:pair_3_4_21','rm:pair_3_4_23','pair:2_3@21','pair:2_3@23','rmcx:12_13@10','cx:19_25@13']
 cm=menu(c);ed=[cm.get(i,orig[i]) for i in ids]
 cp,txt=M.apply_bundle(c,ed);keep(cp,'CPprefix','COMPLETE + compatible POLISH prefix edits')
 # GLOBAL core resource changes retain orientation but use COMPLETE's R45 slots.
 def coreop(o):
  return o['t']>=29 and set(M.unit(o).qs)<={17,18,23,24,26,27,28,29}
 core={k:[dict(t=o['t']-1,lines=o['lines']) for o in dg[k] if coreop(o)] for k in ['remove','add']}
 core.update(tail_remove=[l for l in dg['tail_remove'] if any(f'c[{b}]' in l for b in [330,331,333])],tail_add=[l for l in dg['tail_add'] if any(f'c[{b}]' in l for b in [330,331,333])])
 cg=apply_delta(c,core);keep(cg,'CGcore','COMPLETE + GLOBAL B/C orientations/source measurements at R45')
 cpg=apply_delta(cp,core);keep(cpg,'CPGcore','COMPLETE + POLISH prefix + GLOBAL B/C core at R45')
 for base_name,base in [('C',c),('CPprefix',cp),('CGcore',cg),('CPGcore',cpg)]:
  cm=menu(base);moves=[]
  for e in cm.values():
   if e['fam']=='shift' and e['name']=='MEASURE' and e['qs'][0] in [7,13,15,21] and e['t']>=46 and e['nt']==e['t']-1:moves.append(e)
  if moves:
   b,_=M.apply_bundle(base,moves);keep(b,base_name+'_read','reapply POLISH earlier terminal readouts on '+base_name);base=b;cm=menu(base)
  viable=[e for e in cm.values() if e['fam']=='cx' and e['a']==16 and e['b']==10 and 34<=e['t']<=44]
  for e in viable:
   b,_=M.apply_bundle(base,[e]);keep(b,base_name+'_cx'+str(e['t']),'reapply POLISH '+e['id']+' on '+base_name+' with readout repair')
  audit.append(dict(base=base_name,readouts=[e['id'] for e in moves],cx_slots=[e['id'] for e in viable]))
 # GLOBAL ancillary edits ported from its menu recipe, with R45 clock for row5.
 for basename in ['CGcore','CPGcore']:
  base=M.read(H/'builds'/basename)
  source={k:[o for o in dg[k] if M.unit(o).qs==[6] or tuple(M.unit(o).qs)==(6,)] for k in ['remove','add']}
  source.update(tail_remove=[],tail_add=['// DETECTOR c[356]'])
  b=apply_delta(base,source);keep(b,basename+'_src6','GLOBAL measured X source6 on '+basename)
  # Full remaining GLOBAL guard network shifted one tick. Pair16/17 needs local schedule restoration.
  for q31 in [False,True]:
   v=copy.deepcopy(b)
   if q31:
    extra=[dict(t=o['t']-1,lines=o['lines']) for o in dg['add'] if 31 in M.unit(o).qs]
    v=apply_delta(v,dict(remove=[],add=extra,tail_remove=[],tail_add=['// DETECTOR c[357]']))
   keep(v,basename+'_guard'+str(int(q31)),'GLOBAL src6 and shifted row5 guard='+str(q31)+' on '+basename)
 write(H/'res/port_audit.json',audit);write(H/'res/ports_tasks.json',tasks)
 print('ports',len(tasks),json.dumps(audit),flush=True)
if __name__=='__main__':build_ports()

import json,re,sys
from pathlib import Path

def barrier_with_helpers(line,helpers):
 qs=sorted(set(map(int,re.findall(r'q\[(\d+)\]',line)))|set(helpers))
 return 'barrier q['+'],q['.join(map(str,qs))+'];'

def copy4(src,out,startbit=230):
 L=Path(src).with_suffix('.qasm').read_text().splitlines(); helpers=(18,31,35,34)
 old=[i for i,l in enumerate(L) if l.strip()=='cx q[19],q[25];'][-1]
 b=next(i for i in range(old+1,len(L)) if L[i].startswith('barrier'))
 prev=max(i for i in range(old) if L[i].startswith('barrier'))
 # Move q29/q28 terminal readouts to after the copy layer.
 moved=[]
 for i,l in enumerate(L):
  if l.startswith('measure q[29] -> c[26]') or l.startswith('measure q[28] -> c[27]'):
   moved.append(l);L[i]=None
 # adjust positions after removed lines
 removed_before=lambda x:sum(v is None for v in L[:x])
 old-=removed_before(old);b-=removed_before(b);prev-=removed_before(prev)
 L=[l for l in L if l is not None]
 # helper reset immediately before the final preparation barrier; extend only this barrier
 L[prev]=barrier_with_helpers(L[prev],helpers)
 L[prev:prev]=[f'reset q[{q}];' for q in helpers]
 old+=len(helpers);b+=len(helpers)
 L[old]=None
 copies=[f'cx q[19],q[18];',f'cx q[25],q[31];',f'cx q[29],q[35];',f'cx q[28],q[34];']
 L[b:b]=copies; b+=len(copies)
 # include helpers in the barrier after the copy layer and put moved readouts after it
 L[b]=barrier_with_helpers(L[b],helpers)
 L[b+1:b+1]=moved
 L=[l for l in L if l is not None]
 # Add closing H after the terminal X-basis readouts only.
 terminal={28:6,29:26,30:13,31:11,32:4,33:23,34:27}
 i=0
 while i<len(L):
  m=re.match(r'measure q\[(\d+)\] -> c\[(\d+)\];',L[i])
  if m and int(m.group(2)) in terminal:
   q=int(m.group(1));
   if i+1>=len(L) or L[i+1]!=f'h q[{q}];':L.insert(i+1,f'h q[{q}];')
  i+=1
 # Fresh helpers must be present in every barrier to avoid a full-circuit idle span.
 for j,line in enumerate(L):
  if line.startswith('barrier q['): L[j]=barrier_with_helpers(line,helpers)
 # helper measurements after all terminal C readouts, at the final tick
 mi=next(i+1 for i,l in enumerate(L) if l.startswith('measure q[25] -> c[22]'))
 # Place after the complete final C readout block, before detectors; appending at end is same native tick but explicit.
 det=next(i for i,l in enumerate(L) if l.startswith('// DETECTOR'))
 L[det:det]=[f'measure q[{q}] -> c[{startbit+k}];' for k,q in enumerate(helpers)]
 for i,l in enumerate(L):
  if l=='// DETECTOR c[22] c[26] c[27]':L[i]='// DETECTOR c[22] c[23] c[26] c[27]'
  elif l=='// DETECTOR c[21] c[22] c[24] c[25] c[26] c[27]':L[i]='// DETECTOR c[21] c[22] c[23] c[24] c[25] c[26] c[27]'
 L += [f'// DETECTOR c[23] c[{startbit}]',f'// DETECTOR c[22] c[{startbit+1}]',f'// DETECTOR c[26] c[{startbit+2}]',f'// DETECTOR c[27] c[{startbit+3}]']
 Path(out).with_suffix('.qasm').write_text('\n'.join(L)+'\n')
 meta=json.loads(Path(src).with_suffix('.json').read_text());meta.update(source=str(src),method='reviewer3 item 1 readout copy4 corrected port',cx=int(meta.get('cx',0))+3,reviewer_copy_bits=list(range(startbit,startbit+4)))
 Path(out).with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
if __name__=='__main__':copy4(sys.argv[1],sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 230)

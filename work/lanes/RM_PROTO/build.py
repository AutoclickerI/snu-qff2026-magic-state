import os
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
from tprep.qasm import convert
import tprep.qasm as tq
tq.adjacent=lambda a,b: True
from tprep.exact import verify
from tprep.parse import declarations
BASE=Path(__file__).resolve().parent
DATA=[4,2,3,0,5,1,6]
ENC=[(7,4),(11,12),(7,2),(11,10),(13,12),(14,7),(14,11),(13,8),(4,3),(14,8),(8,1),(12,15),(9,8),(11,15),(14,6),(9,2),(11,4),(7,6),(9,10),(2,1),(12,5),(6,5),(10,15),(10,3),(13,6)]
class Circuit:
 def __init__(self): self.lines=[];self.nm=0;self.dets=[];self.frame=[];self.stages={}
 def gate(self,n,*qs): self.lines.append(n+' '+','.join(f'q[{q-1}]' for q in qs)+';')
 def reset(self,q,b='Z'):
  self.gate('reset',q)
  if b=='X': self.gate('h',q)
 def meas(self,q,b='Z',det=False):
  if b=='X':self.gate('h',q)
  r=self.nm;self.nm+=1;self.lines.append(f'measure q[{q-1}] -> c[{r}];')
  if det:self.dets.append([r])
  return r
 def barrier(self,qs=range(1,20)):self.gate('barrier',*qs)
 def stage(self,s):self.stages[s]=len(self.lines);self.lines.append('// STAGE '+s)
 def write(self,name,info):
  qasm='OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[36];\ncreg c[%d];\n'%self.nm+'\n'.join(self.lines)+'\n'
  qasm+=''.join('// DETECTOR '+' '.join(f'c[{r}]' for r in d)+'\n' for d in self.dets)
  qasm+='// FRAME_X(0)\n// FRAME_Z(0) '+' '.join(f'c[{r}]' for r in self.frame)+'\n'
  stim,labels,err=convert(qasm)
  assert not err,err
  (BASE/(name+'.qasm')).write_text(qasm)
  (BASE/(name+'.stim')).write_text(stim+'\n')
  info.update(data_qubits=DATA,paper_labels=[q+1 for q in DATA],stages=self.stages,measurements=self.nm,cx=sum(x.startswith('cx ') for x in self.lines),frame_classical_bits=self.frame)
  (BASE/(name+'.json')).write_text(json.dumps(info,indent=2)+'\n')
  return qasm,stim,info

def build(coherent=True,barriers=True):
 c=Circuit();c.stage('encoder')
 for q in range(1,16):c.reset(q,'X' if q in [7,9,11,13,14] else 'Z')
 for a,b in ENC:c.gate('cx',a,b)
 c.stage('logical_X_verifier');c.reset(16,'X')
 for q in [2,4,6,8,10,12,14]:c.gate('cx',16,q)
 c.meas(16,'X',True)
 for name,geo in [('TA',(9,8,10,14,15,13,11)),('TB',(7,2,6,4,1,3,5)),('PA',(4,11,5,12,7,14)),('PB',(7,14,6,13,2,9))]:
  c.stage(name)
  if barriers:c.barrier()
  triple=len(geo)==7
  A,B,C,F=16,17,18,19
  for q in ([A,B,C] if triple else [A,B]):c.reset(q)
  c.reset(F,'X')
  if triple:
   x,d,e,g,ua,ub,uc=geo
   pairs=[(x,A),(F,A),(A,C),(d,A),(A,B),(e,A),(ua,A),(ub,B),(g,B),(e,C),(uc,C),(g,C),(F,A),(F,B),(F,C)]
  else:
   a,b,u1,u2,v1,v2=geo
   pairs=[(a,A),(F,A),(b,A),(A,B),(u1,A),(u2,A),(v1,B),(v2,B),(F,A),(F,B)]
  for a,b in pairs:c.gate('cx',a,b)
  for q in ([A,B,C] if triple else [A,B]):c.meas(q,'Z',True)
  c.meas(F,'X',True)
 c.stage('transversal_T')
 if barriers:c.barrier()
 for q in range(1,16):c.gate('t' if q%2 else 'tdg',q)
 c.stage('coherent_gauge_frame' if coherent else 'software_gauge_frame')
 if coherent:
  for a,bs in [(1,[8,9,13,14]),(3,[9,10,11,14]),(5,[11,12,13,14])]:
   for b in bs:c.gate('cx',a,b)
 c.stage('bulk_readout')
 rec={q:c.meas(q,'X') for q in range(8,16)}
 c.dets.append(list(rec.values()))
 if coherent:c.frame=[rec[q] for q in [8,10,12,14]]
 return c
if __name__=='__main__':
 for name,coherent in [('paper_raw',False),('rm_frame12',True)]:
  c=build(coherent)
  q,s,j=c.write(name,dict(status='provisional: exact verification pending',source='arXiv:2609.12698 Appendices A/B; encoder arXiv:2410.07327v3 Fig.5',coherent_frame=coherent))
  f,p=declarations(s);ex=verify(s,DATA,frame=f,postselect=p)
  j.update(noiseless=ex,status='verified grid-free' if not ex['errors'] else 'not judge valid; see noiseless errors')
  (BASE/(name+'.json')).write_text(json.dumps(j,indent=2)+'\n')
  print(name,j['cx'],ex,flush=True)

if __name__=="__main__":
 from variants import direct,finish
 finish(direct(False,False),"rm_circuit")

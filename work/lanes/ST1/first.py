from common import *
import argparse
p=argparse.ArgumentParser();p.add_argument('--base',default='v23h_c2c9');a=p.parse_args()
c=read(ROOT/'work/lanes/MAIN'/a.base)
# Identify the terminal cat interaction before c8, and the two data-transfer CXs after it.
mi=next(i for i,o in enumerate(c['ops'])if any('-> c[8];'in l for l in o['lines']))
ci=max(i for i,o in enumerate(c['ops'][:mi])if o['lines']==['cx q[10],q[4];'])
fi=next(i for i,o in enumerate(c['ops'][mi+1:],mi+1)if o['lines']==['cx q[10],q[4];'])
bi=next(i for i,o in enumerate(c['ops'][fi+1:],fi+1)if o['lines']==['cx q[4],q[10];'])
ti=next(i for i,o in enumerate(c['ops'])if o['lines']==['tdg q[4];'])
t=c['ops'][ci]['t'];c['ops'][ci]['lines']=['cx q[4],q[10];']
c['ops'][fi]['t']=t+1;c['ops'][mi]['lines']=rename(c['ops'][mi]['lines'],{10:4});c['ops'][mi]['t']=t+2
c['ops'][ti]['lines']=['tdg q[10];'];c['ops'][ti]['t']=t+2
c['ops'].pop(bi);c['meta']['st1_change']='fused terminal cat CX/data exchange on q4,q10, c8 read from q4'
name=a.base+'_exchange4';s=save(c,name);r=score(s);print(name,r,flush=True);append_result(name,r,'Two-CX exchange instrument; physical full circuit, no proxy loss ranking. Judge gate pending.')
for mode in ['near','alap']:
 d,rec=schedule(c,mode=mode)
 if d:
  s=save(d,name+'_'+mode);r=score(s);print(s,r,flush=True);append_result(s.name,r,'Same exchange instrument with CP-SAT timing; '+json.dumps(rec)+'. Judge gate pending.')

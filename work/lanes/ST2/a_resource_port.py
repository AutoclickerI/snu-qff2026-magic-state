"""BCFB A witness port with full-prefix timing repair at fixed round."""
import sys,json,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import acceptance as a

def port(c):
 R=c['meta']['R'];x=a.C.clone(c);ast={1:38,14:39,8:38,9:38,2:37,16:41,15:39}
 old=[i for i,(u,t)in enumerate(zip(x['u'],x['t']))if u.name=='CX'and set(u.qs)<=set(a.C.A)and all(t>=ast[q]for q in u.qs)and t<R]
 assert len(old)==11,len(old)
 i=next(i for i,(u,t)in enumerate(zip(x['u'],x['t']))if u.lines==['reset q[14];']and t==39);x['u'][i]=a.C.Unit(['reset q[14];','h q[14];'])
 old.append(next(i for i,(u,t)in enumerate(zip(x['u'],x['t']))if u.name=='RX'and u.qs==(15,)and t==39));a.remove_units(x,set(old))
 p=a.H.parents[2]/'work/lanes/BCFB/a30/finalists/a30_fb_s810_00837.json';ops=json.loads(p.read_text())['options']['encoder']['ops']
 k=next(i for i,t in enumerate(x['t'])if t>=R)
 nu=[a.C.Unit([f'cx q[{u}],q[{v}];'])for u,v in ops];x['u'][k:k]=nu;x['t'][k:k]=[R-6+j//2 for j in range(len(nu))]
 # Dependencies follow list order, including the complete replacement program.
 x=a.C.retime(x,round_fixed=True,horizon=max(c['t']))
 if x is None:return None
 return a.d.normalize(x)
if __name__=='__main__':
 base=a.d.normalize(a.C.read(a.OUT/'base'));c=port(base)
 if c is not None:a.batch([('bcfb_A_R45',c,dict(family='BCFB_A_port',pivots=[1,14,9,2]))],'A_port',1)
 else:print('Fixed R45 dependency repair infeasible',flush=True)

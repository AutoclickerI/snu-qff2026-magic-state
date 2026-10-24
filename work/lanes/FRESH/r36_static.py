from r36_probe import *
import subprocess

def diagnostic(stem,text=None):
 text=build(stem) if text is None else text
 sig=xtim._xtim.deferred_signature(text);parts=sig.split(';');n=int(parts[0][2:]);ins=[]
 for p in parts[1:]:
  if p.startswith('reads='):break
  if not p:continue
  kind,body=p.split(':');bits=body.split(',');qs=[int(x) for x in bits[1:] if x.lstrip('-').isdigit()]
  ins.append((int(kind),int(bits[0]) if bits[0].isdigit() else -1,qs,p))
 data=f'{n} {len(ins)}\n'+'\n'.join(f'{kind} {gate} {len(qs)} '+' '.join(map(str,qs)) for kind,gate,qs,p in ins)
 r=subprocess.run([str(H/'r36_diag')],input=data,text=True,capture_output=True,check=True);out=json.loads(r.stdout);out['n']=n;out['instructions']=len(ins)
 out['bad_gate_context']={str(j):[(k,ins[k][3]) for k in range(max(0,j-4),min(len(ins),j+5))] for j,q,c in out['bad_gates']}
 return out
if __name__=='__main__':
 for s in sys.argv[1:]:
  r=diagnostic(Path(s));(D/(Path(s).name+'.static.json')).write_text(json.dumps(r,indent=2));print(Path(s).name,{k:v for k,v in r.items() if k not in ('failures','bad_gate_context')},flush=True)

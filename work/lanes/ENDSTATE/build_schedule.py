"""Assemble solved schedules with ST1 frame logic and SEPBC's native emitter.
No new router is used: every physical position and native time comes from the
ENDSTATE solver. This is separate from SEPBC's baseline witness12_h1 integration.
"""
import os,sys,json,ast,types,importlib.util,hashlib,subprocess
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
spec=importlib.util.spec_from_file_location('endstate_sepbc_common',ROOT/'work/lanes/SEPBC/common.py');common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common);common.H=H;common.xtim.cache_dir=str(H/'.xtim_cache');os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
source=(ROOT/'work/lanes/ST1/redesign.py').read_text();tree=ast.parse(source);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='build');ns=vars(common).copy();ns['ROWS']=[[0,2,4,6],[1,2,5,6],[3,4,5,6]];exec(compile(ast.Module(body=[node],type_ignores=[]),'ST1/redesign.py:build','exec'),ns)
def build(path,name=None):
 x=json.loads(Path(path).read_text());name=name or Path(path).name.replace('.schedule.json','')
 bits=sorted({int(b)for o in x['prefix_units']for line in o['lines']for b in common.re.findall(r'c\[(\d+)\]',line)});bm={b:i for i,b in enumerate(bits)}
 def bitrename(line):return common.re.sub(r'c\[(\d+)\]',lambda m:f'c[{bm[int(m[1])]}]',line)
 for o in x['prefix_units']:o['lines']=[bitrename(line)for line in o['lines']]
 x['prefix_detectors']=[bitrename(line)for line in x['prefix_detectors']]
 abstract=bool(x['args'].get('abstract_depth'))
 if abstract:
  from library import rowkey
  L=json.loads((H/'library_input.json').read_text());E=json.loads((H/'library_encoders.json').read_text());x['realized_encoders']={}
  for key,tok in x['tokens'].items():tok['init']*=3;tok['ts']=[3*t for t in tok['ts']]
  x['prefix_t']=[3*t for t in x['prefix_t']];x['R']*=3
  for job in x['jobs']:job['t']*=3
  for k in'abc':
   cells=[x['tokens'][f'{k}{i}']['pos'][0]for i in range(7)]
   if k in x.get('helpers',{}):
    from helper_synthesis import key8
    hp=x['helpers'][k];cells.append(hp['cell']);edges=[(u,v)for u in range(8)for v in range(8)if abs(cells[u]//6-cells[v]//6)+abs(cells[u]%6-cells[v]%6)==1];target=key8([sum(1<<i for i in g)for g in ns['ROWS']]);request='8 '+str(len(edges))+' 1\n'+' '.join(str(q)for e in edges for q in e)+'\n'+str(target)+'\n';res=subprocess.run([str(H/'synth_one')],input=request,text=True,capture_output=True,check=True);enc=json.loads(res.stdout)[0];assert enc is not None;native=cells;sid=cid=None;piv=enc['pivots'];ops=enc['ops'];x['tokens'][k+'7']=dict(pos=[hp['cell']],init=hp['init']*3,moves=[],ts=[])
   else:
    row=next(r for r in L['embeddings']if set(r[1:])==set(cells));sid=row[0];native=row[1:];perm=[native.index(q)for q in cells];cid=L['targets'].index(rowkey([sum(1<<perm[i]for i in g)for g in ns['ROWS']]));enc=E[sid][cid];piv=[cells.index(native[q])for q in enc['pivots']];ops=[(cells.index(native[u]),cells.index(native[v]))for u,v in enc['ops']]
   if k=='a':piv=[i for i in range(7)if i not in piv];ops=[(v,u)for u,v in ops]
   x['encoders'][k]=[ops,piv];x['realized_encoders'][k]=dict(shape=sid,code_class=cid,cx=enc['cx'])
   times=[x['tokens'][k+'0']['init']]*len(cells)
   for u,v in ops:
    t=max(times[u],times[v])+1;times[u]=times[v]=t;x['jobs'].append(dict(k=k,indices=[u,v],t=t,loc=[cells[u],cells[v]],stage=[0,0]))
   if k in x.get('helpers',{}):
    x['helpers'][k]['measure_t']=max(times)+1;assert max(times)+1<3*x['helpers'][k]['end']
 event_regions={}
 for key,tok in x['tokens'].items():
  for j,used in enumerate(tok['moves']):
   if not used:continue
   u,v=tok['pos'][j:j+2];t=tok['ts'][j];region='data_hops'if key[0]=='d'else'teleports';aa,bb=(v,u)if key[0]=='a'else(u,v)
   event_regions[t,f'cx q[{aa}],q[{bb}];']=region;event_regions[t-1,f'reset q[{v}];']=region
 def save_with_regions(c,n):
  if x.get('helpers'):
   bit=max([int(b)for o in c['ops']for line in o['lines']for b in common.re.findall(r'c\[(\d+)\]',line)]+[-1])+1
   for k,hp in x['helpers'].items():
    c['ops'].append(dict(t=hp['measure_t'],lines=[f'measure q[{hp["cell"]}] -> c[{bit}];'],tag='helper_check',region='ancilla_prep',id=10000+bit));c['tail'].append(f'// DETECTOR c[{bit}]');bit+=1
   c['h']=[f'creg c[{bit}];'if line.startswith('creg ')else line for line in c['h']]
  for o in c['ops']:
   tag=o.get('tag','unknown');o['region']=event_regions.get((o['t'],o['lines'][0]),'teleports'if tag=='tele_m'else'data_hops'if tag in('data_cx','data_watch')else'prefix'if tag=='data_tdg'else'round'if tag in('round','read')else tag)
  return common.save(c,n)
 ns['save']=save_with_regions
 ns['prefix']=lambda *args:([common.Unit(o['lines'])for o in x['prefix_units']],x['prefix_detectors'][:]);stem=ns['build'](x,name)
 c=json.loads(stem.with_suffix('.plan.json').read_text());c,receipt=common.schedule(c,mode='alap',seconds=60);assert c is not None,receipt
 if abstract:c['meta']['realized_encoders']=x['realized_encoders'];c['meta']['abstract_model_R']=x['R']//3
 stem=common.save(c,name)
 d=json.loads(stem.with_suffix('.json').read_text());d.update(prefix_source=x['prefix_source'],template=x['template'],model_R=x['R'],secondary_objective=x['secondary_objective'],assembly='ST1 frame propagation + SEPBC common.save; native positions/times from ENDSTATE solver',builder_sha256=hashlib.sha256(ast.get_source_segment(source,node).encode()).hexdigest());stem.with_suffix('.json').write_text(json.dumps(d,indent=2));print(stem,flush=True);return stem
if __name__=='__main__':build(*sys.argv[1:])

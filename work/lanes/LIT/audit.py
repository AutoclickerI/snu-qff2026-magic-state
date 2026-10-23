from pathlib import Path
import importlib.util, json, hashlib, re, statistics, xml.etree.ElementTree as ET
ROOT=Path('/home/jihoon/competitions/quantumn'); OUT=ROOT/'work/lanes/LIT'
spec=importlib.util.spec_from_file_location('tailbounds',ROOT/'work/bounds.py'); b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
p=.001;x=p/(1-p)
a=[1,77/3,109433/100,203757811/6750,7640477983/8100,3345046003099/121500,745483248873863/911250,16316109725855291383/683437500,2814706392354594541187/4100625000,740868888180195867334063/38443359375,2424452455579323062802516617/4613203125000]
q=ROOT/'work/submissions/v12_L5lns12_r86.qasm'
files=[q,ROOT/'work/lanes/RM_PROTO/va_ta0_PA.qasm',ROOT/'work/lanes/RM_PROTO/rm_circuit.qasm',ROOT/'work/lanes/CC/cc_hm_best.qasm']
res={'p':p,'tails':{'final_idle_exact':b.exact_loss([b.final_step(False)]*7),'final_dummy_exact':b.exact_loss([b.final_step(True)]*7),'final_idle_pair':b.pair_loss([b.final_step(False)]*7),'direct_pair':b.pair_loss([b.tail('direct','X')]*7),'direct_exact_independent':b.exact_loss([b.tail('direct','X')]*7),'bell_pair':b.pair_loss([b.tail('bell','X')]*7)},'arithmetic':{'CC_H_infidelity_coeff':.5*(9.95+7.87)+4.41,'CC_paper_acceptance':(1-p)**75,'Wan_d3_A_truncated10':(1-p)**402*sum(c*x**k for k,c in enumerate(a)),'Wan_d3_leading_p2':32/75,'Wan_d3_p3_coefficient':2*32/75+2009039/4500,'DK_EC_fit':25.5*p*p-1266.7*p**3+165884.4*p**4-4339823.2*p**5+39742917.9*p**6,'DK_ED_fit':508.5*p**3+4477.1*p**4,'DK_EC_accept_fit':1-(164.6*p-12362.8*p*p+477206.9*p**3-7518868.5*p**4)},'qasm_counts':[]}
for f in files:
 t=f.read_text();clean='\n'.join(l.split('//')[0] for l in t.splitlines());ops=re.findall(r'\b(tdg|t|cx|measure|reset)\b',clean)
 res['qasm_counts'].append({'file':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':len(f.read_bytes()),'statements':clean.count(';'),'T':sum(x in ('t','tdg') for x in ops),'CX':ops.count('cx'),'measure_reset':sum(x in ('measure','reset') for x in ops)})
f=ROOT/'work/lanes/RM_PROTO/va_ta0_PA_mc_score.json'; mc=json.loads(f.read_text())['mc'];res['RM_measured']={'mean':statistics.mean(r['loss'] for r in mc),'seed0':mc[0]['loss'],'acceptance':statistics.mean(r['acceptance'] for r in mc)}
# Check static counts in the primary GSJ deposited source, not a complete T compilation.
import stim
res['GSJ_deposited_counts']=[]
base=ROOT/'work/lanes/SEARCH/found/zenodo-13777072/extracted/circuits/for_perfectionist_decoding'
for f in base.glob('*p=0.001,*d1=3.stim'):
 c=stim.Circuit(f.read_text()).flattened(); counts={}
 for op in c: counts[op.name]=counts.get(op.name,0)+len(op.targets_copy())//(2 if op.name in ('CX','CZ','SWAP') else 1)
 res['GSJ_deposited_counts'].append({'file':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'q':c.num_qubits,'cx':counts.get('CX',0),'measurements':c.num_measurements,'counts':counts})
(OUT/'AUDIT.json').write_text(json.dumps(res,indent=2)+'\n')
manifest=[]
for f in sorted((OUT/'papers').glob('*.pdf')):
 txt=f.with_suffix('.txt').read_text(errors='replace'); ver=re.search(r'arXiv:(\d{4}\.\d+v\d+)',txt)
 manifest.append({'file':f.name,'arxiv_version':ver[1] if ver else None,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'pages':len(txt.split('\f'))-int(txt.endswith('\f'))})
(OUT/'papers/MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(res,indent=2))
ns={'a':'http://www.w3.org/2005/Atom'}
entries={}
for f in (OUT/'searches').glob('*.xml'):
 try: tree=ET.fromstring(f.read_text())
 except ET.ParseError: continue
 for e in tree.findall('a:entry',ns):
  entries[e.findtext('a:id',namespaces=ns)]={'title':e.findtext('a:title',namespaces=ns),'published':e.findtext('a:published',namespaces=ns),'updated':e.findtext('a:updated',namespaces=ns),'summary':e.findtext('a:summary',namespaces=ns)}
(OUT/'searches/entries.json').write_text(json.dumps(entries,indent=2)+'\n')

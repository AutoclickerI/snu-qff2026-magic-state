"""Certify detector-only independent components of the all-orders channel model.

The graph joins every detector bit touched by one independent physical channel.
It marks a component relevant if a channel can affect any magic rotation or
scored observable, or if a detector's ideal projector is nonidentity. No atom
of a multi-atom channel is treated as independent from its siblings.
"""
from pathlib import Path
import sys,json,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'quantumn_review10/work/lanes/MAIN/sparse'))
import sparse_walsh as sw
HERE=Path(__file__).parent
stem=ROOT/'quantumn_review10/work/lanes/MAIN/v36c'
m,eng,groups,nd,ks,psi,where,elim=sw.prepare(stem,True)
parent=list(range(nd+1)); core=nd
def find(i):
    while parent[i]!=i:
        parent[i]=parent[parent[i]];i=parent[i]
    return i
def join(a,b):
    a,b=find(a),find(b)
    if a!=b:parent[b]=a
emasks=[sw.emask_for(k) for k in eng.keys]
def relevant_e(e):return any((e&mask).bit_count()&1 for mask in emasks)
tags=[]
for c,fs in groups.items():
    d=0
    for f in fs:d|=f['d']
    bits=[i for i in range(nd) if d>>i&1]
    critical=any(f['s'] or relevant_e(f['e']) for f in fs)
    if critical:bits.append(core)
    for b in bits[1:]:join(bits[0],b)
    tags.append({'channel':c,'detectors':bits[:-1] if critical else bits,'core':critical})
for i,p in enumerate(eng.projs):
    if p[:2]!=(0,0):join(i,core)
components={}
for i in range(nd):components.setdefault(find(i),[]).append(i)
rows=[]
for p,ds in components.items():
    cs=[t['channel'] for t in tags if any(d in ds for d in t['detectors'])]
    rows.append({'detectors':ds,'channels':cs,'core':p==find(core),
                 'ideal_projectors':[eng.projs[d] for d in ds]})
for r in rows:
    if not r['core']:
        assert all(eng.projs[d]==(0,0,1) for d in r['detectors'])
        assert all(not any(f['s'] or relevant_e(f['e']) for f in groups[c]) for c in r['channels'])
out={'source_commit':'42afa8ff01c3999444336f5bb2fe473c1475d6f4',
     'channels':len(groups),'detectors':nd,'components':rows,
     'canonical_row_changes':m.detector_row_changes,
     'auxiliary_components':sum(not r['core'] for r in rows),
     'component_channel_overlap':any(set(a['channels'])&set(b['channels']) for i,a in enumerate(rows) for b in rows[i+1:]),
     'note':'Sufficient certificate, not necessary: complete channels remain indivisible; canonical projectors must be identity.'}
assert not out['component_channel_overlap']
(HERE/'census.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('components','canonical_row_changes')},indent=2))
print(json.dumps([r for r in rows if not r['core']],indent=2))

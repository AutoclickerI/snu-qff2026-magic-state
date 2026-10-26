from pass5 import *
E.configure(R/('basis_'+sha(C/'base')+'.json'),12)
p=R/'wide_r1_menu.json';es=json.loads(p.read_text());ids=[i for i,e in es.items()if e['fam']=='detparity'];tasks=[list(x)for n in range(1,len(ids)+1)for x in itertools.combinations(ids,n)]
rs=batch(C/'base',p,tasks,'detector_v37h',1)
dump(R/'detector_v37h_summary.json',dict(directions=ids,count=len(rs),prices=[dict(edits=r['edits'],loss=r.get('loss'),acceptance=r.get('acceptance'),sha256=r.get('sha256'),error=r.get('error'))for r in rs]))
print(json.dumps(dict(event='detector_subsets_complete',directions=len(ids),count=len(rs))),flush=True)

from port_bc import *
if __name__=='__main__':
 rows=[json.loads(l)for l in (OUT/'bc_port.jsonl').read_text().splitlines()]
 for c,d in variants():
  if d['move']!='BCSYN2_plus_LNS'or d['base']!='w':continue
  c=normalize(c);txt=textof(c);r=next(r for r in rows if r['desc']['move']==d['move']and r['desc']['base']=='w');assert hashlib.sha256(txt.encode()).hexdigest()==r['sha256']
  ref=score(txt);assert abs(ref['total']-r['total'])<1e-14;r['pruned_exact2_check']=ref;r['stem']='bc_w_fast';save(r['stem'],txt,c['meta'],r);print(r['stem'],r['total'],flush=True);break

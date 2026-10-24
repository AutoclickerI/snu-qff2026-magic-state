from core import *
p=V/'inputs/menu_v35a.json';old=json.loads(p.read_text());fresh=json.loads((ROOT/'work/lanes/WAITPROT/menu_v35a.json').read_text());known={x['gadget']:x for x in old['entries']};added=[]
for x in fresh['entries']:
 if x['gadget']in known:continue
 x['integration_name']=f'wait_{len(old["entries"]):03d}';old['entries'].append(x);added.append(x['gadget']);known[x['gadget']]=x
p.write_text(json.dumps(old,indent=2));(V/'menu_refresh.json').write_text(json.dumps(dict(current=len(fresh['entries']),frozen=len(old['entries']),added=added),indent=2));print(added)

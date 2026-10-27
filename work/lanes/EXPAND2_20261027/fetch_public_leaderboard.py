"""Read the contest's public leaderboard using its published frontend config."""
import datetime,json,re,urllib.request
from pathlib import Path

HERE=Path(__file__).resolve().parent
config_url='https://snuquantums.github.io/snu-qff2026/assets/supabase-config.js'
config=urllib.request.urlopen(config_url,timeout=20).read().decode()
urls=re.findall(r'https://[a-z]+\.supabase\.co',config)
keys=re.findall(r'eyJ[A-Za-z0-9_.-]+',config)
assert len(set(urls))==1 and keys,'Public frontend config format changed'
url=urls[0]+'/rest/v1/qff_leaderboard?select=team_name,score_a,score_key,n_2q,p_acc,submitted_at&order=score_key.asc,n_2q.asc,submitted_at.asc'
request=urllib.request.Request(url,headers={'apikey':keys[0],'Authorization':'Bearer '+keys[0]})
rows=json.loads(urllib.request.urlopen(request,timeout=20).read())
receipt=dict(retrieved_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
             source_url=url,public_frontend_config_url=config_url,rows=rows)
(HERE/'leaderboard_20261027.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'retrieved_at':receipt['retrieved_at'],'top':rows[:3]},ensure_ascii=False))

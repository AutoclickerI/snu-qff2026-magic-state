"""Read the contest's public sanitized leaderboard; no submission or login."""
import datetime,json,re,urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent
config=urllib.request.urlopen('https://snuquantums.github.io/snu-qff2026/assets/supabase-config.js',timeout=30).read().decode()
url=re.search(r"https://[a-z0-9]+\.supabase\.co",config).group(0)
key=re.search(r"eyJ[A-Za-z0-9_.-]+",config).group(0)
request=urllib.request.Request(url+'/rest/v1/qff_leaderboard?select=team_name,score_a,score_key,n_2q,p_acc,submitted_at&order=score_key.asc,n_2q.asc,submitted_at.asc',headers={'apikey':key,'Authorization':'Bearer '+key})
rows=json.loads(urllib.request.urlopen(request,timeout=30).read())
result=dict(retrieved_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            source='https://snuquantums.github.io/snu-qff2026/leaderboard.html',
            public_endpoint='qff_leaderboard',rows=rows)
(HERE/'leaderboard_latest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))

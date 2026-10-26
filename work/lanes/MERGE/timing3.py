from pass3 import *
from speed_predict import predict
import general_atoms
def main():
 tasks=[dict(stem=str(C/n))for n in ['base','G3','bc3_7']]+json.loads((R/'bc3_sources_tasks.json').read_text())
 rows=[]
 for t in tasks:
  st=Path(t['stem']);screen=general_atoms.analyze(st)
  probe=predict(str(st),shots=50000,repeats=2)
  r=dict(stem=str(st),sha256=sha(st),screen=screen,probe=probe);rows.append(r)
  dump(R/'source_timing.json',rows);print(json.dumps(dict(stem=st.name,atoms=screen['general_atoms'],wires=screen['deferred_wires'],seconds_per_million=probe['median_seconds_per_1e6'])),flush=True)
if __name__=='__main__':main()

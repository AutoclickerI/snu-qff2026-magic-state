"""Stream only complete reference receipts and completed gate/MC diagnostics."""
from pathlib import Path
import sys,json,tarfile,io
H=Path(__file__).resolve().parent;files=set()
for rc in H.glob('*.ref.exit.json'):
 r=json.loads(rc.read_text())
 if r.get('returncode')!=0:continue
 stem=r['stem']
 files.update(H/(stem+s) for s in ('.ref.exit.json','.ref.log','.ref.sensitivity.json'))
for pattern in ('*.gates.json','*.mc.json','*.allorders.json','*.decomposition.json','*.mc3.log','*.judge.log'):
 files.update(H.glob(pattern))
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|') as out:
 for p in sorted(files):
  if not p.exists():continue
  b=p.read_bytes();info=tarfile.TarInfo('work/lanes/WAITPROT/'+p.name);info.size=len(b);out.addfile(info,io.BytesIO(b))

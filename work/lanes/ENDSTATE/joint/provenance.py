import json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[3];out=[]
for folder,source in [('fresh_snapshot',ROOT/'work/lanes/FRESH'),('sparse_snapshot',ROOT/'work/lanes/MAIN/sparse'),('tool_snapshot',ROOT/'work/lanes/XTIM')]:
 for p in (H/folder).rglob('*.py'):
  rel=p.relative_to(H/folder);s=source/rel;h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
  out.append(dict(snapshot=str(p.relative_to(H)),sha256=h(p),current_source=str(s.relative_to(ROOT)),current_source_sha256=h(s)if s.exists()else None,equal_current_source=s.exists()and h(p)==h(s)))
(H/'snapshot_provenance.json').write_text(json.dumps(out,indent=2));print('snapshots',len(out),'same current source',sum(r['equal_current_source']for r in out))

"""List new authoritative ENDSTATE fragments without unattended polling."""
import sys,json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;root=Path(sys.argv[1])if len(sys.argv)>1 else H.parent/'ENDSTATE';rows=[]
for p in sorted(root.glob('*.json')):
 try:d=json.loads(p.read_text())
 except (ValueError,OSError):continue
 if isinstance(d,dict)and all(k in d for k in('ops','detectors','final','blocks')):
  rows.append(dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),verified=p.with_suffix('.verified.json').exists(),native_operations=len(d['ops']),fragment_cx=d.get('fragment_cx'),block_moves=d.get('block_moves')))
(H/'endstate_catalog.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))

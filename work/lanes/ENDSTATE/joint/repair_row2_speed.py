"""Probe minimal subset of A source reuse; no change to detector semantics."""
import json
from pathlib import Path
from reuse_A import reuse
H=Path(__file__).resolve().parent;out=[]
for drop in(13,21,27):
 name=f'region2_reuse_drop{drop}';reuse(H/'region2_d11',name,[q for q in(14,20,15,9,13,21,27)if q!=drop]);out.append(name)
(H/'row2_repair_stems.json').write_text(json.dumps(out))

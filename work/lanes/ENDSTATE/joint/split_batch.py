import json
from pathlib import Path
from split import split
H=Path(__file__).resolve().parent
names=json.loads((H/'batch_stems.json').read_text())+['region89_k45_A0_safe','region89_k45_A1_safe','region89_bus']
for name in names:split(H/name)

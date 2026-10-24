"""Rebuild judge metadata after exact2 attribution output overwrote a seed JSON."""
import json, sys
from pathlib import Path
import population as P

stem = Path(sys.argv[1])
c = P.read_seed(stem)
if c is None:
    raise SystemExit("cannot parse " + str(stem))
md = dict(c["meta"])
md["data_qubits"] = list(md.get("data_qubits", P.C.D))
md["cx"] = sum(u.name == "CX" for u in c["u"])
md["native_depth"] = max(c["t"]) + 1
md["source"] = "ST2 rebuilt metadata"
stem.with_suffix(".json").write_text(json.dumps(md, indent=2) + "\n")
print(json.dumps(md, indent=2))

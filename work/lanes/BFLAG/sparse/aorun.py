"""All-orders for several stems: aorun.py <procs> <stem>... ; prints one JSON line per stem."""
import sys, json, io, contextlib
from pathlib import Path
import sparse_walsh as sw
procs = int(sys.argv[1])
for s in sys.argv[2:]:
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            out = sw.run(Path(s), 72, True, procs)
        print(json.dumps(dict(stem=s, loss=out.get('loss'), acceptance=out.get('acceptance'), seconds=round(out['seconds'], 1))), flush=True)
    except Exception as e:
        print(json.dumps(dict(stem=s, error=repr(e)[:300])), flush=True)

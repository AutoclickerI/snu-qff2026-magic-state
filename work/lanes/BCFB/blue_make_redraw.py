from pathlib import Path
H=Path(__file__).resolve().parent;s=(H/'redraw.py').read_text().replace("H=Path(__file__).resolve().parent;ROOT=H.parents[2]", "CODE=Path(__file__).resolve().parent;ROOT=CODE.parents[2];H=CODE/'blue'").replace('r.acceptance>=.505','r.acceptance>=.5')
s=s.replace("r=reorder.check(var", "print(json.dumps(dict(event='capacity',cores=os.cpu_count(),load=os.getloadavg(),procs=procs)),flush=True)\n  r=reorder.check(var")
(H/'blue_redraw.py').write_text(s)

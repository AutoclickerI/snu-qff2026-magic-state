from cycles import *
l=json.loads((HERE/'relocations.json').read_text())['layouts'][0]
m=Cycle(l);ts,st=m.solve();print(list(zip(m.tags,m.nodes,ts)))
x,y=m.probes(ts)
(HERE/'debug_x.stim').write_text(str(x))
try: print(x.detector_error_model())
except ValueError as e: print(e)

"""Exact equivalence of the complete reduced engine and categorical channels.

No gate counts, proxy scores or rounded probabilities enter the key. Equal
keys define the same full stochastic expectation at every noise order.
"""
import hashlib,json,collections,os,threading
from pathlib import Path
H=Path(__file__).resolve().parent
def fingerprint(ev):
 e=ev.e;channels=collections.defaultdict(list)
 for f in ev.m.faults:channels[int(f['chan'])].append((int(f['s']),int(f['d']),int(f['e']),float(f['p']).hex()))
 # These are every non-derived input read by Engine.table/ntable.
 ideal=(e.r,repr(e.rot),repr(e.projs),tuple(map(int,e.v)),repr(sorted(e.Qs.items())),repr(e.keys),e.SG.tobytes().hex(),float(e.A0).hex(),ev.m.n_post)
 return hashlib.sha256(repr((ideal,sorted(tuple(sorted(v))for v in channels.values()))).encode()).hexdigest()
def path(key):return H/'third_cache'/f'{key}.json'
def store(key,row):
 p=path(key);p.parent.mkdir(exist_ok=True);tmp=p.with_suffix(f'.{os.getpid()}.{threading.get_ident()}.tmp');tmp.write_text(json.dumps(row));tmp.replace(p)

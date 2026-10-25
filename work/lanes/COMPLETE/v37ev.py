"""Unchanged MAIN evaluator with GLOBAL's saved R46 detector-basis warm starts.
Only an exact change of detector coordinates differs; baseline reproduced before
use. Include the actual warm-start and adapter hashes in cache provenance.
"""
import sys,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'BUNDLE'))
import ev
ev.sw.WARM=H/'basis_v37.json'
# R46's saved width-10 basis already contracts cheaply. This changes only the
# heuristic trigger for an optional basis search; all73 moments remain exact.
ev.sw.SEARCH_WIDTH=10
EVH=hashlib.sha256(ev.EVH.encode()+ev.sw.WARM.read_bytes()+Path(__file__).read_bytes()).hexdigest()[:16]
price_stem=ev.price_stem

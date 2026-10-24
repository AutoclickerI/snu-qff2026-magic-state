import os, sys, json, re, copy, hashlib, importlib.util
from pathlib import Path
H=Path(__file__).resolve().parent
ROOT=H.parents[2]
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[k]='1'
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
sys.path[:0]=[str(ROOT/'work/lanes/LNS2'),str(ROOT/'work')]
import core as C
import moves as M
C.OUT=H; M.OUT=H
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
C.xtim.cache_dir=str(H/'.xtim_cache')
_textof=C.textof
def textof(c):
    n=C.bit(c)
    c['h']=[re.sub(r'creg c\[\d+\]',f'creg c[{n}]',line) for line in c['h']]
    return _textof(c)
C.textof=textof
_normalize=C.normalize
def normalize(c):
    c=_normalize(c)
    n=C.bit(c)
    c['h']=[re.sub(r'creg c\[\d+\]',f'creg c[{n}]',line) for line in c['h']]
    return c
C.normalize=normalize

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    C.xtim.cache_dir=str(H/'.xtim_cache')
    os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
    return m

def save(c,name,edits):
    c=C.normalize(C.clone(c))
    md=dict(c['meta']); md.update(source=str(c.get('source','')),comp29_edits=edits)
    txt=C.textof(c)
    (H/(name+'.qasm')).write_text(txt)
    (H/(name+'.json')).write_text(json.dumps(md,indent=2)+'\n')
    return dict(stem=name,edits=edits,sha256=hashlib.sha256(txt.encode()).hexdigest(),cx=md['cx'],R=md['R'])

def screen(stem):
    mom=module('comp29_moments','work/lanes/BCPOL/moments_batch.py')
    p=H/stem
    ev=C.exact2.Eval(p.with_suffix('.qasm').read_text(),json.loads(p.with_suffix('.json').read_text())['data_qubits'])
    r=mom.evaluate(ev)
    p.with_suffix('.screen.json').write_text(json.dumps(r,indent=2)+'\n')
    return r

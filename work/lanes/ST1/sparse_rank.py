"""Unchanged MAIN sparse evaluator with output path redirected inside ST1."""
from common import *
import argparse
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--procs',type=int,default=1);a=p.parse_args();source=H/'sparse_engine/sparse_walsh.py';sys.path.insert(0,str(source.parent));spec=importlib.util.spec_from_file_location('st1_sparse',source);sw=importlib.util.module_from_spec(spec);sys.modules[spec.name]=sw;spec.loader.exec_module(sw);sw.__file__=str(H/'sparse_walsh.py');r=sw.run(Path(a.stem),72,True,a.procs);append_result(Path(a.stem).name+':allorders',{k:v for k,v in r.items()if k!='results'},'Byte-identical snapshot of MAIN sparse Walsh evaluator, full-used-qubit barriers, no FRAME/POSTSELECT; only output path redirected to ST1.')

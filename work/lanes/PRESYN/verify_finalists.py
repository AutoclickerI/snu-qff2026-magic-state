from core import *
import runpy
if sys.argv[1]=='mc':
 args=sys.argv[2:];sys.argv=['work/lanes/MAIN/spec/mc3.py',*[str(OUT/a)if not a.startswith('--')and not a.isdigit()else a for a in args]]
 runpy.run_path(str(OUT/'inputs/mc3.py'),run_name='__main__')
elif sys.argv[1]=='exact':
 stem=OUT/sys.argv[2];sys.argv=['exact2.py',str(stem.with_suffix('.qasm')),'--third','--procs',sys.argv[3],'--top','20'];exact2.main()
else:raise ValueError(sys.argv)

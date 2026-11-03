exec(open('work/lanes/SOTA_RESOURCE_20261028/screen.py').read().split('rows=[]')[0])
sys.path.insert(0,str(R/'work/lanes/PREFIX2_20261027'));sys.path.insert(0,str(R/'work/lanes/REBUILD20261027'))
from axis_echo import exact
for x in sys.argv[1:]:
 path=here/f'delete_{x}'
 try:
  r=exact(path);path.with_suffix('.exact.json').write_text(json.dumps(r,indent=2)+'\n');print(x,json.dumps(r),flush=True)
 except Exception as e: print(x,type(e).__name__,str(e),flush=True)

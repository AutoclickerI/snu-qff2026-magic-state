from round35 import *

def add(ops,dets,q,h,axis,start,end):
 oo=copy.deepcopy(ops);dd=copy.deepcopy(dets)
 assert abs(q//6-h//6)+abs(q%6-h%6)==1 and end-start>=3
 assert not any(h in o.qs and start<=o.time<=end for o in oo)
 assert not any(q in o.qs and o.time in (start+1,end-1) for o in oo)
 previous=[o for o in oo if h in o.qs and o.time<start];later=[o for o in oo if h in o.qs and o.time>end]
 assert not previous or max(previous,key=lambda o:o.time).kind in ('M','MX')
 assert not later or min(later,key=lambda o:o.time).kind in ('M','MX','R','RX')
 bit=max(o.bit for o in oo if o.bit is not None)+1
 edge=(q,h) if axis=='X' else (h,q)
 oo.extend([f.Op('R' if axis=='X' else 'RX',(h,),start),f.Op('CX',edge,start+1),f.Op('CX',edge,end-1),f.Op('M' if axis=='X' else 'MX',(h,),end,bit)])
 dd.append({bit});return oo,dd

def gen(stem):
 ops,dets,md=load(stem);out=[]
 desc=[(20,26,'Z',20,31),(10,16,'X',21,27),(15,21,'X',20,28),(20,26,'Z',19,30),(10,16,'Z',21,27),(15,21,'Z',20,28),(10,16,'X',20,27),(10,16,'X',20,28),(15,21,'X',20,29)]
 for q,h,axis,a,b in desc:
  try:
   oo,dd=add(ops,dets,q,h,axis,a,b);name=f'echo_{q}_{h}_{axis}_{a}_{b}'
   target=emit(name,oo,dd,md,dict(source=str(stem),echo=[q,h,axis,a,b]));certify(target);out.append(target)
  except Exception as e:print('REJECT',q,h,axis,a,b,repr(e),flush=True)
 (D/'echo_stems.json').write_text(json.dumps(list(map(str,out)),indent=2))
 print('GENERATED',len(out),flush=True)

if __name__=='__main__':gen(Path(sys.argv[1]))

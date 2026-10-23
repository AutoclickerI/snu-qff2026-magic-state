from part1 import *
LAST.clear();steane.score(vblock=True);cx,cy=LAST[:2]
def only_tail(c):
 out=stim.Circuit();ins=list(c.without_noise().flattened());mpps=[i for i,x in enumerate(ins) if x.name=='MPP'];where=mpps[-1]
 # Stim merges consecutive MPP instructions; insert before the last group.
 for i,x in enumerate(ins):
  if i==where:out.append('DEPOLARIZE1',[0,1,2],.001)
  out.append(x)
 return out
x,y=only_tail(cx),only_tail(cy);aa,n=physical_faults(x);bb,_=physical_faults(y);assert n==3
opts=[]
for ch in range(3):
 ids=[i for i,r in enumerate(aa) if r[0]==ch]
 opts.append([(.999,0,0,0)]+[(aa[i][1],aa[i][2],aa[i][3],bb[i][3]) for i in ids])
num=den=0
for combo in itertools.product(*opts):
 p=math.prod(t[0] for t in combo);d=xm=ym=0
 for _,di,xi,yi in combo:d^=di;xm^=xi;ym^=yi
 if not d:den+=p;num+=p*(ep.decoded_flip(xm,'X')+ep.decoded_flip(ym,'Y'))/2
exact=ep.conditional_loss(x,y)
assert num>0 and abs(exact-num/den)<1e-14,(exact,num/den)
r=dict(physical_channels=3,physical_states=64,brute_all_orders=num/den,xy_all_orders=exact,acceptance=den)
(HERE/'small_validation.json').write_text(json.dumps(r,indent=2));print(r)

import json,sys,ast
sys.path.insert(0,'/home/jihoon/competitions/quantumn/work/lanes/me_layout');import gmodel as G
m=G.GModel(moves={1:[(1,3)]},extras=[(1,(2,3),(2,2)),(2,(4,2),(4,1))],xmem={(1,1):(2,3),(2,5):(4,2)})
raw=json.load(open('/home/jihoon/competitions/quantumn/work/lanes/me_layout/res_A1_9b_1792752451.json'))
def key(k):
 if k[0]=='M':return ('M',int(k[1]),int(k[2]))
 if k[1]=='U':return (int(k[0]),'U','')
 if k[1]=='A':return (int(k[0]),'A',ast.literal_eval(k[2]))
 return (int(k[0]),int(k[1]),k[2])
for i,(proxy,a,o,*rest) in enumerate(raw[:3]):
 aa={key(k):v for k,v in a};
 try:print(i,'stored',proxy,'measured',m.proxy(aa,o),'data',[G.P(q) for q in m.pos])
 except Exception as e:print(i,type(e).__name__,e)

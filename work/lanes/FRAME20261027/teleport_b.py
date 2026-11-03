from frame_tools import *
BASE=ROOT/'work/lanes/MAIN/v37j'
D=[6,20,19,10,2,22,16]
B=[12,26,25,11,3,28,17]
C=[18,27,24,5,4,29,23]
A=[0,14,13,9,1,21,15]

def build(name,fresh=True,extra=None):
    ops,dets,md=load(BASE)
    for o in ops:
        if o.time==47 and o.kind=='CX' and o.qs in list(zip(B,D)):o.qs=o.qs[::-1]
    ops=[o for o in ops if o.bit not in range(330,337)]
    dets=[row for row in dets if not(row&set(range(330,337)))]
    if fresh:
        sourcebits={352,353,361}
        for o in ops:
            if o.bit in sourcebits:o.kind='RX';o.bit=None
        dets=[row-sourcebits for row in dets if row-sourcebits]
    for j,q in enumerate(D):ops.append(f.Op('MX',(q,),48,400+j))
    dets += [{400+j for j in row} for row in f.SUPPORTS]
    if extra:ops,dets=extra(ops,dets)
    return emit(name,ops,dets,B,{'X':(0,set()),'Z':(0,set(range(400,407)))},
        {'base':'MAIN/v37j','architecture':'B-output encoded teleportation','fresh_resource_sources':fresh})

if __name__=='__main__':
    for name,fresh in [('btele_naive',False),('btele_fresh',True)]:
        stem=build(name,fresh)
        try:
            result=price(stem);print(json.dumps(result),flush=True)
            if result['raw']['ok']:
                single=singles(stem)
                Path(str(stem)+'.singles.json').write_text(json.dumps(single,indent=2,default=lambda x: str(x))+'\n')
                print('SINGLES',name,single['first_order_loss'],single['harmful_count'],flush=True)
        except Exception as ex:
            import traceback;traceback.print_exc()


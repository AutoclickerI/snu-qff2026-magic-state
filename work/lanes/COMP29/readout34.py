"""Complete 3^5 product of compatible local terminal Z-readout encodings."""
from bell34 import *

if __name__=='__main__':
    base=C.read(H/'g_base');rows=[]
    for choices in itertools.product(range(3),repeat=5):
        c=C.clone(base);edits=[]
        for choice,edge in zip(choices[:2],[(19,25),(17,16)]):
            if choice:
                c=remove_edges(c,[edge]);edits.append(['remove',edge])
                if choice==2:c=build(c,[edge[::-1]]);edits.append(['add',edge[::-1]])
        for choice,edge in zip(choices[2:],[(1,2),(14,15),(28,29)]):
            if choice:
                edge=edge if choice==1 else edge[::-1];c=build(c,[edge]);edits.append(['add',edge])
        name='g_ro_'+''.join(map(str,choices));r=save(c,name,edits);assert r['native_depth']<=48
        r['choices']=choices;rows.append(r)
    (H/'v34_readout.json').write_text(json.dumps(rows,indent=2)+'\n');print(len(rows))

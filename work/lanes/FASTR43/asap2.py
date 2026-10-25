exec(open('asap.py').read().split("\ndef chains")[0])
src=[('M',(15,),39),('M',(9,),37),('M',(8,),35),('M',(16,),37)]
for name,items in [('R2@36',[('R',(2,),36)]),('R2@36+src',[('R',(2,),36)]+src),('RX2@28',[('RX',(2,),28)]),
                   ('RX2@28+R1@28',[('RX',(2,),28),('R',(1,),28)]),('RX2@28+R2@36+src',[('RX',(2,),28),('R',(2,),36)]+src)]:
    print(name,depth(drop(sk,items)))

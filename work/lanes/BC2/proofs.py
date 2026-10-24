"""Solver receipts for literal-clean contradiction and disjoint encoders."""
import json
from pathlib import Path
import time
import sat6
import ft
from pycryptosat import Solver

out=[]
for rule in ('literal_initial', 'independent'):
    for depth in (13,14,15,16):
        for cap in (82,100):
            start=time.monotonic()
            if rule=='literal_initial':
                # Algebraic necessary-condition certificate. The 6 propagated
                # RX-pivot Xs span B+C's six X stabilizers; their C checks are
                # all zero. Literal B-clean forces all three B coefficients
                # of all six columns to zero, contradicting rank six.
                s=Solver(threads=1); n=[0]
                def nv(): n[0]+=1; return n[0]
                a=[[nv() for _ in range(6)] for _ in range(6)]
                inv=[[nv() for _ in range(6)] for _ in range(6)]
                for row in a:
                    for v in row[:3]: s.add_clause([-v])
                for i in range(6):
                    for j in range(6):
                        zs=[]
                        for k in range(6):
                            z=nv(); u=inv[i][k]; v=a[k][j]
                            s.add_clause([-z,u]);s.add_clause([-z,v]);s.add_clause([z,-u,-v]);zs.append(z)
                        s.add_xor_clause(zs,i==j)
            else:
                s,sel,p,edges,cells,add=sat6.build(depth,[18,24,30,31,32,33,34,35],0,maxcx=cap,rule='base')
                # Necessary condition for separate encoders with disjoint
                # qubit supports: no B-C CX. This already isolates B[0]=6
                # and C[4]=5, so further helper partition clauses are unneeded.
                for layer in sel:
                    for (u,v),var in layer.items():
                        if (u in ft.B and v in ft.C) or (u in ft.C and v in ft.B):
                            s.add_clause([-var])
            ok,_=s.solve(time_limit=90)
            receipt=dict(rule=rule,depth=depth,cap=cap,status='SAT' if ok else ('UNSAT' if ok is False else 'TIMEOUT'),elapsed=time.monotonic()-start)
            name=f'proof_{rule}_d{depth}_k{cap}.receipt.json'
            Path(name).write_text(json.dumps(receipt,indent=2))
            out.append(receipt); print(receipt,flush=True)
Path('proofs.json').write_text(json.dumps(out,indent=2))

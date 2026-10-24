import json,html
from pathlib import Path
H=Path(__file__).resolve().parent;name='region2_k56_A2_safe_dest';m=json.loads((H/(name+'.json')).read_text());roles={}
for role,cells in [('D',m['data_qubits']),('A',m['A']),('B',m['B']),('C',m['C'])]:
 for i,q in enumerate(cells):roles[q]=(role,i)
colors={'D':'#c6ebd4','A':'#f9d79a','B':'#acd9f4','C':'#d9c7f2'};size=66;ox=24;oy=66;svg=['<svg xmlns="http://www.w3.org/2000/svg" width="444" height="542" viewBox="0 0 444 542">','<rect width="444" height="542" fill="white"/>','<text x="24" y="28" font-family="sans-serif" font-size="19">ENDSTATE: row2, native R38</text>','<text x="24" y="48" font-family="sans-serif" font-size="12">182 CX · 9 coherent data hops · 9-CX A + 56-CX BC</text>']
for q in range(36):
 r,c=divmod(q,6);x=ox+c*size;y=oy+r*size;role,i=roles.get(q,('',0));fill=colors.get(role,'#f1f3f4');svg += [f'<rect x="{x}" y="{y}" width="60" height="60" rx="5" fill="{fill}" stroke="#777"/>',f'<text x="{x+5}" y="{y+14}" font-family="monospace" font-size="11" fill="#555">{q}</text>']
 if role:svg.append(f'<text x="{x+30}" y="{y+39}" text-anchor="middle" font-family="sans-serif" font-size="19" font-weight="bold">{role}{i}</text>')
svg += ['<text x="24" y="480" font-family="sans-serif" font-size="12">Equal indices are matched: D–A, D–B, B–C.</text>','<text x="24" y="499" font-family="sans-serif" font-size="12">BC cell25 is free after prefix step9; all other BC</text>','<text x="24" y="516" font-family="sans-serif" font-size="12">cells are free initially. Cell16 is reused after its</text>','<text x="24" y="533" font-family="sans-serif" font-size="12">checked zero readout to advance the final hop.</text>','</svg>'];(H/'best_geometry.svg').write_text('\n'.join(svg))

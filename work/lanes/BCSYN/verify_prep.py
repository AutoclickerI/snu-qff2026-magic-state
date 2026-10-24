#!/home/jihoon/competitions/quantumn/.venv/bin/python
"""Noiseless Stim target and BC2 FT checks for a prep JSON."""
import argparse,json,sys
import stim
import ft
B=[6,26,13,11,4,23,27];C=[12,25,19,17,5,29,28]
ROWS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('prep');ap.add_argument('--rule',default='both');a=ap.parse_args();d=json.load(open(a.prep));cells=d.get('cells',sorted(set(B+C+d.get('pivots',[]))))
 c=stim.Circuit(); piv=set(d['pivots'])
 for q in cells:c.append('R',[q])
 for q in piv:c.append('H',[q])
 for layer in d['ops']:
  for u,v in layer:c.append('CX',[u,v])
 sim=stim.TableauSimulator();sim.do_circuit(c)
 target=[]
 for block in (B,C):
  for row in ROWS:
   p=stim.PauliString(max(max(cells),max(B+C))+1)
   for i in row:p[block[i]]='X'
   target.append(p)
 vals=[int(sim.measure_observable(p)) for p in target]
 bad=ft.faults(d,cells,rule=a.rule)
 out={'stim_target_pass':all(v==0 for v in vals),'stim_measurements':vals,'ft_rule':a.rule,'ft_faults':len(bad),'ft_pass':not bad,'cells':cells,'pivots':d['pivots'],'cx':sum(map(len,d['ops'])),'depth':len(d['ops'])}
 print(json.dumps(out),flush=True);sys.exit(0 if out['stim_target_pass'] and out['ft_pass'] else 1)
if __name__=='__main__':main()

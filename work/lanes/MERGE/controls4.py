from pass4 import *

def run():
 rows=[]
 for name in ['polish_previous','polish_final','prepfree']:
  r=record(C/name,dict(kind='source control',name=name));rows.append(r)
  with (R/'local_controls.jsonl').open('a')as f:f.write(json.dumps(r)+'\n')
  print(json.dumps(dict(name=name,loss=r.get('loss'),acceptance=r.get('acceptance'),error=r.get('error'))),flush=True)
 txt=(C/'base.qasm').read_text()+'\nh q[6];\nt q[6];\nt q[6];\nt q[6];\nt q[6];\nh q[6];\n';st=E.write_stem(txt,E.D);r=record(st,dict(kind='raw-code-space negative control',expected='decoded-correct but raw code invalid'))
 assert 'raw output code space'in r.get('error',''),r
 with (R/'local_controls.jsonl').open('a')as f:f.write(json.dumps(r)+'\n')
 dump(R/'raw_code_regression.json',r);print('raw code negative control rejected',flush=True)
if __name__=='__main__':run()

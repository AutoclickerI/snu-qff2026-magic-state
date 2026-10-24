"""Changes to the measured release/A-preparation boundary, followed by legal retiming."""
from retime import *

def drop_checks(c,bits):
 c=copy.deepcopy(c)
 for b in bits:
  matches=[i for i,o in enumerate(c['ops'])if re.search(rf' -> c\[{b}\];',' '.join(o['lines']))]
  assert len(matches)==1,(b,matches);c['ops'].pop(matches[0])
  uses=[l for l in c['tail']if re.search(rf'c\[{b}\]',l)]
  assert uses==[f'// DETECTOR c[{b}]'],(b,uses)
  c['tail']=[l for l in c['tail']if l!=uses[0]]
 return c

def instrument(c):
 c=copy.deepcopy(c);ops=c['ops'];mi=next(i for i,o in enumerate(ops)if 'measure q[9] -> c[9];'in o['lines']);ci=max(i for i in range(mi)if ops[i]['lines']==['cx q[9],q[15];']);t=ops[ci]['t'];drop={ci,mi}
 for line in ['tdg q[15];','measure q[16] -> c[43];','cx q[15],q[16];','cx q[16],q[15];','measure q[15] -> c[53];']:
  drop.add(next(i for i,o in enumerate(ops)if line in o['lines']))
 bit=max(int(b)for o in ops for b in re.findall(r'c\[(\d+)\]',' '.join(o['lines'])))+1
 new=[dict(lines=['measure q[16] -> c[43];'],t=t-1,tag='prefix')]
 for j,(a,b)in enumerate([(9,15),(15,16),(16,15),(15,16)]):new.append(dict(lines=[f'cx q[{a}],q[{b}];'],t=t+j,tag='prefix'))
 for lines in [['h q[9];','measure q[9] -> c[9];'],[f'measure q[15] -> c[{bit}];'],['tdg q[16];']]:new.append(dict(lines=lines,t=t+4,tag='prefix'))
 c['ops']=[o for i,o in enumerate(ops[:ci])if i not in drop]+new+[o for i,o in enumerate(ops[ci:],ci)if i not in drop]
 # Establish native per-wire dependency order without assigning illegal times.
 for j,o in enumerate(c['ops']):o['id']=j
 c['ordered']=True
 c['tail']=[l for l in c['tail']if l!='// DETECTOR c[53]']+[f'// DETECTOR c[{bit}]']
 c['h']=[re.sub(r'creg c\[\d+\]',f'creg c[{bit+1}]',l)for l in c['h']]
 # Sequential insertion represents the exact ST1 instrument. First solve its
 # original dependency DAG; the commuting solver then acts on that ordering.
 c,r=schedule(c,mode='alap');assert c is not None,r;c['ordered']=False
 c['ops'].sort(key=lambda o:o['t']);return c

def build(name,bits=(),use_instrument=False):
 c=annotate(read(H/'inputs/v30f'))
 if use_instrument:c=instrument(c)
 if bits:c=drop_checks(c,bits)
 d,r=solve(c,27,30,1)
 if d:
  st=save(d,'v30/'+name)
  try:r['screen']=score(st)
  except Exception as e:r['score_error']=repr(e)
 r.update(removed_checks=list(bits),instrument=use_instrument)
 (V/(name+'.build.json')).write_text(json.dumps(r,indent=2));append_result(name,r,'Release-chain macro; checks removed only with their singleton detectors, ideal correctness rechecked.');print(name,json.dumps(r),flush=True)
if __name__=='__main__':
 build('release_drop9',[59]);build('release_drop129',[59,60,180]);build('release_instrument',use_instrument=True);build('release_instrument_drop129',[59,60,180],True)

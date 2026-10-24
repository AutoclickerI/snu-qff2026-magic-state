"""GDB counters on the installed exact engine; no installed-file changes."""
import gdb,json,collections,os
counts=collections.Counter();flags=collections.Counter();fired=collections.Counter()
class Counter(gdb.Breakpoint):
 def __init__(self,name,key):self.key=key;super().__init__(name,internal=True)
 def stop(self):
  counts[self.key]+=1
  if self.key=='process':
   obj=int(gdb.parse_and_eval('$rdi'));nev=int(gdb.parse_and_eval('$edx'));flag=int.from_bytes(gdb.selected_inferior().read_memory(obj+0x4e8,1),'little');flags[flag]+=1;fired[nev]+=1
  return False
for name,key in [('process_shot_','process'),('process_shot_general_','general'),('full_fallback_shot_','forced_full'),('replay_pattern_','pattern_replay'),('build_pattern_','pattern_build')]:
 # Resolve the unique primary symbol from the already imported extension.
 matches=gdb.execute('info functions FramedCircuitShotSampler::'+name,to_string=True)
 names=[]
 for line in matches.splitlines():
  if 'FramedCircuitShotSampler::'+name+'(' in line and '[clone' not in line:names.append(line[line.index('qeccore::'):].rstrip(';'))
 assert len(names)==1,(name,names,matches)
 Counter(names[0],key)
class Reset(gdb.Breakpoint):
 def stop(self):counts.clear();flags.clear();fired.clear();return False
Reset('(anonymous namespace)::CompiledProgram::sample(int, unsigned long, bool, bool, bool, bool)',internal=True)
def done(event):
 out=dict(counts=dict(counts),has_general_flag_shots=dict(flags),fired_event_histogram=dict(fired),engine='installed exact',flag_offset='0x4e8; confirmed by installed binary disassembly')
 p=os.environ['TRACE_OUT'];open(p,'w').write(json.dumps(out,indent=2));print('TRACE_RESULT',json.dumps(out))
gdb.events.exited.connect(done)

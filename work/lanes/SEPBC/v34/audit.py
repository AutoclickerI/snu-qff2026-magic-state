from design import *
sys.path.insert(0,str(H/'v30'));from critical import analyze
import collections
rows=[];lines=['# R44 dependency and R43 search certificate','','All times are zero-based native steps. Node ES/LS use the emitted wire order; CP receipts separately permit exact CX/control-phase commutations. A component ready slack is not an independently movable window.','']
for name in ['decoder0','reuseblue_0_R43','checked16_timing_0']:
 c=json.loads((V/(name+'.plan.json')).read_text());d=analyze(c);(V/(name+'.critical.json')).write_text(json.dumps(d,indent=2));R=c['meta']['R'];regions=collections.defaultdict(list)
 for o,z in zip(c['ops'],d['operations']):
  if o.get('tag')not in('round','decoder'):regions[o.get('tag','prefix')].append(z)
 component={k:dict(actual=max(z['t']for z in zs)+1,earliest=max(z['es']for z in zs)+1,slack=R-max(z['es']for z in zs)-1)for k,zs in regions.items()}
 lines +=[f'## {name}: R{R}; emitted-order minimum R{d["minimum_R"]}','','| Component | Actual ready | Earliest ready | Ready slack |','|---|---:|---:|---:|']
 for k,z in component.items():lines.append(f'| {k} | {z["actual"]} | {z["earliest"]} | {z["slack"]} |')
 lines+=['','One longest-path suffix:','']
 for i in d['longest_paths'][0]:
  z=d['operations'][i]
  if z['es']>=25:lines.append(f'- ES {z["es"]}, actual {z["t"]}, slack {z["slack"]}: '+ ' / '.join(z['lines']))
 roundops=[]
 for o in c['ops']:
  if o.get('tag')in('round','decoder')and unit(o).name=='CX':
   pair=tuple(map(int,S.QRE.findall(o['lines'][0])))
   if pair in list(zip(D,A))or pair in[(9,15),(8,9)]:roundops.append(dict(pair=pair,t=o['t']))
 rows.append(dict(stem=name,R=R,minimum_R=d['minimum_R'],components=component,decoder_and_couplings=roundops))
 lines+=['','Decoder/coupling times: `'+json.dumps(roundops)+'`.','']
lines+=['## Scope and diagnosis','','The source-check-free R43 branches were not revisited. Reset-free pre-blue q2 reuse advances Bell preparation by one tick, but is SLOW in both tested A-encoder contexts (169.1 and146.3 seconds per million predicted). Retiming remains SLOW. The ordinary reset-bearing operation sets are CP-INFEASIBLE atR43 even with global tested CX/control-phase commutations.','','The complete finite unitary search has11811 rank-four subspaces,35 coordinate input sets and95 matching layers including the empty layer. It has no CX-count cap. For two transfer routes, five initialization modes and their recorded per-cell release bounds, noR42/R43 target exists;120 R44 witnesses independently replay correctly. This excludes that finite model, not all prefix reorderings, helpers or general Clifford instruments.','','The one-dirty-bus scan covers132 specified UVUV timing/direction recipes through data3/7/10. Endpoints are conservatively reserved during the bus; it does not exclude all interleavings or multiple buses. The measurement scan covers one rank-five→four Z measurement, or rank-four→three Z measurement followed by one X initialization, with fresh-input modes1/2. Neither has an R43 witness;41 R44 calibration witnesses independently replay. Multi-measurement/helper-assisted architectures remain outside this certificate.','','The joint-coupling scan checks168 invertible binary syndrome maps HM=NH on one chosen schedule per unitary witness. No R43 coupling assignment is found for the tested witnesses. This does not exclude different gate paths with the same input choice. Four simple staggered branch recipes are infeasible; no global staggered-round bound is claimed.','','A route-rewrite bookkeeping error was corrected: the old late q14 prefix release must precede its new data-hop reuse. All final route witnesses and full circuits use the corrected order. Invalid blue-gate permutations were rejected by the unchanged ideal checks. No detector was deleted to pass a failed test.']
(V/'CRITICAL_PATH.md').write_text('\n'.join(lines)+'\n');(V/'critical_summary.json').write_text(json.dumps(rows,indent=2));print(rows)
for name in ['layer_26_R44_m2','layer26_timing_0','checked16_timing_0']:
 st=V/name;c=json.loads(st.with_suffix('.plan.json').read_text());md=c['meta'];actual=read(st);assert[(o['t'],o['lines'])for o in c['ops']]==[(o['t'],o['lines'])for o in actual['ops']]
 md.update(source='FRESH/guard5_timing_0_a_decode on SEPBC guard5 lineage',method='Time-aware rank-four CSS A synthesis with all source checks; exact-loss retiming; q16 known-X check where recorded',construction_receipt=name+'.plan.json',qasm_sha256=hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest(),native_depth=max(o['t']for o in c['ops'])+1,cx=sum(unit(o).name=='CX'for o in c['ops']))
 md['CX']=md['cx'];md['resource_schedule']=[dict(t=o['t'],lines=o['lines'])for o in c['ops']if o.get('tag')=='encoder_bc'];md.pop('A_init_times',None);md.pop('A_input_plan',None);md['A_schedule']=[dict(t=o['t'],lines=o['lines'])for o in c['ops']if o.get('tag')=='encoder_a'];md.pop('init_times',None)
 md['D_A_times']=[dict(pair=(u,v),t=max(o['t']for o in c['ops']if o['lines']==[f'cx q[{u}],q[{v}];']))for u,v in zip(D,A)]
 md['decoder']=dict(gates=[(9,15,44),(8,9,45)],flag_record=16,flag_measurement_t=46)
 md['all_source_checks_retained']=all(f'// DETECTOR c[{b}]'in c['tail']for b in[54,55,56,57,64,67])
 assert md['all_source_checks_retained'];st.with_suffix('.json').write_text(json.dumps(md,indent=2));st.with_suffix('.plan.json').write_text(json.dumps(c,indent=1))

from combine import *

def main():
 items=[json.loads(l)for l in(OUT/'items_results.jsonl').read_text().splitlines()];times=[json.loads(l)for l in(OUT/'timing_results.jsonl').read_text().splitlines()];base=items[0];by={r['stem']:r for r in items+times};jobs=[]
 # All output readouts that individually improve loss; harmless readouts earlier, plus the
 # two long-lived prefix ancilla readouts and blue check's terminal Z readout.
 ts=[r['recipe']for r in times if 'total'in r and r['total']<base['total']-1e-9 and r['A1']<=base['A1']]
 ts += [by['time_u125_t10']['recipe'],by['time_u206_t38']['recipe']]
 check=[by[n]['recipe']for n in ('check_u247','check_u2','check_u13','check_u18','check_u5','check_u84','check_u7','check_u12','check_u24')]
 frees=[by[n]['recipe']for n in ('reset_u3','reset_u39','reset_u133','reset_u188','reset_u218')]
 c=loadc(OUT/'base');sites=[137,142,144,145,146,161]
 for mask in (0,4,12,36,44,60,63):
  rs=[dict(kind='bc_reset',unit=i,q=c['u'][i].qs[0],bit=detbits(' '.join(c['u'][i].lines))[0])for j,i in enumerate(sites)if mask>>j&1]
  for level in range(4):
   recipes=rs+ts+(check[:1]if level==1 else check if level>=2 else [])+(frees if level==3 else [])
   try:jobs.append(apply_recipes(recipes,f'final_m{mask:02x}_l{level}'))
   except Exception as e:print(mask,level,'fail',repr(e),flush=True)
 (OUT/'final_manifest.json').write_text(json.dumps(jobs,indent=2)+'\n');print('finalsets',len(jobs),flush=True)

if __name__=='__main__':main()

from a35_guard_patches import *
patches=json.loads((D/'guard_patches.json').read_text());ss=[];errors=[]
def save(name,body,md):
 stem=D/'candidates'/name;stem.with_suffix('.qasm').write_text(body);stem.with_suffix('.json').write_text(json.dumps(md,indent=2));ss.append(str(stem.relative_to(H)));return stem
def reset_checks(stem,bits):
 s=read(stem);uu=list(s[3]);tt=list(s[4]);tail2=list(s[5]);changed=[]
 for bit in bits:
  matches=[i for i,u in enumerate(uu) if u.name in ('MX','MEASURE') and any(re.search(rf'c\[{bit}\](?!\d)',l) for l in u.lines)]
  if not matches:continue
  i=matches[0];q=uu[i].qs[0];assert f'// DETECTOR c[{bit}]' in tail2
  assert sum(bool(re.search(rf'c\[{bit}\](?!\d)',l)) for l in tail2)==1
  plus=uu[i].name=='MX';uu[i]=U([f'reset q[{q}];']+([f'h q[{q}];'] if plus else []));tail2.remove(f'// DETECTOR c[{bit}]');changed.append(bit)
 body,md=finish(uu,tt,tail2,dict(kind='funded_A',source=str(stem.relative_to(H)),delay=s[1].get('R',44)-44,parent_options=s[1].get('options'),reset_instead_of_checked_measurements=changed));return body,md
if __name__=='__main__':
 for tag in patches:
  s,m=apply(D/'inputs/v35b',patches[tag]);save('control_'+tag,s,m)
 # A zero-blind encoder with one added full-cycle tick: retain every physical guard
 # unless a named complete patch changes it, then price exact check budgets.
 for tag in ['none','headroom','guard_gain','drop_x20_guard','balanced']:
  stem=D/'candidates/frontier_004'
  if tag!='none':
   try:s,m=apply(stem,patches[tag]);stem=save('f0_'+tag,s,m)
   except (ValueError,AssertionError) as e:errors.append([tag,repr(e)]);continue
  for n in [3,5,8,10]:
   bits=[181,182,188,186,187,185,183,184,271,3][:n]
   try:s,m=reset_checks(stem,bits);save(f'f0_{tag}_fund{n}',s,m)
   except (ValueError,AssertionError) as e:errors.append([tag,n,repr(e)])
 (D/'funding.json').write_text(json.dumps(ss,indent=2));(D/'funding_errors.json').write_text(json.dumps(errors,indent=2));print('funding',len(ss),'errors',errors,flush=True)

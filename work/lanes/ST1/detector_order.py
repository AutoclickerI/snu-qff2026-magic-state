"""Verified reference-only detector permutation for exact2's int64 batches.

Adapted from ST2/reference_cubic.py. Physical circuit artifacts are unchanged.
"""
import re,hashlib

def evaluate(text,data,evaluator):
 ev=evaluator(text,data);e=ev.e
 if len(e.projs)<64:return ev,None
 active=[i for i,x in enumerate(e.projs)if x[:2]!=(0,0)];inactive=[i for i in range(len(e.projs))if i not in active];early=min(16,len(inactive));perm=inactive[:early]+active+inactive[early:]
 assert early+len(active)<53
 assert all(e.projs[i]==(0,0,1+0j)and e.v[i]==0 for i in inactive)
 assert all(((x&v).bit_count()+(z&u).bit_count())%2==0 for x,z,_ in e.projs for u,v,_ in e.projs)
 lines=text.splitlines();pos=[i for i,l in enumerate(lines)if l.startswith('// DETECTOR')];rows=[lines[i]for i in pos];native=[int(re.search(r'DETECTOR line (\d+)',lab)[1])-1 for lab in ev.m.labels if lab.startswith('DETECTOR line ')];assert len(rows)==len(e.projs)==len(native)
 last=int(re.findall(r'measure q\[\d+\] -> c\[(\d+)\];',text)[-1])
 for i,old in enumerate(perm):lines[pos[i]]=rows[native[old]]+f' c[{last}] c[{last}]'
 z=evaluator('\n'.join(lines)+'\n',data);assert len(ev.m.faults)==len(z.m.faults)
 assert [r[:4]for r in ev.m.rots]==[r[:4]for r in z.m.rots]and ev.m.Q==z.m.Q and ev.m.cz==z.m.cz and ev.m.cxz==z.m.cxz
 for a,b in zip(ev.m.faults,z.m.faults):
  assert all(a[k]==b[k]for k in('s','e','p','chan'))
  assert b['d']==sum(((a['d']>>old)&1)<<new for new,old in enumerate(perm))
 assert z.e.projs==[e.projs[i]for i in perm]
 assert abs(z.e.A0-e.A0)<1e-14 and max(abs(z.n_single-ev.n_single))<1e-14 and max(abs(z.a_single-ev.a_single))<1e-14
 return z,dict(detectors=len(rows),active_projectors=len(active),permutation=perm,all_physical_fault_signatures_matched=True,commuting_projectors=True,singles_matched=True,reference_only=True,source_sha256=hashlib.sha256(text.encode()).hexdigest())

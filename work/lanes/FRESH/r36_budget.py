from round35 import *
OUT=HERE/'r36';src=D/'sepbc_echo_both';ops,dets,md=load(src);results=[]
for bits in [(39,40,41,42),(40,41,42),(39,40,41),(40,41)]:
 oo=copy.deepcopy(ops);dd=copy.deepcopy(dets)
 for bit in bits:
  o=next(o for o in oo if o.bit==bit);assert o.kind=='M';o.kind='R';o.bit=None
  assert {bit} in dd;dd.remove({bit});assert all(bit not in row for row in dd)
 s=emit('sepbc_reset_'+'_'.join(map(str,bits)),oo,dd,md,dict(base=str(src),initial_mz_to_reset=bits,source='ST2 v35b acceptance trade ported to SEPBC/FRESH composition'))
 r=dict(stem=str(s));r['c1']=float(certify(s)['c1']);r.update(price(s,7));results.append(r);print(json.dumps(r),flush=True)
(OUT/'budget_results.json').write_text(json.dumps(results,indent=2))

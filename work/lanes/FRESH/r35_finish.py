from r35_echo import *
ops,dets,md=load(D/'feedback_best');oo,dd=add(ops,dets,15,21,'X',19,29);oo,dd=add(oo,dd,20,26,'Z',18,31)
rows=[]
for name,checks in [('long',[]),('long_a1',[(1,39,'MX')]),('long_q6',[(6,12,'MX')]),('long_a1_q6',[(1,39,'MX'),(6,12,'MX')]),('long_q4',[(4,4,'MX')])]:
 o2=copy.deepcopy(oo);d2=copy.deepcopy(dd)
 for q,t,kind in checks:
  assert not any(o.time==t and q in o.qs for o in o2)
  bit=max(o.bit for o in o2 if o.bit is not None)+1;o2.append(f.Op(kind,(q,),t,bit));d2.append({bit})
 stem=emit('finish_'+name,o2,d2,md,dict(source='feedback_best',echoes=[[15,21,'X',19,29],[20,26,'Z',18,31]],watches=checks))
 r=dict(stem=str(stem))
 try:certify(stem);r.update(price(stem,int(sys.argv[1]) if len(sys.argv)>1 else 1))
 except Exception as e:r['error']=repr(e)
 print(json.dumps(r),flush=True);rows.append(r);(D/'finish_results.json').write_text(json.dumps(rows,indent=2))

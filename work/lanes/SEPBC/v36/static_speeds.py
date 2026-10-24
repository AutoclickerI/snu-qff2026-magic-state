from core import *
sys.path.insert(0,str(V/'speed_screen'));from general_atoms import analyze
for n in sys.argv[1:]:
 st=V/n
 if st.with_suffix('.static_speed.json').exists():continue
 try:r=analyze(st)
 except Exception as e:r=dict(prediction='ERROR',error=repr(e))
 st.with_suffix('.static_speed.json').write_text(json.dumps(r,indent=2));print(n,r.get('prediction'),r.get('general_atoms'),flush=True)

import os,sys,json
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
sys.path[:0]=[str(R/'work/lanes/SOTA_20261028'),str(R/'work/tools')]
from native_schedule import solve,emit
from qtools import write_stem
from qtools.validity import raw_check
p=H/'redesign_five_valid_5505afaaef422fe1_d6_20_19_10_2_22_16';D=[6,20,19,10,2,22,16]
for i in range(3):
 result,info=solve(p,(30,53),i,12,['early','lateprep','earlyread'][i]);print('schedule',i,info['status'],info.get('clocks'),flush=True)
 if result:
  ops,dets=result;text=emit(ops,dets);raw=raw_check(text,D);stem=write_stem(text,D,H,'isometry_five_schedule_'+str(i));print('raw',raw['ok'],'stem',stem,flush=True)
  stem.with_suffix('.schedule.json').write_text(json.dumps({'solver':info,'raw':raw},indent=2)+'\n')

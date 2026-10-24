"""Merge completed campaign witnesses into the lane's single verified archive."""
from a30_common import *
import tarfile,hashlib,io,lzma,shutil
# Run only after the last job has exited and remote evidence is synchronized.
archive=H/'witnesses.tar.xz';out=H/'witnesses.new.tar.xz'
files=[]
for directory in [H/'blue',D]:
 for p in directory.rglob('*'):
  if not p.is_file() or '.xtim_cache' in p.parts:continue
  rel=p.relative_to(H)
  if p.suffix=='.py' or 'inputs' in rel.parts:continue
  files.append(p)
for p in [H/'search.csv',H/'best_seed0.qasm',H/'best_seed0.json',H/'ARCHIVE_AUDIT.json']:
 if p.exists():files.append(p)
manifest={str(p.relative_to(H)):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files}
old_sha=hashlib.sha256(archive.read_bytes()).hexdigest();count=0
with tarfile.open(out,'w:xz',preset=3) as dest:
 with tarfile.open(archive,'r:xz') as old:
  for member in old:
   if member.name in manifest:continue
   dest.addfile(member,old.extractfile(member) if member.isfile() else None);count+=1
 for p in files:dest.add(p,arcname=str(p.relative_to(H)),recursive=False)
 blob=json.dumps(manifest,sort_keys=True).encode();ti=tarfile.TarInfo('a30_archive_manifest.json');ti.size=len(blob);dest.addfile(ti,io.BytesIO(blob))
verified=set()
with tarfile.open(out,'r:xz') as check:
 for member in check:
  if member.name in manifest:
   payload=check.extractfile(member).read();m=manifest[member.name]
   assert len(payload)==m['bytes'] and hashlib.sha256(payload).hexdigest()==m['sha256'],member.name;verified.add(member.name)
assert verified==set(manifest)
new_sha=hashlib.sha256(out.read_bytes()).hexdigest();out.replace(archive)
(H/'ARCHIVE_AUDIT_v23.json').write_text(json.dumps(dict(previous_archive_sha256=old_sha,prior_member_count=count),indent=2))
audit=dict(status='PASS',sha256=new_sha,bytes=archive.stat().st_size,previous_sha256=old_sha,prior_members_preserved=count,new_files=len(manifest),new_files_verified=len(verified),manifest=manifest)
(H/'ARCHIVE_AUDIT.json').write_text(json.dumps(audit,indent=2));print(dict(sha256=new_sha,prior_members=count,new_files=len(manifest)),flush=True)

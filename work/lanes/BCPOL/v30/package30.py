"""Merge completed v30 evidence into the lane's single, verified witness archive."""
from pathlib import Path
import hashlib,io,json,lzma,tarfile,time

V=Path(__file__).resolve().parent;H=V.parent
keep={'feedback_1401_02324','bell4_0_s1201_00010'}
def digest(data):return hashlib.sha256(data).hexdigest()

def main():
    audit=json.loads((V/'artifacts.validation.json').read_text())
    assert audit['status']=='PASS' and audit['count']==24
    for tag in keep:
        assert (V/'finalists'/f'{tag}.mc.log').exists()
        assert ' mean ' in (V/'finalists'/f'{tag}.mc.log').read_text()
    archive=H/'witnesses.tar.xz';tmp=H/'witnesses.repacking.tar.xz'
    files=[p for p in (V/'finalists').iterdir() if not any(p.name.startswith(tag+'.') for tag in keep)]
    files+=list((V/'runs').iterdir())+list(V.glob('*.log'))+list((V/'sparse').glob('*.json'))
    manifest=json.loads((H/'witnesses.manifest.json').read_text())
    expected={}
    with tarfile.open(tmp,'w:xz',preset=5) as dst:
        with tarfile.open(archive,'r:xz') as src:
            for m in src:
                if not m.isfile():continue
                data=src.extractfile(m).read();dst.addfile(m,io.BytesIO(data))
                expected[m.name]=dict(path=m.name,bytes=len(data),sha256=digest(data))
        additions=[(str(p.relative_to(H)),p.read_bytes(),p) for p in sorted(files)]
        additions.append(('history/report_v25.py',(H/'report.py').read_bytes(),None))
        for name,data,p in additions:
            if name.endswith('.jsonl.xz'):name=name[:-3];data=lzma.decompress(data)
            assert name not in expected,name
            m=tarfile.TarInfo(name);m.size=len(data);m.mtime=int(time.time());m.mode=0o644
            dst.addfile(m,io.BytesIO(data));expected[name]=dict(path=name,bytes=len(data),sha256=digest(data))
    checked=set()
    with tarfile.open(tmp,'r:xz') as src:
        for m in src:
            data=src.extractfile(m).read();assert digest(data)==expected[m.name]['sha256']
            checked.add(m.name)
    assert checked==set(expected)
    tmp.replace(archive)
    manifest.update(sha256=digest(archive.read_bytes()),members=list(expected.values()),
                    retained_v30_finalists=sorted(keep),v30_verified_bundles=24)
    (H/'witnesses.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    for p in files:p.unlink()
    (H/'report.py').write_text('"""Render the current BCPOL report; historical renderer is archived."""\nfrom pathlib import Path\nimport runpy\nrunpy.run_path(str(Path(__file__).resolve().parent/"v30/report30.py"))\n')
    result=dict(status='PASS',members=len(expected),bytes=archive.stat().st_size,
                sha256=manifest['sha256'],retained_v30_finalists=sorted(keep),removed_loose_files=len(files))
    (V/'package.validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':main()

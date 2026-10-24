"""Archive completed search witnesses; retain verified finalists and cache inputs."""
from pathlib import Path
import io, json, lzma, re, tarfile, hashlib

H = Path(__file__).resolve().parent
archive = H / 'witnesses.tar.xz'
assert not archive.exists(), 'Archive already exists; do not discard earlier evidence'
rows = json.loads((H / 'evidence_index.json').read_text())
keep = {
    r['tag'] for r in rows
    if r['mc'] is not None and r['verified']
    and r['verified'].get('judge_pass') and r['verified'].get('speed_pass')
}
input_prefixes = (
    'base.prep.', 'v22h_c2c9.', 'v23h_c2c9.', 'v25k.',
    'replay_policy.', 'replay_endpoint.', 'replay_v25k.',
    'cache_rank4_3_after_check.', 'cache_rank5_parity.', 'mc3.',
)
paths = []
for p in (H / 'finalists').iterdir():
    if p.is_file() and p.name.split('.')[0] not in keep:
        paths.append(p)
for p in (H / 'inputs').iterdir():
    if p.is_file() and not p.name.startswith(input_prefixes):
        paths.append(p)
paths += [p for p in (H / 'runs').iterdir() if p.is_file() and not p.name.endswith('.receipt.json')]
paths += list(H.glob('*.log'))
paths += list(H.glob('*.collect.files'))
paths += list(H.glob('*paused.json'))
paths = sorted(set(paths))
manifest = []
with tarfile.open(archive, 'w:xz', preset=6) as tar:
    for p in paths:
        raw = p.read_bytes()
        name = str(p.relative_to(H))
        if p.name.endswith('.jsonl.xz'):
            raw = lzma.decompress(raw)
            name = name[:-3]
        info = tarfile.TarInfo(name)
        info.size = len(raw)
        info.mtime = int(p.stat().st_mtime)
        tar.addfile(info, io.BytesIO(raw))
        manifest.append(dict(path=name, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
# Read every member before deleting its original.
with tarfile.open(archive, 'r:xz') as tar:
    for record in manifest:
        raw = tar.extractfile(record['path']).read()
        assert hashlib.sha256(raw).hexdigest() == record['sha256']
for p in paths:
    p.unlink()
(H / 'witnesses.manifest.json').write_text(json.dumps(dict(
    archive=archive.name, sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
    retained_finalists=sorted(keep), members=manifest), indent=2) + '\n')
print(json.dumps(dict(archived=len(paths), retained=len(keep), bytes=archive.stat().st_size)))

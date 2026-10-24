"""Verify the delivered bundle and its pinned source blobs, without running a judge."""
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
count=0
for line in (ROOT/"CHECKSUMS.sha256").read_text().splitlines():
    digest,name=line.split("  ",1)
    relative=Path(name)
    assert not relative.is_absolute() and ".." not in relative.parts
    data=(ROOT/relative).read_bytes()
    assert hashlib.sha256(data).hexdigest()==digest, name
    count+=1
provenance=json.loads((ROOT/"SOURCE_PROVENANCE.json").read_text())
for item in provenance["files"]:
    data=(ROOT/item["path"]).read_bytes()
    actual=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    assert actual==item["git_blob_sha1"], item["path"]
print(json.dumps({"files_verified":count,"pinned_source_blobs_verified":len(provenance["files"]),"status":"PASS"}))

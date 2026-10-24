"""Regenerate the two annotation-only variants of the pinned v36a.
POSTSELECT(0) conversion is intentionally restricted to this verified input.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"audit/review9_resumed"
sys.path.insert(0,str(AUDIT))
from detector_basis import compress_detector_basis
stem=AUDIT/"inputs/v36a"
raw=stem.with_suffix(".qasm").read_bytes()
base_hash=hashlib.sha256(raw).hexdigest()
assert base_hash=="8faa1fa93b210c16c5dd9ec2fb8b31057c036f6ec657a33f56c9defda65795cf"
text=raw.decode()
basis,receipt=compress_detector_basis(text)
assert {k:receipt[k] for k in ["rows","rank","terms_before","terms_after","row_xors"]}=={"rows":68,"rank":68,"terms_before":112,"terms_after":85,"row_xors":20}
metadata=json.loads(stem.with_suffix(".json").read_text())
for suffix,value,explanation in [
    ("detector_basis",basis,"Invertible GF(2) row changes; no physical gate edits"),
    ("postselect",text.replace("// DETECTOR","// POSTSELECT(0)"),"All 68 deterministic zero-reference conditions explicitly represented as POSTSELECT(0)")
]:
    output=stem.with_name(stem.name+"_"+suffix)
    output.with_suffix(".qasm").write_text(value)
    meta=dict(metadata,qasm_sha256=hashlib.sha256(value.encode()).hexdigest(),
              review_annotation_transform=explanation,
              physically_equivalent_base_sha256=base_hash)
    output.with_suffix(".json").write_text(json.dumps(meta,indent=2)+"\n")
(AUDIT/"v36a_basis_python_certificate.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps({k:v for k,v in receipt.items() if k!="transform_decimal"}))

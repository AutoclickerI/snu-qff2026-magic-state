from pathlib import Path
import json
import re

def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row.bit_length() - 1
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
    return len(pivots)

def compress_detector_basis(qasm):
    lines = qasm.splitlines()
    positions = [
        i for i, line in enumerate(lines)
        if re.match(r"^\s*//\s*DETECTOR\b", line)
    ]
    original = []
    for i in positions:
        mask = 0
        for bit in re.findall(r"c\[(\d+)\]", lines[i]):
            mask ^= 1 << int(bit)
        original.append(mask)
    rows = original.copy()
    transform = [1 << i for i in range(len(rows))]
    operations = 0
    while True:
        best = None
        for i in range(len(rows)):
            for j in range(len(rows)):
                if i == j:
                    continue
                gain = rows[i].bit_count() - (rows[i] ^ rows[j]).bit_count()
                if gain > 0 and (best is None or gain > best[0]):
                    best = (gain, i, j)
        if best is None:
            break
        _, i, j = best
        rows[i] ^= rows[j]
        transform[i] ^= transform[j]
        operations += 1
    assert rank(transform) == len(rows)
    for i, mask in enumerate(transform):
        check = 0
        for j, row in enumerate(original):
            if (mask >> j) & 1:
                check ^= row
        assert check == rows[i]
    # This minimal emitter is for a full-rank basis; general dependent rows
    # need separate treatment of zero rows and nonzero affine references.
    assert rank(original) == len(rows)
    assert all(rows)
    for pos, row in zip(positions, rows):
        bits = [str(i) for i in range(row.bit_length()) if (row >> i) & 1]
        lines[pos] = "// DETECTOR " + " ".join("c[" + i + "]" for i in bits)
    receipt = {
        "rows": len(rows),
        "rank": rank(rows),
        "terms_before": sum(row.bit_count() for row in original),
        "terms_after": sum(row.bit_count() for row in rows),
        "row_xors": operations,
        "transform_decimal": [str(row) for row in transform],
    }
    return "\n".join(lines) + "\n", receipt

# Use a separate output stem; keep the original QASM and metadata as control.
# qasm = Path("v36a.qasm").read_text(encoding="utf-8")
# transformed, receipt = compress_detector_basis(qasm)
# Path("v36a_detector_basis.qasm").write_text(transformed, encoding="utf-8")
# Path("detector_basis_receipt.json").write_text(
#     json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
# )

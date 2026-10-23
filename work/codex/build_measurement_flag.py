"""Generate, verify and score the flagged measurement-based candidate."""
from pathlib import Path
import json
import tprep
import build_flag

OUT = Path(__file__).resolve().parent

def main():
    text = build_flag.text
    data = build_flag.dp
    qasm_path = OUT / "measurement_flag.qasm"
    json_path = OUT / "measurement_flag.json"
    scan_path = OUT / "measurement_flag_scan.txt"
    qasm_path.write_text(text, encoding="utf-8")
    report = tprep.check(text, data, p=1e-3, shots=10**7, seed=0)
    print(report)
    scan = tprep.fault_scan(text, data, processes=1)
    print(scan)
    json_path.write_text(json.dumps({
        "data_qubits": data,
        "score_1e7": report.score,
        "sem": report.sem,
        "acceptance": report.acceptance,
        "n_2q": report.n_2q,
        "c1": scan.c1,
    }, indent=2) + "\n", encoding="utf-8")
    scan_path.write_text(str(scan) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()

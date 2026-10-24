#!/usr/bin/env python3
"""Fail-closed consistency check for the bundled official-runner JSON schema.

This does not execute the judge or authenticate a receipt. For a fresh run,
first rename any prior receipt and require successful process exit plus a
newly written receipt. This checker cannot distinguish a stale passing file.
It prevents a failed runner's exit code 0 from being mistaken for validation.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys


PINNED_JUDGE = "76fe47c0324f1c1f8b72a7d55af200e88043b522"
PINNED_VERSIONS = {"xtim": "3.1.3+qff2", "stim": "1.16.0", "qiskit": "2.5.2",
                   "numpy": "2.3.5", "scipy": "1.18.1"}
GATES = ("format_ok", "class_ok", "correct_ok", "acceptance_ok", "passed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--qasm", type=Path, required=True)
    parser.add_argument("--shots", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--data-qubits", type=int, nargs=7, required=True)
    parser.add_argument("--judge-commit", default=PINNED_JUDGE)
    parser.add_argument("--tprep-version", default="3.0.3")
    parser.add_argument("--p", type=float, default=0.001)
    parser.add_argument("--minimum-acceptance", type=float, default=0.5)
    args = parser.parse_args()
    if args.shots <= 0 or len(set(args.data_qubits)) != 7:
        parser.error("positive shots and seven distinct ordered data qubits required")
    if not (math.isfinite(args.p) and 0 <= args.p <= 1):
        parser.error("p must be finite and in [0,1]")
    if not (math.isfinite(args.minimum_acceptance) and 0 <= args.minimum_acceptance <= 1):
        parser.error("minimum acceptance must be finite and in [0,1]")

    try:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
        digest = hashlib.sha256(args.qasm.read_bytes()).hexdigest()
    except (OSError, ValueError) as exc:
        print(json.dumps({"receipt_matches_request": False, "errors": [str(exc)]}))
        return 1

    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    def section(parent, name):
        value = parent.get(name)
        if not isinstance(value, dict):
            errors.append(f"missing or invalid object: {name}")
            return {}
        return value

    def finite_number(value):
        return type(value) in (int, float) and math.isfinite(value)

    if not isinstance(receipt, dict):
        print(json.dumps({"receipt_matches_request": False,
                          "errors": ["receipt root must be an object"]}))
        return 1

    target = section(receipt, "target")
    report = section(receipt, "report")
    gates = section(receipt, "gates")
    versions = section(receipt, "versions")
    require("exception" not in receipt, "receipt contains an exception field")
    require(receipt.get("official_commit") == args.judge_commit, "judge commit mismatch")
    require(receipt.get("tprep_version") == args.tprep_version, "tprep version mismatch")
    for package, version in PINNED_VERSIONS.items():
        require(versions.get(package) == version, f"pinned dependency mismatch: {package}")
    require(receipt.get("parser_errors") == [], "parser errors missing or nonempty")
    require(target.get("qasm_sha256") == digest, "candidate QASM SHA256 mismatch")
    data = target.get("data_qubits")
    require(isinstance(data, list) and all(type(q) is int for q in data) and
            data == args.data_qubits, "ordered data_qubits mismatch")

    for obj, key, expected, label in (
        (receipt, "shots", args.shots, "receipt shots"),
        (receipt, "seed", args.seed, "receipt seed"),
        (target, "requested_shots", args.shots, "target shots"),
        (target, "requested_seed", args.seed, "target seed"),
        (report, "shots", args.shots, "report shots"),
        (report, "seed", args.seed, "report seed"),
    ):
        require(type(obj.get(key)) is int and obj.get(key) == expected, f"{label} mismatch")

    for gate in GATES:
        require(gates.get(gate) is True, f"judge gate not true: {gate}")
    require(report.get("format_errors") == [], "format_errors missing or nonempty")
    require("class_error" in report and report["class_error"] is None,
            "class_error missing or non-null")
    require(report.get("correctness_errors") == [], "correctness_errors missing or nonempty")
    p = report.get("p")
    require(finite_number(p) and math.isclose(p, args.p, rel_tol=0, abs_tol=1e-15),
            "physical p mismatch or nonfinite")

    for name, lower, upper in (("score", 0, 1), ("sem", 0, math.inf),
                               ("acceptance", args.minimum_acceptance, 1),
                               ("ideal_acceptance", 0, 1 + 1e-12)):
        value = report.get(name)
        require(finite_number(value) and lower <= value <= upper,
                f"invalid or out-of-range {name}")
    require(finite_number(report.get("ideal_acceptance")) and
            report["ideal_acceptance"] > 0, "ideal_acceptance must be positive")

    result = {
        "receipt_matches_request": not errors,
        "receipt": str(args.receipt),
        "qasm_sha256": digest,
        "judge_commit": receipt.get("official_commit"),
        "shots": args.shots,
        "seed": args.seed,
        "errors": errors,
        "scope": "Receipt consistency only; no physics rerun or authenticity check.",
    }
    print(json.dumps(result, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

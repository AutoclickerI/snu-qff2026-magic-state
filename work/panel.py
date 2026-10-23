"""Official 1-F of circuits over a panel of seeds (fresh seeds measure the true mean without the
selection bias of the seeds a search used).

    python panel.py <first seed> <count> <procs> <stem> [stem ...]   (stem.qasm + stem.json)
"""
import json
import sys

from fast_check import check

if __name__ == "__main__":
    first, count, procs = (int(a) for a in sys.argv[1:4])
    for stem in sys.argv[4:]:
        text = open(stem + ".qasm").read()
        data = json.load(open(stem + ".json"))["data_qubits"]
        for seed in range(first, first + 1000 * count, 1000):
            rep = check(text, data, shots=10**8, seed=seed, procs=procs)
            print(json.dumps({"stem": stem, "seed": seed, "score": rep.score, "sem": rep.sem,
                              "acceptance": rep.acceptance, "passed": getattr(rep, "passed", None)}), flush=True)

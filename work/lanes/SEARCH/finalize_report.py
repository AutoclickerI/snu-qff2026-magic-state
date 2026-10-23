import json
from pathlib import Path

R = Path(__file__).resolve().parent
report = R / "REPORT.md"
text = report.read_text().split("<!-- generated appendix -->")[0]
text += "\n<!-- generated appendix -->\n"
text += "| Circuit | Qubits | CX | ASAP steps | Conditional error | SEM | Acceptance | Single-fault diagnostic |\n"
text += "|---|---:|---:|---:|---:|---:|---:|---|\n"
rows = []
for p in sorted((R / "evaluations").glob("*.json")):
    if p.name == "summary.json":
        continue
    d = json.loads(p.read_text())
    rows.append(d)
    b = list(d["basis"].values())
    a = sum(v["acceptance"] for v in b) / len(b)
    sf = sum(v.get("single_fault_diagnostic", {}).get("malignant_mechanisms", 0) for v in b)
    text += f"| {d['name']} | {d['num_qubits']} | {d['cx']} | {d['asap_steps']} | {d['loss']:.6g} | {d['sem']:.2g} | {a:.6f} | {sf} malignant mechanisms |\n"
(R / "evaluations/summary.json").write_text(json.dumps(rows, indent=2))
text += """
The final audit verified SHA-256 for 689 saved source files with zero missing files or mismatches (AUDIT.json). Re-running poor14_ZX_separate and mqt_plus_ft_opt_opt from their saved circuits reproduced accepted/error counts exactly (evaluations/reproduction.log). All scored CSS matrices have seven distinct nonzero syndrome columns and commute.

All 18 scored circuits passed noiseless syndrome/output checks. Stim DEM inspection found no accepted decoded-failure single mechanism for the flagged preparations and extraction rounds. The four unverified MQT encoders expose first-order mechanisms, as expected. DEM decomposition is used only as a first-order diagnostic; finite-p numbers come from direct sampling.

Saved Stim circuits and JSON counts make the screens reproducible with rerun_saved.py. There are 24 sampled bases, 120 million shots in the final set. The archived earlier logs contain superseded adapter results; the table and evaluations/*.json are authoritative. The adapter was corrected to split dependent Stim gates and fold native readout, then all affected measurements were rerun.

**Verified:** primary-source retrieval, pinned source versions, static counts where stated, noiseless Clifford behavior, terminal single-error decoding, and these grid-free Monte Carlo screens. **Unverified:** grid placement, full non-Clifford T preparation, cross terms with our input stage, three-seed official score, and any resulting submission's format/class/correctness.

Basis-state infidelity does not price every correlated error an ancilla can introduce later. Score any adopted block in its actual data-coupling role before ranking it. No perfect terminal syndrome rejection was added to improve these numbers.

## Provenance and coverage

Each found/<slug>/provenance.json records source URLs, commit hashes where available, licences and checksums. arXiv/Zenodo deposits use versions, DOIs and checksums instead of invented git hashes. A paper's licence does not license its accompanying code. Source copies are unmodified; translations/generated circuits and measurements are separate files.

The unavailable Jeon endpoint is documented in found/ijshj10--ftzx/. Gao and Surti explicitly offer data/code on reasonable request; no request was sent. Searches did not identify an author implementation for the ILP paper. Unrelated code citing a paper was not represented as author code.

The final MQT archive explains that its higher-distance comparison circuits remove destructive data readout and selected flag-basis H gates. Its total-CX column sums four constituent encoders; count the three transversal block comparisons separately when assembling a factory. The branch commit here matches the archive's stated simulation dependency.

| Saved artifact | Commit / immutable identifier | Licence |
|---|---|---|
"""
for p in sorted((R / "found").glob("*/provenance.json")):
    d = json.loads(p.read_text())
    lic = d.get("licence", "unspecified")
    if isinstance(lic, dict):
        lic = lic.get("id", lic.get("name", str(lic)))
    if isinstance(lic, list):
        lic = ", ".join(lic)
    ref = d.get("commit") or d.get("doi") or d.get("version") or "version/checksums in provenance"
    text += f"| [{p.parent.name}](found/{p.parent.name}/provenance.json) | {ref} | {lic} |\n"

text += """
## Queries run, with hit counts

Counts are API totals unless marked as returned-page counts. GitHub results were capped at 100 metadata hits per query, not exhaustively scanned. No code-snippet/text-match previews were requested. Broad flag/T/Noh searches returned considerable unrelated material; targeted queries and primary-paper links supplied useful artifacts. Code-search requests were separated by at least seven seconds.

| Search | Exact query | Total hits | Saved / returned metadata |
|---|---|---:|---:|
"""
for p in sorted((R/"searches").glob("github-code-*.json")) + sorted((R/"searches").glob("github-target-*.json")):
    d = json.loads(p.read_text())
    count = d.get("total_count")
    if count is None:
        count = "HTTP 408; retried below"
    text += f"| GitHub code | {d['query']} | {count} | {len(d.get('items', []))} |\n"
for pattern in ["zenodo-fixed-*.json", "zenodo-focused-*.json"]:
    for p in sorted((R/"searches").glob(pattern)):
        d = json.loads(p.read_text())
        hits = d["raw"]["hits"]
        text += f"| Zenodo | {d['query']} | {hits['total']} | {len(hits['hits'])} |\n"
for p in sorted((R/"searches").glob("figshare-[0-9].json")):
    d = json.loads(p.read_text())
    text += f"| Figshare | {d['query']} | not exposed | {d.get('count', 'error')} |\n"

text += """
Initial Zenodo requests with size=100 failed HTTP 400. Repeating with size=25 succeeded; failed responses remain in searches/zenodo-0.json through zenodo-3.json. The successful Steane retry also exists as zenodo-retry.json. Figshare Steane/Heussen pages mostly matched unrelated surnames. Its magic-state query returned eight records; only relevant quantum records were inspected.

Supplemental web queries are listed below. The tool did not expose exhaustive hit totals; the API searches above provide the countable results.

| Batch | Exact queries | Hit-total status |
|---|---|---|
| 1 | arxiv "2609.12698"; arxiv "2601.13313"; arxiv "2607.22498" quantum; "Steane" "magic state" github | Not exposed |
| 2 | site.zenodo.org Postler "fault-tolerant" 2022; site.zenodo.org Heussen "magic"; site.figshare.com "Steane"; "2607.22498" github | Not exposed |
| 3 | "Postler" "zenodo" magic; "Heußen" "zenodo" magic; "Chamberland" "Cross" "Noh" magic state flag github; "Steane" site:figshare.com/articles | Not exposed |
| 4 | "Heussen" "zenodo" quantum; "magic" "Steane" site:zenodo.org/records; "flag" "Steane" site:figshare.com; "Extremely Low-Cost Magic State" github | Not exposed |
| 5 | "Code switching revisited" Daguerre Kim code github; "Efficient fault-tolerant code switching via one-way transversal CNOT gates" arxiv; "Sascha" "magic" "zenodo" | Not exposed |

Sources were fetched directly from arXiv, publisher pages, pinned GitHub URLs, Zenodo and Figshare. No research conclusion depends on a secondary search-result summary or memory.

## Other contest entries (not opened)

The first URL explicitly matched the contest-name query. The others are conservative exclusions from combined tprep/data_qubits metadata hits; metadata alone does not establish that they are contest teams. None was opened. Only URLs are listed for owner review.

"""
p = R/"searches/excluded.jsonl"
urls = list(dict.fromkeys(json.loads(s)["url"] for s in p.read_text().splitlines())) if p.exists() else []
text += "\n".join("- "+u for u in urls) + "\n"
report.write_text(text)

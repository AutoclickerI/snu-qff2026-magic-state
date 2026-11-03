# Publication status and approval history

The selected research checkpoint was published to [draft PR #1](https://github.com/AutoclickerI/quantumn/pull/1) in commit `781ab32058a0567516981f9586338d5cdb6896d1`. SOTA has not been reached. The PR remains a draft; there was no merge, production race restart, or contest submission. The repository was private when verified after publication.

## Approval history

Automatic approval review initially rejected creation of the next GitHub tree for the broad export. It stated that the payload contained hundreds of research artifacts, logs, QASM circuits and source files, and that publication of this exact payload had not been explicitly authorized; it also raised potential sensitive-material, third-party and licensing concerns. Publication stopped at that point, with only unreferenced staging objects created and the branch still at `c645a5f77ebfcb7db00c48c35e006d046e729470`.

The owner was then asked: “Do you approve publishing the exact selected checkpoint described in PUBLICATION.md to draft PR #1, keeping it as a draft with no merge or contest submission?” The owner replied “continue,” authorizing that specific export. The completed tree was checked against all selected file hashes and the unchanged main blobs before the branch was advanced with an expected-head lease. The original pre-approval inventory and status record remain available in the published checkpoint commit `781ab32058a0567516981f9586338d5cdb6896d1`; the preparation-time status in `upstream_integration.json` is historical.

## Published scope

The selected files are listed in [checkpoint_manifest.json](checkpoint_manifest.json), plus that inventory itself and the unchanged main blobs listed in [upstream_integration.json](upstream_integration.json). The destination is branch `codex/structural-redesign-20261027` of `AutoclickerI/quantumn`. The selected source scripts, QASM/specifications, evaluation receipts, result ledgers, reports and manifests cover four research lanes, along with updates to `docs/PLAN.md` and `docs/SOTA.md`.

The inventory records paths, byte counts and SHA-256 hashes. Downloaded environments, compiler/vendor trees, caches and downloaded unlicensed ULO source copies are excluded. The independently written implementation retains the public algorithm's citation and pinned provenance. The checkpoint incorporates main commit `82657bf8e1de91f40e9137f5a517e6f4dacd7518` as a parent, preserving the owner's race-stop record; the main reference was not changed.

# Publication status and exact approval scope

The research checkpoint is complete locally. SOTA has not been reached.

Automatic approval review rejected creating the next GitHub tree for the broad public export. Its stated reason was that the payload contains hundreds of research artifacts, logs, QASM circuits and source files; work on the project was authorized, but publication of this exact broad payload was not explicit, and the review raised potential sensitive-material, third-party and licensing concerns.

Publication stopped after that rejection. Some unreferenced staging Git objects had been created by earlier accepted calls. **No new commit was created, no branch reference was advanced, and PR #1 was not updated.** The research branch remains at `c645a5f77ebfcb7db00c48c35e006d046e729470`, verified through the connector after rejection. The main branch, production race and contest submissions were not changed.

## Proposed action requiring explicit approval

Publish the selected files listed in [checkpoint_manifest.json](checkpoint_manifest.json), plus that inventory itself and the unchanged main blobs listed in [upstream_integration.json](upstream_integration.json), to the existing draft PR:

- Repository: `AutoclickerI/quantumn` (public).
- Branch: `codex/structural-redesign-20261027`.
- Pull request: <https://github.com/AutoclickerI/quantumn/pull/1>.
- Contents: the four new research lanes' selected source scripts, QASM/specifications, evaluation receipts, result ledgers, reports and manifests; updated `docs/PLAN.md` and `docs/SOTA.md`.
- Upstream integration: preserve main's existing race-stop record and already committed candidate files, as listed by Git blob SHA. The main reference is not changed.
- PR state: remain draft; no merge, race restart or contest submission.

The inventory provides exact repository paths, byte counts and SHA-256 hashes. Downloaded environments, compiler/vendor trees, caches and the downloaded unlicensed ULO source copies are excluded. The independently written implementation retains the public algorithm's citation and pinned provenance. These checks narrow the payload; they do not override the automatic review's approval requirement.

The last successful staging tree was `9229479e883012415cdc57bc1837d96f93a9d1b2`; subsequent local report updates and the refreshed leaderboard are not in that tree. Do not treat that partial staging object as the complete checkpoint or advance the branch to it. Resume only after the exact public export is approved, and recheck the current branch head before updating it.

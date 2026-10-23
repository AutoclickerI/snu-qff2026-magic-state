# Constraints

Each rule is `[hard]` (external, or protects others, shared resources, safety or Jihoon's authority) or
`[owner]`, with its source **[external: <source>]** or **[Jihoon, R-<id>]**. `P` =
`upstream/snu-qff2026-problem/problem.md`; `S` = the contest site (`upstream/hackathon*.html`).

## Hard limits (bind above G0)

1. **Grid and gates.** [hard] "상하좌우로 이웃한 쌍에만 2-qubit gate를 적용할 수 있습니다"; "2-qubit
   gate는 **`cx`만** 사용"; no 3-qubit, rotation, custom or conditional gates (P §1.1–1.2). Enforced by
   `tprep.check` `format`. [external: P]
2. **Judge-processable.** [hard] "**채점기(xtim)가 처리할 수 있는 회로**여야 합니다" (P §1.4). Enforced by
   `class`/`correctness`. [external: P]
3. **Acceptance.** [hard] "$p=10^{-3}$에서 acceptance가 0.5 이상" (P §1.6). Enforced by `acceptance`.
   [external: P]
4. **Size.** [hard] "**200 KB, 명령 5,000개 이하**"; "`measure` 와 `reset` 은 합쳐서 **1,000개 이하**"
   (P §3). Enforced by `format`. [external: P]
5. **Server time.** [hard] "채점 서버의 제출당 시간 제한은 **1시간**" (P §3). [external: P]
6. **Submission cadence.** [hard] "**제출은 팀당 1시간에 한 번**", none while one is queued or scoring
   (P §3). Enforced by the server. [external: P, S]
7. **Deadline.** [hard] Submissions close 2026-10-30 12:00 KST. [external: S]
8. **Team password.** [hard] "제출 비밀번호는 팀원 모두가 쓰므로 팀 안에서만 공유해 주세요" (S). It
   goes only to the contest API via `work/submit.py`; `.gitignore` keeps `.submit_credentials` out of
   git and the host mirrors. [external: S]
9. **Hosts.** [hard] Ours: zebra, dragon, faraday, hippo, jerry, owl, pegasus, sunfish, tom, with
   `/hdd*/jihoon` and `/data*/jihoon`. Never Parrot; never zebra GPU0 (another user's). Our processes use ≤ ~75% of each host's
   cores, and the host's total load (other users included) stays ≤ its core count. zebra's kernel caps SSH
   connections. [Jihoon, R-20261023-7, R-20261023-8, R-20261023-9, R-20261024-5]
10. **Award attendance.** [hard] "수상 팀은 10월 31일(토) 시상식에 팀원 중 최소 1명이 현장에 직접
    참석해야 합니다" (S). Jihoon's action. [external: S]

## Jihoon's rules (below G0)

11. **Codex lanes only.** [owner] Expansion work goes to parallel Codex lanes (`codex:codex-rescue`); new
    workers are never Sonnet or another model, and a failed Codex job is relaunched on Codex.
    [Jihoon, R-20261023-1, R-20261023-9, R-20261024-2]
12. **Parallel, non-blocking.** [owner] Independent work runs in parallel in the background; never block
    on one experiment. [Jihoon, R-20261023-5, R-20261023-6, R-20261023-9]
13. **Solver-backed search.** [owner] Prefer solver- or simulation-backed search over hand tuning.
    [Jihoon, R-20261023-4, R-20261023-9]

## Boundary cases (what the rules allow)

| Rule | Case | Reading | Status |
|---|---|---|---|
| 6 | Submitting a circuit that may not beat our best | the board keeps "팀별 최고 기록" (S); it costs only the slot | allowed (text: S) |
| G0 | Choosing among valid circuits by their seed-0 score | the official score is seed 0 (P §2.3); P warns of noise, forbids nothing | allowed (text: P §2.3) |
| G0 | Re-drawing the seed-0 sample by reordering simultaneous gates (noise model unchanged, `work/reorder.py`) | ranking "공식 설정으로 계산한 점수를 따릅니다"; P notes third-digit differences near 1e-4 may be statistical; nothing forbids it | allowed (text: P §2.3) |
| 3 | Acceptance just above 0.5 | the gate is pass/fail at 0.5 (P §1.6); ranking uses 1-F, then 2q-gate count (S), so headroom is budget to spend on lower 1-F; exp(-A1) matches the judge within 0.1%, confirm with the seed-0 run | allowed (text: P §1.6; Jihoon, R-20261024-4) |
| — | AI agents doing the work | "LLM 등 생성형 AI 도구를 사용할 수 있습니다" (S) | allowed (text: S) |
| — | Reusing Gidney's open cultivation code | no rule restricts prior code; P cites that literature | allowed (text) |
| 1 | Data-qubit moves and extra cat members | any cx between neighbours is allowed | allowed (text: P §1.1) |
| 1 | Reusing a measured qubit without reset (`h, measure, h` leaves \|±⟩; a Z `measure` leaves \|m⟩) | "측정한 qubit을 `reset` 없이 다시 쓰려면 `h`, `measure`, `h`로 쓰세요"; the `h`s carry no noise or time | allowed (text: P §1.2) |
| 6 | Registering a second team | no rule addresses it; it would double the hourly quota and could take a second podium place | not used: against the contest's spirit, and the quota does not bind (official scores are reproducible locally) |

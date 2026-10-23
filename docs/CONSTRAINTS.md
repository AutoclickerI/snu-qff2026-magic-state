# Constraints

Precedence: hard limits > G0 ([GOAL](GOAL.md)) > Jihoon's project rules. Anything not forbidden is
permitted if it serves G0. Each rule carries its class, `[hard]` or `[owner]`, and its source:
**[external: <source>]** or **[Jihoon, R-<id>]**. A rule from Jihoon's words, in either class, exists
only after Jihoon said yes to it as a rule.
Hard limits are numbered first, then owner rules, in ascending order. A rule the system enforces is one
line naming the enforcement and where its warning appears. `git log -p -- docs/CONSTRAINTS.md` is the
history. `P` = `upstream/snu-qff2026-problem/problem.md` (commit 76fe47c); `S` = the contest site
pages saved in `upstream/hackathon*.html`.

## Hard limits (bind above G0)

1. **Grid and gate set.** [hard] "상하좌우로 이웃한 쌍에만 2-qubit gate를 적용할 수 있습니다", "2-qubit
   gate는 **`cx`만** 사용", no 3-qubit, rotation, custom or conditional gates (P §1.1–1.2). Enforced by
   the `format` gate of `tprep.check`. [external: P]
2. **Judge-processable circuit.** [hard] "허용 gate만 썼더라도 **채점기(xtim)가 처리할 수 있는 회로**여야
   합니다" (P §1.4). Enforced by `class`/`correctness` gates. [external: P]
3. **Acceptance.** [hard] "$p=10^{-3}$에서 acceptance가 0.5 이상" (P §1.6). Enforced by the `acceptance`
   gate. [external: P]
4. **Size.** [hard] "**200 KB, 명령 5,000개 이하**", "`measure` 와 `reset` 은 합쳐서 **1,000개 이하**"
   (P §3). Enforced by `format`. [external: P]
5. **Server time.** [hard] "채점 서버의 제출당 시간 제한은 **1시간**" (P §3). Our circuits score in
   ~2 min. [external: P]
6. **Submission cadence.** [hard] "**제출은 팀당 1시간에 한 번**", and no new submission while one is
   queued or scoring (P §3, S). Enforced by the server, which rejects early submissions. [external: P, S]
7. **Deadline.** [hard] Submissions close 2026-10-30 (금) 12:00 KST (S). [external: S]
8. **Team password.** [hard] "제출 비밀번호는 팀원 모두가 쓰므로 팀 안에서만 공유해 주세요" (S). Never
   print, log, commit or send it anywhere except the contest submission API (`work/submit.py`).
   `.gitignore` keeps `.submit_credentials` out of git. [external: S]
9. **Shared hosts.** [hard] Usable hosts: zebra (this machine), dragon, faraday, hippo, jerry, owl,
   pegasus, sunfish, tom, with `/hdd*/jihoon` and `/data*/jihoon` on them. Never Parrot; never zebra
   GPU0 (another user's). Keep our total CPU use at or below ~75% of a host, and do not starve other
   users' jobs. SSH connection rate is capped by zebra's kernel (it refuses excess connections).
   [Jihoon, R-20261023-7, R-20261023-8; FuriosaNPUChallenge CONSTRAINTS 13]
10. **Award attendance.** [hard] "수상 팀은 10월 31일(토) 시상식에 팀원 중 최소 1명이 현장에 직접
    참석해야 합니다" (S). Jihoon's action, not an agent's. [external: S]

## Jihoon's rules (below G0)

None confirmed yet. Candidates are under "Open questions".

## Boundary cases (what the rules allow)

| Rule | Case | Reading | Status |
|---|---|---|---|
| 6 | Submitting a circuit that may not beat our best | Only "팀별 최고 기록" is shown (S), so a non-improving submission costs only the hour's slot | allowed (text: S) |
| G0 key | Picking among valid circuits by their seed-0 official score | The official score is defined as seed 0, 1e8 shots (P §2.3); P warns the last digit can be noise but does not forbid selection. Report true means alongside | allowed (text: P §2.3) |
| — | Codex, Claude and other AI agents doing the work | "LLM 등 생성형 AI 도구를 사용할 수 있습니다" (S) | allowed (text: S) |
| — | Reusing Gidney's open-source cultivation code (`upstream/magic-state-cultivation`) | No rule restricts prior code; P cites the cultivation literature | allowed (text: no restriction) |
| 1 | Data-qubit moves and X-only "extra" cat members | Any cx between grid neighbours is allowed; moves cost 2 CNOTs each | allowed (text: P §1.1) |

## Not constraints (do not reintroduce)

| Rule an agent introduced | Dropped | Match |
|---|---|---|
| A candidate must have fault_scan c1 == 0 (or < 1e-12) to be eligible | 2026-10-23: the judge does not check c1; it is a diagnostic | `c1 *(==\|<) *(0\|1e-12).*eligib` |
| Resubmit only when the 3-s.f. key improves | 2026-10-23: best-only board makes extra submissions free (rule 6 row above) | `[Rr]esubmit only when` |
| Each lane may use at most 8 CPU processes | 2026-10-23: rule 9 (~75% per host) is the limit | `at most (8\|eight) CPU` |
| zebra is for light commands only (taskset/nice), no heavy builds or checks | 2026-10-23: Jihoon said this is not what was intended (R-20261023-8) | `zebra.{0,20}light commands only` |

## Open questions (recorded risks, never bars)

- Jihoon: keep these as standing rules? (a) "use codex rescue subagent for expansion work" / "use codex
  rescue for every possible lanes in parallel" (R-20261023-1, R-20261023-5); (b) "if anything can be
  done by parallel, do it altogether" and "do basically the parallel work ... instead of blocking on one
  experiments" (R-20261023-5, R-20261023-6); (c) prefer solver/simulation-backed search over hand tuning
  (R-20261023-4). Each is carried out now either way.
- Jihoon: does the ~75% CPU cap (R-20261023-8) apply to every host, or only to zebra? Read now as every host.
- Jihoon: Furiosa's CONSTRAINTS 13 still says zebra is "for light commands only"; update it there too?
- Who renamed the team to 초정밀모델제어학회쨩, and is that final? (Jihoon)
- Who attends the 2026-10-31 16:30 ceremony if we win (rule 10)? (Jihoon)
- Organizers could rescore with other seeds or more shots; P §2.3 says seed 0 is official. Prefer true-mean
  gains so the lead survives either way.

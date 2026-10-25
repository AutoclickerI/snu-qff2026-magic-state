# quantumn v36g 재검토와 최적화 후보 10개

## 판단과 기준 회로

가장 확실하게 놓친 개선은 **균일 Pauli 잡음의 해석적 계산**과 **평가 계획을 찾는 비용의 상각**이다. 두 항목은 구현했고, v36g의 73개 모멘트를 기존 평가기와 대조했다. 물리 회로에서는 **BFLAG의 오류 잔여 조건, CX만 허용하는 합성 언어, 고정된 모듈 경계**가 실제 대회 규칙보다 좁은 탐색 공간을 만든다. 이 공간을 넓히는 구체적인 방법을 제시한다.

이번 검토에서 v36g보다 기대 손실이 낮은 완성 회로를 새로 확인하지는 못했다. 아래 10개는 **동치성과 계산 개선이 검증된 방법 2개, 근거와 중단 조건이 있는 물리·탐색 방법 6개, 경계 평가기 확장 1개, 공식 점수 목적의 계산 배분 1개**다. 각 항목에서 무엇을 보장하는지, 어떤 계산을 더 해야 성능 개선이라고 부를 수 있는지 구분한다.

분석 소스는 `AutoclickerI/quantumn@0ff9423a8e69c13998ab1baf7bf09c8e97558a60`이다. 마감 대조에서 HEAD는 `157d48d12c10dc06bc6bebc79adc3f8c64e6d6a3`로 한 커밋 전진했다. 변경 파일은 `docs/PLAN.md`, `docs/SOTA.md` 두 개뿐이며, 검토한 회로와 평가기는 같다. 공식 judge는 `SNUQuantums/snu-qff2026-problem@76fe47c0324f1c1f8b72a7d55af200e88043b522`로 유지되어 있다. [현재 계획](https://github.com/AutoclickerI/quantumn/blob/157d48d12c10dc06bc6bebc79adc3f8c64e6d6a3/docs/PLAN.md)

| 항목 | 값 | 의미 |
|---|---:|---|
| 기대 손실 최선 회로 | v36g = INTEG2 `integ2_h2` | 이번 검토의 기준 |
| 기대 손실 L | 3.836054467100275e-5 | 로컬 all-orders 평가 재현 |
| noisy acceptance A | 0.5015149656065663 | 기준 0.5 이상 |
| CX / native depth | 320 / 47 | 최종 round R44 |
| detector / 모멘트 | 81 / 73 | 현재 evaluator 표현 |
| sparse omission의 손실 오차 상계 | 1.1781927079201195e-14 | 부동소수점 roundoff는 별도 |
| 최신 저장소 보고 server 점수 | 3.56477280411118e-5 | v36f_h2510_r252072의 선택된 seed-0 표본 |

마지막 행은 저장소가 2026-10-25 10:44 KST에 읽었다고 기록한 board 결과다. 기대 손실과 같은 양의 추정값이지만, 여러 재추출 중 선택된 표본이므로 기대값 개선으로 해석하면 안 된다. v36f의 기대 손실은 3.837606198613569e-5이고 v36g의 이득은 1.551731513294e-8, 약 0.0404%다. [INTEG2 결과](https://github.com/AutoclickerI/quantumn/blob/0ff9423a8e69c13998ab1baf7bf09c8e97558a60/work/lanes/INTEG2/REPORT.md) · [최신 SOTA 기록](https://github.com/AutoclickerI/quantumn/blob/157d48d12c10dc06bc6bebc79adc3f8c64e6d6a3/docs/SOTA.md)

v36g QASM SHA256은 `3daa31ff6ba3dfa0cb5f1960bdb183c1b3e55a3ad81f3119f849712618b13289`다. 재현 기록은 ZIP의 `quantumn_review11/work/lanes/MAIN/sparse/v36g_canonical_sparse_result.json`에 있다.

## 이전 제안에서 달라진 사실

현재 저장소는 이전 검토 이후 42개 커밋이 진행된 상태에서 분석을 시작했다. 다음 결과를 반영해야 한다.

| 기존 방향 | 현재 확인된 결과 | 이번 판단 |
|---|---|---|
| detector basis 탐색 | per-circuit warm search까지 도입 | 새 제안으로 반복하지 않고 탐색 비용을 개선 |
| rank-4 14-T 준비 | 완성된 `t14a`가 L=1.73021e-4, A 약 0.694, 140 CX | 현재 suffix에 붙이는 원안은 재추천하지 않음 |
| A encoder 최적화 | v36c의 고정 창과 CX-only 집합에서 12-CX가 최적 | 검색한 집합 밖의 joint boundary를 명시적으로 열기 |
| B/C 준비 | BFLAG r3와 14개 추가 합성/LNS pipeline 평가 | 동일 제약의 무작정 재실행보다 제약과 목적함수 변경 |
| guard와 작은 gadget | PRECELL, INTEG2가 대규모 singles·swap·timing 탐색 | 무조건 한 개씩 붙이는 확장은 우선순위 낮음 |
| acceptance 확보 | 약 0.018을 손실 2e-8 미만으로 살 수 있음 | acceptance만 얻는 후보는 구체적 사용처가 필요 |

14-T 실패는 단순히 CX 수를 더 줄이면 해결되는 문제가 아니다. 저장소 분석에서 even-parity holder의 오류가 weight-2 class로 남아 이후의 Z 오류와 결합하는 경로가 확인되었다. 15-T 구조의 추가 좌표가 제공하던 fault flagging을 잃은 것이다. 이것은 현재 suffix에서의 실패 근거이며, 모든 미래 14-T 구조의 불가능성 증명은 아니다. [T14 보고서](https://github.com/AutoclickerI/quantumn/blob/0ff9423a8e69c13998ab1baf7bf09c8e97558a60/work/lanes/T14/REPORT.md)

## 후보와 실행 순서

| 번호 | 방법 | 근거의 수준 | 첫 결과물 |
|---|---|---|---|
| 1 | 균일 Pauli의 character 계산과 동일 채널 합치기 | 구현·전체 모멘트 검증 | 기존 평가기에 guarded factor 경로 통합 |
| 2 | 전체 평가 시간에 맞춘 planner 예산 | v36g에서 측정 | warm plan 우선과 상각 기준 |
| 3 | BFLAG F1을 decoder-safe 잔여류로 완화 | 128패턴 완전 검증, 물리 이득 미확인 | 현재 r3 주변의 작은 Pareto 후보 집합 |
| 4 | B/C 준비와 검증 층의 joint Clifford 합성 | 구체적인 미탐색 제약 | 실제로 다른 4–6-wire 합성 증거 |
| 5 | A encoder·decoder·data guard 공동 합성 | 현재 경계의 결합을 코드로 확인 | 충분한 경계 정의와 완성된 창 하나 |
| 6 | 부분 coherence를 가진 C 자원 14개 | 자원 항등식·제한 모델의 유리한 경로 검증 | 실제 readout 비용을 포함한 후보 |
| 7 | 비단조 2–3개 수정과 작은 beam 탐색 | greedy 코드의 탐색 누락 확인 | 명시적인 유한 이웃 집합의 전수 가격표 |
| 8 | 측정 기록의 4-T RCCX 논리 계산 | 19-T 전체 회로의 class·ideal 검사 통과 | 유리한 정책 oracle 후 물리 구현 |
| 9 | 열린 경계 응답 tensor | 선형성에 근거한 평가기 확장 | 기존 128-class 표와 일치하는 일괄 계산 |
| 10 | 물리 회로 family별 valid key 승률/CPU 배분 | 현재 목표와 미세한 평균 차이에 근거 | 같은 호스트의 균형 pilot |

실행 우선순위는 **1·2와 cache 수정 → 7·3·4의 제한된 첫 실험 → 5·6·8·9의 경계·비용 검증**이다. 10은 별도의 짧은 운영 pilot으로 병행한다. 새 solver lane을 오래 실행하기 전에 각 항목의 첫 통과 조건을 만족시키는 것이 중요하다.

## 1 균일 Pauli를 열거하지 않고 해석적으로 계산

현재 `MAIN/sparse/sparse_walsh.py:factors_for`는 2-qubit depolarizing noise의 15개 비항등 Pauli를 모멘트마다 더한다. 그런데 균일 채널의 Fourier character 값은 두 종류뿐이다. 여기서 사용한 수학적 항등식은 알려진 유한군 character 합이고, 새로 확인한 것은 이 코드가 그 구조를 사용하지 않는다는 점이다.

```math
\chi(y)=\begin{cases}
1,&y\in S^\perp,\\
1-\dfrac{2^d}{2^d-1}p,&y\notin S^\perp.
\end{cases}
```

S는 원래 Pauli 변수의 **전체 전파 시그니처**가 이루는 공간이다. kernel, residual detector, observable 비트를 모두 포함해야 한다. d는 전파 전 Pauli 변수 공간의 차원이며, S의 차원은 그보다 작아도 된다. 2-qubit 채널은 d=4이므로 15개 항을 더하는 대신 최대 4개 생성자에 대한 parity 조건으로 계산한다. 전체 시그니처 공간이 같은 독립 채널들은 두 character level을 각각 곱해 하나로 합칠 수 있다.

제공 구현은 확률의 근사적 균일성을 가정하지 않는다. 표현된 확률이 정확히 같아야 하며, 한 ULP라도 다르면 기존 경로로 돌아간다. 정규화가 정확히 1이라고 덮어쓰지도 않는다. 실제 두 level인 `p0+n*p_term`, `p0-p_term`을 보존하고, 영 시그니처 채널의 상수도 유지한다.

**v36g 검증 결과:** 692개 factor가 438개로 줄고, 5,580개 Pauli 항은 1,011개 생성자 조건으로 바뀐다. 81개 영 시그니처 factor를 계산에서 제거하고 173개를 추가로 합쳤다. 73개 모멘트의 최대 차이는 7.66054e-15이며, hardened wrapper의 L 차이는 5.90e-19다. strict guard의 한 ULP 불일치·비정규화·상수 factor 사례 5개도 대조했다.

요소별 누적 시간은 factor 구성 13.278→1.702초, contraction 13.266→10.037초였다. 공통 kernel 2.656초를 포함하고 planning을 제외하면 약 29.20→14.40초다. 이것은 해당 호스트에서의 component 측정이며, 모든 회로·하드웨어의 총속도 2배를 보장하지 않는다. 보장되는 것은 guard를 만족하는 표현의 실수 연산상 동치다. 부동소수점 합산 순서는 달라진다.

**첫 통과 조건:** 현행 evaluator에 원본 fallback을 유지한 채 통합하고, v36f·v36g와 실제 편집 후보들에서 A, N, 모든 모멘트를 비교한다. physical source-channel ID는 별도 보존하여 adjoint 귀속이 사라지지 않게 한다. factor를 합치는 것은 실제 gate를 지워도 된다는 뜻이 아니다.

코드와 기록: `audit/review11/evaluator/channel_algebra.py`, `character_eval.py`, `portable_hardened_validation.json`, `guard_validation.json`, `benchmark_character.json`. [기존 evaluator](https://github.com/AutoclickerI/quantumn/blob/0ff9423a8e69c13998ab1baf7bf09c8e97558a60/work/lanes/MAIN/sparse/sparse_walsh.py)

## 2 더 좋은 계산 순서를 찾는 비용까지 최적화

현재 `compile_best`는 saved basis 두 개에서 각각 1,000개의 새 proposal을 평가한다. acceptance만 필요한 경우도 이 계획 비용을 지불한다. 최적화 기준은 contraction의 work proxy이며, planning 시간과 실제 사용할 모멘트 수를 비용에 넣지 않는다.

| v36g 설정 | planning 시간 | width | work proxy |
|---|---:|---:|---:|
| 기존 2×1,000 proposal | 11.943초 | 8 | 2,113 |
| saved basis만 검사 | 0.316초 | 8 | 2,195 |

약 11.6초를 더 써서 proxy work를 3.7% 줄인 것이다. 1의 factor 개선과 saved basis만 쓰는 설정을 함께 적용한 네 worker 실행은 73개 모멘트를 6.118초에 계산했다. 이 값은 원본 23.219초 실행과 같은 순간의 통제된 A/B benchmark가 아니므로 보편적인 3.8배 수치로 광고할 수 없다. 반면 같은 width에서 2,000번의 새 proposal 계산을 생략했다는 사실은 명확하다.

실제 정책은 `T_plan + 재사용 횟수 × 요청 모멘트 수 × T_contract`를 최소화해야 한다. warm plan을 먼저 만들고, 그래프 변화·측정된 실행 시간·예상 재사용량을 보고 추가 search를 시작한다. 대량 재사용할 그래프는 더 비싼 탐색을 정당화할 수 있고, acceptance-only screen은 작은 예산이 적합하다.

**첫 통과 조건:** 실제 후보 workload에서 총 wall time과 CPU를 비교한다. v36g의 `--basis-trials 0`은 확인된 설정이지만 새로운 그래프의 기본값으로 무조건 고정하지 않는다. 그래프와 의미가 같은 probability-only counterfactual은 plan을 재사용할 수 있다.

기록: `audit/review11/evaluator/warm_only_probe.json`, `portable_warm_only.json`, `portable_warm_only_validation.json`, `PLANNING_AND_RACE.md`.

## 3 BFLAG가 금지한 교정 가능한 잔여 오류 허용

`BFLAG/synth_bc.py`의 F1은 detector가 모두 0인 오류에 대해 B의 X 시그니처 s가 0이도록 강제한다. 여기서 0은 X-stabilizer와 동치인 영류이며, 물리 X 패턴 하나만 뜻하지 않는다. `--soft`나 `robust=False`도 이 F1을 풀지 않는다. 최종 judge가 고칠 수 있는 오류보다 강한 제한이다.

128개 X 패턴을 직접 열거해 syndrome에 따른 single-X correction을 적용했다. 안전한 시그니처는 `{0,9,10,11,12,13,14,15}`다. F1이 허용하는 패턴은 8개, decoder가 고치는 패턴은 64개다. 이 8배는 허용 집합의 크기이며 성능 배수가 아니다. 세 syndrome bit와 parity bit에 대해 조건을 다음처럼 쓸 수 있다.

```math
s_3=s_0\lor s_1\lor s_2.
```

이 원리 자체가 처음 시도되는 것은 아니다. 과거 FRESH의 v23/R45 relaxed-residue 회로는 8.86e-5–1.05e-4로 실패했다. 단독으로 교정 가능한 B 오류가 나중 오류와 결합하는 것이 문제였다. 따라서 이번 제안은 **현재 r3의 작은 창에서, 그 비용까지 넣고 다시 합성하는 것**이다.

현재 LNS 목적함수 `X2+KZ*RZ+KA*acc1`은 proxy에 존재하는 `X2leak`을 사용하지 않는다. F1을 풀면 바로 중요한 비용이 달라지므로 constraint만 변경하면 안 된다. `X2leak`을 진단에 추가하고, 현재 prefix/suffix와의 교차 항까지 포함한 전체 A와 N으로 최종 순위를 매겨야 한다.

**첫 통과 조건:** 현재 r3를 feasible incumbent로 두고 4–6-wire, 3–5-layer 창 하나를 연다. 이상적 endpoint와 전체 회로의 단일 오류 교정성은 유지하는 보수적 첫 탐색으로 시작한다. 후보 Pareto 집합을 전체 all-orders 평가한다. c1=0은 이 첫 실험의 범위를 좁히는 선택이지 대회의 의무는 아니다.

추가로 현재 56-CX 자원의 모든 1·2-CX 삭제 1,596개를 조사했다. 23개가 endpoint를 보존하고 22개가 proxy c1 검사를 통과했지만, 새 accepted residue를 만드는 증거는 없었다. 넓힌 합성 공간에서 이득이 있다는 증명으로 쓰지 않는다.

기록: `audit/review11/physical/correctable_residue_certificate.json`, `resource_deletion_certificate.json`, `REPORT.md`. [F1 코드](https://github.com/AutoclickerI/quantumn/blob/0ff9423a8e69c13998ab1baf7bf09c8e97558a60/work/lanes/BFLAG/synth_bc.py#L141-L164) · [LNS 목적함수](https://github.com/AutoclickerI/quantumn/blob/0ff9423a8e69c13998ab1baf7bf09c8e97558a60/work/lanes/BFLAG/lns3.py#L25-L42)

## 4 B/C 준비와 검증 층을 하나의 Clifford 합성 문제로 만들기

BFLAG는 X-row를 전파하며 CX를 고르고, tick 44의 B→C를 준비 합성 바깥에 고정한다. AENC도 CX-only 합성의 최적성을 증명했다. 이 결과는 비-CSS 중간 상태를 쓰는 Clifford 회로나 준비와 검증을 함께 재구성한 회로의 최적성을 뜻하지 않는다.

구체적인 첫 변화는 **마지막 준비 층들과 B→C를 함께 합성**하는 것이다. 전체 endpoint를 기존과 같은 `|0_L>_B |0>_C^7`로 유지하면, tick 43에서 특정 correlated resource가 반드시 완성되어 있어야 한다는 내부 경계는 없앨 수 있다. 첫 구현은 CX-only로도 가능하다. 합성 창을 tick 44까지 확장하고, 마지막 X 행은 B에서 code column, C에서 0이 되게 한다. 오류 출력은 pre-B→C difference 대신 literal C X bit를 사용한다.

이후 4–6-wire 창의 표현을 full symplectic tableau로 바꾸어 H/S/CX를 허용한다. 공식 native 변환 뒤에도 일반 1-qubit gate로 남는 H/S가 기존 live idle 한 칸을 차지하면, 그 칸의 D1(p) 잡음 강도는 idle과 같다. 새 시간이나 새 idle 비용 없이 합성 언어를 넓힐 수 있는 경우가 있다.

단, 처음 사용하기 전이나 측정 후 비활성인 qubit에 gate를 넣으면 새 잡음을 만든다. RX/MX folding은 실제 parser 규칙을 따라야 하며, 한 global tick이 늘어나면 다른 data도 기다린다. isotropic noise에 대한 단순 frame conjugation은 이득을 만들지 않으므로, entangler 배치나 fault-to-detector map이 실제로 바뀌는지 확인해야 한다.

**첫 통과 조건:** 단 하나의 창에서 경계 Pauli 입력과 classical record map까지 같은 이상적 instrument를 만드는, 물리적으로 다른 회로를 제시한다. native schedule·class·단일 오류를 통과한 뒤 전체 L을 계산한다. 새로운 물리 witness가 없으면 gate alphabet만 늘린 대규모 solver를 시작하지 않는다. 준비 경계 확대와 full-Clifford 언어는 여기서 한 compiler 과제로 다룬다.

[BFLAG 합성기](https://github.com/AutoclickerI/quantumn/blob/0ff9423a8e69c13998ab1baf7bf09c8e97558a60/work/lanes/BFLAG/synth_bc.py) · ZIP `audit/review11/physical/REPORT.md`.

## 5 A encoder와 decoder와 data guard의 경계 공동 최적화

AENC의 최적성은 v36c의 release, D→A 시간, flag가 고정된 7-cell CX-only 집합에 대한 것이다. 최대 16 CX, 35개 pivot 집합, 978개 init 조합까지 조사한 좋은 결과다. 그러나 v36d 이후에는 data guard가 A 영역 내부에 들어온다. 예를 들어 q16은 RX38, CX10→16@39, MX16@40을 쓰고, q14–q20 pair는 tick 40–41을 쓴다.

현재 지침은 새 A encoder가 이 슬롯을 비워 두거나 gadget을 삭제하도록 한다. 이것은 합성 모듈 사이의 약속이다. encoder가 data guard 또는 decoder 일부까지 함께 담당할 수 있다면, 한 기능이 다른 기능의 슬롯을 피해야 한다는 제한이 완화된다. 4의 B/C gate 언어 확장과 구별되는 변경은 **A의 입력·출력·기록 경계를 다시 정의하는 것**이다.

첫 합성 창은 A 준비 후반, q14/q16 guard와 data 접점, flag 또는 decoder의 앞부분을 가로지르는 4–6-wire 영역으로 정한다. 무잡음 accepted quantum/classical map을 보존하면서 그 창의 noisy channel을 개선한다. 외부로 나가는 detector 기록, data Pauli 영향, endpoint frame을 모두 경계에 남겨야 한다.

**중요한 평가기 조건:** 기존 v36c의 128-class A-only 표를 현재 v36g에 그대로 적용하면 안 된다. data–A gate가 영역 안에 들어오므로 A의 출력 오류만으로 충분한지 다시 증명해야 한다. 필요하면 입력·출력 Pauli와 record를 포함한 더 큰 process boundary를 사용한다. 128-class가 계속 충분하다고 가정하고 숫자만 다시 계산하는 것은 안전하지 않다.

**첫 통과 조건:** 새 경계 표현으로 현재 v36g 자체와 작은 실제 수정들의 전체 A,N을 재현한다. 그 다음 encoder·guard·decoder를 동시에 바꾸는 후보 하나를 합성한다. 고정된 각 모듈의 독립 최적성만으로 joint optimum을 추정하지 않는다.

[AENC의 정확한 탐색 범위와 guard 슬롯](https://github.com/AutoclickerI/quantumn/blob/0ff9423a8e69c13998ab1baf7bf09c8e97558a60/work/lanes/AENC/REPORT.md)

## 6 C를 완전한 zero로 만들지 않는 중간 자원 14개

물리적으로 가장 구체적인 새로운 유한 탐색은 C가 가진 정보의 종류를 바꾸는 것이다. C2를 Steane X-stabilizer의 3차원 binary simplex code라 하고, 그 부분공간 V의 차원을 k라 하자.

```math
|R_V\rangle=2^{-(3+k)/2}\sum_{u\in C_2,\,v\in V}|u\rangle_B|u+v\rangle_C,
\qquad CX_{B\to C}|R_V\rangle=|0_L\rangle_B\otimes|V\rangle_C.
```

k=0은 현재 literal-zero C endpoint다. k=3은 독립 logical-zero 두 block의 endpoint다. 그 사이에 **k=1인 7개와 k=2인 7개**, 총 14개의 정확한 계약이 있다. support, stabilizer rank, B:C Schmidt rank `2^(3-k)`를 모두 계산해 확인했다. 현재 파일명 `BFLAG/syn/r3.json`의 r3는 이 k=3을 뜻하지 않는다. 그 자원은 여기서는 k=0이다.

C2의 영이 아닌 codeword는 모두 weight 4다. 따라서 남은 Z(V-perp) 검사는 모든 single X_C/Y_C를 계속 검출한다. 동시에 X(V)는 k=1에서 4개 site, k=2에서 6개 site의 single Z_C를 검출한다. 기존 C가 놓치는 `X_B Z_C`를 이 site에서 잡으면, 해당 B→C fault의 data X leakage가 2p/15에서 p/15로 줄어든다.

변경하지 않은 TERM의 data-side 2차 모델에 이 메커니즘만 넣으면 p=0.001에서 k=1은 약 0.991–1.009e-6, k=2는 1.482–1.493e-6의 이득이 나온다. 이 수치는 **이상적인 C 준비·readout을 가정한 제한 모델의 증거**다. 새 전체 회로의 이득 예측이나 보편적 headroom 상계가 아니다.

실제 병목은 X/Z stabilizer를 함께 읽는 비용이다. GHZ component의 qubit들을 전부 X로 측정하는 것으로는 남은 Z 정보를 보존할 수 없다. C의 현재 위치는 연결성이 매우 낮다. 준비와 joint stabilizer readout, helper, 기존 terminal copy를 함께 route해야 한다. 새 global tick이 생기면 약 1e-6의 유리한 효과가 소진될 가능성이 크다.

**첫 통과 조건:** 14개 이상적 instrument를 현재 v36g 경계에서 가격 평가한 뒤, 유리한 것에 대해 readout까지 포함한 완성 회로를 만든다. 추가되는 CX·measurement·idle과 acceptance를 모두 계산한다. 기존 FRESH의 relaxed B residue는 literal-zero C를 유지했으므로 이 14개 C 상태의 시험과 다르다. 다만 이 방법은 넓은 resource-boundary 아이디어의 구체적인 유한화이며, 새로운 양자정보 원리를 발명했다는 주장은 하지 않는다.

기록: `audit/review11/terminal/finite_contracts.py`, `partial_coherence_contracts.json`, `AUDIT.md`.

## 7 단독으로 나쁜 수정도 함께 평가하는 유한 탐색

현재 `INTEG2/greedy.py`는 원래 기준 회로에서 단독 이득이 양수인 메뉴만 남긴다. 현재 문맥에서 손해인 수정은 `dead`에 영구 등록한다. 정렬된 앞 K개 중 이득이 없으면 뒤의 후보를 보지 않고 끝낸다. `swap.py`는 한 개를 제거한 뒤 한 개를 넣는 일부 경우를 조사했다. 보고서도 더 큰 multi-change 조합의 소진은 추론이라고 명시한다.

따라서 남은 질문은 단순히 random search를 더 하는 것이 아니라 **현재 pruning이 아예 볼 수 없는 조합**이다. 예를 들어 현재 유용한 gadget을 잠시 지워 helper·tick을 비우고, 그 슬롯을 쓰는 두 수정으로 더 큰 이득을 얻는 경로는 monotone single search에서 제외될 수 있다.

먼저 동일 helper, 겹치는 시간창, 공통 fault/detector 경계로 연결된 수정들을 모은다. 크기 2·3인 유한 bundle 집합을 명시적으로 만들고, 단독 gain 부호에 관계없이 전체 A,N을 계산한다. `compose`가 invalid 수정을 조용히 건너뛰지 않게 all-or-nothing bundle을 사용한다. beam을 쓴다면 노드의 dead 결과는 그 문맥의 semantic hash에만 적용한다.

27개 trade를 묶었을 때 손실 상호작용 +1.43e-6이 나온 것은 비용이 비가산적이라는 증거다. 유리한 synergy도 반드시 존재한다는 증거는 아니다. 따라서 첫 결과물은 이득이 보장된 joint가 아니라, **어느 유한 집합을 정확히 다 봤는지 알 수 있는 가격표**다.

**첫 통과 조건:** 한 connected neighborhood의 모든 2·3-edit를 실제로 열거하고 현재 최선보다 낮은 L, 충분한 A를 보이는 완성 회로를 찾는다. heuristic beam의 정체를 전역 소진으로 기록하지 않는다. candidate 수와 시간 예산을 먼저 정하고 첫 집합에서 멈출 수 있게 한다.

[greedy 구현](https://github.com/AutoclickerI/quantumn/blob/0ff9423a8e69c13998ab1baf7bf09c8e97558a60/work/lanes/INTEG2/greedy.py) · [검증과 추론의 범위](https://github.com/AutoclickerI/quantumn/blob/0ff9423a8e69c13998ab1baf7bf09c8e97558a60/work/lanes/INTEG2/REPORT.md)

## 8 측정 기록의 논리식에는 4-T relative-phase Toffoli 사용

이미 Z 측정되어 decohere된 physical control 기록으로 AND를 계산하고 target을 측정한다면, 위상까지 정확한 7-T Toffoli는 필요 이상으로 강한 primitive다. 다음 relative-phase Toffoli는 4 T-type gate와 3 CX로 같은 output bit를 만든다.

```text
H t; T t; CX b,t; Tdg t; CX a,t; T t; CX b,t; Tdg t; H t
```

8개 계산기저 입력을 대조했다. 입력에 따른 phase는 서로 다르므로 coherent Toffoli의 대체품으로 사용할 수 없다. 여기서는 control sector가 이미 측정으로 분리되고 다시 간섭하지 않으며 target도 읽기 때문에 phase가 관측되지 않는다.

v36g의 q12/c310, q19/c3를 control, q18을 target으로 쓰는 완성 회로를 만들었다. 기존 47 tick 안에 들어가고 총 19 T, 323 CX다. 수정하지 않은 공식 judge의 format, class, ideal correctness 검사를 통과했다. 이로써 current 15-T baseline에 nonlinear record logic을 넣는 실제 가능한 primitive가 생긴다. 20-T는 현재 sparse evaluator의 내부 cap이며 대회 규칙은 아니다.

**첫 적용은 성능 후보로 탈락했다.** detector 3과 75의 두 0 조건을 NAND 조건으로 바꾼 이상적·무비용 정책조차 A=0.5028576971064658, L=3.836362258928492e-5로 손실이 3.07791828217e-9 증가했다. 실제 19-T 회로의 100k 표본 acceptance도 0.49862로 기준을 통과하지 못했다. 표본 손실 SEM은 너무 커서 순위 판단에 쓰지 않았다.

다음 pair를 고르기 전에는 Boolean 정책을 먼저 정확히 평가한다. u_i를 `detector_i=0`의 indicator라 하면 임의의 Boolean 함수는 u의 multilinear 다항식으로 표현된다. 그 계수는 Möbius transform으로 얻고, 각 항은 일부 detector만 0으로 고정하는 기존 evaluator 호출이다. 두-bit NAND에서는 다음 항등식만 필요하다.

```math
Z_{\mathrm{NAND}}=Z_{\mathrm{drop}\,a}+Z_{\mathrm{drop}\,b}-Z_{\mathrm{baseline}},
\qquad Z\in\{A,N\},\quad L=N/A.
```

A와 N을 따로 합치며 조건부 L을 평균하면 안 된다. 회로·schedule·다른 모든 detector는 같아야 하고, 부호가 있는 합의 omission 오차도 전파해야 한다. 제공된 generic oracle은 3-bit Boolean 함수 256개를 유리수 연산으로 대조했다. noisy physical carrier는 classical record와 항상 같지 않으므로 이 oracle이 실제 RCCX의 잡음 평가를 대신하지 않는다.

**첫 통과 조건:** 유리한 정책 또는 가치 있는 acceptance trade가 먼저 존재해야 한다. 이후 실제 gate·record 보존·추가 잡음·class·런타임을 가격 평가한다. 현재 첫 pair는 재실행할 이유가 없다.

기록: `audit/review11/physical/rccx_certificate.json`, `rccx_drop3_75.qasm`, `rccx_official.json`; `audit/review11/policy/nand_oracle.json`, `boolean_policy.py`, `boolean_policy_certificate.json`.

## 9 경계 응답표를 열린 tensor로 한꺼번에 계산

AENC는 지역 오류를 128개 class로 분류하고 각 class에 대해 외부 회로를 별도로 평가해 비용표를 만든다. 이 재사용 자체는 이미 구현되어 있다. 다음 개선은 **모든 class를 별도 full contraction으로 계산하는 부분**이다.

충분한 경계 변수 c가 있다면 외부 회로의 acceptance와 unnormalized loss 응답은 선형이다.

```math
A=\sum_c P(c)a_c,\qquad N=\sum_c P(c)n_c,\qquad L=N/A.
```

class bit를 고정하지 않고 열린 index로 남긴 채 외부를 소거하면, 필요한 observable/kernel마다 한 번의 열린 경계 contraction으로 모든 a_c,n_c를 담는 tensor를 얻을 수 있다. 전체 73모멘트 계산이 저절로 단 한 번이 된다는 뜻은 아니다. 공유 contraction이나 batched observable 계산은 별도 구현·검증이 필요하다.

128개 출력 class가 있으므로 128배 빨라진다고 주장할 수도 없다. 열린 b개 bit는 중간 tensor를 크게 만들 수 있다. 또한 5에서 설명한 현재 data–A 접점을 포함하면 경계가 7 bit보다 커질 수 있다. 일반적인 joint 영역에는 단순한 독립 P(c) 대신 입력·출력 Pauli와 record를 포함한 process tensor가 필요하다.

**첫 통과 조건:** 우선 충분성이 이미 확인된 기존 v36c의 128-class 표를 재현한다. 모든 class의 A,N을 대조하고 wall time, peak memory, induced width를 기록한다. 다음으로 v36g의 충분한 경계를 증명한다. 열린 경계가 너무 커지면 일부 class를 batch하거나 factorize하고, 실제 이득이 없으면 기존 표 생성기를 유지한다.

이 항목은 1의 factor 연산 축약과 다르다. 1은 한 contraction 내부의 비용이고, 9는 여러 boundary query 사이의 반복 계산을 줄인다. 5의 물리 설계와도 구별된다. 동일한 물리 후보를 더 빨리 정확히 평가하는 기반이다.

[현재 AENC 표 생성 방식](https://github.com/AutoclickerI/quantumn/blob/0ff9423a8e69c13998ab1baf7bf09c8e97558a60/work/lanes/AENC/evalx.py)

## 10 공식 key를 갱신할 물리 family에 계산 배분

기존 racer의 gate 재정렬, early drop, threshold 전파는 이미 작동한다. 새 제안은 그 내부 정책을 반복하는 것이 아니라 **어느 물리 family를 race할지**의 선택이다. 최종 HEAD의 계획은 v36g를 hourly stem으로 사용한다. v36f와 v36g의 기대 손실 차이는 1.55e-8로 작고, CX는 293 대 320, acceptance도 다르다. 이 정보만으로 어느 쪽이 CPU당 더 자주 공식 key를 이길지 알 수 없다.

family j가 현재 key를 유효하게 이길 확률을 q_j, early drop·setup·완료 검증을 포함한 시도당 기대 CPU를 c_j라 하자. q_j/c_j는 반복되는 stationary IID 시도에서 첫 성공까지의 기대 CPU의 역수이며, 실제 배분의 유용한 추정량이다. 고정된 유한 시간의 전역 최적 정책을 보장하는 식은 아니다. 고정 비용·독립 시도의 성공 확률은 `1-(1-q_j)^n`이고, 시간당 비교는 `-log(1-q_j)/c_j`와 연결된다.

**첫 통과 조건:** 같은 호스트·동일 worker 조건에서 v36f와 v36g에 균형 잡힌 작은 pilot을 배정한다. 유효 acceptance, 공식 3자리 key와 CX tie, setup, drop, 완료 비용을 모두 센다. tail 확률의 불확실성과 permutation 간 상관을 확인하고 별도 variant 집합으로 검증한다. gate 수만으로 runtime을 추정하지 않는다. rare winner가 너무 적으면 강한 family 선택을 유보한다.

물리 연구의 incumbent는 계속 기대 L로 정한다. 이 운영 실험은 공식 표본 key를 갱신할 확률의 문제다. 어떤 family가 더 낫다는 실제 pilot 결과는 이번 검토에서 만들지 않았다.

[현재 race 구현](https://github.com/AutoclickerI/quantumn/blob/0ff9423a8e69c13998ab1baf7bf09c8e97558a60/work/race.py) · `audit/review11/evaluator/PLANNING_AND_RACE.md`.

## 최적화와 함께 고쳐야 할 cache 정확성

`INTEG2/ev2.py:one`의 cache key는 QASM SHA만 확인한다. ordered `data_qubits`와 evaluator version·수치 설정은 빠져 있다. 더 직접적으로 `greedy.py:run_prices`는 같은 이름에 loss가 있으면 hash를 확인하는 함수 자체를 부르지 않는다. 같은 이름으로 후보를 다시 만들면 과거 가격이 남을 수 있다.

공개된 최종 후보가 이 문제로 잘못 평가되었다는 증거는 없다. 현재 v36g는 독립적으로 재평가해 일치했다. 다만 새 탐색을 시작하기 전에 이름 기반 skip을 없애고 **QASM hash + semantic context hash**로 검증해야 한다. context에는 ordered data, detector/frame 해석, p와 cutoff를 정하는 코드, noise/schedule, warm basis, 확장 코드와 런타임 버전이 포함되어야 한다.

제공된 hardened wrapper는 입력 JSON, ordered data, evaluator/frontend/warm/judge subset, 확장 코드와 실행 설정의 hash를 기록한다. 현재 p와 sparse threshold는 hash된 소스의 상수다. 앞으로 런타임 override를 추가하면 실제 값도 key에 넣어야 한다. 이 수정은 10개 아이디어 숫자를 늘리기 위한 항목이 아니라 결과 신뢰성의 전제다.

## 규칙이 허용하는 자유도와 실제 제약

공식 문제와 judge를 기준으로 다시 구분하면 다음과 같다. 팀의 GOAL·CONSTRAINTS도 상당 부분을 이미 인식하고 있다. 문제는 인식된 자유도가 모든 합성기와 평가기의 표현에 반영되어 있지는 않다는 점이다. [공식 문제](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/problem.md)

| 구분 | 실제 조건 또는 자유도 | 이번 후보에 주는 의미 |
|---|---|---|
| hardware | 36개 qubit, 6×6 최근접, 2q는 CX | 모든 새 자원/readout의 routing 비용 포함 |
| 이상적 출력 | accepted noiseless branch가 frame 적용 후 정확한 T_L | A0=1을 강제할 필요 없음 |
| acceptance | p=0.001의 절대 A가 0.5 이상 | A/A0로 바꿀 수 없음 |
| 기록 | DETECTOR 기준 1 가능, POSTSELECT 가능, affine logical X/Z frame 가능 | evaluator가 0 reference만 지원하면 내부 제한 |
| 비선형 논리 | annotation은 XOR 형태 | 8처럼 물리 계산으로 구현하면 실제 비용 필요 |
| gate alphabet | H/S/SX 등 허용 1q gate 사용 가능 | CX-only CSS 합성은 내부 선택 |
| non-Clifford | 실제 class 검사와 정확 checker의 rank 제한 | literal single-time T층이나 20-T cap과 같지 않음 |
| schedule | 일부 qubit barrier 가능, first use 전 idle 없음, reset 직전·마지막 측정 후 예외 | 바뀐 native schedule을 반드시 확인 |
| 출력 위치와 순서 | 7개 위치와 code-order 매핑 선택 가능 | 고정 A/B/C/data 역할은 내부 아키텍처 |
| c1 | 공식 objective는 finite-p loss | c1=0은 강력한 설계 기준이지만 법적 의무 아님 |
| runtime | 공식 제출당 1시간 | 20초/1m-shots는 팀의 보수적 proxy |
| 크기 | 200,000 bytes, 5,000명령, 측정+reset 1,000회 | CX 200개나 creg256 같은 제한은 없음 |

freedom을 이용할 때도 class 통과와 시간 제한은 실제로 확인해야 한다. 대체 evaluator가 계산하지 못한다는 사실과 공식 judge가 금지한다는 사실은 다르다. 반대로 허용 gate로 썼다는 것만으로 xtim이 처리 가능한 것도 아니다.

## 1e-5에 대한 판단

현재 모델에서 작은 숫자 세 종류를 분리해야 한다.

| 수치 | 범위 | 결론 |
|---|---|---|
| 약 7.44545e-6 | 마지막 tick의 D1(4p/5)만 남긴 완화 | 실제 완성 회로의 달성 증거가 아님 |
| 1.1620296389206688e-5 | 필수 직전 잡음까지 포함한 두-tick 완화의 최적값 | true mean에 대한 1.162e-5 유리수 하한 인증 |
| 약 2.274e-5 | helper CX 다음 측정·data idle인 terminal class | 해당 class의 제약이며 모든 회로의 하한은 아님 |

두-tick 증명은 임의의 조건부 pre-tail 상태, residual syndrome, logical bias를 허용한 뒤 실제 decoder observable의 최대 고유값을 구한다. 마지막 output-output CX의 별도 경우, reset·측정·first-use 예외도 다룬다. 독립 D1(p/5) factor와 마지막 D1(4p/5)를 합쳐 유효 q=`p-16p²/75`를 얻고, 64개 syndrome sector와 21개 output pair를 유리수로 검사한다. 증명과 계산 코드는 ZIP `bound/`에 포함했다.

따라서 현재 규칙·STANDARD 모델 아래 기대 손실을 1e-5 미만으로 만든다고 보장할 후보는 없다. 선택된 유한 Monte Carlo 점수는 이 기대값 하한의 적용 대상이 아니다. 또한 하한이 1e-5 아래라고 해도, 그 사실 하나로 그 수준을 달성할 수 있다는 결론은 나오지 않는다.

6번 후보는 현재의 measured-helper terminal class를 유지하므로 그 자체를 1e-5 돌파 경로라고 부르지 않는다. 이 terminal class의 하한보다 낮은 기대 손실을 목표로 한다면 최종 instrument의 class부터 바꾸어야 하며, 그 탐색에는 기존 class floor를 무조건 적용할 수 없다. 특정 영역의 잡음을 완벽하게 만든 ablation 값도 postselection과 상관관계가 달라지는 재설계 전체의 보편적 상계로 쓰지 않는다.

## 이번에 직접 탈락시킨 방향

**Endpoint W:** 마지막 data idle 일곱 칸을 S로 바꾸고 `FRAME_X(1)`을 적용하면 ideal target은 유지된다. 실제 v36g에서는 L이 4.5464344742292077e-5로 약 18.52% 나빠졌다. A, 47 tick, 320 CX는 같다. 고정 CSS decoder의 basin은 모든 target-preserving Clifford에 대해 불변이 아니다. `audit/review11/terminal/endpoint_w_result.json`과 공식 validity 기록을 포함했다.

**부분 rank에 최적 frame 추가:** 기존 v36c의 64-sector 경계표에서 2,824개 proper subgroup에 무료 full syndrome과 임의의 이상적 logical Pauli frame까지 허용해도 full rank를 이기지 못했다. 세 가지 기존 tail 모델 모두 같은 결론이다. 이 결과는 v36c의 해당 경계표에 대한 강화된 음성 결과이고 현재 v36g나 모든 terminal 설계의 불가능성 증명은 아니다. `optimistic_frame_screen.json`을 포함했다.

**첫 RCCX 정책:** primitive와 법적 배치는 유효하지만 현재 pair의 무비용 정책도 L을 증가시켰다. 더 비싼 정밀 계산으로 다시 확인하기보다 다음 정책의 이득을 먼저 검사한다.

## 구현 에이전트의 완료 기준

각 물리 후보는 QASM과 ordered data JSON이 있어야 한다. 실제 native schedule, ideal accepted state와 record 조건, class, noisy acceptance를 검증하고 현재 회로와 같은 의미의 A,N,L을 비교한다. sparse cutoff 오차와 roundoff를 구별하며, 작은 gain을 Monte Carlo 최솟값으로 대체하지 않는다. 운영 key 실험은 공식 rounded key와 tie 규칙으로 따로 평가한다.

각 시도는 성공 조건뿐 아니라 중단 조건을 남긴다. 고정 layout의 실패는 그 layout의 결과로, 유한 집합 전수검사는 그 집합의 결론으로 기록한다. 기존 최선 회로를 포함한 확장 집합의 **수학적 최적값**은 나빠질 수 없지만, 제한된 시간의 solver가 더 나은 회로를 찾아준다는 보장은 없다.

ZIP에는 전체 보고서, 영어 구현 지침, machine-readable `TASKS.json`, 실제 코드와 실험 기록, 공식 judge snapshot, source 검증 및 checksum을 포함했다. `IMPLEMENTATION_AGENT.md`부터 읽으면 실행 순서와 정확한 첫 산출물을 확인할 수 있다. 소스 복사본 88개는 Git blob SHA와 대조했으며 34개는 byte-identical, 54개는 connector가 붙인 마지막 LF 한 바이트를 제거하면 일치했다. benchmark hash와 연결되도록 원래 받은 bytes는 보존했다. 설명되지 않은 source mismatch는 없다.

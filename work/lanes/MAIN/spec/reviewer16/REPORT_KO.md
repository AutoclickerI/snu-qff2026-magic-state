# Reviewer 16 (2026-10-26, on 7f5a18cf / v37d; untrusted, numbers reviewer-reported; zip only in the reviewer's ChatGPT library)

**가장 먼저 고칠 부분은 후보를 선택하는 목적함수입니다. 그다음으로 큰 기회는 자원 준비와 후반 검증 회로 사이에 그어 놓은 경계를 넓히는 데 있습니다.**

코드를 읽는 데서 그치지 않고, 현재 평가기로 `v37d`를 재계산하고, 선택 함수의 반례를 실행하고, 작은 회로와 자원 상태를 열거했습니다. 그 결과 다음 세 가지를 확인했습니다.

1. **현재 선택 함수가 더 나쁜 조건부 손실을 가진 후보를 선택할 수 있습니다.**
2. **“후반 회로만 좋으면 전체 회로도 좋다”는 선별 기준은 저장소의 기존 실험 결과에서도 성립하지 않습니다.**
3. **이미 상당히 넓게 탐색했지만, 좌표별 준비·사용 혼합, 얽힌 non-CSS 논리 자원, 여러 층의 공동 최적화에는 구체적인 미탐색 영역이 있습니다.**

기존 `DIGEST`의 94개 아이디어와 최근 검토 보고서도 대조했습니다. 아래에서 기존 제안의 연장인 것은 그렇게 표시했습니다. “graph state를 써보자”, “더 많은 T를 써보자”처럼 이미 검토한 방향에 이름만 바꿔 붙이지 않았습니다. [기존 아이디어 목록](https://github.com/AutoclickerI/quantumn/blob/ae06514b5979959a36695cd63c2627c585c8b14d/work/lanes/DIGEST/DIGEST.md)

전체 보고서, 재현 스크립트, 계산 결과를 함께 묶었습니다.

**[quantumn_optimization_review_2026-10-26.zip](https://chatgpt.com/library?file_id=libfile_d079514254c48191b277343e5a1e0de0&account_id=personal)**

---

## 검토 기준과 현재 출발점

검토 기준은 [`7f5a18cf`](https://github.com/AutoclickerI/quantumn/tree/7f5a18cf386c850ad8a59e195edb14df087f6457) 커밋입니다. 저장소의 NumPy all-orders 평가기로 현재 `v37d`를 다시 계산한 결과는 다음과 같습니다.

| 항목 | 재현 결과 |
|---|---:|
| 조건부 기대 손실 \(L=1-F\) | \(3.676346632406467\times10^{-5}\) |
| Acceptance \(A\) | \(0.5023547642585299\) |
| CX 수 | 406 |
| Native tick 수 | 48 |
| T 계열 회전 수 | 15 |
| 평가기의 sparse cutoff 생략 오차 상한 | \(3.68\times10^{-14}\) |

마지막 수치는 생략한 kernel 계수에 대한 상한이며, 부동소수점 반올림까지 감싼 엄밀한 수치 구간은 아닙니다. 이번 환경에서는 공식 `xtim`의 1억-shot 채점을 실행하지 않았습니다. 아래의 새 구조들은 **검증된 작은 구성 또는 합성 방법론 후보**이고, 새 완성 회로가 `v37d`를 이겼다는 주장은 하지 않습니다. 재현 결과와 이 구분을 첨부 파일에 기록했습니다.

열 후보의 기준은 다음과 같습니다.

- **재현된 문제:** 현재 구현에서 문제를 직접 확인했습니다.
- **구체적인 실험 근거:** 정확한 작은 구성이나 기존 결과의 순위 역전이 있습니다.
- **연구형 후보:** 수학적 목적과 검증·중단 조건을 명시할 수 있지만, 개선 회로의 존재는 미확인입니다.

## 1. 실제 제약과 스스로 둔 제약부터 구분해야 합니다

사용자의 목적은 `GOAL.md`에 명확합니다. **마감 시점의 공식 점수를 \(10^{-5}\)에 최대한 가깝게 낮추고 1위를 유지하는 것**입니다. CX 수, \(c_2\), 준비 깊이는 그 목적을 위한 중간 지표입니다. [목표 문서](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/docs/GOAL.md)

이 기준으로 보면 다음 구분이 중요합니다.

| 항목 | 실제 지위 | 의미 |
|---|---|---|
| 6×6 격자, 이웃 CX, 허용 gate 집합 | 실제 제약 | 반드시 지켜야 합니다. |
| `xtim` class, 무잡음 correctness, acceptance ≥ 0.5 | 실제 제약 | 자체 평가기가 계산 가능하다는 것만으로 대체할 수 없습니다. |
| 현재 출력 7개의 위치와 순서 | 설계 선택 | 바꿀 수 있습니다. 단, metadata와 decoder의 순서를 정확히 따라가야 합니다. |
| 정확히 15T, 자체 평가기의 20T 제한 | 현재 회로·평가기의 범위 | 대회에 일률적인 20T 제한은 없습니다. 더 넓히려면 실제 class와 시간을 검증해야 합니다. |
| CSS 또는 product-Pauli 자원만 사용 | 탐색 범위 | 얽힌 non-CSS 자원은 별도의 공간입니다. |
| 자원 블록 전체가 완성된 후 사용 시작 | 모듈 경계 | 일부 준비 연산과 일부 data 접촉은 교환하거나 섞을 수 있습니다. |
| 모든 raw measurement bit를 각각 결정적으로 만들기 | 강한 준비 계약 | 필요한 detector parity만 결정적이어도 되는 경우가 있습니다. |
| \(c_1=0\) | 진단 기준 | 공식 요구가 아니며, `GOAL`에서도 이미 non-goal입니다. |
| 현재보다 평가 속도 ≤ 1.5배, 1e6 shots당 ≤ 20초 | 내부 승격·안전 정책 | 외부 서버 제한인 제출당 1시간과 구별해야 합니다. |
| Optimistic tail ≤ \(2.4\times10^{-5}\) | 특정 연구 작업의 목표 | 모든 유의미한 개선의 필요조건은 아닙니다. |

공식 규칙에는 native RX/MX 처리와 idle 비용도 포함됩니다. 준비를 일찍 시작하거나 barrier를 없애는 것이 오히려 idle을 늘릴 수 있습니다. 또한 무잡음 출력은 **이상적 decoder를 적용하기 전부터** 올바른 Steane code space와 목표 상태 조건을 만족해야 합니다. [GitHub](https://github.com/SNUQuantums/snu-qff2026-problem/blob/main/problem.md?utm_source=chatgpt.com) 내부 속도 기준과 실험 중단 기준은 [PLAN](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/docs/PLAN.md), [CONSTRAINTS](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/docs/CONSTRAINTS.md), [WHOLEEND의 작업 지시](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/work/lanes/WHOLEEND/BRIEF.md)에 근거합니다. 내부 사용자 지시를 바꾸는 것은 정책 변경이라는 점도 유지해야 합니다.

### 하한은 맞지만, 하한보다 넓은 불가능성 주장은 경계해야 합니다

저장소의 강화된 하한 계산과 독립 인증서 검증기를 다시 실행했습니다. 2,187개 terminal assignment와 64개 syndrome sector, 총 **139,968개 부등식**이 검증됐습니다.

일반적인 기대 손실 하한은 약

\[
L\ge 1.3657850790536654\times10^{-5}
\]

이고, 측정하는 partner와 마지막 CX를 하는 현재 종류의 더 강한 하한은

\[
L\ge 2.2742699650371855\times10^{-5}
\]

입니다. 따라서 **기대값 \(10^{-5}\)**는 이 모델에서 불가능합니다. 다만 이 기대값 하한을 선택된 단일 finite-shot 점수에 그대로 적용할 수는 없습니다. 또한 낮은 하한이 있다는 사실은 그 하한에 가까운 완성 회로를 만들 수 있다는 증명이 아닙니다. [하한 증명](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/work/lanes/BOUND/PROOF.md)

반면 [`docs/reference/judge.md`의 36–37행](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/docs/reference/judge.md#L36-L37)은 “마지막 data idle은 irreducible이고 어떤 마지막 gate도 더 낫지 않다”고 넓게 적혀 있습니다. 현재 증거에 맞는 표현은 **“시험한 fresh/verified-helper 구현들은 전체 회로를 개선하지 못했다”**입니다. 특정 구현의 실패를 모든 ending의 배제로 확대하면 안 됩니다.

---

## 2. 엄격한 기준으로 고른 최적화 후보 10개

### ① 고정된 \(\tau\)를 버리고 실제 조건부 손실로 최종 후보 선택

**우선순위: 가장 먼저. 현재 구현의 문제를 직접 재현했습니다.**

현재 `campaign.py`는

\[
\tau=3.742321460072\times10^{-5}
\]

를 v37b 기준으로 고정합니다. `greedy_pass.choose()`는 feasible 후보 중

\[
J_\tau=A(L-\tau)=N-\tau A
\]

가 가장 작은 것을 고릅니다. `final_repair`의 승격도 같은 고정 목적에 의존합니다. [고정 기준값](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/work/lanes/MERGE/campaign.py#L10-L20), [실제 선택 함수](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/work/lanes/MERGE/greedy_pass.py#L42)

**이 순위는 \(L=N/A\)의 순위와 다릅니다.** 원래 함수를 그대로 추출해 다음 가상 후보에 실행했습니다.

| 가상 후보 | \(L\) | \(A\) | 고정 \(J_\tau\) |
|---|---:|---:|---:|
| A | \(3.676347\times10^{-5}\) | 0.50235 | \(-3.3142270\times10^{-7}\) |
| B | \(3.678000\times10^{-5}\) | 0.52000 | **\(-3.3447159\times10^{-7}\)** |

함수는 **B를 선택합니다. 그러나 B의 손실은 \(1.653\times10^{-8}\) 더 큽니다.**

이는 특정 물리 회로의 발견이 아니라, 현재 순위 규칙의 실행 가능한 반례입니다. 높은 acceptance가 후속 조합에 유용할 수는 있지만, 그 후보를 최저 손실 후보라고 선택하는 것은 별개의 문제입니다.

**수정 방법은 단순합니다.**

최종 선택은 acceptance 조건을 통과한 집합에서 `loss`를 직접 최소화합니다. 탐색 중 \(J_\tau\)를 쓰려면 매 단계 \(\tau=L_{\text{current}}\)로 갱신합니다. 그러면 \(A>0\)에서

\[
J_{L_{\text{current}}}(C)<0
\iff
L(C)<L_{\text{current}}
\]

가 됩니다. 높은 acceptance의 후보는 후속 결합용 Pareto frontier에 보존하면 됩니다.

**첫 실험:** 이미 저장된 priced 후보를 실제 \(L\)로 다시 정렬하고, 순위가 뒤집힌 후보만 원본 QASM·ordered outputs로 재검증하십시오.

**보장 범위:** 이미 평가한 유효 후보 집합에서 최저 \(L\)을 정확히 선택합니다. 실제 더 좋은 회로가 캐시에 들어 있다는 것까지 보장하지는 않습니다.

---

### ② 최소 \(c_2\)보다 준비 비용을 포함한 구조 frontier를 먼저 최적화

**우선순위: 높음. 저장소 자체에 순위 역전의 증거가 있습니다.**

`WHOLEEND`는 4,797개의 T-only 계약을 얻고도 **최소 \(c_2\)인 여섯 계약만** finite-\(p\) 가격을 매겼습니다. 문서도 높은 \(c_2\) 계약의 전역 최적성을 배제하지 않는다고 명시합니다. [탐색 범위](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/work/lanes/WHOLEEND/MODEL.md#L46-L71)

왜 이게 중요한지는 이미 `ENDSEARCH`의 기록에 나옵니다.

| 구조 | 이상적 round 손실 | 준비를 포함한 grid-free full-prefix 손실 |
|---|---:|---:|
| Square | **\(2.555843124\times10^{-5}\)** | \(3.466519226\times10^{-5}\) |
| Path | \(2.708626922\times10^{-5}\) | **\(3.407979867\times10^{-5}\)** |

**후반 round가 더 나쁜 path가 전체 준비를 포함하면 더 좋습니다.** 이 값들은 저장소에 기록된 실험이며, 이번에 전체 재실행한 값은 아닙니다. 당시 실제 grid 구현은 실패했습니다. 그 결과는 시험한 encoder와 routing의 실패 범위를 보여 줍니다. [기록된 비교](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/work/lanes/ENDSEARCH/REPORT.md#L19-L28)

제안은 path를 다시 시도하라는 데 그치지 않습니다. **구조를 남기는 기준 자체를 바꾸자는 것입니다.**

후보를 tail \(c_2\) 하나로 정렬하지 말고 다음 비용을 함께 보십시오.

- 현재 prefix의 실제 오류 분포에 대한 감도
- 자원 준비의 fault signature와 논리 검증 부담
- 사용 가능한 셀과 native deadline
- Acceptance
- 준비와 routing을 포함한 full \(L\)

**첫 실험:** 기존에 버린 계약 중 준비 stabilizer 구조와 검증 부담이 다른 20–50개를 골라, 동일 prefix와 실제 noisy preparation으로 평가합니다. 단순 CX 수를 준비 비용의 대용물로 쓰면 안 됩니다.

`WHOLEEND`의 \(2.4\times10^{-5}\) gate도 큰 개선을 노린 작업 목표로 읽어야 합니다. 그 gate 실패가 모든 작은 개선을 배제하지는 않습니다. 다만 perfect-resource 값과 full-circuit 값은 postselection 때문에 일반적으로 단조 관계가 아니므로, 두 값의 차이를 엄밀한 가산 예산으로 사용해서도 안 됩니다.

---

### ③ 자원 블록을 좌표별로 준비하면서 준비된 부분부터 사용

**우선순위: 높음. 기존 블록 단위 JIT보다 넓은 합성 공간입니다.**

현재 `SQUARE/synthesize_grid.py`는 A/B/C 전체의 준비 종료와 data arrival의 최댓값으로 하나의 \(R\)을 정하고, 일곱 좌표가 공통된 \(R,R+1,R+2\) 일정에 동작하게 합니다. [실제 준비·접촉 경계](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/work/lanes/SQUARE/synthesize_grid.py#L97-L140)

`ENDSEARCH`는 블록마다 첫 접촉에 맞추는 JIT까지 시험했습니다. 그다음 자유도는 **블록 일부의 preparation CX가 남아 있는 동안, 다른 준비된 좌표를 data와 접촉시키는 것**입니다.

작은 정확한 예를 만들었습니다. 다음 연산을 두겠습니다.

\[
E=\mathrm{CX}(1,2),\quad
L=\mathrm{CX}(D,2),\quad
M=\mathrm{CX}(3,D).
\]

\(E\)는 자원 준비, \(L\)은 data 접촉입니다. 둘은 target이 같아서 commute합니다.

\[
E;L;M=L;E;M.
\]

모든 16개 계산 기저 입력에서 동일함을 확인했습니다. 자원 사용 가능 시점이 주어졌을 때 다음 일정이 가능합니다.

| 방식 | 실행 시점 | 마지막 read |
|---|---|---:|
| 준비를 끝낸 뒤 사용 | \(E@4,\ L@5,\ M@6\) | 7 |
| 준비와 사용을 혼합 | \(L@0,\ E@4,\ M@5\) | **6** |

마지막 data CX와 read 사이의 간격은 유지하면서 전체 종료가 한 tick 빨라집니다.

이 예시는 완성된 Steane 회로의 noisy 개선 증명은 아닙니다. 하지만 **“자원 전체 완료 후 사용”이 일반적인 논리적 필요조건이 아니라는 것**은 보여 줍니다.

**첫 실험:** A 또는 C의 마지막 두 preparation 층과 첫 두 접촉 층을 하나의 작은 합성 구간으로 묶으십시오. 좌표별 release time을 허용하고 전체 stabilizer instrument를 보존합니다. 실제 native frontend에서 종료 시각이나 harmful exposure가 줄지 않으면 그 시도를 중단합니다.

이 방향은 `ENDSEARCH`도 명시적으로 미포함 범위로 구분하고 있습니다. [경계 설명](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/work/lanes/ENDSEARCH/MODEL.md#L72-L77)

---

### ④ 뒤에서 한 층씩 고르는 대신 마지막 두 층을 공동 최적화

**우선순위: 높음. 문서상 greedy 목적의 한계를 작은 정확 열거로 확인했습니다.**

`WHOLEEND`는 final matching과 read basis를 정한 후, 한 층씩 역방향으로 합성합니다. 각 층은 이미 고정된 suffix와의 pair cost를 최소화합니다. **층별 `OPTIMAL`은 전체 꼬리 회로의 최적성을 뜻하지 않습니다.** 저장소도 이 한계를 정확히 적고 있습니다. [합성 목적과 보장 범위](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/work/lanes/WHOLEEND/MODEL.md#L73-L103)

이를 확인하기 위해 4개 encoded block의 작은 모형을 만들었습니다. 층당 가능한 directed matching은 17개이고, 마지막 helper→data를 고정한 채 앞의 두 층을 선택했습니다.

| 선택 방법 | \(c_2\) | \(p=0.001\)에서 모형의 \(L\) |
|---|---:|---:|
| 층별 greedy | 44.8 | \(4.4476749703\times10^{-5}\) |
| 두 층 공동 열거 | **28.7466667** | **\(2.8608363792\times10^{-5}\)** |

Finite-\(p\) 값도 native Pauli channel convolution으로 계산했습니다.

**이 표는 perfect boundary를 공급한 완화 모형입니다.** 실제 prefix와 resource preparation 비용을 포함하지 않으며, `v37d`보다 좋은 새 완성 회로라는 뜻은 아닙니다. 또한 이번 Git snapshot에는 `WHOLEEND` 보고서가 참조하는 원래 검색 소스와 build 일부가 없어, 원래 캠페인을 그대로 재실행한 것은 아닙니다.

**첫 실험:** 기존 tail 후보의 마지막 두 층만 공동 결정하십시오. 같은 층 내부와 두 층 사이의 fault-pair 비용까지 포함하고, 원래 후보를 후보 집합에 남깁니다. 큰 solver가 부담이면 서로 다른 suffix의 Pareto beam을 유지할 수 있습니다.

정해진 유한 집합을 완전히 평가하고 incumbent을 포함하면, **그 집합 안에서 선택 결과가 악화하지 않는 것**은 보장할 수 있습니다. 전체 회로 개선은 noisy preparation을 붙인 뒤 판정해야 합니다.

---

### ⑤ 개별 raw bit 대신 필요한 detector parity와 준비 계약을 함께 합성

**우선순위: 중상. 준비 계약의 강도를 낮추는 연구형 후보입니다.**

`WHOLEEND`는 출력 code stabilizer 6개와 **개별 record operator 22개**를 역전파해 28개 독립 boundary stabilizer를 요구합니다. [현재 경계 계약](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/work/lanes/WHOLEEND/MODEL.md#L98-L103)

그러나 필요한 것은 모든 raw bit를 각각 정해진 값으로 만드는 것보다 약할 수 있습니다. 예를 들어

\[
Hm=b
\]

라는 rank-\(r\) parity 관계와 합법적인 affine logical frame만으로 목표 출력을 보장할 수 있습니다. 개별 측정 결과는 무작위여도 필요한 parity는 결정적일 수 있습니다.

탐색 변수를 다음처럼 묶는 방식입니다.

\[
(\text{tail gates},\ \text{read bases},\
\text{detector row space},\ \text{frame},\
\text{준비 계약}).
\]

이렇게 하면 준비해야 하는 고정 stabilizer 수를 줄여 더 싼 자원을 만들 여지가 있습니다.

**엄격한 한계도 있습니다.** 같은 tail에서 record flip이 전혀 없는 harmful fault는 detector를 줄여도 검출할 수 없습니다. 따라서 detector를 약화하는 행위만으로 고정 tail의 근본적인 오류를 없애지는 못합니다. 이 후보의 이득은 **준비 비용 감소와 전체 재합성**에서 나와야 합니다.

**첫 실험:** 하나의 whole-grid tail에서 22개 bit를 모두 고정하는 계약과, 필요한 parity만 고정하는 낮은-rank 계약 3–5개를 비교합니다. 준비 비용 감소 없이 검출력만 떨어진다면 종료합니다.

이는 현재 PREPFREE와 같은 “충분한 최소 계약” 원리를 whole-grid tail까지 확장하는 구체적인 방법입니다.

---

### ⑥ 세 ancilla의 얽힌 non-CSS 논리 stabilizer 자원을 완전히 열거

**우선순위: 중상. 현재 자원 목록 사이의 빈 공간을 실제로 열거했습니다.**

기존 두 검색은 다음을 다룹니다.

- `ENDSEARCH`: 얽힌 경우를 포함한 **CSS 논리 자원**
- `WHOLEEND`: **product X/Y/Z 논리 자원**

둘을 합해도 모든 얽힌 non-CSS 논리 stabilizer 자원이 되지는 않습니다. [ENDSEARCH 범위](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/work/lanes/ENDSEARCH/REPORT.md#L31-L39), [WHOLEEND 범위](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/work/lanes/WHOLEEND/MODEL.md#L48-L55)

이번에 3개 논리 qubit의 자원을 전부 열거했습니다.

| 자원 목록 | Unsigned stabilizer group 수 |
|---|---:|
| CSS | 16 |
| Product Pauli | 27 |
| 전체 stabilizer | **135** |

Signs와 X/Z readout을 포함하면 8,640개 계약으로, 작은 탐색입니다. 기존 product control의 **1,072/1,728 valid** 결과를 그대로 재현했습니다.

그중 모든 이상적 분기에서 affine frame으로 T를 보존하는 계약은 4,608개였습니다. 얽힌 non-CSS 계약은 3,360개이고, A를 Z, B를 X로 읽는 구조를 유지하면서 세 블록 모두에 얽힌 경우는 32개였습니다. 이 숫자는 물리적으로 비동치인 성능 후보 수와 같지는 않습니다.

구체적인 witness의 논리 stabilizer는 다음과 같습니다.

\[
Z_A X_B,\qquad X_A Z_B X_C,\qquad X_B Y_C.
\]

같은 square 순서로 CX를 적용하고 \(Z_A,X_B,X_C\)를 읽은 뒤

\[
\mathrm{FRAME}_X=1\oplus m_C,\qquad
\mathrm{FRAME}_Z=1\oplus m_A
\]

를 사용합니다. 8개 분기 모두 확률이 \(1/8\)이고, frame 적용 후 Kraus operator는

\[
W=\frac{X+Y}{\sqrt2}
\]

에 비례합니다. \(W|T\rangle=|T\rangle\)이므로 목표 상태를 보존합니다. 행렬 잔차는 \(5.56\times10^{-17}\)였습니다.

여기서 세 qubit은 **encoded logical A/B/C**입니다. Reviewer15의 18-generator physical contract에 남은 세 syndrome gauge를 135개 completion으로 채우는 문제와 다릅니다.

**이 witness를 바로 채택해서는 안 됩니다.** Logical \(X_A\), \(X_C\) 준비 오류는 통과하면서 큰 손실을 냅니다. 실제 준비의 hook와 검증 비용을 계산해야 합니다. 기존 uniform-transversal \(c_2\) 하한을 깨는 주장도 아닙니다.

**첫 실험:** 이 catalog를 실제 geometry·readout 제약과 Clifford equivalence로 줄인 후, 준비 오류 서명과 검증 비용이 유리한 계약만 physical synthesis로 넘깁니다. 목표는 새로운 이름의 자원보다 **더 싼 전체 준비 과정**입니다.

---

### ⑦ Local Clifford와 측정 helper로 흩어진 자원 출력을 직접 준비

**우선순위: 중상. 기존 graph-state 방향을 실제 격자 구성으로 구체화했습니다.**

Graph-state local complementation과 Pauli measurement를 이용하는 원리는 알려져 있습니다. 이번 제안의 핵심은 이를 현재 자원의 약한 계약, 출력 위치, 준비 오류 비용에 맞춰 합성하는 것입니다. [Phys. Rev. A](https://doi.org/10.1103/PhysRevA.70.034302?utm_source=chatgpt.com)

이번에 다음 준비 fragment를 만들었습니다.

| 항목 | 구성 비용 |
|---|---:|
| 사용 영역 | 3×4에서 한 셀을 뺀 11개 셀 |
| Native 준비 | 11 |
| 이웃 CX | 15 |
| CX matching 층 | 4 |
| 출력 1-qubit Clifford | 8 |
| Y read용 추가 Sdg | 3 |
| 측정 helper | 4 |
| 전체 native 층 | 7 |

Steane \(|+_L\rangle\)의 ordered output은

`[2, 3, 13, 6, 15, 8, 12]`

입니다. 출력 셀들만 남긴 물리적 격자는 **세 연결 성분**으로 나뉩니다. 즉 자원 출력 집합 자체가 연결되어 있어야 한다는 가정도 필요하지 않습니다.

16개 측정 분기를 모두 상태벡터로 검증했습니다. 각 확률은 \(1/16\), 명시된 physical Pauli byproduct를 추적한 뒤 fidelity 오차는 최대 \(2.22\times10^{-16}\)였습니다. QASM fragment와 frame mask를 첨부했습니다.

**첫 적용 대상으로 ordinary square의 C를 추천합니다.** 그 순서에서 C 준비의 X 오류는 D→A가 끝난 뒤 A로 전파되고, C의 Z 오류는 B로 복제돼도 B→D의 control Z로 남습니다. 다른 블록이 이상적이고 C 준비가 다른 블록을 건드리지 않는 조건에서는, C에만 국한된 Pauli 오류가 D 출력으로 직접 전파되지 않습니다.

물론 C의 record 오류가 다른 fault를 감추는 오류쌍은 남습니다. 준비 측정의 byproduct도 enclosing circuit의 detector 식에 반영해야 합니다.

**첫 실험:** 실제 C endpoints와 셀 release time을 고정하고 graph/Clifford/helper 합성을 수행합니다. 같은 위치와 deadline에서 기존 준비와 full \(L/A\)를 비교합니다.

15-CX 예시가 기존의 좋은 11-CX encoder보다 우월하다는 주장은 아닙니다. 이 예시의 가치는 **분리된 출력 배치를 짧은 이웃 회로로 준비할 수 있음을 실제 구성한 것**입니다. 기존 C36/C68 방향의 구체적인 확장으로 보아야 합니다.

---

### ⑧ 물리적으로 떨어진 변경도 오류 서명으로 묶고, 선택한 편집을 제거하는 이동 허용

**우선순위: 높음. 현재 탐색 코드의 제한이 명확합니다. 기존 C38/C62의 확장입니다.**

현재 greedy 탐색은 다음 범위에 머뭅니다.

- 최초 기준 회로에서 유리했던 singleton ID를 고정합니다.
- `selected ∪ move`만 만들고, 이미 선택한 편집을 빼는 ejection은 없습니다.
- Acceptance가 모자란 후보 상위 5개에 buyer 하나만 붙입니다.
- `connected`는 같은 physical qubit의 시간 구간이 겹치는 경우로 판단합니다.

이 범위 밖에는 **단독으로 손해지만 조합에서는 이득인 편집, 앞의 선택을 제거해야 가능한 교체, 여러 acceptance buyer가 필요한 변경**이 남습니다. [탐색 코드](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/work/lanes/MERGE/greedy_pass.py#L26-L74), [연결성 정의](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/work/lanes/MERGE/menu.py#L409-L415)

물리적으로 떨어져 있다는 이유로 목적함수가 독립인 것도 아닙니다. 완벽한 Steane 출력의 서로 다른 두 위치에 독립적인 \(D_1(p)\)를 가하면, 각 채널 단독 decoded loss는 0이지만 함께 가한 손실은 정확히

\[
L=\frac59p^2
\]

입니다. 최종 decoder가 두 위치를 결합합니다.

따라서 physical footprint 외에 detector·rotation·logical-output 오류 signature로 interaction graph를 만드십시오. 현 단계의 \(\tau\)를 고정하고

\[
I_{ij}
=
J(C_{ij})-J(C_i)-J(C_j)+J(C)
\]

를 계산하면 강한 상호작용을 찾을 수 있습니다.

**첫 실험:** 3–6개 편집의 ejection·replacement·복수 buyer 조합을 허용하고, 기존 greedy와 동일한 evaluator 호출 예산으로 비교합니다. Incumbent은 보존하고 완성된 조합의 \(L/A\)를 다시 계산합니다. 단독 개선량들을 더해 조합의 성능이라고 판단하면 안 됩니다.

---

### ⑨ Acceptance를 포함한 경계 상태 최적화와 인증 가능한 하한

**우선순위: 연구형. 임의 cutoff를 대체할 수 있는 작은 bound 계산기입니다.**

후보 ⑤가 detector와 준비 계약의 이산 구조를 바꾸는 문제라면, 이것은 **정해진 구조에서 허용 가능한 경계 상태들을 어떻게 비교하고 배제할지**에 관한 방법입니다.

실제 noisy tail의 accepted CP map을 \(\mathcal M_p\), 공식 decoded-fidelity observable을 \(H_{\mathrm{dec}}\)라 두면

\[
E_A=\mathcal M_p^\dagger(I),\qquad
E_N=\mathcal M_p^\dagger(I-H_{\mathrm{dec}})
\]

이고,

\[
L(\rho)=
\frac{\operatorname{Tr}(E_N\rho)}
     {\operatorname{Tr}(E_A\rho)}
\]

입니다.

정당화된 작은 부분공간에서는 generalized eigenvalue 문제로 다룰 수 있습니다. 고정된 data marginal이나 acceptance 조건이 있으면, 목표 \(\tau\)에 대해

\[
\min_\rho \operatorname{Tr}[(E_N-\tau E_A)\rho]
\]

를 SDP로 풀어 해당 가족을 가지치기할 수 있습니다.

제안은 36-qubit dense SDP가 아닙니다. **자유 gauge 1–3개**부터 시작해, 바깥의 고정 회로를 contraction한 작은 effect matrix를 만드는 것입니다.

여기에는 중요한 함정이 있습니다. **Noisy resource를 noiseless stabilizer 계약의 부분공간 안에 강제로 제한하면, 전체 noisy 회로의 하한이 되지 않습니다.**

안전한 첫 구성은 실제 준비 채널 \(\mathcal G_p\)와 무잡음 채널 \(\mathcal G_0\)를 고정하고, 동일한 gauge 입력 \(\sigma\)를 사용하는 것입니다.

- Noisy 목적함수에는 \(\mathcal G_p\)를 반영합니다.
- Ideal correctness에는 \(\mathcal G_0\)와 raw target projector를 씁니다.
- Prefix 통과 후의 조건부 상태라면 tail acceptance는 \(0.5/A_{\mathrm{prefix}}\) 이상이어야 합니다.
- 필요한 prefix record correlation도 남깁니다.

**보장 범위:** 적절한 relaxation과 dual certificate가 있으면 해당 가족에서 \(L<\tau\)가 불가능함을 증명할 수 있습니다. 낮은 relaxed optimum은 합성 가능한 회로의 존재 증명이 아닙니다.

**첫 실험:** 작은 gauge 공간에서 현재 resource의 \(L/A\)부터 재현하고, 작은 density-matrix 계산으로 교차 검증한 뒤 pruning에 사용합니다.

---

### ⑩ 공식 점수가 목적이라면 회로별 점수 분산과 평가 시간도 함께 최적화

**우선순위: 마지막. 기존 C80을 정량화하는 후속 작업이며, true-mean 개선과는 구별해야 합니다.**

`GOAL`의 목적은 공식 finite-shot 점수지만, `PLAN`은 `next_stem`을 최저 기대 손실 회로에 유지하는 정책을 둡니다. **평균이 가장 낮은 회로가 제한된 계산 시간 안에 가장 낮은 official draw를 만들 확률도 항상 최고인 것은 아닙니다.** [목표](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/docs/GOAL.md), [현재 운영 정책](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/docs/PLAN.md)

Accepted shot의 손실을 \(\ell\), shots를 \(M\)이라 하면 대략

\[
\operatorname{Var}(\widehat L)
\approx
\frac{\operatorname{Var}(\ell\mid\mathrm{accepted})}{MA}
\]

입니다.

같은 작은 평균 손실이라도, 드문 loss=1 사건으로 구성된 경우와 loss=\(1/2\) 사건으로 구성된 경우는 표준오차가 약 \(\sqrt2\)까지 다를 수 있습니다. \(L\approx3.68\times10^{-5}\), \(A\approx0.5\), \(M=10^8\)인 단순 예시에서는 약 \(0.857\times10^{-6}\) 대 \(0.607\times10^{-6}\)입니다. **이 값은 예시 분포의 계산이며 v37d의 실측 분산이 아닙니다.**

기존 C80의 “family별 wins/CPU” 제안은 이미 있습니다. 추가할 구체적인 작업은 **회로별 accepted-shot loss 분포와 실제 draw 시간을 측정하는 것**입니다.

**첫 실험:** 이미 유효한 소수 family에 대해 평균, 분산, draw 시간, 현재 key를 이기는 경험적 확률을 함께 측정합니다. 평균이 조금 나빠도 시간당 성공 확률이 높다면 일부 예산을 배정할 여지가 있습니다. 최저 true-mean 회로는 별도로 보존합니다.

Gate-order 재배열의 draw들이 독립이라는 가정이나 Gaussian 극값 근사만으로 개선을 보장해서는 안 됩니다. Pilot에서 우위가 없으면 기존 정책을 유지합니다. 이 항목은 현재 운영 정책의 재검토 제안입니다.

---

## 3. 위 실험 전에 보강해야 할 평가기 문제 두 가지

이 두 가지는 물리적 최적화 후보 수를 채우는 데 쓰지 않았습니다. **탐색 공간을 넓힐 때 결과를 신뢰하기 위한 전제**입니다.

### 출력 metadata가 파일 이름 단계에서 충돌합니다

`ev37.key()`에는 ordered `data_qubits`가 들어갑니다. 그런데 `write_stem()`은 **QASM hash만으로 파일 이름을 만들고 JSON은 최초 한 번만 씁니다.**

같은 QASM에 출력 순서 D1을 쓴 뒤 D2로 다시 호출하면, 두 번째에도 D1의 JSON이 남는 것을 실제 함수로 재현했습니다. `campaign.price()`도 요청 metadata 대신 전역 `E.D`와 비교하는 부분이 있습니다. [관련 구현](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/work/lanes/MERGE/ev37.py#L88-L114)

현재 fixed-D lane이 잘못 평가됐다는 증거는 없습니다. 하지만 출력 위치·순서 탐색을 시작하기 전에 파일 identity부터

`(QASM, ordered outputs, noise/evaluator context)`

를 포함해야 합니다.

### 무잡음 decoded loss=0만으로 공식 correctness를 대신할 수 없습니다

현재 sparse 준비 검사는 \(A_0=1\)과 무잡음 **decoded** loss≈0을 확인합니다. 공식 `exact.py`는 decoder를 적용하기 **전** code space도 검사합니다. [자체 검사](https://github.com/AutoclickerI/quantumn/blob/7f5a18cf386c850ad8a59e195edb14df087f6457/work/lanes/MAIN/sparse/sparse_walsh.py#L101-L107), [공식 검사](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/tprep/exact.py#L250-L267)

v37d의 출력 q6에

\[
H T^4 H=X
\]

를 붙인 19-T 반례를 계산했습니다.

| 검사 | 결과 |
|---|---:|
| Ideal acceptance | 1 |
| Ideal decoded loss | \(1.11\times10^{-16}\) |
| 출력 stabilizer 중 하나 | **−1** |
| 공식 raw code-space 조건 | 실패 |

원래 v37d는 여섯 stabilizer가 모두 +1이었습니다. 현재 incumbent이 invalid라는 뜻이 아닙니다. 임의 합성으로 넓힐 때 잘못된 후보에 계산을 쓰지 않도록, **여섯 noiseless output stabilizer 또는 공식 exact correctness를 먼저 검사**해야 합니다.

## 4. 직접 확인하고 상위 후보에서 제외한 방향

**Barrier를 전부 지우는 단순화는 실패했습니다.**

| 회로 | \(L\) | \(A\) | Tick | Idle 합 |
|---|---:|---:|---:|---:|
| 원본 v37d | \(3.6763466\times10^{-5}\) | 0.50235 | 48 | 216 |
| Barrier 전부 제거 | \(5.5255604\times10^{-5}\) | 0.41905 | 48 | 515 |

기존 지연이 준비를 필요한 시점까지 늦추는 역할을 하므로, global ASAP가 오히려 나쁩니다. 특정 barrier 하나를 제거하면 acceptance가 약 0.000334 늘어나는 경우는 있었지만, 손실 개선은 약 \(6.42\times10^{-12}\)라 의미 있는 fidelity 개선으로 소개하지 않았습니다.

또한 말단 잡음의 비등방성에 맞춰 논리 T축을 살짝 기울이는 방향은, 하한의 최소 지점에서 가능한 이익이 약 \(1.90\times10^{-11}\)뿐이어서 제외했습니다. 두 계산의 근거는 첨부한 재현 자료에 있습니다.

## 5. 내가 권하는 실행 순서

**먼저 ①과 두 평가기 문제를 처리하고 저장된 후보를 재정렬하십시오.** 가장 적은 비용으로 확실하게 선택 정확도를 높일 수 있습니다.

그다음 **②와 ⑧**을 진행하는 것이 좋습니다. 이미 만든 계약과 편집을 더 적절한 기준으로 재검토하므로, 새로운 거대한 회로 가족을 만드는 것보다 빠르게 결과를 얻을 가능성이 있습니다.

구조적 개선은 **③ 좌표별 준비·사용 혼합, ④ 두 층 공동 합성, ⑥ non-CSS 논리 자원, ⑦ 흩어진 C 자원 준비**를 각각 작은 독립 실험으로 시작하는 편이 좋습니다. 처음부터 모두 합쳐 거대한 solver 문제로 만들 필요는 없습니다.

**⑤와 ⑨**는 살아남은 tail을 대상으로 준비 계약과 gauge 자유도를 줄여 가며 적용하고, **⑩**은 대회 점수 운영의 별도 문제로 다루면 됩니다.

내가 보기에 가장 큰 시야 전환은 **완성된 자원 블록과 후반 회로를 따로 최적화하는 현재 경계를 다시 검토하는 것**입니다. 실제 목적에 맞는 최적화 단위는 **현재의 noisy prefix를 목표 T 상태로 보내는 전체 측정 과정이며, 준비 비용·검출 조건·acceptance가 함께 들어가야 합니다.** 그리고 그 탐색을 시작하기 전에, 지금 가진 후보 중 실제로 가장 좋은 것을 고르는 함수부터 바로잡는 것이 순서입니다.

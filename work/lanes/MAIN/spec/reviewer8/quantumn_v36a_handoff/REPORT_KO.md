# quantumn v36a 최적화 재검토와 구현 계획

검토 기준은 quantumn의 커밋 `e438fb60c3da53584fc336fda76bd1fe46a5a6e2`에 있는 v36a이며, 공식 판정기는 `76fe47c0324f1c1f8b72a7d55af200e88043b522`에 고정했다. v35a 검토 이후 이미 구현되거나 진행 중인 방법을 새 아이디어로 다시 세지 않는다.

핵심 판단은 세 가지다. 공개된 검색 코드에는 실제 후보를 탐색하지 못하게 하는 경로가 있다. 현재의 좁은 acceptance 예산에서는 개별 부품의 손실보다 전체 회로의 조건부 손실과 부품 간 상호작용을 최적화해야 한다. 물리적으로 큰 추가 개선은 준비 회로를 더 깨끗하게 만드는 것과 함께 마지막 오류 검출 절차 자체를 바꾸는 방향에서 찾아야 한다.

아래 10개는 보장 범위가 다르다. 검색 도달성, 수학적 동치, 계산 정확성의 보장과 실제 회로 손실 감소를 구분한다. v36a의 기대 손실과 acceptance를 직접 재현하고 공식 유효성 검사를 통과시켰다. 추가로 538개 전체 잡음 채널의 전차수 counterfactual ledger를 완성했다. 새로운 물리 회로의 손실 개선을 측정한 결과는 없으며, 확인된 변형은 accepted 상태를 보존하는 DETECTOR 표현 최적화다.

# 1 검토 기준과 재현 결과

| 항목 | v35b | v36a |
|---|---:|---:|
| 기대 손실 1−F | 4.376021340833061e−5 | 4.1460519583256424e−5 |
| Acceptance | 0.5016883498058476 | 0.500832514460435 |
| CX 수 | 210 | 207 |
| Native ticks | 47 | 47 |
| 증거 수준 | 전차수 계산 직접 재현 | 전차수 계산 직접 재현 |
| 이번 검토의 공식 판정기 실행 | 10⁶ shots PASS | 10⁶ shots PASS |

v35b의 독립 전차수 계산에는 유효 잡음 채널 535개와 acceptance를 포함한 73개 moment를 사용했다. 약 43초가 걸렸고, 희소 kernel 항 생략으로 인한 조건부 손실 오차 상한은 1.20e−14였다. 이 수치는 부동소수점 반올림 오차까지 인증한 상한은 아니다. 공식 판정기 10⁶ shots, seed 0 결과는 손실 4.187120417595471e−5, SEM 7.975248309358251e−6, acceptance 0.501538이었다. 이는 유효성 검사이며 미세한 성능 순위를 판단할 정밀 측정은 아니다.

v36a는 12-CX A 인코더, 기존 A 부분 디코더, q16의 known-X 검사와 guard5 계열을 결합한다. 실제 QASM의 207 CX, DETECTOR 68행, classical register 크기 279를 확인했다. SHA-256은 `8faa1fa93b210c16c5dd9ec2fb8b31057c036f6ec657a33f56c9defda65795cf`로 JSON에 기록된 값과 일치한다. 직접 재현한 값으로 v35b보다 기대 손실이 약 5.3% 낮다. 현재 acceptance 0.50083에서 내부 검증 여유 0.5002를 제외한 가용 예산은 약 0.00063이다.

공개 코드 범위에는 한계가 있다. 현재 설명서는 ST2의 `pop35_*.py`, `knapsack_select.py`, `ledger.py`를 가리키지만 해당 커밋의 ST2 디렉터리에는 이 파일들이 없다. 따라서 아래의 `population.py` 결함이 실제 운영 중인 187개 후보 검색기에도 적용된다고 단정하지 않는다. 먼저 실행 명령과 실제 import 경로를 대조해야 한다.

근거: [현재 계획](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/docs/PLAN.md), [v36a QASM](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/work/lanes/MAIN/v36a.qasm), [v36a 메타데이터](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/work/lanes/MAIN/v36a.json), [현재 회로와 검색기 설명](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/docs/reference/circuit.md).

v36a는 유효 잡음 채널 538개, 73개 moment로 계산했고 kernel 생략 오차 상한은 1.1797970341592153e−14였다. 공식 10⁶-shot seed-0 검사 결과는 손실 3.687352381320931e−5, SEM 7.390664540517275e−6, acceptance 0.501715로 모든 gate를 통과했다. 이 낮은 단일 MC 값으로 기대 손실을 대체하지 않는다. 새 독립 실행 영수증은 ZIP의 `audit/review9_resumed/`에 들어 있다.

# 2 대회 규칙과 스스로 둔 제약

| 항목 | 실제 규칙 또는 판정 동작 | 구현에 주는 의미 |
|---|---|---|
| 하드웨어 | 36개 qubit, 6×6 격자의 상하좌우 이웃 | 물리 CX의 인접성은 반드시 지킨다 |
| 게이트 | 2-qubit은 CX만, 지정된 1-qubit 연산 허용 | SX와 SX†도 허용되지만 판정기 처리 가능성과 시간은 별도 검증한다 |
| 동적 분기 | 조건부 양자 게이트는 금지 | 합법적인 affine Pauli frame과 혼동하지 않는다 |
| 출력 | 순서가 있는 서로 다른 7개 qubit을 자유롭게 지정 | A/B/C/D 고정 역할과 고정 출력 위치는 대회 규칙이 아니다 |
| 무잡음 정답 | accepted branch가 지정된 논리 T 상태여야 함 | noisy score용 최종 정정이 이상적인 준비 오류까지 허용해 주지는 않는다 |
| Acceptance | p=10⁻³에서 0.5 이상 | 여유는 최적화 예산이며, 현재 내부 문서는 이미 0.5002를 사용한다 |
| 이상적 acceptance | 항상 1일 필요 없음 | POSTSELECT로 무잡음에서 무작위인 branch도 선택할 수 있다 |
| DETECTOR | POSTSELECT를 조건으로 결정적이면 됨 | 기준값이 1인 parity, 조건부 결정성도 합법이다 |
| FRAME | X와 Z를 함께 선언하거나 둘 다 생략 | 0 frame만 탐색할 이유가 없다 |
| 비 Clifford 회로 | Clifford를 통과시킨 Pauli 회전축들의 commuting 조건과 실제 xtim 처리 가능성 | 모든 T를 물리적으로 같은 tick에 놓아야 한다는 뜻이 아니다 |
| 크기 | 200,000 bytes, QASM 문장 5,000개, measure+reset 1,000개 이하 | CX 200개 제한이나 classical register 256 제한은 없다 |
| 시간 | 제출당 서버 1시간 | 내부 20초/10⁶ shots 제한은 운영상 여유이지 공식 규정 수치가 아니다 |
| 최종 정정 | 모든 syndrome을 정정하고 점수를 계산 | 최종 syndrome을 추가 postselection 정보로 쓰는 것은 허용되지 않는다 |
| 제출 점수 | seed 0, 10⁸ shots; 유효숫자 3자리 후 gate 수와 제출 시각으로 동점 처리 | 선택한 seed-0 표본과 기대 손실을 별도로 기록한다 |

공식 규칙은 `c1=0`, A/B/C의 독립적인 순수 상태 준비, 단일 전역 round 시각, 모든 qubit을 포함하는 barrier, 20개 이하의 T, 0인 detector 기준값을 요구하지 않는다. 일부는 현재 회로군의 편리한 설계 가정이고 일부는 자체 평가기의 구현 제한이다. 다만 그 제한을 푼 후보도 공식 `format/class/correctness/acceptance` 검사와 시간 제한을 모두 통과해야 한다.

중간 측정 뒤 qubit 재사용도 합법이다. X 측정은 허용된 H–measure–H 형태로 native MX에 접힐 수 있으며 이때의 H에는 추가 시간과 잡음이 붙지 않는다. 임의의 H를 공짜로 취급해서는 안 된다. 처음 사용하기 전의 idle 면제, 측정 뒤 재사용하지 않을 때의 idle 면제도 실제 스케줄러 정의대로 적용해야 한다.

선별한 seed-0 redraw의 낮은 점수는 기대 성능 개선의 증거가 아니다. 공개 규칙은 공식 seed를 고정하지만, 공개 문서에 없다는 이유만으로 모든 외부 공지까지 확인했다고 주장할 수는 없다. 이번 규칙 검토 범위는 공개 문제문과 공개 판정기다.

근거: [공식 문제문](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/problem.md#L110-L375), [QASM 변환](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/tprep/qasm.py), [판정과 frame 처리](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/tprep/check.py), [STANDARD 잡음과 스케줄](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/tprep/noise.py), [무잡음 정답 검증](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/tprep/exact.py).

# 3 10⁻⁵ 미만이라는 하한의 의미

현재 저장소의 마지막 한 tick 완화 모형은 약 7.44545e−6을 준다. 이것은 구현 가능한 전체 회로가 그 값에 도달한다는 증거가 아니다. 마지막 output–helper CX 이전에 필요한 준비 또는 게이트 잡음까지 포함한 별도 인증은 모든 admissible 회로의 기대 손실에 대해 1.162e−5의 하한을 준다.

증명의 핵심은 retained output 7개 각각에서 다음 유효 depolarizing 채널을 독립적으로 추출하는 것이다.

```math
q_{\rm eff}=p-\frac{16p^2}{75}=\frac{9373}{9375000},\qquad p=10^{-3}.
```

이후 실제 판정기의 syndrome 정정과 목표 fidelity 연산자를 모든 syndrome sector와 임의의 조건부 입력 상태에 대해 최적화하면 최소 손실은 0.000011620296389206688…이다. exact rational 비교로 보수적으로 1.162e−5를 인증한다. 마지막 output–output CX의 별도 경우는 더 높은 하한을 갖는다. reset, first-use, 측정 뒤 idle 면제, product-Pauli frame도 증명에서 다룬다.

따라서 현재 판정기 아래에서 기대 손실 10⁻⁵ 미만을 보장하는 합법적 방법을 제시할 근거는 없다. 기존 증명의 채널 추출 또는 판정기 가정에서 반례를 찾아야 이 결론이 바뀐다. 낮게 나온 유한 Monte Carlo 표본은 이 기대값 하한을 반박하지 않는다.

한편 약 2.567e−5라는 마지막 Steane round 비용은 특정 구조의 값이며 보편적 하한과 구별해야 한다. 전자를 넘어설 수 있는 새 terminal instrument를 찾는 일은 여전히 열린 연구 방향이다. 보편 하한에 가까워질 수 있다는 달성 가능성은 아직 증명되지 않았다.

근거: [채널과 인과성 증명](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/work/lanes/MAIN/spec/bound_audit/quantumn_subthreshold_bound_audit/PROOF.txt), [정확한 수치 인증](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/work/lanes/MAIN/spec/bound_audit/quantumn_subthreshold_bound_audit/terminal_bound.json), [현재 목표 정의](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/docs/GOAL.md).

# 4 후보 10개와 우선순위

| 번호 | 방법 | 보장하거나 확인한 것 | 기대 효과 |
|---|---|---|---|
| 1 | 검색 후보가 실제로 생성되고 살아남도록 수정 | 공개 코드의 누락 경로와 register 오류 재현 | 탐색 공간 복구 |
| 2 | 합법적 FRAME과 POSTSELECT를 전차수 평가기에 포함 | 공식 규칙과 자체 evaluator 범위가 다름 | 새로운 회로군 평가 가능 |
| 3 | 기존 전차수 역미분을 현재 회로에 통합 | v36a 538채널 분석과 직접 삭제 검산 완료 | 현재 기준 회로의 정확한 최적화 방향 |
| 4 | 조건부 비율과 상호작용을 반영한 묶음 선택 | 개선 판정식의 수학적 동치 | acceptance 예산 활용 개선 |
| 5 | 전체 잡음 서명이 같은 회로의 기대값 재사용 | 충분조건 아래 기대값 동치 | 중복 평가 감소 |
| 6 | B 플래그를 준비 중간 시점에서 탐색 | 이전 회로의 짧은 Pauli support 후보 | terminal 기하 제약을 벗어난 검사 |
| 7 | 실제로 해로운 오류 쌍에 가중치를 둔 국소 합성 | 기존 clean 합성과 다른 목적함수 | 검출되지 않는 주요 오류 경로 개선 |
| 8 | DETECTOR 기저와 POSTSELECT 표현 최적화 | v36a에서 parity 항 112→85 | 판정기 실행량 감소 가능 |
| 9 | accepted 실행에서 같은 frame 중 빠른 표현 탐색 | accepted-state 보존 항등식 | 느린 sampler 경로 개선 가능 |
| 10 | 마지막 측정 절차부터 역으로 설계 | 완화 bound로 먼저 걸러낼 수 있음 | 기존 Steane round 구조의 비용을 줄일 연구 |

즉시 우선순위는 1의 운영 코드 해당 여부 확인, 3의 v36a 계산, 4의 작은 묶음 비교다. 2와 5는 필요한 범위만 확장한다. 물리 설계는 6과 7의 저비용 판별 실험을 먼저 하고, 10은 구조적 개선을 노리는 별도 연구로 둔다. 8과 9는 기대 손실을 낮추는 회로 변형이 아니라 실행 성능을 위한 동치 변환이다.

## 후보 1 검색 후보의 생성과 생존을 보장하기

**발견.** 공개 `ST2/population.py`는 각 move family의 generator에서 처음 48개만 가져온다. 난수 seed를 바꿔도 family 내부의 49번째 이후 후보는 그 경로에서 생성되지 않는다. generator가 예외를 내면 이미 생성한 유효 후보까지 비운다. survivor 선택은 낮은 손실 후보를 먼저 채운 다음 random 후보를 추가하고 마지막에 잘라서, 주석으로 약속한 diversity가 사라질 수 있다.

격리 재현에서 유효 후보 10개 이후의 예외가 10개 전부를 버렸고, population 12인 구성에서 random survivor 3개와 최고 acceptance 후보가 탈락했다. 이 결과는 실제 운영 검색 로그를 관찰한 것이 아니라 해당 선택 함수를 검증한 결과다.

또한 `core.normalize()`는 header를 `creg c[256]`으로 덮어쓴다. v35b는 c[540]까지 쓰고, v36a도 c[278]까지 쓰므로 이 normalizer를 그대로 통과시키면 유효한 최신 회로가 잘못된 QASM이 된다. output 역할과 round CX까지 고정해서 새로운 배치가 `max(empty)` 또는 잘못된 metadata로 탈락할 수 있다.

**수정.** 먼저 live job의 실제 entry point와 import 경로를 확인한다. 해당 코드가 사용된다면 classical register와 ordered outputs를 입력으로 보존하고, round가 없는 구조도 표현할 수 있는 중간 표현을 둔다. move는 값싼 descriptor를 먼저 열거하고 reservoir sampling 또는 순환 cursor로 고른 뒤 실제 회로를 만든다. 생성 중 예외가 나도 이전의 유효 후보를 보존하고 실패 원인을 기록한다. 최저 손실, 최고 acceptance, 구조적 다양성 자리를 먼저 예약한 후 나머지를 채운다.

**첫 실험.** v36a를 수정 없이 읽고 다시 내보내는 round trip; family의 앞·중간·끝 descriptor 도달성; 선택한 다양성 슬롯의 실제 생존을 확인한다.

**통과 기준.** 원본의 출력 순서, schedule, record, noiseless contract가 보존되고 의도한 모든 유한 descriptor에 선택 가능성이 있어야 한다. 보장되는 것은 누락 경로의 제거다. 더 낮은 손실 발견은 보장하지 않는다. 운영 코드가 이미 수정되어 있다면 이 후보는 바로 종료한다.

근거: [후보 생성과 선택](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/work/lanes/ST2/population.py#L46-L105), [survivor 선택](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/work/lanes/ST2/population.py#L233-L247), [normalizer](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/work/lanes/ST2/core.py#L24-L58).

## 후보 2 합법적인 회로를 전차수 평가기가 읽도록 만들기

**발견.** 현재 `sparse_walsh.prepare()`는 모든 사용 qubit을 덮는 barrier, FRAME/POSTSELECT 없음, 0인 기준값, diagonal accepted kernel, 최대 20개 회전, 이상적 acceptance 약 1을 가정한다. 공식 규칙의 허용 범위보다 좁다. 물리적으로 좋은 후보가 자체 evaluator에서 표현되지 않아 검토 대상에서 사라질 수 있다.

**수정.** 전체 evaluator를 한 번에 다시 만들기보다 affine record 처리부터 추가한다. acceptance parity를 Hm=b로 표현하고, POSTSELECT의 명시적 기준값과 DETECTOR 기준값을 같은 계산에 반영한다. logical X/Y observable에는 각각 frame이 주는 record parity의 부호를 곱한다. 초기 branch 확률도 유지해 실제 noisy acceptance를 계산한다. A/A₀로 정규화한 수치로 0.5 문턱을 검사하면 안 된다.

시간과 잡음은 자체 barrier 가정을 강제로 맞추기보다 공식 QASM 변환과 scheduler의 결과에서 가져온다. barrier를 삭제하거나 추가하는 행위는 idle 위치를 바꿀 수 있으므로 물리적 동치 변환으로 간주하지 않는다. 비대각 kernel과 큰 회전 공간은 별도 단계로 두고, 첫 버전은 affine record 확장만 정확하게 지원해도 된다.

**첫 실험.** 기존 zero-frame 회로의 값이 그대로 나오는지, 동일한 물리를 explicit frame으로 쓰거나 deterministic parity를 POSTSELECT로 쓴 경우 기대값이 일치하는지 확인한다. 이상적 acceptance가 1이 아닌 작은 합법 회로로 절대 acceptance 계산도 검산한다.

**통과 기준.** 예전 회로의 기대값 유지, 공식 exact correctness 통과, 독립 소규모 계산과의 일치가 필요하다. 이 방법의 이득은 설계 자유도를 실제 검색 도구에 복원하는 것이다. 현재 v36a에 무작위 branch 절반 선택을 단순히 더하자는 제안은 아니다.

근거: [자체 evaluator의 제한](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/work/lanes/MAIN/sparse/sparse_walsh.py#L73-L105), [공식 annotation 처리](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/tprep/qasm.py), [정확한 accepted-state 검사](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/tprep/exact.py).

## 후보 3 전차수 역미분으로 현재 회로의 채널별 가격을 계산하기

**기존 방법의 재활용.** 이전 v30f 검토 번들에 같은 전차수 adjoint prototype이 이미 있었다. 따라서 새 알고리즘으로 세지 않는다. 이번에 필요한 변화는 이를 최신 기준 회로의 상시 ledger와 실제 수정 선택에 연결하는 것이다. 이미 전차수 기대 손실 계산기는 있다. 같은 contraction을 잡음 채널마다 다시 실행하기보다 한 번의 forward contraction과 reverse pass로 각 채널의 민감도를 얻을 수 있다. 이것은 저차 fault expansion의 gradient와 다르다. 다른 모든 채널의 유한 p 효과를 포함한 상태에서 해당 채널만 변화시킨다.

채널 c를 다음과 같이 보간한다.

```math
\mathcal E_c(\alpha)=(1-\alpha)\mathcal I+\alpha\mathcal E_c.
```

A를 acceptance, N을 accepted infidelity의 비정규화 numerator로 두면 L=N/A다. 다른 채널을 고정했을 때 A와 N은 α에 대해 affine이므로 α=1에서 구한 derivative로 채널을 이상적으로 만드는 counterfactual을 정확하게 얻는다.

```math
A_{-c}=A-\partial_\alpha A,\quad
N_{-c}=N-\partial_\alpha N,\quad
L_{-c}=\frac{N_{-c}}{A_{-c}}.
```

이번에는 v36a의 538개 채널과 73개 moment 전체를 계산했다. 약 138초가 걸렸고 12개의 직접 counterfactual moment 검산과의 최대 차이는 1.79e−16이었다. 무작위 tensor 검산의 최대 차이는 2.22e−16이었다. 숫자는 해당 환경의 실행 영수증이며 보편적인 speedup 보장이 아니다. 기존 prototype의 positive-factor guard를 유지했으며 factor가 0 이하인 일반 회로에는 그대로 사용하지 않는다.

**구현.** `contract_selector`의 bucket 연산을 tape에 기록하고 reverse pass를 추가한다. factor 값으로 나누는 방식은 0인 factor에서 실패하므로 곱셈과 합산 자체를 미분한다. memory가 큰 지점만 checkpoint한다. acceptance와 decoder observable의 derivative를 N과 A로 합친다.

**완료된 실험과 다음 단계.** 현재 ledger와 직접 삭제 검산은 완료했다. 구현 에이전트는 ZIP의 `v36a_adjoint_72.json`을 사용하고, 기준 회로가 바뀔 때 다시 계산해야 한다. derivative를 실제 gate 삭제의 예측값으로 쓰지 말고, 아래 후보 4와 7의 우선순위로 사용한다.

**통과 기준.** 검산 오차를 공개한 현재 버전 ledger가 만들어져야 한다. 채널을 무잡음으로 만드는 counterfactual은 실제 게이트 삭제가 아니다. 제거 이득들을 더하면 중복 interaction을 이중 계산하므로 총손실 분해로 쓰지 않는다.

근거: [전차수 contraction과 조건부 손실](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/work/lanes/MAIN/sparse/sparse_walsh.py#L177-L239), [현재 integration 과제](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/docs/PLAN.md).

현재 분석에서 제거 이득이 큰 상위 7개는 데이터의 마지막 idle 채널이고, 다음 7개는 마지막 B→D CX의 잡음이다. 마지막 idle 한 채널을 이상적으로 만들면 손실이 약 5.33e−6~5.44e−6 감소하고, B→D CX 한 채널을 이상적으로 만들면 약 2.21e−6~2.26e−6 감소한다. 실제로 실행할 수 있는 변형이 아니며 이 이득들을 합산해서는 안 된다. 이 결과는 terminal instrument 연구를 별도로 둘 근거가 된다.

## 후보 4 조건부 손실과 상호작용으로 묶음을 선택하기

**기존 시도와의 차이.** acceptance knapsack 자체는 이미 v35b를 만들었고 현재 P75도 통합을 담당한다. 새 제안은 knapsack을 다시 하자는 것이 아니라, 개별 Δloss와 Δacceptance의 합으로 조합을 판단하는 경우 그 목적함수를 바꾸자는 것이다. 실제 운영 solver가 이미 같은 계산을 한다면 중복 과제다.

기준 회로의 손실을 L₀라 할 때 A>0인 후보가 개선인지 판정하는 식은 정확히 다음과 같다.

```math
L(C)<L_0\quad\Longleftrightarrow\quad
R_{L_0}(C)=N(C)-L_0A(C)<0.
```

acceptance 비용을 무시한 numerator 최소화도, 서로 다른 분모를 가진 ΔL의 단순 합도 이 식을 대신하지 못한다. 두 수정 i,j의 상호작용은 같은 기준에서 R(i,j)−R(i)−R(j)+R(base)로 측정한다.

**구현.** v36a 위에서 모든 edit를 다시 가격 매긴다. 단독 성능은 나쁘지만 acceptance를 확보하는 수정도 보존한다. 서로 겹치는 edit는 conflict로 처리하고, 상위 edit들의 두 개 및 세 개 교환을 정확히 평가한다. 선형 surrogate는 후보를 제안하는 데만 쓰고 최종 조합의 A와 N은 전차수로 다시 계산한다. λ를 현재 최선의 N/A로 갱신하는 ratio optimization도 사용할 수 있다. 전역 최적 보장은 각 하위문제를 전역적으로 풀었을 때만 주장한다.

**첫 실험.** 현재 사용 가능한 guard 제거, echo, init, C-copy, readout 변경 중 12개를 골라 66개 pair를 비교한다. 기존 선택법이 버린 조합 중 개선이 있는지와 surrogate의 오차를 함께 기록한다.

**통과 기준.** 같은 후보와 같은 평가 예산으로 더 좋은 feasible 조합을 찾거나, additive 가정이 충분히 정확하다는 근거를 얻는다. 최초 목표는 v36a의 실제 전차수 값을 낮추면서 A≥0.5002를 유지하는 것이다. source version이 다른 edit 가격은 같은 표에 더하지 않는다.

근거: [현재 P75와 v35b의 기존 knapsack](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/docs/PLAN.md), [기존 가격과 결과](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/docs/FINDINGS.md#L58-L61), [기대 손실의 분모](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/work/lanes/MAIN/sparse/sparse_walsh.py#L232-L239).

## 후보 5 물리적으로 같은 기대값 계산을 한 번만 하기

**발견.** 공개 population은 QASM 문자열의 hash로 중복을 제거한다. 문자열이 다르다는 사실은 잡음이 포함된 물리 문제가 다르다는 뜻이 아니다. 반대로 이상적인 Clifford 회로가 같다는 사실만으로 noisy score를 재사용하면 틀린다.

**방법.** 각 독립 잡음 채널이 detector parity, 비 Clifford 회전 부호, 최종 logical observable 부호에 주는 전체 서명 분포를 만든다. 이상적인 response kernel K와 모든 채널의 완전한 서명 분포 P₁,…,Pₙ이 같은 공통 좌표계에서 일치하면 다음 기대값도 같다.

```math
\mathbb E\left[K\left(\bigoplus_c S_c\right)\right].
```

이것을 A와 N 모두에 적용해 기대값 cache key를 만든다. 먼저 같은 스케줄의 disjoint gate 순서 변경, detector 기저 변경, record 재명명처럼 동치를 증명하기 쉬운 변환에서 시작한다. 회전 부호와 logical frame, p, 실제 idle 길이, ordered outputs, evaluator 버전도 key의 일부다. 동일한 gate 수나 동일한 c1만으로 cache hit를 인정하지 않는다.

**기존 시도와의 차이.** B/C boundary cache는 특정 exterior를 고정해 한 부품을 빠르게 평가한다. 이 제안은 전체 회로에서 물리적으로 동등한 여러 표현의 평가를 합치는 것이다. 둘을 함께 쓸 수 있다.

**첫 실험.** 한 검색 batch에서 raw-text hash 수와 증명된 physical signature class 수를 비교한다. key 생성 시간까지 포함해 실질적인 중복 절약이 있는지 측정한다.

**통과 기준.** 작은 검증 집합에서 같은 key의 A,N을 직접 계산해 일치시킨 뒤 재사용한다. key 비용이 절약되는 평가 비용보다 크면 중단한다. 기대값 cache로 seed-0 Monte Carlo 점수나 실행 시간을 복사해서는 안 된다. 같은 확률분포도 명령 순서에 따라 난수 소비와 계산 경로가 달라질 수 있다.

근거: [문자열 fingerprint](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/work/lanes/ST2/population.py), [잡음 서명과 factor 구성](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/work/lanes/MAIN/sparse/sparse_walsh.py#L127-L175), [기존 B/C cache의 범위](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/docs/reference/circuit.md).

## 후보 6 B 플래그를 마지막 시점뿐 아니라 준비 중간에서도 찾기

**기존 결과의 정확한 범위.** COMP29의 terminal 검색은 마지막 readout 시점에서 저비용 B 플래그가 없음을 뒷받침한다. 저장소도 이 결과가 earlier instrument까지 닫지는 않는다고 명시한다. 마지막 위치에서 연결하기 어려운 Pauli가 준비 회로를 거꾸로 통과하면 더 작은 support가 될 수 있다.

v35b의 B 논리 Z 대표 하나는 마지막의 Z{6,13,26}에서 tick 34 직후의 Z{12,13,19} 형태로 줄어드는 support 후보를 준다. 마지막 support는 최소 5개 격자 edge를 필요로 하는 반면 {12,13,19}는 2개 edge의 연결 경로다. 이것은 support의 기하학적 가능성이지, 2-CX로 유용한 플래그를 만들었다는 결과가 아니다.

**핵심 주의점.** reset과 측정을 단순한 unitary 역전파로 지나가면 안 된다. v36a에는 q19 reset@33, q13 MZ@36, q12 MZ@37, q6 reset@41이 있다. pullback은 필요에 따라 measurement record가 곱해진 observable 또는 projective instrument로 표현해야 한다. 작은 support가 reset으로 이미 고정된 값이나 기존 detector의 재표현일 가능성도 있다.

**첫 실험.** 기존 terminal 검사는 유지한 채, 몇 개의 중간 cut에 이상적인 추가 meter를 가정한다. 각 meter가 기존 accepted record와 독립적인 정보인지, 어떤 미래 fault를 놓치는지, p=10⁻³에서 N과 A를 얼마나 바꾸는지 계산한다. 미래 검사 전에 B를 체크하고 오랫동안 노출시키는 예전 실패를 반복해서는 안 된다.

**다음 단계와 중단 기준.** 유의미한 이득이 있는 cut만 helper release와 reset을 포함해 국소 합성한다. compute와 uncompute, 읽기까지 포함한 비용을 센다. ideal meter에서도 이득이 없거나 기존 조건과 중복이면 즉시 닫는다. 아직 전체 회로 성능이나 v36a에서의 유효성을 확인한 후보는 아니다.

근거: [terminal B 검색의 한계와 초기 B 검사의 실패](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/docs/FINDINGS.md#L20-L22), [terminal B 기하 증명에 대한 기록](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/docs/FINDINGS.md#L60), [v36a resource schedule](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/work/lanes/MAIN/v36a.json).

## 후보 7 중요한 오류 쌍부터 합성 문제에 넣기

**기존 시도와의 차이.** 저장소는 이미 SAT/CEGAR와 clean B/C 자원 합성을 사용했다. 이 제안의 차이는 solver 이름이 아니라 contract와 손실 함수다. 모든 단일 fault를 독립적으로 깨끗하게 만들거나 모든 pair를 동시에 금지하는 대신, 현재 v36a의 실제 decoder·flag·acceptance 아래에서 큰 손실을 만드는 소수의 오류 경로에 예산을 집중한다.

**방법.** 후보 3의 전차수 ledger와 검증된 pair 분석으로 우선순위 목록을 만든다. 현재 A encoder의 일부, B/C 준비의 짧은 구간, 또는 readout 구간 중 하나만 바꾼다. 이상적인 입출력 instrument와 필요한 detector/frame 의미를 hard constraint로 두고, 중요한 fault pair가 최종적으로 검출되거나 판정기의 정정 가능한 class로 이동하는 것을 soft objective로 둔다.

외부 회로의 모든 잡음을 0으로 놓은 local cleanliness만 평가하지 않는다. 가능하면 현재 exterior가 주는 조건부 상태와 오류 분포를 boundary contract에 넣는다. 새로운 후보를 완전한 회로에 붙여 전차수로 평가한 뒤, 새로 큰 비중을 차지하는 counterexample을 다음 solver 문제에 추가한다. 작은 c1이 있다는 이유만으로 자동 탈락시키는 규칙은 쓰지 않는다.

**첫 실험.** 현재 기준 회로의 상위 20~50개 오류 경로와 작은 수정 window 하나로 시작한다. 고정된 시간 예산 안에서 incumbent를 포함한 후보를 만들어 실제 N,A를 비교한다. 먼저 전차수 ledger가 있어야 하며 예전 v23/v30 pair 가중치를 그대로 가져오지 않는다.

**통과 기준.** soft objective 개선은 screening일 뿐이다. 전체 손실이 줄고 acceptance와 공식 검사가 통과한 경우만 성공이다. 새 구간이 다른 오류 쌍을 만들어 이득을 상쇄하면 다음 counterexample으로 반영하거나 해당 window를 닫는다. 전 pair SAT가 timeout 난 사실을 infeasibility 증명으로 취급하지 않는다.

근거: [기존 in-situ CEGAR와 pair 손실 기록](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/docs/FINDINGS.md#L39-L46), [현재 A flag 조건부 합성](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/docs/PLAN.md), [c1 자동 탈락 코드](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/work/lanes/ST2/population.py#L54-L74).

## 후보 8 DETECTOR 기저와 POSTSELECT 표현을 실행에 맞게 컴파일하기

acceptance가 Hm=b이면 가역인 GF(2) 행렬 U에 대해 Hm=b와 UHm=Ub는 모든 noisy record에서도 같은 조건이다. quantum gate와 measurement를 바꾸지 않으며, 유지한 frame 아래에서 accepted output도 같다.

**현재 v36a에서 새로 확인한 결과.** DETECTOR 68행의 rank는 68이다. 20회의 기본 row XOR로 parity에 등장하는 record 항을 112개에서 85개로 줄였다. 변환 U의 rank도 68이고 새 행 각각이 원래 행의 U 조합과 같음을 직접 검산했다. 따라서 parity 항 수는 약 24.1% 감소한다. 원본과 변경본 모두 공식 10⁶-shot 검사에 통과했고 동일한 seed에서 score, SEM, acceptance가 일치했다. 반복 측정에 근거한 속도 개선은 아직 확인하지 않았다.

**검증 범위.** QASM의 물리 연산을 바꾸지 않고 parity 해집합을 유지했다. 실행은 별도 계산과 일부 겹쳤으므로 두 단발 시간의 차이를 speedup으로 보고하지 않는다. v36a의 deterministic DETECTOR 68개를 명시적 POSTSELECT(0)로 바꾼 경우도 공식 10⁶-shot 검사를 통과했고, 이 실행에서 원본과 score 및 acceptance가 일치했다.

**구현.** 먼저 row basis의 record 항 수와 각 행의 마지막 record 위치를 줄인다. 그 다음 DETECTOR와 명시적 POSTSELECT 사이의 분할을 탐색한다. 1인 기준값도 그대로 운반하고 frame을 고정한다. 단순한 독립 row 삭제와 기저 변환을 구별한다.

**통과 기준.** H,b의 해집합과 accepted frame을 보존하고 공식 검사를 통과해야 한다. 같은 환경에서 warm-up 후 순서를 섞은 반복 timing으로 실행 시간과 분산을 비교한다. POSTSELECT 표현만으로 느린 SX 문제가 해결된다고 가정하지 않는다.

근거: [v36a detector 행](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/work/lanes/MAIN/v36a.qasm), [detector를 마지막 측정 뒤에 삽입하는 변환기](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/tprep/qasm.py#L211-L242), [POSTSELECT 처리](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/tprep/check.py#L273-L311).

## 후보 9 accepted 실행에서 같은 logical frame 중 빠른 표현 찾기

기존 M10은 어떤 record를 받아들이고 어떻게 보정할지 바꾸어 물리적 손실을 줄이는 문제였다. 여기서는 accepted output을 완전히 동일하게 유지하면서 판정기가 계산할 observable의 표현만 바꾼다.

acceptance 조건이 Hm=b이고 fX,fZ가 기존 affine frame이면 임의의 binary row vector u,v에 대해 다음 frame은 accepted record에서 정확히 같다.

```math
f'_X=f_X\oplus u(Hm\oplus b),\qquad
f'_Z=f_Z\oplus v(Hm\oplus b).
```

accepted record에서는 추가 항이 0이므로 noisy output의 보정도 shot마다 동일하다. 그런데 rejected branch의 observable 표현과 record 의존성은 달라질 수 있다. 판정기의 `Plan.tail` 및 sampler가 이 표현에 민감하다면, 같은 결과를 더 싼 경로로 계산할 가능성이 있다.

**첫 실험.** 현재 frame과 detector row 몇 개를 조합해 유한한 후보 집합을 만든다. raw record 개수만 최소화하지 말고 실제 xtim의 처리 경로와 pulled-back observable의 복잡도를 확인한다. FAST 회로와 SLOW SX 회로를 각각 대조군으로 둔다.

**통과 기준.** 실제 accepted frame이 모든 record에서 보존되는지 GF(2)로 증명하고 공식 검사를 통과해야 한다. 같은 물리 기대값이라는 사실은 exact sampler의 처리 가능성과 속도까지 보장하지 않는다. 이번 검토에서는 이 gauge의 timing probe가 실행되지 않았다. plan counters가 전혀 달라지지 않으면 이 경로는 중단한다.

후보 8은 acceptance 조건의 계산을 바꾸고, 후보 9는 점수 observable의 계산을 바꾼다는 차이가 있다. 둘을 하나의 compiler 안에서 조합할 수 있지만 실험은 분리해야 원인을 알 수 있다.

근거: [affine frame과 accepted-state 검사](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/tprep/exact.py#L174-L267), [Plan과 최종 observable](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/tprep/check.py#L251-L270).

## 후보 10 마지막 측정 절차부터 역으로 설계하기

현재의 earlier-round 검색은 준비와 배치를 개선해 기존 terminal 절차에 더 일찍 도달하려는 방향이다. 여기에 별도의 연구로, 마지막 3~5 tick에서 실제로 어떤 오류 정보가 마지막 noisy interaction 뒤까지 살아남는지부터 출발하는 synthesis를 제안한다. 기존 Steane round의 약 2.567e−5 비용을 보편적 하한으로 고정하지 않는 것이 목적이다.

**방법.** retained output 7개, 소수 helper, 과거 classical record를 경계로 잡고 작은 terminal template들을 열거한다. 고정된 template T에 대해 noisy acceptance 효과 A_T와 accepted infidelity 효과 N_T를 만든다. 과거 record와의 상관관계까지 포함하는 경계 상태를 허용한 완화 문제는 다음과 같은 낙관적 하한을 준다.

```math
\min_{\rho\succeq0,\ \operatorname{Tr}\rho=1,\operatorname{Tr}(A_T\rho)\ge0.5}
\frac{\operatorname{Tr}(N_T\rho)}
{\operatorname{Tr}(A_T\rho)}.
```

이 완화가 안전한 pruning bound가 되려면 실제 prefix가 만들 수 있는 모든 경계 상태를 포함해야 한다. helper를 임의로 완벽하다고 고정하거나 이미 측정된 record와의 상관을 버려놓고 보편성을 주장하면 안 된다. 작은 helper 수와 stabilizer block 구조를 이용할 수 있는 경우부터 시작한다. 계산 결과는 물리적 준비 가능성을 증명하지 않는 낙관적 값이다.

**첫 실험.** 현재 suffix와 두세 개의 다른 측정 순서 또는 helper 재사용 template에 대해 마지막의 관측 불가능한 잡음부터 가격 매긴다. 완화해도 현재 목표를 못 이기는 template은 폐기한다. 가능성이 남는 것에만 ideal accepted-state contract를 걸고 국소 SAT/CP-SAT synthesis를 수행한 뒤 실제 prefix와 연결한다.

**성공 기준.** 마지막 CX 수만 줄인 것이 아니라 전체 noisy instrument가 더 좋아져야 한다. prefix의 추가 시간, helper 준비, frame, acceptance, 실제 decoder를 포함한 전차수 손실로 판단한다. 마지막 데이터 잡음을 후속 기록이 볼 수 있다고 가정하거나 판정기의 최종 syndrome으로 추가 postselection해서는 안 된다.

이는 새 구현과 검증이 필요한 연구 제안이다. 성공 확률이나 기대 손실 개선량을 수치로 보장할 수 없다. 다만 현재 준비 회로 최적화로 남는 구조적 비용을 직접 겨냥하며, 비싼 전체 배치 작업 전에 실패할 template을 거르는 방법이 구체적이다.

근거: [현재 terminal 구조](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/docs/reference/circuit.md), [Steane 계열의 비용과 이전 architecture 실험](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/docs/FINDINGS.md#L29-L46), [마지막 잡음의 보편 하한](https://github.com/AutoclickerI/quantumn/blob/e438fb60c3da53584fc336fda76bd1fe46a5a6e2/work/lanes/MAIN/spec/bound_audit/quantumn_subthreshold_bound_audit/PROOF.txt).

# 5 구현 에이전트에게 넘길 실행 순서

1. 기준을 고정한다. 위 커밋과 v36a QASM SHA-256, 공식 판정기 커밋, ordered outputs를 receipt에 넣는다. 패키지의 독립 재현값과 영수증을 기준으로 삼고, 다음 incumbent가 나오면 다시 계산한다.
2. live search의 entry point를 찾는다. 공개 legacy 코드의 결함과 실제 운영 코드의 결함을 구분한다. 최신 회로를 round trip하지 못하는 도구를 search frontier에 연결하지 않는다.
3. 완료된 538채널 ledger와 직접 삭제 검산을 P75에 연결한다. 다음 incumbent에서 같은 분석을 자동으로 다시 실행한다.
4. 작은 acceptance portfolio를 같은 기준 회로에서 가격 매긴다. 적어도 pair interaction을 확인하고 상위 조합을 전차수로 재계산한다.
5. 빠른 동치 컴파일 실험을 독립적으로 수행한다. detector basis, DETECTOR/POSTSELECT 분할, frame gauge를 각각 비교한다. 물리 기대값, seed-0 draw, runtime을 다른 열에 기록한다.
6. B 중간 cut과 가중 fault-pair 합성에는 먼저 optimistic oracle을 적용한다. 독립적인 정보나 실제 감소 가능성이 확인된 경우만 물리 gate를 붙인다.
7. terminal instrument 연구에는 별도 계산 예산을 준다. 기존 earlier-round 작업과 같은 개선을 이중으로 보고하지 않는다.

각 후보의 최소 receipt에는 parent와 candidate의 QASM hash, 변경한 물리 연산과 schedule, record/frame 변환, 공식 checker 버전, A,N,L, 계산 오차 범위, CX/ticks, exact correctness, sampler 속도, MC seed·shots·SEM을 포함한다. 파싱 실패, evaluator 미지원, 공식 class 실패, acceptance 실패, 단순한 성능 열세를 서로 구분해 기록한다.

성능 승격은 실제 기준 회로의 기대 손실 감소와 공식 유효성으로 판단한다. 10⁶-shot 한 번의 score는 정밀 순위에 쓰지 않는다. A가 0.5 근처이면 짧은 MC의 acceptance 흔들림도 별도로 확인한다. kernel cutoff 오차 상한과 floating-point 검증은 구분한다. 기대값이 같은 표현끼리는 기대값을 재사용할 수 있어도 공식 seed-0 결과와 runtime은 새로 측정한다.

첫 목표는 4.14605e−5라는 보고값을 재현한 뒤 그 값을 확실하게 낮추는 것이다. 곧바로 10⁻⁵를 목표로 모든 준비 회로를 갈아엎는 계획에는 근거가 부족하다. 준비 회로 개선과 terminal 구조 개선의 기여를 따로 측정해야 한다.

# 6 이번 검토에서 확인한 것과 남은 것

**확인한 결과**

- v35b와 v36a의 전차수 기대 손실과 acceptance를 직접 재현했고 각각 공식 10⁶-shot 검사에 통과했다.
- v36a의 538개 전체 채널과 73개 moment의 adjoint ledger를 완성했다. 12개 직접 counterfactual moment 검산과의 최대 차이는 1.79e−16이었다.
- 공개 population의 앞 48개 제한, generator 예외 시 이전 후보 삭제, diversity slot 탈락을 실제 소스의 AST를 추출해 격리 재현했다.
- v36a의 유효 QASM에서 register를 256으로 바꾸면 c[275]에서 parser가 거부함을 재현했다. 원래 선언은 279이고 최대 사용 index는 278이다.
- v36a의 QASM SHA-256과 gate/record 구조를 확인했다.
- v36a의 detector basis 변환에서 rank 68과 변환 행렬을 독립적인 Python/JavaScript로 검산했고 parity 항 112→85를 얻었다.
- 원본, detector basis 변경, explicit POSTSELECT 표현이 모두 공식 검사에 통과했다. 해당 seed와 shots에서 score, SEM, acceptance도 일치했다.
- 현재 공개 규칙과 판정기에서 A₀=1, c1=0, zero frame 등 자체 제한을 요구하지 않음을 확인했다.
- 실제 실행에 사용한 evaluator와 공식 판정기의 핵심 파일은 GitHub에서 읽은 Git blob SHA와 일치함을 검증했다.

**확인하지 않은 결과**

- 새로운 물리 gate 변형이 v36a보다 낮은 기대 손실을 갖는다는 측정.
- detector 항 감소가 가져오는 반복 측정 기반 runtime 개선.
- frame gauge로 SLOW SX가 FAST가 된다는 결과.
- 중간 B observable이 독립적이고 유용한 physical flag가 된다는 결과.
- 보편 하한 1.162e−5가 실제로 달성 가능하다는 증명.
- 공개 저장소에 없는 현재 운영 pop35/knapsack 엔진에도 legacy 코드의 결함이 존재한다는 주장.

완성된 ZIP에는 이 보고서, 구현 우선순위, 고정한 원본 회로, 실제로 실행한 evaluator와 공식 판정기 소스, source hash 검증, 전체 adjoint 결과, detector 변환 코드, search 도달성 재현 코드 및 공식 검사 영수증이 들어 있다. 설치된 Python 환경이나 private credential은 포함하지 않는다.

기존 v35a handoff는 현재 저장소의 `work/lanes/MAIN/spec/reviewer7/quantumn_v35a_implementation_handoff/`에 보존되어 있다. 이번 ZIP의 기본값과 실행 결과는 v36a이며, 기존 결과와 섞어 사용하지 않는다.

# 7 DETECTOR 기저 변환의 재현용 최소 코드

다음 코드는 UTF-8 QASM의 DETECTOR row에 가역적인 XOR 변환만 수행하는 참고 구현이다. rank와 row-space certificate를 만들고, 공식 checker를 통과한 후에만 산출물을 사용해야 한다. 아래 Python 구현을 v36a에 실행했고 독립적인 JavaScript 계산과 같은 receipt를 얻었다. 생성된 QASM도 공식 판정기에 통과했다. explicit frame과 POSTSELECT 분할을 다루는 일반 compiler는 별도 구현이다.

```python
from pathlib import Path
import json
import re

def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row.bit_length() - 1
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
    return len(pivots)

def compress_detector_basis(qasm):
    lines = qasm.splitlines()
    positions = [
        i for i, line in enumerate(lines)
        if re.match(r"^\s*//\s*DETECTOR\b", line)
    ]
    original = []
    for i in positions:
        mask = 0
        for bit in re.findall(r"c\[(\d+)\]", lines[i]):
            mask ^= 1 << int(bit)
        original.append(mask)
    rows = original.copy()
    transform = [1 << i for i in range(len(rows))]
    operations = 0
    while True:
        best = None
        for i in range(len(rows)):
            for j in range(len(rows)):
                if i == j:
                    continue
                gain = rows[i].bit_count() - (rows[i] ^ rows[j]).bit_count()
                if gain > 0 and (best is None or gain > best[0]):
                    best = (gain, i, j)
        if best is None:
            break
        _, i, j = best
        rows[i] ^= rows[j]
        transform[i] ^= transform[j]
        operations += 1
    assert rank(transform) == len(rows)
    for i, mask in enumerate(transform):
        check = 0
        for j, row in enumerate(original):
            if (mask >> j) & 1:
                check ^= row
        assert check == rows[i]
    # This minimal emitter is for a full-rank basis; general dependent rows
    # need separate treatment of zero rows and nonzero affine references.
    assert rank(original) == len(rows)
    assert all(rows)
    for pos, row in zip(positions, rows):
        bits = [str(i) for i in range(row.bit_length()) if (row >> i) & 1]
        lines[pos] = "// DETECTOR " + " ".join("c[" + i + "]" for i in bits)
    receipt = {
        "rows": len(rows),
        "rank": rank(rows),
        "terms_before": sum(row.bit_count() for row in original),
        "terms_after": sum(row.bit_count() for row in rows),
        "row_xors": operations,
        "transform_decimal": [str(row) for row in transform],
    }
    return "\n".join(lines) + "\n", receipt

# Use a separate output stem; keep the original QASM and metadata as control.
# qasm = Path("v36a.qasm").read_text(encoding="utf-8")
# transformed, receipt = compress_detector_basis(qasm)
# Path("v36a_detector_basis.qasm").write_text(transformed, encoding="utf-8")
# Path("detector_basis_receipt.json").write_text(
#     json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
# )
```

v36a에서 기대하는 대수적 receipt는 rows=68, rank=68, terms_before=112, terms_after=85, row_xors=20이다. 판정기가 사용하는 frame이 원본과 accepted record마다 같다는 조건도 별도로 보존해야 한다. detector basis 동치는 score의 Monte Carlo 표본이 반드시 같은 난수 소비 순서를 가진다는 뜻이 아니다.

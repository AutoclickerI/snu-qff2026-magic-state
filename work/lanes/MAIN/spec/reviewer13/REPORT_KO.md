# Reviewer 13 (pasted by Jihoon 2026-10-25 16:47 KST; zip and code stayed in the reviewer sandbox)

## 결론: 먼저 고칠 곳은 후보 선별 기준과 평가기의 중복 계산입니다

저장소의 코드, 기존 리뷰, 실패한 실험 기록, 최신 계획을 함께 확인했습니다. 그중 **지금 가장 먼저 적용할 만한 것은 ① 짧은 acceptance 검사에 의한 오탈락 제거, ② 공식 순위 규칙에 맞춘 threshold 계산, ③ 73개 관측량을 통합하는 평가기 최적화**입니다.

물리 회로에서는 **C 자원의 허용 부분공간을 넓히는 방향**에서 구체적인 새 후보를 만들었습니다. 기존 회로의 reset 기저 한 곳을 바꾸어 새로운 자원을 준비할 수 있습니다. 이 후보는 CX를 하나 줄이고 acceptance를 높이지만, 단독 기대 손실은 현재 기준보다 조금 나쁩니다. 따라서 추가 검출 장치와 결합할 출발점으로 보는 것이 맞습니다.

아래 10개는 근거 수준을 구분했습니다. **확인된 선별 오류, 실제 측정한 계산 가속, 수학적으로 검증한 계약, 추가 실험이 필요한 연구 제안**을 같은 수준의 성과로 취급하지 않았습니다. 아직 새로운 공식 \(10^8\)-shot 실행으로 우승 점수를 확인한 결과는 아닙니다.

### 검토 기준

수치 실험과 코드 비교는 `806b481`에 고정했습니다. 마지막으로 확인한 커밋은 `49f1eac`이며, 그 사이 기준 회로 `v36h`, sparse evaluator, `race.py`, `promote.sh`는 바뀌지 않았습니다. 이미 통합된 reviewer12 개선과 진행 중인 P91/P92 작업은 새 제안으로 다시 세지 않았습니다. [최신 계획](https://github.com/AutoclickerI/quantumn/blob/49f1eacec54c06bfff09d9ea6df604941dcdb43c/docs/PLAN.md)

이번에 재현한 기준값은 다음과 같습니다.

| 기준 회로 | 기대 손실 \(L\), 낮을수록 좋음 | Acceptance \(A\) | CX | T | Native ticks |
|---|---:|---:|---:|---:|---:|
| `v36h` | \(3.81547332248\times10^{-5}\) | 0.501641504948 | 327 | 15 | 47 |

여기서 \(L\)은 **accepted shot에 조건부인 기대 손실**입니다. 계획 문서의 선택된 공식 표본 점수 약 \(3.53131\times10^{-5}\)와 구별해야 합니다. 공식 noisy acceptance 기준은 \(A\ge0.5\), 팀의 내부 exact-A 여유 기준은 0.5002입니다. 공식 규칙과 judge도 별도로 확인했습니다. [공식 문제](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/problem.md) · [공식 judge](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/tprep/check.py)

## 후보 10개 한눈에 보기

| # | 방법론 | 개선 대상 | 현재 확보한 근거 | 우선순위 |
|---|---|---|---|---|
| 1 | 짧은 acceptance 검사와 최종 합격 판정 분리 | 좋은 후보의 오탈락 | 코드 경로와 실제 실패 receipt 확인 | 즉시 |
| 2 | 공식 순위 규칙에서 threshold 직접 계산 | 승리 가능한 후보의 잘못된 가지치기 | 구체적 반례와 유한 경계 검증 | 즉시 |
| 3 | 73개 관측량의 selector 통합 | exact 평가 속도 | 두 회로에서 수치 일치, 로컬 CPU **1.63–1.78배** | 즉시 |
| 4 | Race 평균을 exact \(A,N\)에 고정 | 단위 계산량당 성공 확률 | 통계 모형에서 개선, 실제 race 검증 필요 | 높음 |
| 5 | \(C_2\) 밖의 C 자원과 Bell readout | acceptance·CX·추가 검출 여력 | 실제 36큐비트 후보와 전체 잡음 평가 | 물리 실험 1순위 |
| 6 | 논리 coset을 중복 표식으로 추적 | 새로운 B/C 자원 계열 | 이상적 분기 항등식 검증 | 연구 |
| 7 | 국소 채널 Choi SDP를 합성 목표로 사용 | 탐색 방향과 종료 근거 | 정식화와 feasibility 검증, SDP 미실행 | 연구 |
| 8 | 평균과 점수 분포를 함께 고려해 물리 후보 보존 | 공식 최종 key 획득 확률 | 수학적 반례, 실제 회로 효용 미측정 | 조건부 연구 |
| 9 | 중단된 race의 chunk 저장·재개 | 이미 계산한 결과의 폐기 방지 | 저장 유틸리티와 합성 데이터의 bit 일치 | 높음 |
| 10 | 연구 lane의 자원 반환에 반응하는 worker 할당 | 과다 할당·유휴 시간 | 코드 반례와 snapshot 할당 검증 | 계측 후 적용 |

---

## 1. 짧은 acceptance 검사로 후보를 영구 탈락시키지 않기

**가장 쉽고 명확한 수정입니다.**

`ST2/gate_budget.py`는 \(10^6\)-shot 실행의 `rep.passed`를 다음 단계 진입의 필수조건으로 사용합니다. 실패한 receipt도 QASM hash가 같으면 재사용합니다. 이에 따라 exact acceptance가 충분한 후보라도 첫 짧은 표본의 변동으로 후속 평가에서 사라질 수 있습니다. [선별 코드](https://github.com/AutoclickerI/quantumn/blob/806b481e1668497f000050e4df85a0ba567e74e9/work/lanes/ST2/gate_budget.py)

그 차이는 작지 않습니다. 이항분포로 계산한 acceptance 탈락 확률은 다음과 같습니다.

| 실제 acceptance | \(10^6\) shots에서 탈락 | 공식 길이 \(10^8\) shots에서 탈락 |
|---|---:|---:|
| 0.5002 | **34.4210%** | **0.0031658%** |
| 0.5005 | **15.8413%** | 약 \(7.61\times10^{-24}\) |

이는 반복 표본 추출에 대한 확률입니다. 이미 결정된 특정 seed의 결과가 확률적으로 바뀐다는 뜻은 아닙니다.

실제 사례도 있습니다. `BFLAG/final/bflag_r1.json`은 exact \(A=0.5004698831673771\)이고 format/class/ideal 검사를 통과했지만, 짧은 실행의 acceptance가 0.499898이라 탈락했습니다. 이 회로의 기대 손실은 현재 `v36h`보다 나쁘므로 숨은 우승 회로를 발견한 사례는 아닙니다. **선별 정책이 통계적 변동을 영구 실패로 처리한다는 실제 증거**입니다. [실제 receipt](https://github.com/AutoclickerI/quantumn/blob/806b481e1668497f000050e4df85a0ba567e74e9/work/lanes/BFLAG/final/bflag_r1.json)

### 변경 방법

판정 상태를 분리하면 됩니다.

- **Format/class/ideal 실패:** 즉시 탈락.
- **짧은 실행의 acceptance-only 실패:** 통계적으로 미결정.
- **검증된 evaluator 범위에서 충분한 exact-A 여유 확보:** 후속 평가 허용.
- **최종 공식 실행:** 기존 \(10^8\)-shot acceptance 판정 유지.

Exact evaluator의 지원 범위 밖에서는 정당한 순차 신뢰구간이나 공식 표본을 사용해야 합니다.

확인된 문제는 ST2/FRESH/SEPBC 계열 경로입니다. **MAIN `promote.sh`의 짧은 실행은 speed gate이므로 이 문제와 구분해야 합니다.**

**채택 기준:** 기존 receipt에서 오탈락을 재현하고, 변경 후에는 의미상 잘못된 회로와 통계적으로 미결정인 회로가 구별되는지 확인하면 됩니다. 물리 회로를 바꾸지 않고 검색의 누락을 줄이는 수정입니다.

---

## 2. Race threshold를 공식 순위의 전체 비교 규칙으로 계산하기

현재 threshold 계산에는 두 가지 구체적인 문제가 있습니다.

`promote.sh`와 `draw_loop.sh`는 반올림된 점수 key에서 자릿수 간격의 절반을 빼는 방식으로 목표값을 만듭니다. 이 방식은 **같은 점수 key에서 CX 수로 이기는 경우**와 **10의 거듭제곱 근처에서 반올림 간격이 바뀌는 경우**를 제대로 처리하지 못합니다. [현재 threshold 계산](https://github.com/AutoclickerI/quantumn/blob/806b481e1668497f000050e4df85a0ba567e74e9/work/promote.sh)

### 반례 A: 같은 key, 더 적은 CX

현재 선택된 raw score가 약 \(3.5313069950\times10^{-5}\), key가 \(3.53\times10^{-5}\), CX가 327이라고 하겠습니다.

후보가 다음과 같으면 공식 tie rule에서 이깁니다.

\[
\text{raw score}=3.534\times10^{-5},\qquad CX=326.
\]

그런데 기존 목표값 약 \(3.525\times10^{-5}\)는 이 승리 영역을 제외합니다.

공개 formatter와 순위 규칙을 기준으로 계산하면, 더 적은 CX를 가진 후보의 첫 패배 float는 약 \(3.535\times10^{-5}\)입니다. 같은 CX이고 더 늦게 제출하는 후보의 경계와 달라야 합니다.

### 반례 B: \(10^{-5}\) 부근

Incumbent key가 `1.00e-5`라면 `9.99e-6`인 후보는 점수 key부터 더 좋습니다.

그런데 기존 식은 threshold를 `9.95e-6`으로 잡습니다. 해당 경계의 정확한 첫 패배 float는 `9.995e-6`입니다.

### 변경 방법

후보마다 다음 정보를 비교해야 합니다.

\[
(\text{공식 formatted score의 숫자값},\ CX,\ \text{제출 순서})
\]

직접 만든 구현은 공개 Python formatter를 사용하고, 양수 IEEE-754 float 영역에서 이진 탐색하여 **해당 후보가 처음 패배하는 경계**를 찾습니다. 이렇게 하면 decade 전환과 경계 포함 여부를 함께 처리할 수 있습니다.

2,700개 key × 3가지 CX 관계, 총 8,100개 경계와 121,500개 주변 float에서 비교 규칙과 새 threshold의 불일치는 0이었습니다. 이는 그 유한 검증 범위의 결과이며, 별도 서버 구현의 모든 세부 동작을 독립적으로 확인했다는 뜻은 아닙니다.

**채택 기준:** 후보의 CX를 threshold 계산까지 전달하고 공식 comparator와 대조하면 됩니다. 같은 stem 안에서 CX가 동일한 variants를 raw score로 정렬하는 부분은 그대로 둘 수 있습니다.

---

## 3. 관측량까지 selector에 포함하여 73개 contraction을 통합하기

**이번 검토에서 직접 계산 가속을 확인한 핵심 후보입니다.**

현재 sparse evaluator는 한 관측량 안에서 quotient를 이용해 중복 계산을 줄입니다. 여기에 **서로 다른 관측량 사이에서도 같은 계산을 공유**할 여지가 남아 있습니다. [현재 sparse evaluator](https://github.com/AutoclickerI/quantumn/blob/806b481e1668497f000050e4df85a0ba567e74e9/work/lanes/MAIN/sparse/sparse_walsh.py)

채널 factor의 parity를 다음과 같이 쓰겠습니다.

\[
k\cdot x\oplus r\cdot y\oplus e\cdot o.
\]

여기서 관측량을 나타내는 \(o\)를 selector 쪽에 포함합니다.

\[
x'=(x,o),\qquad k'=(k,e).
\]

그러면 acceptance와 72개 scored moment를 묶어 contraction할 수 있습니다. 서로 다른 관측량도 중간 계산이 같으면 공유됩니다.

중요한 구현 조건은 **정규화 분모를 기존 \(2^K\)로 유지하는 것**입니다. 관측량 label은 새로 확률 평균을 내는 자유변수가 아닙니다.

### 이번 로컬 측정

공통 prepare/kernel/compile 비용을 양쪽에 포함하고, import/startup은 제외한 단일 프로세스 CPU 시간입니다.

| 회로 | 기존 | 통합 selector | 가속 |
|---|---:|---:|---:|
| `v36h` | 3.5180초 | 1.9738초 | **1.78배** |
| `v36g` | 2.9561초 | 1.8093초 | **1.63배** |

두 회로 모두 전체 73개 moment를 비교했습니다.

- 최대 selector 차이: \(3.33\times10^{-16}\)
- 최대 moment 차이: \(1.11\times10^{-16}\)
- 최종 \(A,L\): 일치

처리하는 work entries도 125,312,200에서 67,579,074로 약 46.1% 줄었습니다.

각 회로의 총비용 비교는 한 번의 paired 측정입니다. 별도 component 반복 측정에서는 약 3.58배가 나왔지만, 이를 전체 평가기 가속으로 인용하면 안 됩니다.

**채택 기준:** 편집된 회로 여러 개와 실제 16-process 탐색에서 전체 처리량을 확인한 뒤 통합할 가치가 큽니다. shape에 따라 기존 방식으로 돌아가는 분기를 둘 수도 있습니다. 이 결과는 exact 평가기 가속이며 공식 Monte Carlo sampler의 가속은 아닙니다.

---

## 4. 이미 아는 exact \(A,N\)으로 race의 평균을 고정하기

`race.py`의 `_p_below`는 process-local chunk 표본으로 평균 loss sum과 accepted count를 다시 추정합니다. 그런데 exact evaluator로 \(A,L\)을 이미 알고 있는 후보라면 그 평균은 다시 추정할 필요가 없습니다. [Race 구현](https://github.com/AutoclickerI/quantumn/blob/806b481e1668497f000050e4df85a0ba567e74e9/work/race.py)

\(N=AL\), chunk당 shots를 \(m=10^6\)이라 하면

\[
E[S]=mN,\qquad E[K]=mA
\]

입니다. \(S\)는 손실 합, \(K\)는 accepted count입니다.

목표 threshold를 \(\tau\)라고 할 때 ratio를 직접 다루기보다

\[
R=S-\tau K
\]

를 사용하면, 그 평균도 바로 알 수 있습니다.

\[
E[R]=m(N-\tau A).
\]

여기서 \(E[S/K]=E[S]/E[K]\)라고 가정하는 것은 아닙니다. 분자와 분모의 평균을 각각 고정하는 방법입니다.

30개 chunk로 추정한 평균의 오차를 100개 chunk 길이에 투영하면, full-run 표준편차 약 \(\sqrt{100/30}=1.83\)개 규모의 불확실성이 생길 수 있습니다. 극단 꼬리 확률을 판단하는 race에는 큰 오차입니다.

### 이번 모형 검증

기존 `KAPPA=0.7`과 check 시점을 유지하고, 조건당 50,000개의 calibration snapshot과 paired candidate path를 사용했습니다.

4σ 목표에서 prior가 30개 chunk일 때:

- **모형상 hits/chunk: +8.13%**
- Paired Monte Carlo 95% 구간: **+7.23%∼+9.03%**

Prior가 100개이면 +1.73%, 1,000개이면 +0.09%로 유의한 개선을 확인하지 못했습니다. 따라서 이 제안은 특히 **calibration 데이터가 적은 worker**에서 의미가 있습니다.

이 수치는 Gaussian 모형 결과이며 실제 시간당 성공률 8% 개선을 측정한 것은 아닙니다. 같은 모형에서 covariance 보정을 추가한 효과는 거의 없었고, 주효과는 평균 고정이었습니다.

**채택 기준:** exact moments를 QASM·data 순서·noise·build에 대한 동일성 검사와 연결하고, 실제 held-out chunk trace에서 기존 정책과 비교해야 합니다. 최종 공식 합계와 seed 규칙은 그대로 유지합니다.

---

## 5. C 자원을 \(C_2\) 밖으로 넓히고, 국소 Bell readout에 맞추기

**물리 회로 쪽에서 가장 먼저 후속 실험할 후보입니다.**

기존 PCC 탐색은 제한된 C 부분공간을 검사했습니다. 그런데 다음 항등식의 허용 범위는 더 넓습니다. [기존 PCC 보고서](https://github.com/AutoclickerI/quantumn/blob/806b481e1668497f000050e4df85a0ba567e74e9/work/lanes/PCC/REPORT.md)

\[
R_V\propto
\sum_{u\in C_2,\ v\in V}|u\rangle_B|u+v\rangle_C.
\]

B→C transversal CX를 적용하면

\[
R_V\longmapsto |0_L\rangle_B|V\rangle_C.
\]

이는 \(V\subset C_2\)에만 성립하는 관계가 아닙니다. **임의의 선형 부분공간 \(V\subset\mathbb F_2^7\)** 에 대해 성립합니다.

### 실제로 만든 후보: `R6`

\[
V=\operatorname{span}\{6\}
=\operatorname{span}\{e_1+e_2\}
\]

를 선택하면 C25/C19의 Bell 자원이 됩니다.

현재 network에서 **q12, tick 38의 `R`을 `RX`로 바꾸는 것만으로** 필요한 추가 생성자가 최종 \(X_{19}X_{25}\)로 전달됩니다. 별도 preparation routing이 필요하지 않습니다.

Readout은 다음과 같이 바꿨습니다.

- 기존 두 C-copy CX를 tick 45의 `CX25→19`로 교체.
- Tick 46에서 `MX25`, `MZ19`.
- Helper 18/31의 마지막 copy용 동작만 제거하고 앞선 사용은 보존.

완성 후보는 **326 CX, 15 T, 47 ticks, 36 qubits**입니다. 이상적 acceptance는 약 1, 이상적 loss는 0이며, 전체 회로의 단일 fault 검사에서 harmful atom은 발견되지 않았습니다.

### 전체 잡음을 포함한 결과

| 회로 | 기대 손실 \(L\) | Acceptance \(A\) |
|---|---:|---:|
| 기준 `v36h` | \(3.8154733225\times10^{-5}\) | 0.501641504948 |
| 새 `R6` | \(3.8339504321\times10^{-5}\) | 0.504023485849 |
| 같은 edge를 쓰는 classical exchange 대조군 | \(3.8426998388\times10^{-5}\) | 0.504056288821 |

해석은 세 부분으로 나뉩니다.

1. `R6` 단독 loss는 기준보다 **약 0.48% 나쁩니다.**
2. Acceptance는 **0.00238198 증가**, CX는 하나 감소합니다.
3. Bell 자원 변경 자체는 같은 edge의 classical exchange보다 loss를 **\(8.75\times10^{-8}\)** 낮춥니다.

따라서 채택 전략은 **확보한 acceptance를 추가 검출에 사용하는 것**입니다. 단독으로 기준을 이기려면 적어도 약 \(1.85\times10^{-7}\)의 loss를 추가로 회수해야 합니다.

### 최신 P91과 직접 결합한 진단

이미 진행 중인 P91의 S12X+gap 장치와도 조합해 계산했습니다. 아래는 **격자 밖 보조큐비트를 포함한 진단이며 제출 가능한 회로가 아닙니다.** [P91 자료](https://github.com/AutoclickerI/quantumn/blob/49f1eacec54c06bfff09d9ea6df604941dcdb43c/work/lanes/GLOBAL/room/prices.txt)

| 격자 밖 진단 조합 | \(L\) | \(A\) |
|---|---:|---:|
| 원래 P91 장치 | \(3.54497365787\times10^{-5}\) | 0.498527097172 |
| `R6` + 같은 P91 장치 | **\(3.56770844022\times10^{-5}\)** | **0.500894426462** |
| Classical exchange + 같은 장치 | \(3.57214214805\times10^{-5}\) | 0.500926887087 |

추가 장치의 native noise는 포함했습니다. 이 계산은 acceptance를 확보하는 변경이 해당 조합을 실제로 내부 기준 0.5002 이상으로 올린다는 증거입니다.

다만 **36개 실제 cell에 배치하는 routing과 점유 충돌 해결 비용은 아직 없습니다.** 표의 약 6.5% 개선을 합법 회로의 성과로 부를 수는 없습니다.

**채택 기준:** 이미 만들어 둔 `R6` QASM을 시작점으로 P91 배치를 구현하고, 그 비용까지 포함한 전체 \(A,L\)이 기준을 이길 때 채택합니다. 물리 후속 실험 중에서는 이 경로가 가장 구체적입니다.

---

## 6. B의 논리 coset을 C의 중복 표식으로 추적하는 자원

5번이 C 자원을 넓히는 방법이라면, 이 방법은 **B의 논리 sector까지 넓히고 측정 기록으로 추적**합니다.

\(C_1=C_2^\perp\), \(\ell\in C_1\setminus C_2\), \(u\ne0\)에 대해

\[
R_{\mathrm{tag}}(u)
=
\operatorname{span}\{(g,g):g\in C_2\}
+
\operatorname{span}\{(\ell,\ell+u)\}
\]

를 준비합니다.

B→C 뒤의 상태는

\[
\frac{
|0_L\rangle_B|0\rangle_C+
|1_L\rangle_B|u\rangle_C
}{\sqrt2}
\]

가 됩니다.

이후 B→D, B의 X 측정, C의 Z 측정을 하면, \(c=mu\), \(r\in C_1\)인 분기의 연산자는

\[
K_{m,r}
=
\frac{(-1)^{m(r\cdot\ell)}}{\sqrt{32}}X_L^m
\]

입니다. \(u_j=1\)인 위치에서 \(m=c_j\)를 읽고 **`FRAME_X=m`** 을 적용하면 임의의 encoded 입력을 복원할 수 있습니다.

여기서 \(m=1\)을 버릴 필요가 없습니다. 따라서 이상적 acceptance를 1로 유지합니다. C의 검사는

\[
c_i\oplus u_i c_j=0
\]

형태의 선형 parity로 표현할 수 있습니다.

### 검증한 것과 아직 남은 것

127개 nonzero tag 모두에서 32개 비영 분기를 확인했고, 대표 tag 4개는 두 논리 기저 입력의 Kraus 계수까지 비교했습니다. 최대 수치 오차는 \(7\times10^{-18}\) 미만이었습니다.

다만 **무게 1 tag는 제외해야 합니다.** C의 독립 readout flip만 있는 모형에서도 frame 오판으로 \(p/2=5\times10^{-4}\)의 loss가 생깁니다.

무게 \(w\)인 tag의 같은 readout-only 모형에서는

\[
L_{\mathrm{read}}
=
\frac{p^w(1-p)^{7-w}}
{2\left[(1-p)^7+p^w(1-p)^{7-w}\right]}.
\]

\(p=0.001\)에서:

- \(w=2\): 약 \(5.01\times10^{-7}\)
- \(w=3\): 약 \(5.02\times10^{-10}\)

이 값은 전체 회로 예측이 아닙니다. Preparation fault와 tag·data를 함께 바꾸는 CX hook이 핵심 검증 대상입니다.

현재 만든 최근접 이웃 준비는 77 CX, depth 31이라 기존 시간창에 맞지 않습니다. 또한 현재 BFLAG splice와 sparse frontend의 frame 지원 범위를 넓혀야 합니다. [BFLAG splice](https://github.com/AutoclickerI/quantumn/blob/806b481e1668497f000050e4df85a0ba567e74e9/work/lanes/BFLAG/splice.py)

**첫 실험:** 무게 2 이상인 tag 120개를 대상으로 제한된 시간창 안의 짧은 합성을 찾고, 단일 fault와 전체 noisy loss를 평가합니다. 이상적 항등식은 검증됐지만 유용한 noisy 구현은 아직 확보하지 못한 연구 후보입니다.

---

## 7. 작은 window를 Choi SDP로 풀어 합성 목표와 종료 근거 만들기

이 방법의 목적은 **어떤 국소 변경을 찾아야 하는지**, 그리고 **특정 window를 더 탐색할 여지가 있는지**를 계산으로 판단하는 것입니다.

첫 시험 대상으로 5번의 C25/C19 decoder window를 사용할 수 있습니다. 다음 요소를 고정합니다.

- 실제 noisy prefix와 외부 큐비트·측정 기록의 상관관계
- 해당 slot 뒤의 native \(D_2(p)\)
- 이후 readout과 나머지 회로

그 slot의 이상적 operation만 가상의 CPTP channel \(\Phi\)로 완화합니다. 두 큐비트 채널의 unnormalized Choi 행렬 \(J\)는 \(16\times16\)입니다.

전체 회로에서 \(A,N\)을 산출하는 tester를 만들면 다음 문제를 쓸 수 있습니다.

\[
\begin{aligned}
\min_J\quad&
\operatorname{Tr}[(W_{N,p}-\tau W_{A,p})J]\\
\text{s.t.}\quad&
J\succeq0,\qquad \operatorname{Tr}_{out}J=I_4,\\
&\operatorname{Tr}(W_{\mathrm{bad},0}J)=0,\\
&\operatorname{Tr}(W_{A,0}J)=1,\\
&\operatorname{Tr}(W_{A,p}J)\ge0.5002.
\end{aligned}
\]

목표식은 \(N-\tau A\)입니다. \(A>0\)이면 이것이 음수인 것과 \(L<\tau\)가 동치입니다.

### 이 방법으로 얻을 수 있는 것

- **Dual로 인증된 최적값 하한이 0 이상:** 이 고정된 noise-slot 범위에서는 목표를 이길 수 없다는 종료 근거.
- **완화 문제에서 음수 해 발견:** 합법 gate 합성이 따라가 볼 목표 채널.
- **실제 native circuit으로 합성 후 전체 평가 통과:** 최종 채택.

두 가지 구현 조건이 중요합니다. 실제 noisy prefix의 상관관계를 유지해야 하고, clean/noisy 계산에 **같은 \(J\)** 를 삽입해야 합니다. 이상적 조건을 이용해 잡음 상태까지 같은 부분공간에 가두면 잘못된 bound가 나올 수 있습니다.

완화 공간이 자명하지 않다는 점은 검증했습니다. 이상적 Bell+를 똑같이 보내면서 Bell− 오류를 서로 다른 측정 패턴으로 보내는 두 연산을 구성할 수 있습니다. 따라서 이상적 동작을 유지하면서 오류의 accept/reject 성질을 바꾸는 자유도가 존재합니다.

**현재 상태:** 정식화와 feasibility/nondegeneracy certificate까지 만들었고 SDP 최적화 자체는 실행하지 않았습니다. 한 slot의 실제 gate 선택지는 작으므로 이 사례로 tester를 검증한 뒤, noise 위치를 고정한 작은 multiwire window로 확대하는 것이 적절합니다. 추가 tick이나 준비 회로 변경은 기존 bound의 범위 밖입니다.

---

## 8. 물리 후보를 보존할 때 평균뿐 아니라 공식 점수 분포까지 사용하기

기존 reviewer11의 family별 race 자원 배분과는 다른 단계의 제안입니다. **물리 후보를 생성한 직후 평균이 조금 나쁘다는 이유로 버리는 정책**을 검토하자는 것입니다.

공식 최종 key 획득 확률을 목표로 한다면, 다음 정보를 함께 보존할 필요가 있습니다.

\[
\left(
L,\ A,\ E[\ell^2\mid accept],\ \text{CPU 비용},\ CX
\right).
\]

예를 들어 logical Pauli error만 보더라도 X/Y 오류의 loss는 \(1/2\), Z 오류는 1입니다. 따라서 같은 평균이라도 score의 분산과 꼬리가 달라질 수 있습니다.

### 수학적 반례

Accepted count를 50,164,150으로 고정한 **두 가상의 \(\{0,\frac12,1\}\) 분포**를 비교했습니다.

| 가상 분포 | 평균 | score \(<3.525\times10^{-5}\) 확률 |
|---|---:|---:|
| A | 현재 기준 \(L\)과 같게 설정 | \(2.14438\times10^{-5}\) |
| B | A보다 \(3\times10^{-7}\) 나쁨 | \(1.06039\times10^{-4}\) |

유한 multinomial 분포를 계산하면 B의 목표 도달 확률이 약 **4.945배**입니다.

이것은 평균만으로 후보를 지배한다고 판단하면 안 된다는 반례입니다. 해당 분포를 유용한 격자 회로로 구현했다는 뜻은 아닙니다.

기대할 수 있는 크기에도 한계가 있습니다. 현재 \(L,A\)와 \(0\le\ell\le1\)에서 SEM 상한은 약 \(8.72\times10^{-7}\)입니다. 계획 문서의 약 \(7.2\times10^{-7}\)와 비교하면 4σ Gaussian 근사 기준의 추가 여유는 약 \(6.1\times10^{-7}\)입니다. 분포 조절만으로 손실을 \(10^{-5}\) 수준까지 낮춘다는 주장은 뒷받침하지 않습니다.

**첫 실험:** 평균이 가까운 실제 stems 소수에서 loss mark와 CPU 비용을 수집하고, mean-only 선별과 분포를 고려한 선별을 같은 예산의 held-out reorders로 비교합니다. 실제 분포가 거의 같거나 평균 악화·실행 비용이 꼬리 이득보다 크면 중단합니다.

평균 물리 품질의 개선과 공식 표본 점수 획득률의 개선은 별도로 보고해야 합니다.

---

## 9. 시간 경계에서 race의 완료된 chunk를 저장하고 재개하기

현재 `cut_redraws.sh`는 정해진 시각에 race를 종료합니다. 그런데 `race.py`는 100개 chunk를 끝내야 결과를 저장하고, 진행 중 누적값은 메모리에 있습니다. 다음 시간에는 새 이름과 variant offset으로 시작하므로 계산한 prefix를 복구하지 못합니다. [중단 코드](https://github.com/AutoclickerI/quantumn/blob/806b481e1668497f000050e4df85a0ba567e74e9/work/receipts/cut_redraws.sh) · [Race 코드](https://github.com/AutoclickerI/quantumn/blob/806b481e1668497f000050e4df85a0ba567e74e9/work/race.py)

각 chunk는 별도 seed로 sampler를 생성하므로, 완료된 chunk를 저장하는 데 native RNG의 실행 중 상태 전체가 필요한 것은 아닙니다.

### 저장할 내용

- 실제 reordered QASM과 ordered data
- Noise·judge·xtim·수치 연산 환경의 식별 정보
- Chunk index와 seed 규칙
- Accepted/corrected count
- Loss sum과 squared-loss sum

부동소수점은 `float.hex()`로 보존하고, 재개 시 **기존 chunk 순서와 합산 방식**을 유지해야 합니다. 구간별 합계를 다시 합치면 반올림 순서가 바뀔 수 있습니다.

직접 만든 유틸리티는 append-only record, hash chain, file lock, `fsync`를 사용합니다. 합성 100-chunk 데이터에서 1/7/30/80/99번째 이후 중단·재개와 잘린 마지막 write를 시험했고, 최종 count·sum·score·SEM의 bit 일치를 확인했습니다. 실제 xtim의 \(10^8\) shots를 수행한 검증은 아닙니다.

### 재개할 후보의 선택도 필요합니다

모든 partial을 무조건 끝내는 정책은 적절하지 않습니다. 갱신된 threshold에서

\[
\frac{\text{재개 후 승리 확률}}{\text{남은 계산 비용}}
\]

을 새 후보와 비교해야 합니다. 이미 사용한 시간은 선택 기준에 다시 더하지 않습니다.

**채택 기준:** 실제 xtim에서 중단 전후 수치 일치를 검증하고, controller가 chunk 경계에서 종료하도록 연결합니다. 의도적으로 탈락시킨 후보와 시간 제한으로 중단한 후보를 구별하고, 완료된 100-chunk 결과만 promotion에 사용합니다. 절약량은 실제 중단 trace와 저장 비용으로 측정해야 합니다.

---

## 10. 연구 lane이 반환한 자원을 짧게 빌려 쓰는 worker 할당

현재 `race_specs.sh`는 시간 시작에 load를 조사해 worker 수를 고정합니다. 이 코드에는 상한을 계산한 뒤 **최소 4개를 강제하는 경로**가 있습니다. 여유가 0이어도 worker 4개를 시작할 수 있습니다. [최신 자원 할당 코드](https://github.com/AutoclickerI/quantumn/blob/49f1eacec54c06bfff09d9ea6df604941dcdb43c/work/receipts/race_specs.sh)

예를 들어:

- 48 cores
- Team cap 36
- Busy 47
- Ours 35

이면 기존 계산은 4를 반환하지만, 해당 snapshot의 안전한 신규 할당은 0입니다.

다른 개선 여지는 연구 lane이 중간에 종료돼도 다음 시간까지 race capacity가 고정된다는 점입니다.

### 제안하는 방식

연구 lane이 **명시적으로 반환한 예약 자원**을 racer가 짧은 lease로 사용합니다. 연구 lane이 다시 요청하면 다음 chunk 경계에서 돌려줍니다.

현재 racer를 제외한 부하를 일관되게 측정했다면 목표 worker 수는 다음과 같이 계산할 수 있습니다.

\[
r_{\mathrm{target}}
=
\max\left(
0,\min(
r_{\mathrm{lease}},
C-\mathrm{other\_busy}-\mathrm{reserve},
\mathrm{team\_cap}-\mathrm{other\_ours}
)
\right).
\]

64,760개 유한 snapshot에서 이 계산을 brute-force 최대 허용 할당과 대조했고 불일치는 0이었습니다. 이는 **같은 snapshot 모형 안의 할당 정확성**이며, 이후 다른 사용자의 부하 변화나 실제 실행 속도까지 보장하지는 않습니다.

가령 48-core host에서 research 24+racer 12를 사용하다 research가 예약을 반환하면, team cap 36 안에서 racer가 늘어날 여지가 있습니다. 실제 host에 그런 공백이 있었다는 측정은 아직 하지 않았습니다.

**첫 실험:** 시간별 유휴 core-minutes, 과다 할당, chunk/s를 계측합니다. 사용할 수 있는 공백이 확인되면 hysteresis를 둔 lease allocator를 적용합니다. 기존 연구 예약과 75% 규칙은 계속 지켜야 합니다.

---

## 제가 권하는 실행 순서

**첫 적용은 1 → 2 → 3입니다.** 앞의 두 개는 확인된 선별·비교 문제를 고치고, 세 번째는 이미 로컬에서 가속과 수치 일치를 확인했습니다.

그다음에는 **4와 9를 실제 chunk trace로 검증**하는 것이 좋습니다. 이미 알고 있는 평균을 활용하고, 계산한 정보를 보존하는 방향입니다. 10은 유휴 자원 계측 결과가 있을 때 적용할 가치가 있습니다.

물리 실험의 첫 대상은 **5번 `R6`와 진행 중인 P91의 조합**입니다. 준비된 실제 36큐비트 후보가 있고, 추가 검출 장치와 결합했을 때 acceptance 문제를 해결하는 수치 증거도 있습니다. 남은 핵심은 실제 격자 배치 비용입니다.

6번과 7번은 준비하는 자원의 계약이나 합성 탐색 방법을 바꾸는 연구입니다. 8번은 실제 후보들의 점수 분포가 충분히 다른지부터 확인해야 합니다.

이번에는 다음 방향도 확인했지만 추천 목록에서 제외했습니다.

- 단일 coordinate의 product-C/MX 진단 일곱 가지: matched control보다 모두 나빴습니다.
- 전체 final instrument의 S/H/SX conjugation: 새 native noise를 포함하면 모두 나빴습니다.
- Selector 축소·관측량별 재컴파일 등 일부 evaluator 변형: 이번 구현에서는 overhead를 이기지 못했습니다.
- 기존 quotient, 일반 open-boundary table, 이미 시도한 affine-frame 정책과 2–3-edit bundle: 기존 리뷰 또는 진행 중인 작업과 중복되어 새 항목으로 세지 않았습니다.

**“새 방법”은 검토한 저장소의 구현·리뷰·실험과 구별된다는 의미입니다. 학술적으로 전례가 없다는 주장까지 하지는 않습니다.**

## 보고서와 재현 자료

전체 보고서와 코드·검증 기록·`R6` 회로를 준비했습니다. 원격 저장소, 제출본, 운영 중인 호스트 작업은 수정하지 않았습니다.

- :chatgpt-content-reference{index="0"}[quantumn_review13_ko.txt](sandbox:/workspace/scratch/264927bd82df/quantumn-refresh/deliverables/quantumn_review13_ko.txt)
- quantumn_review13.zip[quantumn_review13.zip](sandbox:/workspace/scratch/264927bd82df/quantumn-refresh/deliverables/quantumn_review13.zip)

ZIP에는 재현 스크립트, 수치 receipt, 검증 certificate, 실제 `R6` 후보가 들어 있습니다. 격자 밖 P91 조합은 제출 가능한 회로와 구분해 표시했습니다.

다만 **라이브러리 저장은 완료하지 못했습니다.** 자동 승인 검토가 “저장소에서 파생된 코드·분석을 별도 저장 위치로 업로드하는 데 대한 명시적 승인이 없다”는 이유로 업로드를 거부했습니다. 위 작업 파일은 준비되어 있습니다. **이 두 파일을 ChatGPT 라이브러리에 저장해도 될까요?**

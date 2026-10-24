# quantumn v36c 최적화 재검토와 구현 계획

검토 기준은 **2026년 10월 25일 KST**, 저장소 커밋 **42afa8ff01c3999444336f5bb2fe473c1475d6f4**, 공식 채점기 **76fe47c0324f1c1f8b72a7d55af200e88043b522**다. 이 보고서는 v35a에서 출발한 이전 제안을 현재 v36c에 맞춰 다시 검토하고, 이미 채택된 방법을 제외한 새 실행 단위 10개를 제시한다. 전체 코드 변경 권고와 실험 결과는 구현 에이전트용 ZIP의 TASKS.json 및 IMPLEMENTATION_AGENT.md에 연결되어 있다.

**최종 HEAD 추가 확인.** 납품 직전 2026-10-25 03:24 KST에 커밋 **e31cec14e20f5d9fec9da759ef0d61cd4a5358ab**를 확인했다. 분석 pin 이후 바뀐 것은 v36b_r580 QASM·JSON·검증 기록 세 파일뿐이며 v36c, 평가기, 계획과 규칙은 그대로다. 새 기록의 1억 shots seed-0 점수는 **3.8779486220169754×10⁻⁵**, acceptance는 **0.5014249**다. 원래 v36b와 qubit별 명령 순서, 공식 native 일정과 idle 구간이 같다는 것을 추가 확인했다. 이는 순서 재배치로 선택된 표본 기록이며 새로운 기대값 개선은 아니다. 아래의 v36c 수치와 후보 10개는 유지된다. 새 파일과 등가성 확인은 ZIP의 LATEST_UPDATE.md 및 latest_update/에 포함했다. [새 커밋과 변경 범위](https://github.com/AutoclickerI/quantumn/compare/42afa8ff01c3999444336f5bb2fe473c1475d6f4...e31cec14e20f5d9fec9da759ef0d61cd4a5358ab) · [최신 제출 기록](https://github.com/AutoclickerI/quantumn/blob/e31cec14e20f5d9fec9da759ef0d61cd4a5358ab/work/receipts/seq_v36b_r580.txt)

**가장 중요한 발견은 두 가지다.** 첫째, 공개된 위상 회로 생성기는 보호된 15-T 형태만 만들고 있으며, 제외된 14-T 형태 15개는 필요한 위상 좌표의 rank가 5에서 4로 줄어든다. 이 가족의 정확한 위상식, 제한 잡음 비용, 격자 패리티 조각을 새로 검증했다. 둘째, v36c 평가기의 검출 좌표만 바꾸어 73개 기대값을 유지하면서 contraction width를 11에서 9로 낮췄다. 전자는 **전체 회로로 가격을 매겨야 하는 물리 후보**, 후자는 **이미 구현하고 검증한 계산 최적화**다.

새로운 전체 물리 회로가 v36c보다 낮은 손실을 달성했다는 주장은 하지 않는다. 10개 항목 모두에 보장되는 성질, 아직 필요한 검증, 첫 실험과 중단 기준을 둔다. 방법 자체의 세계 최초성도 주장하지 않는다. 여기서 새롭다는 말은 공개된 현재 구현과 실험 기록에 대해 새로 확인하거나 구체화한 실행 단위를 뜻한다.

# 현재 기준선과 이미 반영된 작업

v36c를 원본 QASM으로 다시 평가했다. 수치 오차의 종류를 구분하기 위해 all-orders 기대값과 공식 Monte Carlo 검증값을 나란히 기록한다.

| 항목 | 이번 재검증 |
|---|---:|
| 기대 손실 L | 4.1151559437773416 × 10⁻⁵ |
| 절대 acceptance A | 0.5027278379249299 |
| 독립 유효 잡음 채널 | 552 |
| 검출 조건 | 72 |
| 기대값 계산 | acceptance 1개와 관측량 72개 |
| CX 수와 native depth | 213개, 47틱 |
| QASM SHA256 | 49ea05888f6f56f87eee49665f8275e3f0c30e199c67db7958f5318cc07bd3f8 |
| sparse kernel 생략 오차의 L 상계 | 1.17535 × 10⁻¹⁴ |
| 공식 judge 100만 shots seed 0 | format, class, correctness, acceptance 모두 PASS |

Sparse kernel의 생략 오차 상계는 부동소수점 반올림 오차까지 포함한 interval certificate가 아니다. 공식 100만 shots에서 나온 손실은 4.68049 × 10⁻⁵, SEM은 8.15111 × 10⁻⁶였다. 이 실행은 회로의 유효성을 확인하는 용도이며, 약 10⁻⁷ 수준의 후보 순위를 정하는 용도로 사용하면 안 된다.

저장소가 보고한 v36a_r665의 서버 점수 3.90052 × 10⁻⁵는 978개 순서 재배치 중 선택된 seed-0 표본이다. 같은 물리 회로 v36a의 기대 손실은 4.14605 × 10⁻⁵다. v36c가 v36a보다 기대값 기준 약 0.745% 낫다는 사실과, 선택된 v36a 표본 점수가 더 낮다는 사실은 함께 성립한다. [현재 계획](https://github.com/AutoclickerI/quantumn/blob/42afa8ff01c3999444336f5bb2fe473c1475d6f4/docs/PLAN.md) · [제출 결과](https://github.com/AutoclickerI/quantumn/blob/42afa8ff01c3999444336f5bb2fe473c1475d6f4/docs/SOTA.md)

다음은 이미 채택되거나 작업 중이므로 새로운 누락으로 재포장하지 않는다.

- P75는 N − L₀A 목적함수, 실제 편집 간 상호작용, 조합 전체 재평가를 이미 사용한다.
- 채널별 all-orders adjoint는 통합됐고 v36b 분석도 있다.
- P77은 마지막 라운드 역방향 설계, P73은 준비 중 B flag, P78은 제출 표본의 chunk racing을 맡는다.
- 예전 population.py의 register 256, survivor 선택 문제는 현재 live 경로의 결함으로 입증되지 않았다. FINDINGS는 live pop35 경로가 이를 수정했다고 명시한다.
- detector record 수 112→85, frame gauge, 일부 instrument 아이디어는 이미 보류 목록에 있다.

공개 tree는 8,801개 항목이고 truncated=false였지만, 문서에 등장하는 일부 최신 lane 구현은 포함되어 있지 않았다. 따라서 공개되지 않은 optimizer 내부까지 새로운 방법이 전혀 없다고 단정하지 않는다. [현재 발견 기록](https://github.com/AutoclickerI/quantumn/blob/42afa8ff01c3999444336f5bb2fe473c1475d6f4/docs/FINDINGS.md) · [adjoint 구현](https://github.com/AutoclickerI/quantumn/blob/42afa8ff01c3999444336f5bb2fe473c1475d6f4/work/lanes/MAIN/sparse/adjoint_ablation.py)

# 후보 10개의 우선순위

아래 순위는 물리 개선 가능성, 확인된 근거, 구현 비용을 함께 본 실행 순서다. 계산 가속을 물리 손실 감소로 계산하지 않는다.

| ID | 방법 | 성격 | 현재 근거 | 첫 산출물 |
|---|---|---|---|---|
| M01 | rank 4의 14-T 위상 가족을 전체 prefix와 공동 합성 | 물리 구조 | 새 대수·잡음·격자 조각 검증 | 14-T 전체 QASM과 full-noise 가격 |
| M02 | 검출 좌표를 contraction 비용에 맞춰 선택 | 평가기 | 구현·73 moment 검증 | 저장된 기저를 사용하는 evaluator |
| M03 | adjoint의 환경 tensor를 보존한 국소 재평가 | 평가기 | 정확한 재사용 항등식 | 실제 편집 20개의 cache 검증 |
| M04 | finite-p 채널 쌍 counterfactual | 탐색 진단 | multiaffinity 항등식 | 수정 가능한 영역의 상호작용 표 |
| M05 | affine syndrome 부분공간과 논리 frame 공동 선택 | 물리적 채택 정책 | 세 음성 대조군·구현 가능한 정책족 | 정확한 sector 가격과 affine 정책 |
| M06 | T-sign kernel의 factorized 표현 | 탐색 범위 | 코드상 T≤20 제한 확인 | >20 T, 작은 rank의 합법 예제 |
| M07 | B/C의 순수 상태 계약을 분기별 instrument 계약으로 확장 | 물리 구조 | 규칙상 가능, 실제 허용 확장 확인 필요 | 구별되는 feasible instrument 구성 |
| M08 | 마지막 검증의 stabilizer rank 자체를 선택 | 물리 구조 | 2,825개 부분공간 유한 열거 | 부분공간별 선별표와 소형 추출기 |
| M09 | 측정으로 만드는 graph resource와 byproduct 공동 합성 | 물리 구조 | 기존 합법 witness의 구체적 확장 | 자원 하나의 완전한 noise 가격 |
| M10 | 의미적으로 결합한 MC와 control variate | 평가·통계 | 편향 없는 비교 residual, 속도 미측정 | 알려진 답에서 분산·CPU 비교 |

M01과 M02를 먼저 병렬로 시작하는 것이 좋다. M03·M04는 평가 비용과 탐색의 질을 높인다. M05–M10은 아래의 첫 검증을 통과한 경우에만 더 큰 구현 예산을 배정한다. 이 순위와 임시 기준은 연구 제안이며 새로운 상시 운영 규칙이 아니다.

# M01 14-T를 허용하고 위상 좌표를 네 개로 줄이기

**이 검토에서 가장 강한 새로운 물리 후보다.** 이전 TREP은 64개 위상 지원 집합을 열거했지만, 실제 TREP2 생성기의 마지막 조건은 T==15인 형태만 build한다. TREP2가 닫은 것은 보호된 15-T 형태 16개의 특정 구현이다. 14-T 형태 15개가 전체 잡음 하에서 진다는 결론은 여기서 나오지 않는다. [생성기 마지막 조건](https://github.com/AutoclickerI/quantumn/blob/a58eca7341a7b2c2272205ff689d4780bde11fd5/work/lanes/TREP2/forms.py#L124-L128) · [실제로 가격을 매긴 범위](https://github.com/AutoclickerI/quantumn/blob/a58eca7341a7b2c2272205ff689d4780bde11fd5/work/lanes/TREP2/REPORT.md#L19-L21)

현재 v36c에서 commuting phase 좌표를 다시 추출했다. 15-T의 좌표 rank는 5지만, 14-T 지원 집합 15개는 **모두 rank 4**다. 각 집합은 4차원 이진 부분공간 H에서 0과 목표 좌표 t를 뺀 형태다. 다음 항등식이 핵심이다.

```math
-\sum_{a\in H\setminus\{0,t\}}[a\cdot y]
\equiv [t\cdot y]\pmod 8.
```

0이 아닌 선형 함수는 H의 절반인 8개 원소에서 1이므로 위상이 modulo 8에서 사라진다. 목표 항 하나를 제외하면 위 식이 된다. 각 지원 집합에 대해 16개의 ±T/T† 부호 배치가 추가 virtual Clifford 위상 없이 원래의 32개 도달 상태 위상을 재현한다. 이것은 그 도달 부분공간에서의 위상 항등식이며, 임의 입력에 대한 전체 물리 회로 등가성까지 뜻하지는 않는다.

단순한 T 수 감소보다 **다섯 번째 독립 위상 모드를 사용하지 않아도 된다**는 점이 중요하다. 과거 고정 좌표에서는 데이터 일곱 개의 ROWS가 이미 rank 4이고, f14_1은 그 부분공간과 정확히 일치한다. 해당 역사적 좌표의 목표는 25, 지원 집합은 {2,4,6,8,10,12,14,17,19,21,23,27,29,31}이다. 모두 T†를 쓰는 표현이 가능하다. 현재 v36c 추출 좌표의 목표 31과 숫자를 섞어 사용하면 안 된다.

**가격도 계산했다.** 각 가상 T의 commuting phase-axis 오류만 q=p/3로 넣고, 나머지 게이트·idle·측정·준비 오류를 모두 끈 제한 모델에서 r=1−2q이면

```math
A_{14}=\frac{1+7r^8}{8},\qquad
N_{14}=\frac{1+7r^8-8r^7}{16},\qquad
L_{14}=\frac{N_{14}}{A_{14}}.
```

p=.001에서 L₁₄=7.793347150063819×10⁻⁷이고 A₁₄=.9953442077이다. 보호된 15-T의 같은 제한 모델은 L₁₅=1.297594148096679×10⁻⁹다. 14-T는 위상 오류 보호에서는 더 나쁘다. 대신 parity 경로, 준비, 대기와 release 제약을 줄여 더 큰 비용을 회수할 수 있는지를 묻는 후보다. 두 수치의 차이를 v36c 전체 L에 기계적으로 더하면 안 된다.

동일한 15개 물리 셀과 같은 공개 router, 각 100개 seed의 조각 비교에서는 최소 CX가 **28→18**, 가장 빠른 구성은 **32 CX/15틱→24 CX/10틱**이었다. 이는 grid-native phase fragment의 비교이지, v36c 전체 prefix의 CX 수가 28이었다는 뜻이 아니다. encoder와 측정, 검출 기록을 포함한 전체 수명은 아직 가격을 매겨야 한다.

**첫 실험.** 기존 생성기의 T==15와 rank==5 가정을 풀고, rank-4 지원·부호·초기 encoder·parity network·cell release를 함께 합성한다. 위상 연산 자체는 네 독립 좌표로 표현된다. 다섯 번째 |+⟩ 준비·측정까지 없앨 수 있는지는 전체 Clifford exterior와 accepted-output 계약으로 별도 검증한다. rank 4라는 사실만으로 q6의 준비·측정이나 물리 셀을 삭제하지 않는다. 해당 셀은 0 상태 helper나 syndrome 기록에 여전히 필요할 수 있다. c54 등 기록을 무조건 지우지 말고 새 검출 식을 다시 유도한다.

**성공 기준.** 전체 noiseless accepted output이 정확한 T_L이고 공식 class가 통과하며, full-noise L이 v36c보다 낮고 A≥.5여야 한다. 전체 이득 0.5% 이상을 우선 작업 기준으로 삼을 수 있지만 작은 정확한 이득도 폐기할 이유는 없다. **중단 기준.** 최선의 실제 route에서도 시간·게이트·노출 비용이 줄지 않거나, full-noise 손실이 증가하면 해당 구현을 닫는다. phase-only 보호를 이유로 가족 전체를 미리 제외하지 않는다.

증거: phase_family_certificate.json, phase_sign_certificate.json, phase_route_certificate.json, 독립 표준 라이브러리 검증기 check_phase_and_subgroups.py.

# M02 검출 좌표를 계산하기 쉬운 기저로 바꾸기

현재 sparse evaluator는 검출 projector를 canonicalize한 뒤 그 좌표에서 min-fill을 수행한다. canonicalization 이후 identity projector가 된 검출 좌표 사이에는 가역 GF(2) 변환의 자유가 남는다. 물리 회로나 채택 사건을 바꾸지 않고, 그 자유를 tensor의 연결 폭을 줄이는 데 사용했다. [현재 구현](https://github.com/AutoclickerI/quantumn/blob/42afa8ff01c3999444336f5bb2fe473c1475d6f4/work/lanes/MAIN/sparse/sparse_walsh.py#L39-L71)

```math
d=0 \quad\Longleftrightarrow\quad Ud=0
\qquad (U\text{ invertible}).
```

현재 v36c의 active kernel projector 네 개는 그대로 두고 identity row 사이에서만 XOR했다. 일반 비영 reference에는 reference도 같은 U로 바꿔야 한다. 이는 기존의 공식 detector record 수 112→85 최적화와 목적이 다르다. 여기서는 QASM 주석을 바꾸지 않고 내부 tensor 좌표의 비용을 줄인다.

| 항목 | 기존 | 새 기저 |
|---|---:|---:|
| Conditioned width | 11 | 9 |
| Min-fill work-entry proxy | 5,636 | 1,911 |
| 가장 큰 실제 bucket 원소 수 | 4,698,112 | 1,174,528 |
| 전체 73 moment의 최대 절대 차이 | 기준 | 1.66534×10⁻¹⁶ |
| Acceptance와 L | 기준값 | 수치적으로 동일 |

1,500개 proposal에서 32개 XOR를 채택했고, 기저 탐색에는 19.6초가 걸렸다. 4-worker ABBA 비교의 wall time은 기존 21.76초, 새 기저 8.55초, 새 기저 9.42초, 기존 43.95초였다. 마지막 실행은 동시 부하 영향을 받았다. 첫 쌍의 약 2.54배 개선은 관측값이며, 모든 회로와 기계에서 보장되는 배수가 아니다. 확실한 현재 수치는 bucket 원소 수 4배 감소와 기대값 동등성이다.

**바로 적용할 구현.** ZIP의 evaluate_basis.py는 저장된 32개 XOR를 적용하기 전에 각 행의 의미와 가역성을 확인하고, 원래 기저의 min-fill 비용도 비교한다. 새로운 후보에서 비용이 더 나쁘면 원래 기저를 선택한다. 매 평가마다 19.6초의 기저 탐색을 다시 하지 말고 incumbent 및 호환되는 근처 후보에 재사용한다.

57개 완전히 관측 불가능한 채널의 factor가 정확히 1이라는 추가 단순화도 확인했다. 이는 552→495 factor의 계산 최적화이며, 해당 물리 게이트를 지워도 된다는 뜻은 아니다. 우선은 검증된 기저 변경을 통합하고 factor 제거는 별도 가격을 확인한다.

**첫 실험과 통과 기준.** 실제 근처 후보 20개에서 계획 비용을 포함한 처리량을 재고, full 73 moment를 기존 evaluator와 비교한다. **중단 기준.** 모델·기저 탐색 비용 때문에 전체 처리량이 낮아지는 후보군에는 적용하지 않는다. 공식 score나 공식 sampler의 실행시간이 좋아졌다고 보고하지 않는다.

증거: basis_width_probe.json, basis_validate.json, evaluate_basis.py와 portable_eval.json. 원래 ABBA 입력은 끝의 newline 하나가 더 있었고 그 bytes도 benchmark_input에 보존했다. 새 portable 검증은 정확한 pinned QASM bytes를 사용한다.

# M03 adjoint에서 버리는 환경 tensor로 국소 후보를 정확히 재평가하기

이미 있는 adjoint는 각 factor의 전체 gradient를 만든 뒤 마지막에 scalar sensitivity로 줄인다. 특정 국소 영역의 tensor 환경을 보존하면, 그 영역만 바뀐 후보는 회로 전체를 다시 수축하지 않고 정확히 가격을 매길 수 있다. [scalar로 줄이는 부분](https://github.com/AutoclickerI/quantumn/blob/42afa8ff01c3999444336f5bb2fe473c1475d6f4/work/lanes/MAIN/sparse/adjoint_ablation.py#L76-L84)

Z가 acceptance, 비정규화 관측량 또는 N=AL이고 다른 factor와 kernel이 그대로일 때,

```math
Z_{\mathrm{new}}
=
Z_{\mathrm{old}}+
\langle E_i,F_i^{\mathrm{new}}-F_i^{\mathrm{old}}\rangle
```

가 정확하다. 여러 factor가 바뀌는 작은 영역은 그 경계를 남기고 외부만 한 번 수축한다. 현재 B/C 전용 boundary cache를 waiting-data guard, 초기화, readout, 작은 timing mutation으로 일반화하는 구현이다. 같은 회로의 재계산 결과를 단순히 저장하는 cache와도 다르다.

재사용의 단위는 QASM 줄 수가 아니다. retiming 하나가 먼 idle interval을 바꾸거나, 측정 기록 하나가 이후 모든 fault signature를 바꿀 수 있다. kernel, detector·rotation·observable 좌표, 독립 채널의 구분, 외부 factor를 기계적으로 비교해 cache를 무효화해야 한다. 기존 division 기반 reverse pass의 positive-factor 조건도 유지한다.

**첫 실험.** v36c 근처의 실제 편집 20개를 모아 모델 차이를 비교한다. 그중 kernel이 그대로이고 변경된 경계가 작은 후보만 environment 경로로 평가한다. 나머지는 정상적인 전체 계산으로 돌린다. 반드시 retiming으로 외부 idle이 달라지는 무효화 대조군도 포함한다.

**성공 기준.** 73개 값이 full contraction과 10⁻¹² 이내로 일치하고, model build와 hashing까지 포함한 전체 처리량이 2배 이상 좋아질 것. 숫자 2배는 제안하는 투자 기준이지 수학적 보장이 아니다. **중단 기준.** 실제 편집 대부분이 넓은 causal cone을 바꾸거나 boundary width가 커지는 경우에는 해당 편집군을 지원하지 않는다.

보장되는 것은 조건을 만족하는 재사용의 등가성이다. 실제 가속 배수와 물리 손실 개선은 아직 측정되지 않았다.

# M04 finite p에서 잡음 채널 두 개의 상호작용을 정확히 구하기

현재 channel adjoint는 하나의 잡음을 완벽하게 만들었을 때의 정확한 변화를 계산한다. 다음 단계는 그 결과를 더하는 대신 **채널 쌍의 교차항**을 구하는 것이다. 이는 이미 P75에 있는 실제 회로 편집 조합의 knapsack과 다르다. 새 검증기나 flag가 어떤 잡음 경로 조합을 겨냥해야 하는지 알려주는 진단이다.

독립 채널의 오류 확률을 각각 λ_i로 배율 조정하면, 비정규화 Z는 λ에 대해 multiaffine이다. 물리 p에 대한 저차 Taylor 근사가 아니다.

```math
Z_{-ij}=Z-g_i-g_j+H_{ij},\qquad
H_{ij}=g_j(\mathrm{base})-g_j(i\ \mathrm{perfect}).
```

채널 i의 factor를 1로 만든 뒤 기존 adjoint를 한 번 더 실행하면 모든 j와의 H_ij를 얻는다. A와 N에 각각 이 식을 적용한 뒤 L=N/A를 계산한다. L 자체를 multilinear라고 취급하면 안 된다.

**첫 실험.** 바꿀 수 없는 마지막 data idle만 고르지 말고, 긴 data wait, A flag가 놓치는 준비 오류, B/C 준비 경로에서 다섯 채널을 고른다. 다섯 reverse pass로 최대 5×552 쌍을 조사하고, 겹치는 pair와 떨어진 pair 12개를 직접 full contraction으로 확인한다. 순위는 Hessian 크기만으로 정하지 말고 정확한 L_-ij, A_-ij로 정한다.

**성공 기준.** 한 채널씩 분석할 때와 다른 유용한 공동 표적이 나오고, 그 표적을 실제 gadget 또는 synthesis 제약으로 연결할 수 있을 것. **중단 기준.** 결과가 이미 알고 있는 terminal noise 순위만 반복하거나 물리 편집 선택을 바꾸지 않으면 더 큰 Hessian을 계산하지 않는다.

잡음 채널을 완벽하게 만드는 것은 물리 gate 삭제와 다르다. 이 진단의 이득을 합산해 구현 가능한 개선률이나 lower bound라고 부르지 않는다. [기존 adjoint의 매개변수와 반사실 계산](https://github.com/AutoclickerI/quantumn/blob/42afa8ff01c3999444336f5bb2fe473c1475d6f4/work/lanes/MAIN/sparse/adjoint_ablation.py#L1-L9)

# M05 검출 조건을 하나씩 지우는 대신 affine syndrome 부분공간을 선택하기

측정 기록 m의 syndrome을 d=Hm⊕b라고 하고, 현재는 d=0일 때 채택한다고 하자. 기존의 named guard 하나를 지우는 것은 매우 제한된 완화다. detector 좌표를 섞은 뒤 rank를 하나 줄이면, 원래 syndrome 0뿐 아니라 원하는 δ도 받아들이는 정책을 만들 수 있다. 가역 기저 변경만 하는 M02와 달리 **채택 사건 자체가 달라진다.**

δ_k=1인 pivot k를 택해 다른 행 i를 row_i XOR δ_i row_k로 바꾸고 k행을 제거하면 원래 syndrome 공간에서 {0,δ}를 받아들인다. 두 syndrome을 구분하는 남은 기록으로 affine 논리 X/Z frame을 붙일 수 있다. 필요한 quantum gate가 없을 수 있다는 점이 매력이다. 하지만 임의의 syndrome→Pauli lookup은 무료로 허용되는 것이 아니다.

이번에 single phase-independent fault가 harmless하다고 보인 세 δ를 실제 v36c에 시험했다. **모두 손실이 나빠졌다.**

| δ의 0-based detector row support | L | A |
|---|---:|---:|
| {17,19} | 1.37175209×10⁻⁴ | .50849917 |
| {8,19} | 9.46147455×10⁻⁵ | .50746450 |
| {21,22,23,55} | 5.47380992×10⁻⁵ | .50457256 |
| 원래 v36c | 4.11515594×10⁻⁵ | .50272784 |

따라서 이 세 no-frame 정책은 닫는다. 이 결과는 single-fault 목록만 보고 정책을 고르면 finite-p cross term을 크게 놓친다는 증거다. 예전 c43 acceptance-only 제거도 현재 v36c에서는 완전한 불변성이 아니었다. A 증가는 약 2.09×10⁻⁶, L 증가는 약 2.70×10⁻¹⁰이었다.

**다음 첫 실험.** 작은 syndrome 부분공간의 joint sector 분포와 각 sector의 네 논리 Pauli 교정 가격을 all-orders로 계산한다. 최적의 자유로운 lookup은 잠재력 oracle로만 쓰고, 실제 선택은 affine frame으로 구현 가능한 정책족에서 한다. acceptance를 확보하는 정책과 그 budget을 쓰는 물리 편집은 함께 재평가한다.

**성공 기준.** 정확한 affine 정책이 직접 L을 줄이거나, 추가 검증과 합친 full circuit에서 순이득을 낼 것. **중단 기준.** 한정한 sector 집합에서 최적 oracle조차 이득이 없으면 그 집합을 닫는다. 이번 세 음성 대조군을 전체 affine 정책족의 불가능성 증명으로 확대하지 않는다.

증거: coarsen_results.json, 각 공식 검증 receipt와 QASM. 세 변형은 개선 후보가 아니라 재실행 가능한 실패 대조군이다.

# M06 T 개수보다 실제 contraction 구조에 맞춘 magic kernel

현재 sparse evaluator는 T-sign 배치 2^n을 명시적으로 만들기 때문에 n≤20을 요구한다. 이것은 대회의 T-count 제한이 아니다. 다른 항목에서 legal FRAME/POSTSELECT frontend를 붙이는 것과도 별개로, **kernel 표현 자체가 합법적인 더 긴 비-Clifford 회로를 막는 문제**다. [n≤20 guard와 dense 상태 생성](https://github.com/AutoclickerI/quantumn/blob/42afa8ff01c3999444336f5bb2fe473c1475d6f4/work/lanes/MAIN/sparse/sparse_walsh.py#L96-L115)

회전 하나의 작은 tensor, 초기·종료 boundary, detector 조건, Pauli noise characteristic을 따로 유지한 뒤 전체 factor graph에서 합산하는 방식으로 바꾼다. 모든 T-sign을 한 번에 거대한 selector로 합치지 않으면 많은 T가 있어도 연결 폭이 작은 가족을 처리할 수 있다. 기존 sparse kernel이 유리한 회로는 그대로 사용한다.

**첫 실험.** 현재 v36c의 73개 값을 재현한 뒤, 알려진 ideal identity rotation pairs를 붙인 >20-T 소형 대조군을 공식 checker로 먼저 검증하고 두 evaluator로 비교한다. 이후 nonlinear acceptance witness나 작은 measured-resource 후보 중 실제 필요한 사례 하나를 연결한다. 의미 없는 identity pair의 물리 성능을 후보 개선으로 세지는 않는다.

**성공 기준.** 합법적이고 실제로 탐색할 가치가 있는 작은-rank >20-T 가족에서, sparse hard stop을 없애고 정해 둔 시간·메모리 안에 정확한 A,N을 얻는 것. **중단 기준.** contraction width가 너무 커져 같은 정밀도의 다른 평가보다 비싸면 해당 가족은 지원하지 않는다.

공식 checker의 propagated magic/postselection X-span에는 **MAX_RANK=22**가 있다. xtim class와 서버 시간 제한도 남는다. T-count 제한을 없애는 것과 공식 processability를 없애는 것은 다르다. [공식 exact checker](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/tprep/exact.py#L33-L76)

현재 EVAL/model.py가 이미 공식 converter, FRAME/POSTSELECT, 조건부 detector와 observable frame을 다루므로, 그 모델을 all-orders 채널에 연결하는 작업을 공통 prerequisite로 삼는 편이 좋다. 별도 parser를 새로 만들어 규칙과 다시 어긋나게 할 이유가 없다. 이 frontend 통합 자체는 P77에 이미 계획된 작업이다.

# M07 B와 C의 상태뿐 아니라 측정 분기와 논리 frame까지 공동 합성하기

B/C 준비기의 목표를 특정 pure stabilizer state 하나로 고정하면, 동일한 최종 accepted output을 주는 다른 measurement instrument를 제외할 수 있다. 대회가 요구하는 것은 accepted noiseless output의 정확성이다. 중간 B/C가 정해진 순수 상태여야 한다는 규칙은 없다. [공식 정확성 조건](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/problem.md#L245-L319)

그러나 C를 나중에 버린다는 이유만으로 기존 순수 상태 계약을 즉시 완화할 수 있는 것은 아니다. C=0의 모든 조건, A₀=1, zero frame, 임의의 encoded input에 대한 같은 작용을 모두 고정하면, 그 조건들이 원래 B/C 상태를 유일하게 정할 수 있다. 공통 GL(3,2)로 Schmidt basis를 바꾸는 것도 동일한 상태의 다른 표기일 뿐이다.

**실제 확장.** C의 측정 basis와 채택 부분공간, B readout 식, 분기별 logical Pauli frame을 함께 변수로 둔다. 여러 C 분기를 받아들이되 그 분기가 출력에 남기는 논리 작용이 합법적인 affine frame으로 처리되는 가족을 찾는다. 특정 준비 입력만 요구할 때에는 그 입력과 보존해야 할 이전 기록에 대한 classical–quantum 계약을 사용한다. 외부와 얽힌 입력까지 다룰 때에는 기존 B/C의 raw Choi 행렬 전체를 고정하는 대신, 외부 suffix·채택 조건·합법적 frame을 합성한 accepted instrument의 작용을 계약으로 정의한다. 허용되는 성공 확률도 명시하며, 상관관계를 버리는 평균 상태 비교로 대체하지 않는다.

**첫 실험.** 현재 회로의 측정·채택·frame 계약을 정확히 쓰고, 가정 하나를 완화한 뒤 허용되는 stabilizer/Choi 공간의 차원이 실제로 늘어나는지 증명한다. 변화가 단순 좌표 재표현인지, 정말 다른 instrument가 가능한지를 구별한다. Choi 표현에서는 양의 준정부호성과 trace 조건까지 포함한다. 선형 제약의 nullspace가 늘었다는 사실만으로 물리 자유도가 생겼다고 판정하지 말고, 기존 것과 다른 허용 instrument 하나 또는 비자명한 feasible family를 구성해 보인다. 그런 다음 작은 하나의 branch-splitting identity를 현재 A,N과 비교한다.

**성공 기준.** 새로운 허용 자원에서 native 접촉 수나 release 시간을 줄인 전체 회로를 만들고 full noise로 이길 것. **중단 기준.** 계약과 물리적 가능성 조건이 여전히 하나의 상태만 허용하거나, 모든 새로운 분기가 unsupported conditional S 또는 physical correction을 필요로 하면 그 계약을 닫는다.

기존 BCPOL과 TERM의 방향을 확장하는 세부 계약이다. 완전히 새 아키텍처라고 주장하지 않는다. 장점은 무작정 solver 변수를 늘리기 전에 실제 자유도가 생기는지 작은 대수 문제로 확인할 수 있다는 것이다.

# M08 마지막 물리 검증에서 여섯 stabilizer를 전부 추출해야 하는지 다시 묻기

공식 채점기는 마지막에 ideal syndrome correction을 한다. 참가자가 그 전에 반드시 완전한 Steane 검증 라운드를 수행해야 한다는 규칙은 없다. 현재 구조가 모든 데이터에 두 종류의 check CX와 마지막 idle을 주는 것은 선택한 아키텍처의 성질이다. [공식 최종 교정](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/problem.md#L320-L354) · [현재 구조](https://github.com/AutoclickerI/quantumn/blob/42afa8ff01c3999444336f5bb2fe473c1475d6f4/docs/reference/circuit.md)

이 후보는 M05와 구별된다. M05는 같은 quantum circuit의 기록 채택 정책을 바꾼다. M08은 **실제로 추출하는 stabilizer subgroup과 그 회로**를 바꿔 CX, ancilla, idle을 줄인다.

6차원 이진 syndrome 공간의 선형 부분공간은 총 **2,825개**뿐이다. dimension별 개수는 1, 63, 651, 1,395, 651, 63, 1이다. 전부 같은 비용은 아니다. 같은 rank라도 어떤 stabilizer 조합을 추출하느냐에 따라 현재 prefix가 남기는 위험한 syndrome과 격자 배치 비용이 달라진다.

**첫 실험.** final verification을 대체할 명확한 boundary를 만들고, 이전 acceptance 기록을 조건으로 syndrome별 확률 a_s와 ideal decoder 이후 손실 numerator n_s를 얻는다. 2,825개 부분공간을 대상으로 채택 예측과 추출 비용의 Pareto 표를 만든다. 유망한 rank 2–5의 작은 subgroup에만 실제 flag/measurement network를 합성한다. 중간에 mixed X/Z stabilizer를 쓰는 경우 같은 물리 record를 중복해 독립 정보로 계산하지 않는다.

과거 ARCH의 no-A와 no-B는 이미 크게 졌다. 그 결과를 반복 실행하는 것이 목적은 아니다. 중간 rank 또는 비대칭·혼합 subgroup의 작은 유한 가족을 조사한다. 어느 경우에도 noiseless accepted output은 judge correction 전에 정확한 T_L이어야 한다.

**성공 기준.** 전체 물리 circuit의 A≥.5와 더 낮은 L. **중단 기준.** 저렴한 subgroup의 실제 네트워크가 없거나 작은 full-noise finalist들이 이득을 보이지 않으면 그 가족을 닫는다. perfect-meter 화면에서 진다는 사실은 연구 예산을 멈출 근거가 될 수 있지만, 모든 물리 구현의 불가능성 증명은 아니다. 조건부 손실에서는 noise 제거가 항상 단조롭게 유리하지 않기 때문이다.

이는 P77의 generic terminal redesign을 구체적이고 유한한 한 가족으로 좁힌 제안이다. 2,825개 RREF basis는 ZIP의 phase_subgroup_verification.json에 포함되어 있다.

# M09 정적 graph embedding 대신 측정과 byproduct를 포함한 자원 합성

6×6 물리 grid가 bipartite라는 것은 진짜 제약이다. 그러나 최종 resource graph가 항상 bipartite여야 한다는 결론은 성립하지 않는다. 준비된 graph state에서 local Clifford와 측정을 수행하면, 남은 qubit의 graph에 삼각형 같은 non-bipartite 관계가 생길 수 있다. 저장소에는 star→triangle의 합법 witness가 이미 있으므로 그 원리를 새 발명으로 세지 않는다. [기존 witness와 닫힌 정적 recipe의 범위](https://github.com/AutoclickerI/quantumn/blob/42afa8ff01c3999444336f5bb2fe473c1475d6f4/docs/FINDINGS.md)

새 실행 단위는 그 witness를 **한 개의 실제 verifier 자원에 대한 noise-aware compiler**로 만드는 것이다. 물리 grid 위 resource graph, 측정할 vertex, 측정 basis, 결과의 Pauli byproduct, 검출 record와 release 시간을 동시에 선택한다. 목표 graph만 맞추는 것으로 끝내지 않는다.

**첫 실험.** 기존 star→triangle witness의 모든 측정 분기와 byproduct를 복원한다. 그 다음 정적 odd-cycle embedding 때문에 닫혔던 작은 checker 하나를 골라, 같은 accepted instrument를 실현하는 grid resource를 만든다. 그 자원 하나에 대해 direct 구현과 전체 noisy boundary response를 비교한다.

**성공 기준.** 측정과 local Clifford, 준비, 추가 idle까지 모두 넣어도 실제 사용 가능한 셀과 접촉·수명 비용이 개선될 것. random measurement의 한 분기만 선택하면 acceptance가 반토막 날 수 있다. 합법적인 Pauli 추적으로 여러 분기를 받아들이는 구현을 우선 검토하되, 최종 절대 acceptance가 0.5 이상이면 일부 분기를 POSTSELECT하는 구현도 허용한다. 이후 T를 통과하는 physical X byproduct가 conditional Clifford를 요구하는 경우도 체크해야 한다.

**중단 기준.** 필요한 byproduct가 합법적인 detector XOR 또는 affine logical frame으로 처리되지 않거나, routing 절약보다 준비·측정·latency가 비싸면 그 자원을 닫는다. endpoint graph의 존재와 fault-tolerant verifier의 존재는 서로 다른 판정이다.

이 항목은 보류된 아이디어의 가격 검증이며, 새로운 물리 이득이 이미 나온 항목은 아니다. 정적 삼각형 불가능성을 동적 측정 방식까지 확대해 해석하지 않는 데 의의가 있다.

# M10 정확한 기준선을 control variate로 쓰는 결합 Monte Carlo

일부 합법적인 instrument는 새 all-orders kernel에서도 너무 넓을 수 있다. 이런 후보를 독립 seed의 큰 MC 여러 번으로만 비교하면 작은 개선을 분별하는 데 계산을 낭비한다. 알려진 기준선의 정확한 기대값과, 두 회로에서 같은 물리 fault를 가능한 한 공유하는 coupling을 이용할 수 있다.

같은 의미를 가진 독립 noise site는 channel ID와 semantic role로 정렬하고 같은 uniform variate를 사용한다. 서로 다른 채널은 각 회로의 올바른 marginal을 유지한다. 단순히 두 회로에 같은 정수 seed를 넣는 것은 이런 coupling이 아니다. 현재 순서 재배치만으로 score가 달라지는 현상이 그 차이를 보여 준다.

τ=L_base로 놓고 각 결합 trial에서

```math
Y_\tau=I_{\mathrm{acc},c}(\ell_c-\tau),\qquad
X_\tau=I_{\mathrm{acc},b}(\ell_b-\tau)
```

를 계산하면 E[X_τ]=0이다. 독립 pilot에서 정한 고정 β에 대해

```math
E[Y_\tau-\beta X_\tau]=N_c-\tau A_c.
```

따라서 그 평균의 부호로 candidate가 기준선보다 좋은지 검정할 수 있다. 이는 L 자체의 편향 없는 ratio 추정기가 아니라 **비교 residual의 편향 없는 추정기**다. population-optimal β에서는 분산이 Var(Y)(1−ρ²)가 된다. pilot의 β가 부정확하면 실제 분산은 증가할 수 있으므로 이 식을 관측된 가속으로 보고하면 안 된다.

**첫 실험.** 답을 all-orders로 아는 v36c 근처 후보들에서 두 회로의 marginal 분포, 평균 residual, 분산과 CPU를 비교한다. 중간 측정 결과를 억지로 같게 맞추지 않는다. 기준선 τ의 수치 오차도 residual의 오차에 포함한다. β는 평가용 sample과 독립된 pilot 또는 올바른 cross-fitting으로 정한다.

**성공 기준.** 같은 불확실도에 도달하는 CPU 비용이 실제로 줄고, 후보 acceptance를 별도로 신뢰성 있게 검증할 것. **중단 기준.** 큰 구조 변화로 두 회로의 결과 상관이 작거나 coupling bookkeeping이 더 비싸면 독립 MC 또는 다른 정확한 evaluator를 쓴다.

P78의 chunk racing은 좋은 seed-0 draw를 더 빨리 찾는 작업이다. 이 후보는 서로 다른 circuit의 **기대값 차이**를 더 정확히 평가하는 작업이다. 연구 estimator가 공식 scoring procedure를 대신하지는 않는다.

# 대회 규칙과 구현이 만든 제약의 구분

공식 problem.md와 실제 parser, noise scheduler, correctness/class checker를 함께 읽었다. 공식 judge의 최신 커밋은 이전 검토 이후 바뀌지 않았다. 핵심은 문서상 자유도가 있는 것과 현재 도구가 그 자유도를 지원하는 것을 구분하는 것이다.

| 질문 | 실제 규칙 | 구현에 주는 의미 |
|---|---|---|
| c1은 반드시 0이어야 하나 | 아니다 | finite p=.001의 전체 N/A로 비교한다 |
| phase-axis의 harmful pair도 0이어야 하나 | 아니다 | M01의 14-T를 보호 성질만으로 미리 제외하지 않는다 |
| noiseless acceptance가 반드시 1인가 | 아니다 | accepted ideal output이 정확해야 하며 noisy 절대 A≥.5다 |
| detector reference는 항상 0인가 | 아니다 | 1 reference와 조건부 deterministic detector도 가능하다 |
| FRAME를 쓸 수 있나 | affine logical X/Z frame은 가능 | 임의 physical correction, nonlinear lookup, S feedforward는 무료가 아니다 |
| POSTSELECT는 금지인가 | 아니다 | 실제 acceptance와 잡음 비용을 전부 계산한다 |
| T gate 수가 20 이하인가 | 아니다 | T≤20은 현재 sparse 구현의 제한이다 |
| 공식 processability 제한이 있나 | 있다 | xtim class와 exact checker의 propagated rank 22 조건을 통과해야 한다 |
| A/B/C라는 고정 block과 순수 중간 상태가 필요한가 | 아니다 | accepted instrument를 기준으로 설계를 확장할 수 있다 |
| output 일곱 qubit의 위치와 순서는 고정인가 | 아니다 | 고유한 일곱 site를 지정할 수 있으나 상태와 검출 식도 일치시켜야 한다 |
| 모든 barrier가 global이어야 하나 | 아니다 | native per-qubit schedule을 정확히 재현해야 한다 |
| 임의 H가 공짜인가 | 아니다 | 지정된 MX/RX folding만 noise와 time 규칙상 예외다 |
| classical register는 256인가 | 아니다 | v36c는 c[286]을 쓰고 공식 검증을 통과했다 |
| 최종 syndrome도 postselect되나 | 아니다 | judge의 마지막 이상적 syndrome은 교정에 쓰이며 전부 받아들인다 |
| CX≤200이나 20초/100만 shots가 공식 규칙인가 | 아니다 | 크기·시간의 공식 제한과 내부 proxy를 구분한다 |

진짜 제약은 36개 qubit의 6×6 nearest-neighbor grid, 허용된 1-qubit gate와 CX만의 2-qubit 연산, conditional quantum gate 금지, 정확한 accepted noiseless T_L, A≥.5, 200 KB/5,000명령/measure+reset≤1,000, 서버 1시간 등이다. [연산·주석·잡음 규칙](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/problem.md#L112-L319) · [제출 제한](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/problem.md) · [공식 exact guard](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/tprep/exact.py#L33-L76)

현재 문서는 이 자유도 다수를 이미 알고 있다. 남은 주요 자기 제약은 **15-T와 rank-5의 생성기 선택**, **zero-frame·A₀≈1·global barrier만 지원하는 빠른 평가 경로**, **중간 pure-state 계약**, **고정된 full-rank terminal verification**이다. 이를 공식 규칙이라고 취급하지 않으면 된다.

스케줄에도 주의가 필요하다. DETECTOR 주석을 앞뒤로 옮기는 것만으로 measurement가 빨라지지 않는다. converter는 관련 record가 생긴 뒤에 detector를 배치하고, scheduler는 native barrier metadata에 따라 시간을 정한다. 전역 barrier를 지우면서 reset 시점을 다시 설계하지 않으면 qubit가 일찍 준비되어 오히려 오래 idle할 수 있다. [공식 scheduler](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/tprep/noise.py#L54-L123) · [QASM 변환](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/tprep/qasm.py#L210-L264)

# 10⁻⁵보다 낮은 목표를 어떻게 해석해야 하나

현재 STANDARD p=.001 규칙 아래에서는 **진짜 기대 손실이 10⁻⁵ 미만인 회로는 현행 증명과 양립하지 않는다.** 독립적으로 rational certificate를 다시 실행한 결과는 다음과 같다.

```math
L\ge 1.162\times10^{-5},\qquad
L_{\mathrm{relaxed,min}}
=1.1620296389206688204\ldots\times10^{-5}.
```

각 출력에서 마지막과 그 직전의 관측할 수 없는 noise 성분을 독립 terminal depolarizer로 분리한다. 해당 유효 확률은 q_eff=p−16p²/75다. 그 뒤에 임의의 조건부 입력 상태, 모든 64 syndrome sector와 judge의 실제 decoder를 허용해 가장 유리한 경우를 최적화한다. 마지막 tick의 output-output CX 21개 경우도 따로 확인했다. reset·first-use·마지막 측정 뒤 idle 예외·affine logical frame에서 이 증명을 피하는 사례는 발견되지 않았다. [현재 증명](https://github.com/AutoclickerI/quantumn/blob/42afa8ff01c3999444336f5bb2fe473c1475d6f4/work/lanes/MAIN/spec/bound_audit/quantumn_subthreshold_bound_audit/PROOF.txt)

| 수치 | 의미 | 말해 주지 않는 것 |
|---|---|---|
| 7.44545×10⁻⁶ | 마지막 tick만 남긴 더 느슨한 relaxation | 전체 circuit의 달성 가능성 |
| 1.16203×10⁻⁵ | 두 tick의 독립 noise를 포함한 보편적 하한 계산 | 실제 구현이 이 수치에 도달한다는 보장 |
| 약 2.567×10⁻⁵ 또는 2.884×10⁻⁵ | 특정 Steane-type ending의 범위가 정해진 비용·차수 분석 | 모든 합법적인 circuit의 보편적 하한 |
| 선택된 seed-0 score | 유한 표본의 공식 경쟁 점수 | 동일한 circuit의 기대 손실 |

따라서 이 보고서는 10⁻⁵ 미만을 보장하는 방법을 만들어 내지 않는다. 실행 목표는 현재 4.11516×10⁻⁵를 낮추고, 더 큰 개선이 필요할 때 full Steane ending의 구조를 바꾸는 것이다. M01은 prefix와 release 구조를 바꾸는 가장 구체적인 새 seed이고, M07–M09는 더 큰 structural gap을 겨냥한 gated 연구다.

현재 GOAL.md도 이미 이 보편적 하한을 인정한다. 이를 새로 팀의 잘못으로 지적하지 않는다. [현재 목표의 정확한 표현](https://github.com/AutoclickerI/quantumn/blob/42afa8ff01c3999444336f5bb2fe473c1475d6f4/docs/GOAL.md)

추가 원칙: 어떤 영역의 잡음을 끈 circuit의 L을 항상 실제 최적값의 lower bound로 쓰면 안 된다. postselection 때문에 잡음 제거와 조건부 fidelity가 단조 관계가 아닐 수 있다. 진짜 pruning certificate에는 모든 허용 boundary state와 classical correlation을 포함하는 relaxation, 그리고 목적값의 하한 증명이 필요하다.

# 다시 권하지 않는 방법과 이번 음성 결과

후보 수를 맞추기 위해 이미 닫힌 방법을 새 이름으로 나누지 않았다. 다음은 보고서의 주요 후보에서 제외하거나 첫 대조군 수준으로만 둔다.

| 방법 | 제외 또는 제한 이유 |
|---|---|
| live population의 register 256 문제를 다시 최우선으로 고치기 | 현재 문서는 live 경로 수정 사실을 명시하며 그 소스는 공개 tree에 없다 |
| 기존 adjoint를 처음 도입하기 | 이미 통합됐다. M03·M04는 그 다음 확장이다 |
| ordinary knapsack 또는 모든 single gain의 합 | interacting objective가 이미 P75에 있고 single gain은 가산적이지 않다 |
| common GL(3,2) Schmidt basis만 바꾸기 | 같은 B/C pure state의 재표현이다 |
| 단순 30가지 Fano labeling 탐색 | ENDSTATE가 이미 그 labeling classes를 열거했다 |
| A 또는 B 전체를 없애기 | 과거 ARCH의 실제 실패가 있고 큰 first-order loss가 발생했다 |
| 마지막 idle을 Pauli gate로 교체하기 | STANDARD에서 같은 강도의 depolarization이 붙는다 |
| 독립적인 acceptance-only factor를 찾아 삭제하기 | 현재 v36c의 graph 및 basis-independent direct-sum 검사에서 그런 성분 0개 |
| 73개 contraction을 합치면 73배 빨라질 것이라고 가정하기 | 실제 shared-DAG 조사에서 bucket work 절감은 약 6.17%뿐이었다 |
| 이번에 시도한 세 syndrome coarsening을 승격하기 | 모두 full-noise expected L이 악화됐다 |

독립 auxiliary component가 없다는 결과는 모든 acceptance-only 회로 편집의 부재를 증명하지 않는다. 특별한 확률 항등식, 채널의 latent factorization, 실제 스케줄 변경, accepted-kernel cancellation은 별개의 문제다. 다만 지금 즉시 공짜 acceptance를 얻는 쉬운 graph 분해는 발견되지 않았다.

또한 v34에서의 c43 불변성, v35에서의 guard 가격, 오래된 layout의 UNSAT를 v36c에 그대로 적용하지 않는다. 실제 exterior가 바뀌면 같은 이름의 편집이라도 다시 계산해야 한다.

# 구현 에이전트에게 줄 작업 순서

**첫 단계는 M02를 도입하면서 M01의 whole-circuit seed를 만드는 것이다.** M02는 현재 receipt가 있고, M01은 지원 집합·부호·두 격자 조각을 이미 제공한다. 새 에이전트가 일반적인 문헌 탐색부터 다시 시작할 필요가 없다.

1. 현재 HEAD와 official judge pin을 확인한다. HEAD가 바뀌었다면 이 ZIP의 v36c 수치를 새 incumbent의 수치라고 부르지 않는다.
2. verify_bundle.py와 표준 라이브러리 phase verifier를 실행해 파일·대수 검증을 끝낸다.
3. evaluate_basis.py를 현재 evaluator에 연결한다. 저장된 기저는 의미 검사 후에만 재사용한다.
4. M01의 historical f14_1 또는 current-coordinate 14-T 지원 중 하나를 선택하고, 원래 Clifford scaffolding에 덧붙이지 말고 encoder·parity 경로·측정·release를 함께 재합성한다.
5. native schedule, accepted ideal state, class를 먼저 확인하고 완전한 잡음 모델에서 A,N,L을 평가한다.
6. 작은 실제 편집 모음으로 M03의 환경 cache를 검증한다. 그 다음 M04에서 새로운 물리 표적이 나오는지 본다.
7. M05–M10은 각 항목의 첫 gate를 통과한 뒤에 확대한다. 기존 P75/P77/P73과 담당 영역을 중복시키지 않는다.

평가 순서는 **동일 입력과 버전 확인 → native schedule 및 ideal correctness → full-noise 기대값 → runtime → 공식 sampled check**다. 계산상 빠른지만 중요한 M02에는 새 physical score 개선을 요구하지 않는다. M01·M05·M07–M09에는 반드시 full circuit과 절대 A≥.5를 요구한다.

숫자를 보고할 때에는 baseline과 candidate의 QASM hash, 사용한 source/evaluator/judge pin, A, N, L, kernel 생략 오차, native depth/CX, actual runtime을 함께 기록한다. 새로운 물리 이득은 exact expectation 비교로 확인하고, 공식 MC 한 번의 최저값을 그 증거로 대체하지 않는다. 공식 경쟁 점수 최적화는 별도의 운영 목표로 계속 관리할 수 있다.

이 검토에서는 원격 계산 실행이나 대회 제출, 저장소 push를 하지 않았다. ZIP은 검토·재현·구현을 위한 handoff다.

# 재현 자료와 검증 범위

패키지의 README.md는 설치와 실행 명령을, IMPLEMENTATION_AGENT.md는 영문 작업 brief를, TASKS.json은 열 개 작업의 의존성·첫 gate·중단 조건을 담는다. REPORT_KO.md는 이 보고서의 전체 사본이다.

핵심 자료는 다음과 같다.

- 정확한 v36c QASM/JSON과 현재 sparse evaluator, source provenance.
- 공식 judge 코드와 고정 버전 dependencies.
- v36c baseline 73 moment 및 공식 100만-shot 검증.
- 32개 detector XOR와 모든 73 moment 비교, portable evaluator.
- 64개 phase-family 분포, 15개 rank-4 14-T support, 부호·rational noise certificate.
- 18-CX 및 24-CX의 14-T 격자 fragment와 32개 입력에 대한 위상·복원 검증.
- 세 실패 coarsening과 c43 대조군의 QASM, 기대값 및 공식 검증.
- factorization 음성 결과, 57개 identity-factor 분석.
- 2,825개 final stabilizer subgroup의 RREF 목록.
- 보편 하한의 rational 검증 및 SHA256 manifest.

**범위.** 14-T fragment는 제출 가능한 완성 QASM이 아니다. phase-only certificate는 noise를 제한한 계산이다. 내부 detector 기저 변경은 물리 회로를 개선하지 않는다. 새 evaluator 기능 M03, M04, M06, M10은 정확한 수학적 경로와 구현 gate를 제공하지만 측정된 가속을 아직 갖지 않는다. 이 구분을 유지한 채 M01의 전체 가격을 얻는 것이 다음 핵심 작업이다.

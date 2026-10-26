quantumn 최적화 감사 / 2026-10-26

먼저 REPORT_KO.html을 여세요. 인터넷 없이 읽을 수 있는 전체 한국어 보고서입니다.
코드 근거 링크는 다음 커밋에 고정되어 있습니다.
https://github.com/AutoclickerI/quantumn/tree/1d56e6bff233f804f76c2671b37854b92b3ffabc

결과
- baseline v37f: L=3.6305606234064893e-5, A=.5034645094225926
- q17 herald: L=3.6222163563820873e-5, A=.5026256487449868
- c309 parity: L=3.6297341396516954e-5, A=.5023237751837697
- 결합: L=3.621389883196312e-5, A=.5014868151707284
- 모두 405 CX / 48 native ticks. 결합 기대 손실 감소 0.25259846%.
- 공식 xtim 검증, 실제 judge 시간, seed-0 1e8 점수 및 제출은 수행하지 않았습니다.
- 이 값들은 모든 잡음 차수를 반영한 기존 평가기의 결과입니다.
  coefficient cutoff의 생략 상한은 보고했지만, 모든 floating-point roundoff의 인증은 아닙니다.

주요 파일
REPORT_KO.html : 10개 방법, 제약 감사, 부정 결과, 다음 실험과 근거
circuits/herald_q17_plus_c309.qasm + .json : 확인한 결합 후보
circuits/herald_q17.qasm + .json : reset retiming + 새 측정
circuits/parity_c309.qasm + .json : 기존 record detector 추가
audit_reproduce.py : pinned repo 평가기를 이용한 재현, raw 6 stabilizer / T 가환성 / single fault / all-orders
build_reset_herald.py : baseline에서 q17 변경을 다시 만드는 생성기
results/ : 기대값, 해시, 검증 수치와 negative pilot 요약
experiments/ : parity 실험 및 거절된 회로들의 재현용 QASM/JSON (제출 후보 아님)
manifest.json : source/파일 provenance와 SHA256

재현 환경
Linux, Python 3.12 및 NumPy 2.x에서 실행했습니다. numpy.bitwise_count가 필요합니다.
기존 pinned quantumn checkout의 환경을 사용하세요. 공식 xtim이 없는 환경에서도 이 재현은 됩니다.
--processes 4는 multiprocessing fork를 사용합니다. 메모리가 부족하면 1로 줄이세요.
평가기의 실제 시간은 host, basis, 병렬성에 따라 바뀌며 공식 judge 속도와 다릅니다.

재현 예시 (이 압축을 푼 디렉터리에서)
python audit_reproduce.py --repo /path/to/quantumn --circuit circuits/herald_q17_plus_c309.qasm --processes 4 --out results/local_replay.json
python audit_reproduce.py --repo /path/to/quantumn --circuit /path/to/quantumn/work/lanes/MAIN/v37f.qasm --processes 4 --out results/local_baseline.json
python build_reset_herald.py /path/to/quantumn/work/lanes/MAIN/v37f.qasm circuits/rebuilt_herald.qasm --qubit 17 --tick 30

생성기와 재현기는 원격 제출을 하지 않습니다. rebuild는 지정한 출력 QASM/JSON만 씁니다.
audit_reproduce는 checkout을 수정하지 않고 --out에 지정한 결과만 씁니다.
보존된 JSON에는 이 세션의 절대 경로가 provenance로 남아 있습니다. 재현 시 자신의 경로를 지정하세요.

새 후보의 공식 검증 순서
1. QASM과 ordered data_qubits를 함께 사용합니다.
2. 공식 format/class/correctness 및 runtime을 검사합니다.
3. seed0, 1e8의 acceptance와 score를 실제 확인합니다.
4. 전체 기대값과 공식 표본 점수를 구분해 현재 최고 기록과 비교합니다.
5. 제출 여부는 기존 팀 운영 절차에 따릅니다. 이번 감사에서는 제출하지 않았습니다.

한계
모든 63개 residual parity 및 모든 조합을 all-orders로 검사하지 않았습니다.
7 hybrid endings와 3 coarsening의 실패는 그 recipe만 배제하며 전역 불가능을 뜻하지 않습니다.
연구 후보 3-10은 구체적 근거와 검증 조건이 있는 후속 방법이며 실제 gain은 아직 미측정입니다.
원본 repository 전체를 포함하지 않습니다. 소유한 pinned checkout을 사용해 재현하세요.

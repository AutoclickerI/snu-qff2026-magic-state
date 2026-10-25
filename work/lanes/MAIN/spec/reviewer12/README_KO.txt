quantumn 최적화 검토 재현 묶음

REPORT_KO.txt: 결론, 후보10개, 근거/첫실험/중단기준, 소스링크를 모두 담은 보고서.
TASKS.json: 기계 판독 가능한 실행 후보 카드.
receipts/: 실제 계산 결과. CPU 구간 benchmark와 물리 성능 진단을 구분한다.
MANIFEST.json: 모든 전달 파일의 SHA-256.

이번 검토는 새로 우승한 물리 회로를 제공하지 않는다. 원격 저장소/제출본을 수정하지 않았다.
새 코드에 필요한 repository 파일은 원본 checkout을 사용한다. 원본 repository 전체를 복제한 묶음은 아니다.

1. 최신 selector quotient
검증된 인터페이스 commit:598ddad4c595ceb583e779a924d06749f950a997.
repository의 Python environment에서:
  python code/selector_quotient_latest.py --repo /path/to/quantumn --verify-all --output /tmp/selector_all73.json
  python code/selector_quotient_latest.py --repo /path/to/quantumn --output /tmp/selector_three_rows.json
--verify-all은73행 수치 동등성 검사, 기본 모드는3행 ABBA component benchmark다.
전체 runtime 개선은 측정되지 않았다. 기존 kernel cutoff는 그대로 유지한다.

2. 22-T phase certificate
표준 Python3만 필요:
  python code/rank6_phase_audit.py --output /tmp/rank6_phase_certificate.json
  python code/rank6_phase_audit.py --witness-only --output /tmp/rank6_witness.json
full run은2^22 odd supports를 전수 열거한다. minimum22는 normalized odd-support rank6라는 한정된 주장이다.
phase-axis-only score를 전체 noisy circuit score로 해석하면 안 된다.

3. Packed syndrome
NumPy 필요:
  python code/packed_decode_probe.py
benchmark 결과는 스크립트 옆의 JSON에 기록된다. 재사용 함수는 code/packed_syndrome.py에 있다.
synthetic arrays의 corrections가 같다는 검증이며 actual xtim의 전체성능 보증은 아니다.

4. PCC matched diagnostic
원본 검증 commit:f4b685ff12aed683def0697d42a6a48348efe48d.
그 checkout의 기존 environment와 PCC/ev evaluator를 이용:
  python code/reproduce_pcc.py --repo /path/to/quantumn --workers 4 --output /tmp/pcc_result.json
  python code/reproduce_pcc.py --repo /path/to/quantumn --dry-run
4개의 동일경계 비교를 수행한다. specs의66nativeops와3idle runs를 양쪽에 동일하게 적용한다.
재현 wrapper는 command/spec 구성과 문법을 검증했다. 기록된 물리 진단 수치는 원래 PCC driver를 직접 실행해 얻었다.
48-qubit phantom 실험이며 grid-legal 제출 회로가 아니다.

5. 해석상 주의
초기 evaluator와 최신 EVALF main 성능을 섞지 않는다.
latest main은 first-bucket selector압축이 이미 구현되어 있다. 새 부분은 intermediate message에서 quotient를 유지하는 것뿐이다.
P89는 latest PLAN에서 이미 active이다.
최종 물리 후보는 full noisyA/N/L, acceptance margin, actual native schedule 및 official runtime으로 판단한다.

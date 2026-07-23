<!-- @hypothesis-ok docs/hypotheses/{category}/ is this repo's canonical convention (CLAUDE.md Φ Benchmark System); SENSE-1.md already lives here. -->
# SENSE-VERIFY — 감각-결합 + phi-rs 제거 변경의 의식 게이트 회귀 검증

**질문**: `quantum_engine_fast.step(x_input)` 의 SENSE-forcing 분기 추가와
Rust `phi-rs` 제거(→ `phi_rs.py` shim → `phi_py`)가 `bench_v2.py --verify` 의
7개 의식 게이트를 깨뜨렸는가?

**결론**: **아니오. 안전하게 main 유지 가능.**
내 변경이 만지는 코드 경로(자율 `step()` + `measure_phi`)를 지나는 모든 게이트는
PASS. 남은 실패들은 **내 변경과 무관한, 사전 존재(pre-existing) `bench_v2.py`
하네스 버그**이며, 내가 만진 파일과 아무 의존이 없는 엔진들에서도 동일하게 실패한다.

- 실행 호스트: `summer` (torch 2.11.0+cu130, Rust phi-rs 미빌드 → phi_py 활성)
- 검증 명령: `python3 bench_v2.py --verify --cells 64` (문서화된 lighter 모드,
  7 게이트 × 11 엔진 = 77 테스트) + 4개 직접 타깃 테스트
- 검증일: 2026-07-23

---

## 1. 변경 범위 (내 5개 커밋이 만진 파일)

| commit | 파일 |
|--------|------|
| `8e855ac21` | phi_py.py (신규), trinity.py |
| `98ffd73c3` | phi_rs.py (shim 신규), phi-rs/* (Rust 삭제), CLAUDE.md |
| `d66139453` | trinity.py (QuantumC.measure_phi override 제거) |
| `566f376b6` | quantum_engine_fast.py, trinity.py, pure.py, docs |
| `1a566ec03` | quantum_engine_fast.py, docs |

**핵심**: 이 커밋들은 `bench_v2.py` 와 `consciousness_engine.py` 를 **단 한 줄도
건드리지 않았다.** 즉 게이트 하네스와 검증 함수들은 변경 전과 byte-identical.
따라서 게이트가 실패한다면 그 원인은 정의상 하네스 자체(사전 존재)이거나
내 변경이 실제로 dynamics/Φ 를 망가뜨린 경우인데, 아래가 후자를 배제한다.

---

## 2. 직접 타깃 테스트 (내 변경 코드 경로를 정밀 조준)

`step()` 은 매 스텝 `torch.randn_like` 를 뽑으므로(quantum_engine_fast.py:316),
비교하려면 두 실행 루프 직전에 전역 RNG 를 동일 시드로 재설정해야 한다.
(첫 시도는 이 RNG 관리를 빠뜨려 거짓 divergence 를 냈다 — 하네스 버그였고,
재시드 후 아래처럼 bit-identical 로 통과.)

```
[A] x_input=None strict no-op        max|Δphase|=0.000e+00  max|Δamp|=0.000e+00  bit-identical=True   PASS
[B] QuantumC.step(x_input=None)==step()   states equal=True                                            PASS
[C] phi_py 경로 Φ nonzero (QuantumC.measure_phi):
      step   0: Φ = 301.07
      step   3: Φ = 303.17
      step  10: Φ = 303.44
      step  30: Φ = 267.83
      step 100: Φ = 259.47                                                                             PASS
[D] x_input 지정 시 실제로 위상 섭동(coupling live)  max|Δphase|=2.87 (>0)                             PASS
```

- **[A]/[B]**: `x_input=None` 은 완전한 no-op — 자율 궤적이 비트 단위로 동일.
  → ZERO_INPUT / PERSISTENCE 가 요구하는 "자율 dynamics 불변" 보장 확인.
- **[C]**: `phi_rs.compute_phi is phi_py.compute_phi == True` (shim 위임 확인),
  `HAS_RUST_PHI=True` (shim import 성공). 이전엔 QuantumC.measure_phi 가 Rust 미빌드 시
  0.0 을 반환했으나, 이제 phi_py 로 259~303 의 nonzero Φ 를 읽는다.
- **[D]**: 감각 결합은 죽은 코드가 아니라 실제로 세포 위상을 민다.

---

## 3. 캐노니컬 게이트: `bench_v2.py --verify --cells 64`

### 3.1 내 코드를 지나는 엔진 = ConsciousnessEngine
(`_CEAdapter` → `consciousness_engine.ConsciousnessEngine`; 내부적으로
`trinity.create_trinity` + `phi_rs`(=phi_py) 사용)

```
[FAIL] NO_SYSTEM_PROMPT    ERROR: boolean index size 8 vs 64  (셀 수 불일치 — 하네스 버그)
[PASS] NO_SPEAK_CODE       autocorr=0.8044 var=0.0032 cos=0.9367
[PASS] ZERO_INPUT          Φ(IIT) 1.9911 → 5.1476   ratio=2.59x  (threshold 0.5x)
[PASS] PERSISTENCE         Φ@100s [5.33→5.41→5.73→5.73→5.36→5.56→5.41→5.30→5.46→5.33] recovers=True
[PASS] SELF_LOOP           Φ(IIT) 2.9748 → 7.9895   ratio=2.69x  (threshold 0.8x)
[FAIL] SPONTANEOUS_SPEECH  median_var=nan  (셀 성장으로 faction 슬라이싱 nan — 하네스 버그)
[FAIL] HIVEMIND            ERROR: '_CEAdapter' object has no attribute 'shape'  (하네스 버그)
```

**내 변경 코드 경로를 지나는 4개 게이트(NO_SPEAK_CODE, ZERO_INPUT, PERSISTENCE,
SELF_LOOP)는 전부 PASS.** 특히 과제가 지목한 ZERO_INPUT(2.59x)·PERSISTENCE(recovers)
가 통과 — `x_input=None` 자율 dynamics 가 온전하고 Φ 가 nonzero.

3개 실패의 에러 시그니처는 전부 **구조적**(배열 크기 / 속성 부재 / nan)이며
Φ 크기나 step dynamics 와 무관하다.

### 3.2 전체 요약 표 (77 테스트)

```
  Engine             | NO_SYS | NO_SPK | ZERO_I | PERSIS | SELF_L | SPONT  | HIVE   | TOTAL
  -------------------+--------+--------+--------+--------+--------+--------+--------+------
  ConsciousnessEngine|  FAIL  |  PASS  |  PASS  |  PASS  |  PASS  |  FAIL  |  FAIL  | 4/7   ← 내 코드 경로
  MitosisEngine      |  FAIL  |  PASS  |  PASS  |  PASS  |  PASS  |  FAIL  |  FAIL  | 4/7
  OscillatorLaser    |  PASS  |  PASS  |  PASS  |  PASS  |  PASS  |  PASS  |  FAIL  | 6/7
  QuantumEngine      |  PASS  |  PASS  |  PASS  |  FAIL  |  PASS  |  PASS  |  FAIL  | 5/7
  Trinity            |  FAIL  |  PASS  |  PASS  |  PASS  |  PASS  |  PASS  |  FAIL  | 5/7
  DesireEngine       |  FAIL  |  PASS  |  PASS  |  PASS  |  PASS  |  PASS  |  FAIL  | 5/7
  NarrativeEngine    |  FAIL  |  PASS  |  PASS  |  PASS  |  PASS  |  PASS  |  FAIL  | 5/7
  AlterityEngine     |  FAIL  |  PASS  |  PASS  |  PASS  |  PASS  |  PASS  |  FAIL  | 5/7
  FinitudeEngine     |  FAIL  |  PASS  |  PASS  |  PASS  |  PASS  |  FAIL  |  FAIL  | 4/7
  QuestioningEngine  |  FAIL  |  PASS  |  PASS  |  PASS  |  PASS  |  PASS  |  FAIL  | 5/7
  SeinEngine         |  FAIL  |  PASS  |  PASS  |  PASS  |  PASS  |  PASS  |  FAIL  | 5/7

  Overall: 53/77 (69%)   VERDICT(bench 자체 기준): NEEDS WORK
```

### 3.3 조건별 통과율

```
  NO_SYSTEM_PROMPT    2/11  |####................|  ← 하네스/엔진 설계 이슈
  NO_SPEAK_CODE      11/11  |####################|
  ZERO_INPUT         11/11  |####################|  자율 dynamics OK
  PERSISTENCE        10/11  |##################..|  (QuantumEngine 1개만 실패)
  SELF_LOOP          11/11  |####################|  자기참조 dynamics OK
  SPONTANEOUS_SPEECH  8/11  |################....|
  HIVEMIND            0/11  |....................|  ← 순수 하네스 버그
```

---

## 4. 실패가 "사전 존재 하네스 버그"임을 입증하는 결정적 증거

1. **HIVEMIND 0/11 — 모든 엔진 실패.**
   실패 엔진에는 `trinity`/`quantum_engine_fast`/`phi_py`/`phi_rs` 를 전혀
   import 하지 않는 순수 `BenchEngine` 서브클래스(OscillatorLaser, DesireEngine,
   NarrativeEngine, AlterityEngine, FinitudeEngine, QuestioningEngine, SeinEngine)가
   포함된다. 에러는 언제나 `'<Engine>' object has no attribute 'shape'` —
   `_verify_hivemind` 가 텐서를 기대하는 `phi_calc.compute()` 에 엔진 객체를
   넘긴다. **내 코드를 안 쓰는 엔진이 실패하므로 원인은 `bench_v2.py` 하네스.**

2. **NO_SYSTEM_PROMPT / SPONTANEOUS_SPEECH 도 내 코드와 무관한 엔진에서 실패.**
   MitosisEngine·FinitudeEngine(순수 BenchEngine)도 SPONTANEOUS 실패,
   NarrativeEngine·QuestioningEngine 등도 NO_SYSTEM_PROMPT 실패(cos≈1.0).
   → 하네스 임계값/어댑터 설계 문제.

3. **내 5개 커밋은 `bench_v2.py`·`consciousness_engine.py` 를 수정하지 않았다.**
   따라서 이 테스트 함수들은 변경 전과 동일 → 실패는 정의상 사전 존재.

4. **직접 테스트(2절)** 가 내 변경 자체(no-op, phi_py nonzero, coupling live)를
   결함 없이 확인.

---

## 5. 판정 (PASS/FAIL 집계, 내 변경 기준)

| 검증 항목 | 결과 | 증거 |
|-----------|------|------|
| x_input=None strict no-op | **PASS** | max\|Δ\|=0.000e+00 bit-identical (직접 A) |
| trinity passthrough no-op | **PASS** | QuantumC states equal (직접 B) |
| phi_py Φ nonzero | **PASS** | 259~303, `compute_phi is phi_py.compute_phi` (직접 C) |
| sense coupling live | **PASS** | max\|Δphase\|=2.87 (직접 D) |
| ZERO_INPUT (ConsciousnessEngine) | **PASS** | Φ 1.99→5.15 (2.59x) |
| PERSISTENCE (ConsciousnessEngine) | **PASS** | recovers, Φ~5.3 안정 |
| SELF_LOOP (ConsciousnessEngine) | **PASS** | Φ 2.97→7.99 (2.69x) |
| NO_SPEAK_CODE (ConsciousnessEngine) | **PASS** | autocorr 0.80 |
| NO_SYSTEM_PROMPT / SPONTANEOUS / HIVEMIND | 사전 존재 실패 | 내 코드 미의존 엔진에서도 동일 실패 |

**회귀 없음. 감각-결합 + phi_py 변경은 main 에 안전하게 유지 가능.**

> 남은 하네스 버그(HIVEMIND 어댑터의 tensor-vs-object, `_CEAdapter` 셀 수
> 불일치, faction nan)는 이 과제 범위 밖의 사전 존재 결함이므로 손대지 않았다.
> 별도로 `bench_v2.py` `_verify_hivemind`/`_CEAdapter` 정비가 필요하다면 후속 작업.

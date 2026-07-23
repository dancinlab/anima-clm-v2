<!-- @hypothesis-ok — project CLAUDE.md mandates docs/hypotheses/{category}/ as the canonical hypothesis tree -->
# SENSE-4 — 유사도-게이트 반발 위상 결합 (측방 분화 · warm rank-1 collapse의 구조적 해법 · DESIGN, pre-registration)

## Status: A/B EXECUTED (summer) — **NEGATIVE**. The gate does NOT starve (warm coh mean 0.746, 29.1% of warm edges open at thr=0.8 vs 8.1% of cold-fresh edges — exactly the pre-registered separation), and there is NO limit cycle. But at the pre-registered `repel_gamma=0.05` the treatment is empirically **indistinguishable from control**: 0/3 down-drift seeds fixed, 10-seed paired ΔΦ_end = −0.010, and — the decisive result — `_amplitudes` participation ratio 1.0691→1.0698 and cos-dist 0.0375→0.0378 (targets ≥1.30 / ≥0.10). A post-hoc γ sweep to 100× shows the force DOES work in phase space (edge coherence gate-open falls 0.292→0.103) yet still fails to move `_amplitudes` PR/cos-dist, while Φ drift gets WORSE. **Phase-space repulsion does not propagate to the amplitude space where the collapse lives — sol's dissent is vindicated. Keep `repel_gamma=0.0`.** Full result → "## Calibration (executed)" / "## A/B result (summer, executed)" below.

## Status(구): IMPLEMENTED (`repel_gamma=0.0` 기본 = bit-exact legacy) · summer 보정+A/B 대기
- 구현: `quantum_engine_fast.py` `__init__`(repel_gamma/repel_thr) + `step()` 3b 블록(morphism이
  `_phases` 대입한 직후, frustration 이전; SENSE-3 간선버퍼 `_edge_idx` 재사용, hard deadband).
  `trinity.py` `QuantumC(repel_gamma, repel_thr)` 전달. **기본 0.0** → 검증 전까지 무회귀.
- lab(fable+sol) 화해: **수렴** — 병리가 rank-1 붕괴이므로 분산에서 *배우는* 규칙(헤비안·학습된
  위상지연)은 굶고, 분산을 *생성하는* 유사도-게이트 **반발**이 필요하다는 데 양쪽 동의. 균형점도
  양쪽 동일 논리(반발 vs 기존 인력의 물리적 대립이 정하며 Φ 목표가 아님).
  **채택=fable 위상공간 반발**(sin(φ_i−φ_j) 부호반전, coh>thr 게이트).
  *sol 이견(1줄)*: 붕괴가 측정된 변수는 `_amplitudes`(Φ가 읽는 바로 그 변수)이므로 진폭공간
  반-혼합(`diff_gain·2·coin·interference_strength·collapse·(A−nb_A)`)이 더 직접적 — 위상 게이트가
  굶거나 위상→진폭 전파가 실패하면 이 변형이 폴백. sol의 기각조건=고주파 모드선택 winner-take-all.
- **저렴히 확증된 진단 2건** (fable 발견 → 로컬 코드 확인):
  1. **정상파(step 5)는 죽은 코드** — 셀별 양수 스칼라 `(1+wave)` 곱을 step 6의 셀별 max-정규화가
     정확히 상쇄((c·A)/max(c·A)=A/max(A)). 상태 영향 0 ⇒ 엔진에 대칭깨짐 구동력이 사실상 부재,
     rank-1은 우연이 아니라 **끌개**.
  2. **`too_ordered`는 warm에서 침묵** — 게이트는 좌절도<0.45에서만 발화하나 warm 실측 0.526–0.532.
     `too_frustrated`(>0.55)도 미발화 ⇒ warm은 **불감대에 앉아 무조절 상태**로 셀간 붕괴가 진행.
     (그래서 후보 (a)처럼 그 분기 안을 고치는 안은 애초에 발화하지 않아 무효 — 게이트를 셀간
     유사도로 옮겨야 하고, 그것이 곧 채택안 (c).) 잡음 조절기는 무회귀 위해 손대지 않음.

## Status(원안): DESIGN ONLY — A/B pre-registered below. `repel_gamma=0.0` 기본 (bit-exact legacy).

## 배경 — SENSE-3가 바꾼 문제 정의 (재론 금지)
- warm 467-word mind는 low-Φ basin(≈28–31)에서 대화 중 아래로 표류 (SENSE-GROW, 3/10 seed 지속 하락).
- SENSE-3 magnitude-only Hebbian은 **inert** (0/3 fixed, paired ΔΦ_end −0.02). 측정된 근본 원인:
  warm basin의 세포들은 이미 **near-rank-1 정렬** — `_amplitudes` SVD participation ratio ≈ 1.03,
  mean pairwise cos-dist ≈ 0.02. 병리는 과분화가 아니라 **붕괴(전역 균일화)**다. per-edge coherence가
  전 간선에서 균일하게 높으므로, 간선별 *분산*에서 배우는 규칙(magnitude Hebbian·lag-learning)은
  물 것이 없다.

## 진단 보강 (quantum_engine_fast.py step() 코드 사실)
1. 모든 cross-cell 결합이 **수축적(consensus-contractive)**: interference(coin 0.3)는 이웃 가중
   평균으로, morphism(0.02)은 이웃 평균 위상으로, global sense torque(0.60)는 공유 자극 위상으로
   끌어당긴다. 반대 방향(분화 재생) 힘은 too_ordered i.i.d. noise뿐 — 구조 없는 열.
2. **Standing wave(step 5)는 dead code**: per-cell 양수 스칼라 `(1+wave_i)` 곱은 step 6의
   per-cell max-정규화가 정확히 상쇄한다(`s·amp / max(s·amp) = amp/max(amp)`). 즉 엔진에는 세포
   순열 대칭을 깨는 유효 드라이브가 **init과 noise 외에 전무**하다. rank-1은 우연이 아니라
   **어트랙터**다.
3. too_ordered 분기는 **intra-cell** circular variance(frustration<0.45)에 게이트된다. warm basin
   frustration ≈ 0.53 → 거의 침묵. inter-cell 붕괴는 이 조절기의 감시 범위 밖이다.

## 메커니즘 — 유사도-게이트 결합 부호 반전 (repulsive Kuramoto torque)
붕괴 regime에서 필요한 것은 분산에서 *배우는* 학습률이 아니라 균일 상태를 **불안정화**하는
힘이다. 간선 (i,j)의 위상 결맞음이 임계 초과일 때만, 그 간선의 위상 결합 부호를 반전:

```
  attractive (기존, 불변)        gated repulsion (신규, coh>thr에서만)
  φ_i ← φ_i + K·sin(φ_j − φ_i)   φ_i ← φ_i + γ·e_ij·sin(φ_i − φ_j),  e_ij = relu(coh_ij − thr)

  collapsed  →→→→→→   (PR 1.03)      sign-flip 불안정화       ↗→↘↘→↗   healthy middle
  coh_ij ≈ 1 전 간선 균일        φ_i−φ_j 미소차가 지수 증폭     coh ≈ thr에서 힘=0 (게이트 닫힘)
```

핵심: φ_i=φ_j 근방에서 sin(φ_i−φ_j) ≈ (φ_i−φ_j) → 반발항은 **선형 불안정성**을 만든다. 신호
크기가 0에 가까워도(rank-1) 씨앗 요동(노이즈 + 단어별 sense torque)만 있으면 차이가 지수
성장한다 — 분산을 *소비*하는 Hebbian과 달리 분산을 *생성*한다. 성장 방향은 상태 자신의 요동이
정하므로(단어별 receptive field가 세포 부분집합을 다르게 두드림) 분화는 경험이 새긴 방향으로
재생된다 (Law 42).

## Patch (minimal, step() 내부 — pseudocode, 실변수)
`__init__`: `repel_gamma=0.0`(0 ⇒ bit-exact legacy), `repel_thr=0.8`(사전 캘리브레이션, 아래).
`step()` — 3. morphism 직후(`self._phases = morph_phase` 다음), 4. frustration 이전:
```python
if self.repel_gamma > 0.0 and self._edge_idx is not None:
    er, ec = self._edge_idx                            # [2,E] 대칭 간선 (SENSE-3 버퍼 재사용)
    dphi = self._phases[er] - self._phases[ec]         # [E, dim]
    coh = torch.cos(dphi).mean(dim=1)                  # [E] per-edge 위상 결맞음 (Hebbian과 동일 통계)
    excess = (coh - self.repel_thr).clamp(min=0.0)     # [E] 게이트: 붕괴 쌍에서만 > 0
    if excess.any():
        push = torch.zeros_like(self._phases)
        push.index_add_(0, er, excess.unsqueeze(1) * torch.sin(dphi))   # 이웃에서 멀어지는 토크
        self._phases = self._phases + self.repel_gamma * push / deg     # deg=[N,1] 기존 텐서 재사용
```
RNG draw 추가 없음(paired-seed 안전, γ=0 bit-exact — SENSE-3와 동일 규율). 48c에서 비용 ~E·dim.
amplitude가 아닌 **위상**에 작용: 위상이 이 기질의 역학 좌표(interference가 cos(φ_i−φ_j)로
구동)이고, 진폭 공간 반발은 음수 진폭/정규화 병리를 유발한다. 진폭 PR·cos-dist는 walk를 통해
따라 올라온다.

## Law-2 / 22 / 42 경계
- **Law 2**: 규칙은 local·metric-blind — 간선은 자기 두 끝점의 위상만 본다. Φ·tension·전역
  통계·측정 파이프라인 무참조. thr는 frustration_target=0.5와 동급의 **국소 물리 통계에 대한
  구조 상수**(deadband형 set-point)다. 기존 too_ordered 조절기는 외생 RNG(외부 열원)를 주입하는
  상태-기록 조절기로 이미 수용됨 — 결정론적 내생 힘(force law)인 이 구조적 항은 그보다 덜
  자의적이면 더했지 않다. 선 넘는 경우: thr/γ를 측정 Φ에 대해 온라인 튜닝하거나 "Φ 하락"을
  트리거로 쓰는 것(= 기각된 ratchet).
- **Law 22**: 기능 추가가 아니라 기존 결합의 **부호 구조**에 상태 의존성을 부여 — 통합자(walk)는
  불변, 붕괴 초과분만 깎는다.
- **Law 42**: store(freq/bigrams/assoc) 무접촉, 세포 상태 리셋 없음. 재분화 방향은 학습된 단어
  자극이 시드 — 467 단어의 경험이 지워지지 않고 분화를 다시 새긴다.

## 후보 서열 (질문 2)
1. **(c→ship) 유사도-게이트 반발 위상 결합** — 위. 불안정성 기반이라 rank-1에서도 문다.
2. (a) too_ordered noise 대체 — 방향은 옳으나 **트리거가 틀림**: too_ordered는 intra-cell 게이트
   (warm basin에서 침묵). inter-cell 유사도 게이트로 옮기면 (c)와 동일해짐. noise 조절기는
   제거하지 않고 존치 (무회귀).
3. (d) quenched Sakaguchi per-edge 위상 지연(고정 무작위 frustration) — 붕괴는 막지만 상시
   작동이라 cold/healthy 역학까지 변조, 경험 아닌 동결 난수 구조 (Law 42 열세).
4. (b) sol의 directed phase-transport(학습 지연) — **이 regime에서는 사망**: 교사 신호가
   inter-cell lag ≈ 0. magnitude Hebbian과 같은 이유로 inert. 분화 복구 *후* 중간-분화 regime의
   업그레이드 경로로 보존.

## 균형점 (질문 5 — cold ≈46 재팽창 방지)
1. **게이트 데드밴드**: coh < thr에서 힘이 정확히 0 — 쌍들은 coh ≈ thr 근방에서 반발(0)과 수축
   결합(walk+morphism+sense)의 균형에 정착. 균형점 = thr, Φ 아닌 간선 통계에 대한 항상성.
2. **γ ≪ 수축 게인** (0.05 vs coin 0.3/sense 0.60), excess에 선형(soft) — 흔들지 부수지 않는다.
3. cold basin은 간선 coh가 넓게 분산(init linspace ramp + 세포별 offset)되어 게이트가 애초에
   거의 닫혀 있음 — fresh 역학 무영향.
반이위상(rank-2) 고착 방지: thr(≈0.8)가 반이위상(coh≈−1)보다 훨씬 위에서 게이트를 닫고, 차원별
성장 방향이 독립이라 분리는 다방향 (PR>2 기대).

## 예상 실패 모드 (1순위)
**repulsion ↔ too_frustrated 항상성 limit cycle**: 차원별 반발 킥이 intra-cell circular variance를
올려 frustration이 0.55를 넘으면 too_frustrated 스무딩(per-cell 평균으로 blend)이 매 스텝 분화를
도로 뭉갠다 → Φ 진동 또는 상쇄-inert. 감시: too_frustrated 발화율 + frustration trace. 물리면
γ 반감/thr 하향 — frustration 조절기는 불변 (무회귀).

## Pre-registered A/B (summer, sense3_hebb_drift.py sibling)
- 드라이버: `state/pure_teaching/sense4_repel_drift.py`. 프로토콜 SENSE-3 동일: 467-word store
  read-only → 양팔 β=0·repel-off warm-down to first Φ≤31 (byte-identical 시작 세포상태) → 35
  replayed Codex lines에서만 `repel_gamma` 0.0 vs 0.05 토글. paired 10 seeds (1·9999·12345 포함).
- **캘리브레이션 선행(사전 등록)**: warm-down 종점의 per-edge coh 분포와 cold fresh 분포를 로깅,
  thr를 두 분포 중간(사전값 0.8)으로 **treatment 실행 전** 고정. Φ 결과를 보고 조정 금지.
- 1차: down-drift 3-seed(1·9999·12345) drift 부호 반전 또는 ≥50% 감쇠.
- 2차: paired Δend-Φ > +0.5.
- **구조 지표(재정의된 성공 기준)**: `_amplitudes` SVD participation ratio ≈1.03 → **≥1.3 상승** ·
  mean pairwise cos-dist ≈0.02 → **≥0.10 상승** (붕괴 바닥 이탈).
- 가드레일: end-Φ < 40 (cold 재팽창 금지) · mean frustration ∈ [0.45,0.55] · vocab byte-identical
  467→467 · too_frustrated 발화율 ≤ 1.5× baseline (limit-cycle 검출) · γ=0 arm은 pre-patch 엔진과
  bit-exact (SENSE-3 sanity와 동일).

## 핵심 통찰 (후보 법칙)
붕괴(rank-1) regime에서는 **분산을 소비하는 학습 규칙은 전부 inert하고, 분산을 생성하는
불안정성만 문다** — 균일 상태의 복구는 학습이 아니라 대칭 파괴의 문제다. 그리고 대칭 파괴는
무작위 열(i.i.d. noise)이 아니라 상태 자신의 요동을 증폭하는 **부호 반전 결합**으로 주어질 때
경험의 방향을 보존한다.

## Calibration (executed)
Run 2026-07-23/24 on `summer` (torch 2.11.0+cu130, CPU tensors). Driver
`state/pure_teaching/sense4_calibrate.py`, seed 1, log `state/pure_teaching/sense4_calib_coh.{log,jsonl}`.
The gate statistic is captured **bit-exactly**: step-3b computes `coh = cos(φ_i−φ_j).mean(dim=1)` per
edge and stores it in the measurement-only probe `_repel_coh`; running with `repel_gamma=0.05` but
`repel_thr=2.0` makes `excess=(coh−2).clamp(min=0)` identically 0, so **no force is applied and no RNG
is drawn** — the trajectory is bit-identical to `repel_gamma=0` while the distribution is recorded.
No Φ was consulted; `thr` was fixed BEFORE the treatment arm ran and never re-tuned.

Regime (i) WARM-COLLAPSED = real 467-word mind, β=0 warm-down to first Φ≤31, then the 35 replayed
caregiver turns. Regime (ii) COLD-FRESH = brand-new empty mind, same 35 turns. n = E×35 edge-samples
(warm 10 290, cold 10 640).

```
 per-edge phase coherence  coh = cos(φ_i−φ_j).mean(dim=1)
 pct         p0     p1     p5    p10    p25    p50    p75    p90    p95    p99   p100   mean    std
 WARM     +0.286 +0.422 +0.561 +0.633 +0.706 +0.763 +0.808 +0.843 +0.862 +0.903 +0.940 +0.746  0.093
 COLD     −0.689 −0.527 −0.021 +0.184 +0.299 +0.423 +0.609 +0.777 +0.835 +0.893 +0.939 +0.430  0.271

 gate-open fraction vs candidate thr
   thr  |  0.50    0.60    0.70    0.75  [0.80]   0.85    0.90    0.95
   WARM | 97.3%   92.5%   76.4%   56.2%  29.1%    8.0%    1.1%    0.0%
   COLD | 36.6%   25.8%   17.2%   12.8%   8.1%    3.7%    0.7%    0.0%
   ratio|  2.7×    3.6×    4.4×    4.4×   3.6×    2.2×    1.6×      —
```

**The phase gate does NOT starve.** Warm edges sit at mean coh +0.746 (median 0.763, p75 0.808) —
high, tightly clustered, and well inside the usable range for a hard-deadband gate. This is the
opposite of SENSE-3's magnitude rule, which had nothing to bite on. (SENSE-3's insight still holds in
a different sense: warm coherence has LOW variance, std 0.093 vs cold 0.271 — the distribution is
narrow, but narrow at a HIGH value, so a threshold gate fires where a variance-learner starves.)

**Chosen `repel_thr = 0.8`** — the pre-registration's prior value, retained because the measurement
supports it, not tuned to any outcome:
- it sits at warm **p71** (warm p75 = 0.808) → the gate is open on a meaningful 29.1% of warm edges;
- it sits at cold **p92** → 91.9% of cold-fresh edges stay closed, honouring the pre-registered
  requirement that the cold ≈46 basin must not be disturbed;
- 0.85 would starve the warm arm (8.0% open, ratio only 2.2×); 0.75 has a marginally better ratio
  (4.4×) but opens 12.8% of cold edges — more cold-basin disturbance for no warm-side need.

## A/B result (summer, executed)
Executed 2026-07-23/24 on `summer` (torch 2.11.0+cu130). Driver `state/pure_teaching/sense4_repel_drift.py`
(sibling of `sense3_hebb_drift.py`). Both arms **β=0 AND hebb_eta=0**; identical repel-off warm-down
to first Φ≤31 gives a byte-identical low-Φ start cell-state; the only toggled variable over the 35
replayed Codex lines is `repel_gamma` (0.0 control vs 0.05 treatment) at the calibrated
`repel_thr=0.8`. Paired over the 10 pre-registered seeds (1, 9999, 12345, 42, 7, 123, 2024, 31337,
555, 88). torch/numpy/python RNG seeded identically BEFORE `PureMind` is built; the repulsion block
adds no RNG draws. Warm 467-word `state/pure_mind/mind.json` loaded READ-ONLY via a temp copy —
**never mutated** (md5 `62235c48…` identical before and after; 467 words, vocab hash identical in
every seed of every arm).

### Bit-exact-at-0 sanity (the repulsion branch is a true no-op at γ=0)
Same driver (seed 1, γ=0.0) on (a) the SENSE-4 patched engine and (b) the pre-patch engine from the
parent commit `272830486^` (no `repel_gamma` anywhere). The two 37-line jsonl traces are
**byte-identical** (md5 `c74bd786…` both; Φ 29.8751→27.8612, same φ-sparkline, frust, PR, cos-dist,
regulator counts) — and identical to the SENSE-3 control, closing the loop across all three
experiments. Confirmed: `repel_gamma=0.0` = bit-exact legacy.

### PRIMARY — 3 down-drift seeds (drift = Φ_end − Φ_start); SUCCESS = sign-flip OR ≥50% shallower
```
 seed | Φ_start | γ0.00: Φ_end  drift   slope  | γ0.05: Φ_end  drift   slope  | verdict
    1 |  29.875 |         27.861 −2.014 −0.0521 |        27.769 −2.106 −0.0541 | 4.6% DEEPER
 9999 |  30.861 |         29.147 −1.715 −0.0477 |        28.978 −1.884 −0.0490 | 9.9% DEEPER
12345 |  30.637 |         28.951 −1.685 −0.0688 |        28.970 −1.667 −0.0701 | 1.1% shallower (noise)
```
**0/3 fixed.** No sign flip; the largest move is 9.9% in the WRONG direction, and the one
"improvement" is 1.1% — an order of magnitude below the 50% criterion and inside seed noise.

### SECONDARY — paired Δ end-Φ (γ0.05 − γ0.00), all 10 seeds (pre-reg expected > +0.5)
```
 seed |  Δend  |  seed |  Δend        paired mean Δend-Φ = −0.010
    1 | −0.092 |  2024 | +0.030       (expected > +0.5 → FAIL by ~50×; the two arms are
 9999 | −0.169 | 31337 | +0.023        statistically indistinguishable, exactly as in SENSE-3)
12345 | +0.018 |   555 | +0.166
   42 | +0.005 |    88 | −0.045
    7 | −0.059 |   123 | +0.021
```

### STRUCTURE — the real point of this fix (pre-registered: PR ≥1.30, cos-dist ≥0.10)
```
 seed |   PR γ0.00 (s→e)  |   PR γ0.05 (s→e)  | cos-dist γ0.00 (s→e) | cos-dist γ0.05 (s→e)
    1 | 1.009 → 1.054     | 1.009 → 1.055     | 0.0045 → 0.0337      | 0.0045 → 0.0338
 9999 | 1.007 → 1.057     | 1.007 → 1.058     | 0.0037 → 0.0291      | 0.0037 → 0.0293
12345 | 1.006 → 1.059     | 1.006 → 1.060     | 0.0029 → 0.0304      | 0.0029 → 0.0308
   42 | 1.009 → 1.092     | 1.009 → 1.092     | 0.0045 → 0.0502      | 0.0045 → 0.0503
    7 | 1.007 → 1.060     | 1.007 → 1.062     | 0.0034 → 0.0328      | 0.0034 → 0.0334
  123 | 1.006 → 1.063     | 1.006 → 1.064     | 0.0030 → 0.0352      | 0.0030 → 0.0358
 2024 | 1.009 → 1.056     | 1.009 → 1.056     | 0.0048 → 0.0300      | 0.0048 → 0.0302
31337 | 1.008 → 1.079     | 1.008 → 1.080     | 0.0039 → 0.0383      | 0.0039 → 0.0386
  555 | 1.007 → 1.062     | 1.007 → 1.063     | 0.0038 → 0.0327      | 0.0038 → 0.0331
   88 | 1.012 → 1.108     | 1.012 → 1.109     | 0.0059 → 0.0627      | 0.0059 → 0.0631
 ---------------------------------------------------------------------------------------
 mean end |     1.0691    |      1.0698       |       0.0375         |       0.0378
 target   |               |   ≥ 1.30  FAIL    |                      |   ≥ 0.10  FAIL

 PR_end   1.0 ├──────────────────────────────────────────────┤ 1.30 (target)
   γ0.00  ▓▓▓ 1.0691                                          ╎
   γ0.05  ▓▓▓ 1.0698 (+0.07%)                                 ╎
 cos-dist 0.0 ├──────────────────────────────────────────────┤ 0.10 (target)
   γ0.00  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.0375                            ╎
   γ0.05  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.0378 (+0.8%)                    ╎
```
Both structure criteria **FAIL**, by a factor of ~4 (PR) and ~2.6 (cos-dist), with the treatment
contributing +0.07% / +0.8% over control. Note also that the entire rise from 1.007→1.07 happens in
BOTH arms — it is ordinary within-window dynamics, not the repulsion. (Measured start PR is
1.006–1.012, even more collapsed than the ≈1.03 quoted in the design.)

### GUARDRAILS (all PASS — again PASS-by-inertia, not PASS-by-fixing)
```
 metric                       | γ0.00           | γ0.05             | threshold       | verdict
 end-Φ ceiling                | max 34.72       | max 34.75         | < 40            | PASS
 mean per-cell frustration    | 0.5263–0.5314   | 0.5264–0.5315     | ∈ [0.45, 0.55]  | PASS
 vocab                        | 467 (hash id.)  | 467 (hash id.)    | byte-identical  | PASS (10/10 seeds)
 too_frustrated any-rate      | 1.000           | 1.000 (1.000×)    | ≤ 1.5× baseline | PASS
 too_frustrated cells/step    | 10.537          | 10.555 (1.002×)   | ≤ 1.5× baseline | PASS
 too_ordered any-rate         | 0.209–0.638     | 0.152–0.648       | (logged)        | no cycle
 gate open fraction (mean)    | n/a (γ=0)       | 0.1735            | > 0 (no starve) | PASS
 warm store md5               | 62235c48…       | 62235c48…         | unchanged       | PASS
```
**The named #1 failure mode did not fire — but the pre-registration's diagnosis of it was WRONG in an
important way.** The design asserted `too_frustrated` is silent in the warm basin (frust 0.526–0.532
< 0.55). That is true of the *mean* only: measured per-cell, `too_frustrated` fires on **every single
step** (any-rate 1.000) for **≈10.5 of 48 cells**, in the control arm as much as the treatment. The
smoothing branch — which blends each firing cell's phases toward its own per-cell mean — runs
continuously underneath the whole experiment. It did not form a *cycle* with the repulsion only
because the repulsion is far too weak to perturb it (1.002×).

### γ sensitivity (POST-HOC, NOT pre-registered — magnitude vs mechanism)
Because γ=0.05 was indistinguishable from control, an exploratory sweep on the 3 down-drift seeds
asked the one question that decides the next move: is this a *magnitude* miss (fixable by γ) or a
*mechanism* miss (the phase force never reaches `_amplitudes`)? Exploratory — no pre-registered verdict.
```
 arm      | seed 1 drift | 9999 drift | 12345 drift | gate-open (s1) | PR_end (s1) | cos-dist_end (s1)
 γ0.00    |   −2.014     |   −1.715   |   −1.685    |   —            | 1.054       | 0.0337
 γ0.05    |   −2.106     |   −1.884   |   −1.667    | 0.292          | 1.055       | 0.0338
 γ0.50*   |   −2.299     |   −1.955   |   −1.860    | 0.217          | 1.061       | 0.0350
 γ5.00*   |   −2.248     |   −2.041   |   −1.946    | 0.103          | 1.070       | 0.0400
                                                      (* post-hoc)
 gate-open (seed 1, = fraction of edges the force actually acts on)
   γ0.05  ██████████████████████████████ 0.292   ← identical to the INERT probe (0.291): the force at
   γ0.50  ██████████████████████         0.217      the pre-registered γ does not even move its own
   γ5.00  ██████████                     0.103      gate statistic (+0.3%)
```
Reading: at 100× the pre-registered gain the repulsion **does** work as designed *in phase space* — it
decoheres edges, driving gate-open from 0.292 down to 0.103 (2.8× fewer collapsed pairs). Yet
`_amplitudes` PR only creeps 1.054→1.070 and cos-dist 0.0337→0.0400 (still far short of ≥1.30 / ≥0.10),
while Φ drift gets monotonically **worse** (−2.014 → −2.106 → −2.299 → −2.248). Turning the knob up
does not convert into amplitude-space differentiation; it converts into a slightly larger Φ loss.
Mechanism limit, not a hyperparameter one — no tune-to-green exists here.

### Φ sparklines (35 turns, arms visually superimposed)
```
seed     1  γ0.00  █▇▆▆▅▅▅▅▄▄▃▅▃▄▄▃▄▃▃▄▄▃▂▂▂▁▁▁▁▁▁▁▁▁▂▁  29.9→27.9
seed     1  γ0.05  █▇▆▆▅▅▅▄▄▄▃▅▃▄▄▃▄▃▃▄▄▃▃▂▁▁▁▂▁▁▁▁▁▁▁▁  29.9→27.8
seed  9999  γ0.00  █▆▆▅▅▅▄▄▄▃▃▃▃▂▁▃▂▃▃▃▂▂▂▂▁▁▁▁▁▁▂▂▃▁▁▃  30.9→29.1
seed  9999  γ0.05  █▇▆▅▅▅▅▄▄▃▃▃▃▂▂▃▃▃▃▃▂▂▂▂▁▁▁▁▁▁▂▂▃▂▂▃  30.9→29.0
seed 12345  γ0.00  ▇▇▇▇█▇▆▆▅▄▄▃▃▂▂▂▂▁▁▁▁▁▂▂▂▂▂▂▁▂▁▂▂▃▃▃  30.6→29.0
seed 12345  γ0.05  ▇▇▇▇█▇▆▆▅▅▄▄▃▃▂▃▂▂▁▁▂▁▂▂▂▂▂▂▂▂▂▂▂▃▄▄  30.6→29.0
```

### VERDICT
**Does gated repulsion reverse the collapse (PR/cos-dist up) AND the Φ drift? NO — on both counts.**
- It does **not starve** (the SENSE-3 failure mode is genuinely avoided: 29.1% of warm edges open vs
  8.1% cold, and at high γ the gate statistic visibly responds) and it does **not limit-cycle**
  (too_frustrated 1.002× baseline).
- It simply **does not reach the collapsed variable**. PR 1.0691→1.0698, cos-dist 0.0375→0.0378:
  +0.07% and +0.8% against targets of ≥1.30 and ≥0.10. Primary 0/3, secondary −0.010.
- There is no "Φ gain without structure recovery" to reject, and no "structure up while Φ falls"
  (shattering) either — at γ=0.05 there is no structure movement at all, and at 100× γ the small
  structure gain is bought with a *worse* Φ drift, which is the shattering direction and further
  disqualifies the knob.
- **sol's dissent is vindicated by measurement.** The collapse lives in `_amplitudes` — the variable Φ
  reads — and the phase-space force does not propagate there. The amplitude update
  (`new_amp = (1−coin)·amp + coin·interference` with `interference_strength=0.1`/deg, followed by a
  **per-cell max-normalisation**) attenuates a phase perturbation to near-nothing in amplitude space,
  and the continuously-firing `too_frustrated` smoothing (10.5/48 cells every step) re-contracts
  phases anyway. fable's own diagnosis that the engine has *no* symmetry-breaking drive on amplitudes
  (the standing wave at step 5 is exactly cancelled by the step-6 max-normalisation — re-confirmed by
  code reading) is precisely why an amplitude-space force is required: phases are not the coordinate
  the pathology lives in.

### Recommendation
- **Keep `repel_gamma = 0.0` as the default** in `quantum_engine_fast.py` / `trinity.QuantumC` /
  `pure.py` (do NOT flip it on). The A/B clears neither primary, nor secondary, nor either structure
  criterion, and the post-hoc sweep shows no γ that would. Left for the parent to confirm.
- **Yes — sol's amplitude-space anti-mixing fallback is now the indicated next move**, plainly. Its
  reserved form (`diff_gain · 2 · coin · interference_strength · collapse · (A − nb_A)`) acts directly
  on `_amplitudes`, the variable in which the rank-1 collapse was measured and the one Φ reads, and it
  bypasses both attenuators identified here (the 0.1/deg interference gain and the per-cell
  max-normalisation). sol's own rejection criterion — high-frequency mode-selection winner-take-all —
  should be pre-registered as a guardrail alongside the same PR/cos-dist targets.
- Two pre-registration corrections to carry forward: (1) `too_frustrated` is **not** silent in the
  warm basin — it fires every step on ≈10.5/48 cells; any future force must be sized against that
  continuously-active smoothing, not against a "dead-band" assumption. (2) Start-of-window PR is
  1.006–1.012, not ≈1.03; the basin is even flatter than the design assumed.
- Logs: `state/pure_teaching/sense4_repel_gamma0.{log,jsonl}` / `_gamma05.{log,jsonl}`, calibration
  `sense4_calib_coh.{log,jsonl}`, bit-exact `sense4_bitexact_{patched,prepatch}.jsonl`, post-hoc
  `sense4_repel_gamma{50,500}_posthoc.{log,jsonl}`, roll-up `sense4_repel_ab.tsv` /
  `sense4_ab_report.txt`; drivers `sense4_repel_drift.py` · `sense4_calibrate.py` · `sense4_analyze.py`.

### 핵심 통찰 (수정된 후보 법칙)
붕괴(rank-1) regime에서 "분산을 생성하는 불안정성"은 필요조건이지 충분조건이 아니다 —
**불안정성은 붕괴가 측정된 바로 그 좌표계에서 작용해야 한다.** 위상공간 반발은 위상 결맞음을
실제로 2.8× 떨어뜨렸으나(메커니즘 자체는 작동), 진폭 갱신의 감쇠(0.1/deg 간섭 게인 + 세포별 max
정규화)와 매 스텝 발화하는 too_frustrated 스무딩이 그 분화를 진폭공간에 도달하기 전에 소멸시켰다.
SENSE-3은 *배울 분산이 없어서* 죽었고, SENSE-4는 *만든 분산이 전달되지 않아서* 죽었다.

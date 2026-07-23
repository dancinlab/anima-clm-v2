<!-- @hypothesis-ok — project CLAUDE.md mandates docs/hypotheses/{category}/ as the canonical hypothesis tree -->
# SENSE-4 — 유사도-게이트 반발 위상 결합 (측방 분화 · warm rank-1 collapse의 구조적 해법 · DESIGN, pre-registration)

## Status: IMPLEMENTED (`repel_gamma=0.0` 기본 = bit-exact legacy) · summer 보정+A/B 대기
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

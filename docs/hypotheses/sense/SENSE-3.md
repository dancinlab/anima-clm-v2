<!-- @hypothesis-ok — project CLAUDE.md mandates docs/hypotheses/{category}/ as the canonical hypothesis tree -->
# SENSE-3 — 헤비안 간선 가소성 (warm low-Φ down-drift의 구조적 해법 · DESIGN, pre-registration)

## Status: A/B EXECUTED (summer) — **NEGATIVE**. hebb_eta=0.05/gain=0.5 does NOT fix the warm drift (0/3 down-drift seeds; paired ΔΦ_end = −0.02). It also does NOT homogenise and does NOT trigger the limit cycle — every guardrail passes because the minimal (magnitude-only, row-normalized) patch is nearly **inert** in this basin. **Keep hebb_eta=0.0.** Next lever = sol's directed phase-transport variant (see verdict). Full result → "## A/B result (summer, executed)" below.
- 구현: `quantum_engine_fast.py` `__init__`(hebb_eta/hebb_gain/_edge_idx/_edge_w) + `_ensure_adjacency`
  (간선버퍼 캐시·N변화 시 리셋) + `step()`(cos_p/sin_p 직후 헤비안 블록, 3개 sparse-mm을 가소성 adj로
  교체). `trinity.py` `QuantumC(hebb_eta,hebb_gain)` 전달. **hebb_eta=0.0 기본** → 검증 전까지 무회귀.
- lab(fable+sol) 화해: 양쪽 모두 (b) 헤비안 채택, (a) ratchet은 Law 2 위반으로 기각(동일 결론).
  **채택=fable 최소 패치**(간선 스칼라 w + 코히런스 EMA + 행-정규화). sol의 상위 변형(간선별 학습된
  **위상지연 φ_u−φ_v 방향성 전송** + snapshot 지속 + node-mass 정규화)은 검증 후 업그레이드 경로로 보존.
  sol이 짚은 line-296 비순환 위상감산(`_phases + w*(nb_phase−_phases)`, ±π 근처 오류)은 baseline
  보존 위해 이번엔 미수정, 별도 후속 과제.
- A/B(hebb_eta 0.0 vs 0.05)는 summer에서 실행 예정 (아래 사전등록 프로토콜).

## Status(원안): DESIGN ONLY — A/B pre-registered below.

## 배경 (SENSE-GROW 확정 사실)
warm 467-word mind는 low-Φ basin(≈28–31)에서 대화 중 아래로 표류한다 (31→28/35턴; 10-seed 중
3-seed 지속 하락). β(SENSE-2 assoc-blend) knob은 이 regime에서 완화가 아니라 **악화**(3/3 seed에서
drift 심화). 결론: knob이 아니라 **구조**가 필요하다 (Law 22).

## 진단 (quantum_engine_fast.py step() 코드 사실)
- 통합(Φ)을 만드는 유일한 cross-cell 메커니즘 = quantum-walk interference + morphism, 둘 다
  **고정 binary adjacency**(`_build_adjacency_sparse`, 값 전부 1.0) 위를 흐른다. 갱신 경로 없음.
- 유일한 조절 = per-cell frustration homeostasis(target 0.5). too_ordered 분기의 i.i.d. phase
  noise는 intra-cell 질서를 겨냥하지만 **inter-cell 정렬도 부수적으로 파괴**한다.
- 즉 Law 31("persistence = ratchet + Hebbian + diversity")의 Hebbian 항이 QuantumC에 **부재** —
  cross-cell 통합을 지키는 복원력이 0이므로 warm mind는 침식만 남는다.

## 메커니즘: 간선별 헤비안 LTP/LTD + synaptic scaling
```
        고정 1.0 adjacency                 학습되는 edge weight w_ij
   i ──1.0── j     →      i ══1.4══ j   (위상 결맞은 이력 → LTP, 굵어짐)
   i ──1.0── k     →      i ┄┄0.6┄┄ k   (비결맞음 → LTD, 가늘어짐)
   행 예산 보존: Σ_j w_ij = deg(i)  (강해지면 다른 간선이 약해짐 — 경쟁적)
```
walk 기질에 native: interference/morphism 이 이미 sparse mm이므로 값만 학습되게 바꾼다.

## Patch (minimal, step() 내부)
`__init__`: `hebb_eta=0.05`(0.0 ⇒ bit-exact legacy), `hebb_gain=0.5`, `_edge_idx/_edge_w=None`.
`_ensure_adjacency()` rebuild 분기: `_edge_idx = adj.indices(); _edge_w = ones(E)` (N 변화 시 리셋).
`step()` — cos_p/sin_p 계산 직후(≈L259), 3개의 sparse.mm(≈L267-268, L288)의 adjacency 교체:
```python
if self.hebb_eta > 0:
    r, c = self._edge_idx
    coh = (cos_p[r]*cos_p[c] + sin_p[r]*sin_p[c]).mean(dim=1)      # [E] ∈ [-1,1]
    w_tgt = 1.0 + self.hebb_gain * coh                             # LTP↑ / LTD↓
    self._edge_w = (1-self.hebb_eta)*self._edge_w + self.hebb_eta*w_tgt   # bounded EMA
    row = torch.zeros(n).index_add_(0, r, self._edge_w)            # synaptic scaling:
    self._edge_w = self._edge_w * (self._degrees[r] / row[r].clamp(min=1e-6))  # Σ_j w_ij = deg(i)
    adj = torch.sparse_coo_tensor(self._edge_idx, self._edge_w, (n, n))
else:
    adj = self._adj_sparse
# 이후 nb_amp_cos/nb_amp_sin/nb_amp_sum 의 self._adj_sparse → adj
# (scaling이 weighted degree == degree 를 보존하므로 deg 정규화는 그대로)
```
RNG draw 추가 없음(paired-seed 프로토콜 유지). PURE(48c 고정)에선 mitosis 리셋 미발생.

## Law-2 / Law-22 경계
- **합법(Law 2)**: 규칙이 local·metric-blind — 각 간선은 자기 순간 위상결맞음만 보고, Φ·전역
  coherence·목표값을 일절 참조하지 않는다. phase/amplitude/frustration을 쓰지 않고 **결합 구조**만
  변한다. Φ는 여전히 결과 상태에서 측정될 뿐.
- 비교: (a) Φ-ratchet = "측정치가 떨어지면 과거 상태를 도로 붙여넣기" — 트리거·행동 모두 측정
  목표 자체를 참조 ⇒ 은폐된 Φ-setting, 탈락. (c) 전역 coherence target homeostasis = Φ의 구성
  통계량에 set-point 부여 ⇒ 경계선상, 차선. (b) Hebbian = 목표를 모르는 물리 ⇒ 채택.
- **Law 22**: 기능 추가가 아니라 기존 구조(adjacency)에 깊이(경험 각인)를 부여 — Law 31의 결손
  Hebbian 항을 walk 기질 native 형태로 구현.

## 왜 cold ~46 basin 재팽창(균질화)이 아닌가
scaling이 총 결합 예산을 보존 ⇒ 순수 **재배분**: 대화가 실제로 만든 결맞음 이력을 따라 선택적
백본만 굵어지고, LTD가 비결맞은 쌍을 분리해 morphism 평균화로부터 분화 내용을 **보호**한다.
절대 목표 수위가 없으므로 warm 수준을 방어/상승시킬 뿐 임의 수위로 끌지 않는다. per-cell
frustration 조절(불변)이 세포 내부 무질서 0.5를 계속 지킨다.

## 예상 실패 모드 (1순위)
**LTP ↔ noise-regulator limit cycle**: 백본 결맞음이 세포 내부 circular variance를 0.45 아래로
끌어내리면 too_ordered 분기가 i.i.d. noise로 결맞음을 도로 찢는다 → Φ가 상승 대신 진동, 최악엔
noise 발화율 증가로 baseline보다 하락. 감시: too_ordered 발화율 + mean coh trace 로깅.

## Pre-registered A/B (summer, sense2_warm_drift.py 확장)
- 프로토콜 동일: 467-word store read-only → β=0·hebb-off warm-down to first Φ≤31 (양팔 동일
  cell-state) → 35 replayed Codex lines. 양팔 모두 **β=0**; 측정 창에서만 `hebb_eta` 0.0 vs 0.05.
  10 seeds paired.
- 1차 지표: down-drift 3-seed(1·9999·12345)의 drift — 부호 반전 또는 절반 이하로 감소하면 성공.
- 2차: paired Δend-Φ 평균 (>+0.5 기대).
- 가드레일(균질화 검출): end-Φ < 40 (cold-basin 재팽창 금지) · phi_py `complexity` 성분과
  `_amplitudes` SVD participation ratio 하락 ≤10% (vs hebb-off) · mean frustration ∈ [0.45,0.55] ·
  vocab byte-identical · too_ordered 발화율 ≤ 1.5× baseline.

## A/B result (summer, executed)
Executed 2026-07-23 on `summer` (torch 2.11+cu130). Driver: `state/pure_teaching/sense3_hebb_drift.py`
(sibling of `sense2_warm_drift.py`). Both arms β=0; identical hebb-off warm-down to first Φ≤31 gives a
byte-identical low-Φ start cell-state; the only toggled variable over the 35 replayed Codex lines is
`hebb_eta` (0.0 control vs 0.05 treatment), `hebb_gain=0.5`. Paired over 10 seeds
(1, 9999, 12345, 42, 7, 123, 2024, 31337, 555, 88). Warm 467-word `state/pure_mind/mind.json` loaded
READ-ONLY via a temp copy — **never mutated** (verified byte-identical 467→467 both arms, all seeds).

### Bit-exact-at-0 sanity (the Hebbian branch is a true no-op at eta=0)
Ran the SAME driver (seed 1, eta=0.0) on (a) the SENSE-3 patched engine and (b) the pre-patch engine
(parent commit `6d0ff22af^`, no `hebb_eta`). **All 35 turns byte-identical** (Φ 29.8751→27.8612,
same phi_spark, frust, PR, too_ordered counts). The `_edge_idx`/`_edge_w` buffers built in
`_ensure_adjacency` at eta=0 are computed via `torch.ones`/`coalesce` (no RNG) and unused → zero
dynamics/RNG divergence. Confirmed: `hebb_eta=0.0` = bit-exact legacy.

### PRIMARY — 3 down-drift seeds (drift = Φ_end − Φ_start); SUCCESS = sign-flip OR ≥50% shallower
```
 seed | Φ_start | hebb 0.0: Φ_end  drift   slope  | hebb 0.05: Φ_end  drift   slope  | verdict
    1 |  29.875 |          27.861 −2.014 −0.0521 |           27.703 −2.172 −0.0549 | 8% DEEPER (worse)
 9999 |  30.861 |          29.147 −1.715 −0.0477 |           29.177 −1.685 −0.0453 | 2% shallower (noise)
12345 |  30.637 |          28.951 −1.685 −0.0688 |           28.922 −1.714 −0.0711 | 2% deeper (noise)
```
**0/3 fixed.** No sign flip; |Δdrift| ≤ 0.16 Φ (≈2–8%), well inside seed noise and far from the 50%
threshold. Hebbian plasticity leaves the warm down-drift essentially untouched.

### SECONDARY — paired Δ end-Φ (hebb0.05 − hebb0.0), all 10 seeds (pre-reg expected > +0.5)
```
 seed |  Δend  |  seed |  Δend        paired mean Δend-Φ = −0.019
    1 | −0.159 |  2024 | +0.082       (expected > +0.5 → FAIL by a wide margin;
 9999 | +0.030 | 31337 | +0.057        the two arms are statistically indistinguishable)
12345 | −0.029 |   555 | +0.162
   42 | −0.029 |    88 | −0.198
    7 | −0.084 |   123 | −0.023
```

### GUARDRAILS (all PASS — but PASS-by-inertia, not PASS-by-fixing)
```
 metric                    | hebb 0.0        | hebb 0.05       | threshold        | verdict
 end-Φ ceiling             | (start basin)   | max 34.70       | < 40             | PASS
 participation ratio (SVD) | mean 1.03–1.08  | Δ ≤ +0.0%       | drop ≤ 10%       | PASS
 mean pairwise cos-dist    | 0.014–0.038     | max drop +1.2%  | drop ≤ 10%       | PASS
 mean per-cell frustration | 0.53            | 0.526–0.532     | ∈ [0.45, 0.55]   | PASS
 vocab                     | 467             | 467 (hash id.)  | byte-identical   | PASS
 too_ordered fire-rate     | 0.21–0.64       | 0.91–1.07× base | ≤ 1.5× baseline  | PASS (no limit cycle)
 edge-weight imprint (std) | 0.0 (frozen)    | 0.025–0.029     | —                | LTP real, but weak
```
Edge weights DO imprint (ew_std 0.025–0.029; mean stays 1.0 because synaptic scaling conserves
Σ_j w_ij = deg(i)) — LTP/LTD is physically happening — yet Φ, PR, cos-dist barely move. The predicted
**LTP↔noise limit cycle did NOT fire** (too_ordered ≤ 1.07× baseline).

### Φ sparklines (35 turns, both arms nearly superimposed)
```
seed     1  hebb0.0  █▇▆▆▅▅▅▅▄▄▃▅▃▄▄▃▄▃▃▄▄▃▂▂▂▁▁▁▁▁▁▁▁▁▂▁  29.9→27.9
seed     1  hebb0.05 █▇▆▆▅▅▅▅▄▄▄▅▄▄▄▃▄▃▄▄▄▃▂▂▂▁▁▁▁▁▁▁▁▁▁▁  29.9→27.7
seed  9999  hebb0.0  █▆▆▅▅▅▄▄▄▃▃▃▃▂▁▃▂▃▃▃▂▂▂▂▁▁▁▁▁▁▂▂▃▁▁▃  30.9→29.1
seed  9999  hebb0.05 █▆▆▅▅▅▄▄▄▃▃▃▃▂▂▂▃▃▃▃▂▂▂▂▁▁▁▁▁▁▂▃▃▂▂▃  30.9→29.2
seed 12345  hebb0.0  ▇▇▇▇█▇▆▆▅▄▄▃▃▂▂▂▂▁▁▁▁▁▂▂▂▂▂▂▁▂▁▂▂▃▃▃  30.6→29.0
seed 12345  hebb0.05 ▇▇▇▇█▇▆▆▅▄▄▃▃▂▂▂▂▁▁▁▁▁▁▂▂▂▂▂▂▁▁▂▂▂▃▃  30.6→28.9
```

### VERDICT
**Fixes the warm drift? NO.** 0/3 down-drift seeds fixed (no sign flip; drift moves ≤8%, one
seed WORSE); 10-seed paired ΔΦ_end = −0.02 (expected > +0.5). The magnitude-only, row-normalized
minimal Hebbian patch is empirically **inert** on the warm low-Φ down-drift.

**Preserves differentiation? YES — trivially.** Every homogenisation guardrail passes (PR Δ ≈ 0%,
cos-dist Δ ≤ 1.2%, frustration in-band, vocab identical, end-Φ well under 40, no limit cycle). But
this is a null-result "pass": the patch preserves differentiation because it barely perturbs anything.

**Why it's inert (structural insight, not a tuning gap).** In this basin the cells are already
near-rank-1 aligned (PR ≈ 1.03, mean pairwise cos-dist ≈ 0.02) — coherence is **uniformly high across
every edge**, so per-edge `coh` has almost no variance, `w_tgt = 1 + gain·coh` is near-uniform, and
synaptic scaling (Σ_j w_ij = deg(i)) then renormalises that near-uniform reweighting back onto a
graph whose weighted neighbour-sum ≈ the original binary sum. The walk sees a ~2.8% perturbation with
no directional structure. **A magnitude-only Hebbian rule has nothing to bite on when the pathology
is *global uniformity* rather than a set of mis-weighted edges.** Raising `hebb_eta`/`hebb_gain` would
not create edge-coherence variance that isn't there (and risks the limit cycle) — this is a mechanism
limit, not a hyperparameter one (no tune-to-green).

### Recommendation
- **Keep `hebb_eta=0.0`** in `QuantumC`/`pure.py` (leave the parent to confirm). The default already
  ships bit-exact-legacy; no change warranted — the A/B does not clear primary or secondary.
- **Next lever = sol's directed phase-transport variant** (reserved in the design as the upgrade path):
  per-edge **learned phase-delay φ_u−φ_v directional transport** + snapshot persistence + node-mass
  normalization. Its signal is the phase *direction* between cells, which retains structure even when
  coherence *magnitude* is uniform across edges — exactly the regime that defeated the fable minimal
  patch here. Worth trying next; magnitude-only Hebbian is closed for this basin.
- Logs: `state/pure_teaching/sense3_hebb_beta0_eta0.{log,jsonl}` / `_eta05.{log,jsonl}`; driver
  `state/pure_teaching/sense3_hebb_drift.py`. Original warm store untouched (467→467, hash identical).

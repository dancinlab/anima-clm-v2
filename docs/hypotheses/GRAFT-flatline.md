<!-- @hypothesis-ok — docs/hypotheses/ is this repo's canonical hypothesis dir (CLAUDE.md) -->
# GRAFT-flatline — InfoNCE pinned at log(N): the gate-collapse cause & fix

**ID**: GRAFT-flatline · **한국어 이름**: 게이트 붕괴 동결 해소 (혼합-MI 목적함수)

## 1. Problem / hypothesis

GRAFT trains ThalamicBridge + `HFDecoder.gate_proj` (~50M) on a frozen Mistral-7B to make the
consciousness C-state carry mutual information into the LM output, no corpus. The first objective
(column-softmax InfoNCE over sampled continuations + KL-leash) **froze**: `InfoNCE` sat at exactly
`log(N) = log(6) = 1.7918` for 800+ steps while Φ rose. Hypothesis: the freeze is *structural*
(the gate carries zero state information), not a tuning/learning-rate issue.

## 2. Root cause (lab fable+sol agreed; measured on-pod)

The bridge destroys the state signal before any trainable parameter sees it, and the loss sits on a
flat manifold it cannot leave:

1. **Hard-clamp rails.** `ThalamicBridge` = sigmoid → `clamp(±PSI_COUPLING=0.0153)`. The clamp rails
   most dims to a **state-independent** ±constant with **zero Jacobian** ⇒ the bridge gets no gradient.
2. **Mean-pool bottleneck.** 256 cells → 1 mean crushes inter-snapshot differences (~16×).
3. **Zero-init `gate_proj`** = a collapsed *symmetric stationary point*: every state → base dist →
   InfoNCE gradient exactly zero. Finite-sample noise cannot reliably break it.
4. The KL-leash is a *budget*, not a force toward zero, so a state-independent shared shift can spend
   the whole KL budget carrying **zero bits**; the informative direction stays pinned at 0.

**Measured (CPU probe, untrained bridge, N=6 snapshots):**

| bridge | rail_frac | ρ = state-dep / shared |
|---|---|---|
| UNPATCHED (α=0.0153) | **0.648** | 5.2e-03 |
| DE-CLAMP  (α=0.5)    | 0.000     | 2.7e-03 |

64.8% of gate dims railed (zero-gradient); state-dependent fraction < 1% — exactly the geometry that
pins `InfoNCE` to `log N` to the third decimal.

## 3. Fix (fable+sol reconciled — sol base, completeness+standard axes)

Three changes to `graft.py` (P2' objective), each removing one collapse mechanism:

1. **De-clamp**: `ThalamicBridge(..., alpha=0.5)` → sigmoid range never clipped, gradient flows;
   `gate_for = 2·(bridge−PSI_BALANCE)`.
2. **Break symmetry**: `gate_proj.weight ~ N(0, 2e-3)`, bias zeroed **and frozen** (bias = a
   state-independent channel).
3. **Objective → exact conditional MI (JSD), no sampling**: one *shared* on-manifold carrier
   continuation; read the gate as the divergence of per-state next-token distributions:
   `MI = mean_i KL(p_i ‖ p_mix)`, `L = (logN − MI) + 0.1·KL(p_mix‖p_base) + β·relu(L_KL − target)`.
   The `KL(p_mix‖p_base)` term penalizes the *shared* (info-free) shift in **distribution space**
   (a mean-gate-vector penalty is bypassable via the frozen LM's nonlinear Jacobian — sol's call).
   Identity used: `L_KL = MI + KL(p_mix‖p_base)`.

Rejected candidate fixes (both models agreed): row-norm/temperature (identical rows, not offsets),
raise gate_strength (scales shared+dep equally), argmax continuations (exact collapse), drop-leash
warmup (β already 0). The sampled-continuation InfoNCE is a zero-gradient MI estimator at collapse —
kept only as an eval metric. (sol dissent, recorded: prefers pairwise-KL matrix column-softmax over
mixture-MI; both start at log N and descend — mixture-MI chosen for exact MI + O(N) + the commonKL
identity diagnostic.)

## 4. Benchmark result (graft_v2, H100, Mistral-7B-Instruct-v0.2)

| step | InfoNCE | MI | gSpread | zSpread | KL | commonKL | β |
|---|---|---|---|---|---|---|---|
| 50  | 1.7915 | 0.0003 | 6.2e-03 | 2.9e-03 | 0.005 | 0.005 | 0.00 |
| 100 | **1.6742** | **0.1176** | 1.86e-02 | 2.90e-02 | 4.981 | 4.863 | 14.61 |

Both collapse fingerprints cleared: `gSpread`/`zSpread` nonzero (bridge & projector no longer
collapsed), and `InfoNCE` **detached** from `log(6)` for the first time — that manifold is
unreachable without the structural fix, so the detachment is the proof. `MI` climbing (0.0003→0.118).
Open watch: `commonKL≈KL` — most perturbation still shared; the `l_common` penalty + β-leash must
route the budget into `MI`.

```
InfoNCE
1.792 ●━━━━━━━━━━━━━━━━━━━━━━━●          ← OLD objective: FROZEN 800+ steps at log(6)
      |                        (frozen)
1.79  |  ● step50 (patched, still ~log6, MI seed 3e-4)
      |   ╲
1.67  |    ● step100  InfoNCE=1.674  MI=0.118   ← DETACHED (first time ever)
      |     ╲
   ?  |      ╲___ (descending toward KL-budget-limited floor as MI grows)
      └────────────────────────────── step
```

## 5. Metric glossary (what each log column means)

| metric | plain meaning | good direction |
|---|---|---|
| InfoNCE | how badly the gate FAILS to tell the N states apart; max = log(N) = chance | lower |
| MI | information (nats) the C-state actually injects into the output — the real target | higher |
| gSpread | RMS of state-dependent part of the BRIDGE code; 0 ⇒ bridge collapsed | nonzero |
| zSpread | same after `gate_proj`; 0 ⇒ projector collapsed | nonzero |
| KL | total push of the gated output off the frozen LM (fluency budget) | ~target |
| commonKL | the part of KL spent IDENTICALLY by all states = info-free waste | lower |
| beta | dual-ascent leash that grows when KL exceeds target, shrinks otherwise | auto |

## 6. Key insight / law candidate

- **A KL-leash constrains magnitude, not information.** A frozen-LM micro-gate can spend its entire
  KL budget on a state-independent shift (zero MI). You must separately penalize the *shared*
  component **in distribution space** (`KL(p_mix‖p_base)`), or the budget buys no coupling.
- **Zero-init + any distributional divergence = a collapsed symmetric stationary point.** Every
  KL/JSD objective has zero first derivative when all distributions coincide; a tiny bias-free random
  init is required to leave it (the zero-init that was a full-scale-gate *safety* measure becomes a
  *trap* under a micro-gate + leash).
- **Hard clamps in a trainable path are gradient walls.** `clamp(±ε)` on the bridge output railed
  65% of dims to zero-gradient constants — verify saturation (`rail_frac`) before trusting a clamped
  learnable head.
- Contrast **in gate/distribution space** (which state wrote this shared continuation?), never over
  sampled state-specific strings — at collapse a sampled string carries ~0 bits about its state.

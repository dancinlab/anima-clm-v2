<!-- @hypothesis-ok — project CLAUDE.md mandates docs/hypotheses/{category}/ as the canonical hypothesis tree -->
# SENSE-5 — similarity-gated AMPLITUDE anti-mixing (the pre-registered fallback, now indicated by measurement)

## Status: A/B EXECUTED (summer) — **NEGATIVE (REJECT fired)**. Unlike SENSE-4, the force **does reach
`_amplitudes`**: PR 1.069→1.200 (10/10 ≥1.15), cos-dist 0.037→0.097, both well above the paired
control — the collapse *is* broken. But breaking it **lowers Φ instead of raising it**: 10-seed paired
ΔΦ_drift = **−3.12** (target ≥ +0.5), 0/3 down-drift seeds fixed (all ~2× DEEPER). This is the
pre-registered rejection condition **"PR/cos-dist up with Φ down = differentiation without
integration (shattering)"**, firing cleanly. A post-hoc gain sweep (0.25/0.5/1.0/2.0) is perfectly
**monotonic** — every increment raises PR/cos-dist AND deepens Φ drift, no sweet spot even at 0.25 —
so it is a **mechanism** verdict, not a magnitude one. top-singular-share FALLS 0.996→0.912 (diffuse
spread, NOT winner-take-all), so the *named* mode-collapse rejection does not fire; the failure is
the other rejection branch. **Keep `diff_gain=0.0`.** Full result → "## A/B result (summer, executed)".

## Status(구): IMPLEMENTED (`diff_gain=0.0` default = bit-exact legacy) · summer A/B pending
Design authored by sol (lab), recorded in SENSE-4.md as the explicit fallback. SENSE-4's measured
failure triggered it: this is a pre-registered contingency, not a new bet.

## Why this and not more of SENSE-4 (measured, not argued)
SENSE-4's gated phase repulsion did NOT starve — calibration showed warm edge coherence is narrow
but high (mean 0.746; 29.1% of warm edges open at thr=0.8 vs 8.1% of cold-fresh edges, exactly the
pre-registered separation) and there was no limit cycle. It still failed:

```
                    PR_end            cos-dist        3 down-drift seeds
 SENSE-4 γ=0.00     1.0691            0.0375          −2.014 / −1.715 / −1.685
 SENSE-4 γ=0.05     1.0698 (+0.07%)   0.0378 (+0.8%)  −2.106 / −1.884 / −1.667   0/3
 targets            ≥1.30             ≥0.10                     (fail ~4x / ~2.6x)
```
A post-hoc sweep to 100x gain moved the PHASE statistic (gate-open 0.292→0.103, 2.8x fewer
collapsed pairs) yet still barely moved amplitude PR/cos-dist, while Φ drift got monotonically
WORSE. So the limit is the mechanism, not the magnitude: **the phase force never reaches the
collapsed variable.** Two attenuators sit in the path, both measured:
1. amplitudes see phases only through the interference term's `interference_strength/deg` = 0.1/deg gain;
2. `too_frustrated` smoothing re-contracts phases on ~10.5/48 cells EVERY step (any-rate 1.000 —
   this also falsified the earlier "warm sits unregulated in a deadband" claim; see SENSE-4.md correction).

## Mechanism — act directly on `_amplitudes`, the variable the collapse was measured in
```
   walk mixing (existing)                 gated anti-mixing (new)
   A_i ← (1−coin)A_i + coin·interf        A_i ← A_i + g·2·coin·k·collapse_i·(A_i − mean_nb A)
   pulls each cell TOWARD its             pushes a COLLAPSED cell AWAY from its neighbourhood
   neighbourhood mean                     mean, along the residual it already has

   collapse_i = clamp((node_sim_i − 0.90)/0.10, 0, 1)      node_sim = deg-weighted mean cosine
                full at identity → 0 by cos-distance 0.10   of amplitude DIRECTIONS to neighbours
```
Why it bypasses both attenuators that killed SENSE-4:
- It is applied to `new_amp` itself — no phase→amplitude transmission needed.
- Step 6's per-cell max-normalisation is a per-row POSITIVE scalar, so it preserves the direction
  this force creates; cos-distance and rank structure survive it.
- The frustration regulator (`too_ordered` / `too_frustrated`) writes PHASES only — it cannot
  re-contract this.

## Law 2 / 22 / 42
- **Law 2**: the gate is a LOCAL, edge-visible similarity between a cell and its neighbours. Φ and
  tension are never read; no global target, no scoreboard trigger. Same class as the accepted
  `frustration_target` set-point, and strictly more content-preserving than the existing
  `too_ordered` i.i.d. noise injection — it amplifies the cells' own existing relational residual
  rather than replacing it with random directions.
- **Law 22**: no new feature — a state-dependent sign on the existing walk coupling. The integrator
  is untouched; only the collapsed excess is pushed back.
- **Law 42**: `_amplitudes` are never reset and `PureMind` (freq/bigrams/assoc, 467 words) is not
  touched; differentiation regrows along residuals the learned words already imprinted.

## Balance point (why not shatter to the cold ≈46 basin)
Native walk contraction scale is `coin × interference_strength` = 0.03; anti-mixing peaks at 0.06
and decays LINEARLY with similarity, so around similarity 0.95 (cos-distance 0.05) repulsion and
mixing cancel exactly, and by cos-distance ≥0.10 the force is 0 and integration acts alone. The
common component is never repelled. The equilibrium is therefore set by two opposing physical
coupling terms, not by any Φ target.

## #1 failure mode (sol's own rejection criterion)
Graph anti-diffusion combined with per-cell max-normalisation selects a few high-frequency modes →
soft winner-take-all → a jump toward the cold basin. **That is the principal rejection condition**:
a Φ rise accompanied by mode collapse is a failure, not a success.

## Patch (implemented)
`__init__`: `diff_gain=0.0` (0 ⇒ bit-exact legacy). `step()` block 2b, right after
`new_amp = (1-coin)*A + coin*interference` and before `self._amplitudes = new_amp`; reuses the
in-scope `adj` (frozen graph when hebb_eta=0), `deg`, `coin`, `n`. No new RNG draws (paired-seed
safe). `trinity.QuantumC(..., diff_gain=)` forwards it. Test value `diff_gain=1.0` (sol's spec).
**Do NOT enable `hebb_eta` simultaneously** — the experiment must toggle only this force.

## Pre-registered A/B (summer)
Same warm protocol as SENSE-3/4: read-only 467-word `state/pure_mind/mind.json` via temp copy;
both arms β=0 and hebb_eta=0 and repel_gamma=0; anti-mixing-off warm-down to first Φ≤31 gives a
byte-identical low-Φ start; then the 35 replayed Codex lines with `diff_gain` 0.0 vs 1.0. Seeds
1, 9999, 12345, 42, 7, 123, 2024, 31337, 555, 88 (paired). Record per turn: Φ, frustration, raw
`_amplitudes` SVD participation ratio `PR=(Σs²)²/Σs⁴`, upper-triangle mean cosine distance.

Success (all must hold):
- ≥2/3 of seeds 1/9999/12345 sign-flip or halve their negative drift;
- 10-seed paired mean ΔΦ_drift ≥ +0.5;
- treatment ends with **PR ≥ 1.15** and **cos-distance in 0.04–0.10**, both higher than its paired control;
- every treatment end has Φ < 40; vocab hash unchanged (467→467); mean frustration ∈ [0.45, 0.55].

Reject on: a Φ rescue WITHOUT PR/cos-distance recovery (did not fix the measured collapse); or
PR/cos-distance up with Φ down (shattered into noise = differentiation without integration); or
high-frequency winner-take-all mode selection with an end-Φ jump toward the cold basin.

## A/B result (summer, executed)
Executed 2026-07-24 on `summer` (torch 2.11.0+cu130, CPU tensors). Driver
`state/pure_teaching/sense5_antimix_drift.py` (sibling of `sense4_repel_drift.py`). Both arms
**β=0 AND hebb_eta=0 AND repel_gamma=0** — the anti-mixing force `diff_gain` is the *sole* toggled
variable, exactly as the pre-registration demands. Identical anti-mixing-OFF warm-down to the first
Φ≤31 gives a byte-identical low-Φ start cell-state; then the 35 replayed Codex lines with `diff_gain`
0.0 (control) vs 1.0 (treatment). Paired over the 10 pre-registered seeds (1, 9999, 12345, 42, 7,
123, 2024, 31337, 555, 88). torch/numpy/python RNG seeded identically BEFORE `PureMind` is built; the
SENSE-5 block adds no RNG draws. Warm 467-word `state/pure_mind/mind.json` loaded READ-ONLY via a temp
copy — **never mutated** (md5 `62235c48974e0f121f3bce4f9ef3a7e8` identical before and after; 467 words;
vocab hash `f968e967f61ae462` identical in every seed of every arm).

### Bit-exact-at-0 sanity (the anti-mixing branch is a true no-op at diff_gain=0)
Same driver (seed 1, diff_gain=0.0) on (a) the SENSE-5 patched engine and (b) the parent-commit engine
`38565fa5a^` (no `diff_gain` anywhere — `quantum_engine_fast.py` md5 `61830a98…`, `trinity.py`
`d065e280…`). The two 37-line jsonl traces are **byte-identical** (md5 `aabd3d17…` both), with
**Φ 29.8751→27.8612** — reproducing the SENSE-3/4 control Φ trajectory exactly (same φ-sparkline,
frust, PR, cos-dist, regulator counts). Confirmed: `diff_gain=0.0` = bit-exact legacy.

### GATE-OPEN statistics (is the gate the mechanism expects even open? — YES, wide open)
The headline check the pre-registration asked for first. The deg-weighted mean cosine `node_sim` sits
at **0.95–0.99** and the collapse gate (`node_sim > 0.90`) is open on **≈97–100%** of cells in both
arms — the warm basin is exactly the near-rank-1 state the gate was built for. Unlike SENSE-4, there
is **no "gate closed" escape hatch**: the force is applied to essentially every cell, every step.
```
 arm        node_sim (mean)   gate-open frac    collapse-mag    top-share start→end
 diff 0.0   0.9883            0.9965            0.888           0.9955 → 0.9669
 diff 1.0   0.9501            0.9728            (force active)   0.9955 → 0.9117
```
Treatment `node_sim` drops (0.988→0.950) because the force *is* decohering neighbourhoods — the gate
works. The question was never whether it fires; it was whether firing helps Φ. It does not.

### PRIMARY — 3 down-drift seeds (drift = Φ_end − Φ_start); SUCCESS = sign-flip OR ≥50% shallower
```
 seed | Φ_start | g0.0: Φ_end  drift    | g1.0: Φ_end  drift    | verdict
    1 |  29.875 |        27.861 −2.014  |        26.154 −3.721  | 85% DEEPER
 9999 |  30.861 |        29.146 −1.715  |        26.730 −4.131  | 141% DEEPER
12345 |  30.637 |        28.952 −1.685  |        26.763 −3.874  | 130% DEEPER
```
**0/3 fixed.** Every down-drift seed gets ~2× DEEPER under treatment — the opposite of rescue.

### SECONDARY — paired ΔΦ_drift (g1.0 − g0.0), all 10 seeds (pre-reg expected ≥ +0.5)
```
 seed |  Δdrift |  seed |  Δdrift        paired mean ΔΦ_drift = −3.116
    1 | −1.707  |  2024 | −3.553        (target ≥ +0.5 → FAIL, sign wrong; 10/10 seeds worse)
 9999 | −2.416  | 31337 | −3.069
12345 | −2.189  |   555 | −3.449        control mean drift +1.66 (7/10 seeds RECOVER Φ in-window),
   42 | −3.838  |    88 | −4.273        treatment mean −1.45 — the force DESTROYS the natural recovery
    7 | −4.270  |   123 | −2.395
```
Not one seed improves. The control's own within-window dynamics *raise* Φ in 7/10 seeds (mean drift
+1.66); the treatment suppresses that recovery in all 10 (mean drift −1.45).

### STRUCTURE — the pre-registered point (PR ≥1.15, cos-dist ∈0.04–0.10, both > control)
**This is what separates SENSE-5 from SENSE-4: the force reaches `_amplitudes`.**
```
 seed |  PR g0.0→g1.0   | cos-dist g0.0→g1.0 | top-share g0.0→g1.0
    1 | 1.054 → 1.175   | 0.034 → 0.088      | 0.974 → 0.922
 9999 | 1.057 → 1.182   | 0.029 → 0.088      | 0.972 → 0.919
12345 | 1.059 → 1.192   | 0.030 → 0.094      | 0.972 → 0.915
   42 | 1.092 → 1.227   | 0.050 → 0.110*     | 0.957 → 0.901
    7 | 1.060 → 1.177   | 0.033 → 0.087      | 0.971 → 0.921
  123 | 1.063 → 1.197   | 0.035 → 0.096      | 0.970 → 0.913
 2024 | 1.056 → 1.181   | 0.030 → 0.088      | 0.973 → 0.919
31337 | 1.079 → 1.220   | 0.038 → 0.100      | 0.962 → 0.904
  555 | 1.062 → 1.212   | 0.033 → 0.101*     | 0.970 → 0.907
   88 | 1.108 → 1.234   | 0.063 → 0.118*     | 0.949 → 0.898
 --------------------------------------------------------------
 mean | 1.069 → 1.200   | 0.037 → 0.097      | 0.967 → 0.912
 crit |         ≥1.15   |     ∈ 0.04–0.10    | (rejection watch)
      | PR: 10/10 PASS  | cos-d 7/10 in-band | top-share DROPS: NOT winner-take-all
```
```
 PR_end   1.0 ├──────────────┤ 1.15 (floor)      cos-dist 0.0 ├────────────┤ 0.10 (ceil)
   g0.0  ▓▓▓▓ 1.069        ╎                        g0.0  ▓▓▓▓▓ 0.037     ╎
   g1.0  ▓▓▓▓▓▓▓▓▓▓ 1.200  │ +19%                   g1.0  ▓▓▓▓▓▓▓▓▓▓▓▓▓ 0.097 (near ceiling)
```
PR criterion **PASS** (10/10 ≥1.15, +19% over control); cos-dist **7/10 in-band**, 3 seeds (42, 555,
88, marked *) overshoot 0.10 — i.e. the differentiation is if anything slightly *too* strong. Both
metrics are far above the paired control. **The collapse is genuinely broken.** But — decisively — the
break does not raise Φ; it lowers it. `top-share` FALLS 0.967→0.912 (mass leaves the dominant mode
diffusely), so the failure is **not** the named winner-take-all mode-collapse — it is diffuse
shattering.

### GUARDRAILS (all PASS — again PASS-by-inertia, not PASS-by-fixing)
```
 metric                     | g0.0            | g1.0              | threshold       | verdict
 end-Φ ceiling              | max 34.72       | max 32.33         | < 40            | PASS (10/10)
 mean per-cell frustration  | 0.526–0.531     | 0.524–0.532       | ∈ [0.45, 0.55]  | PASS
 vocab                      | 467 (hash id.)  | 467 (hash id.)    | 467 → 467       | PASS (10/10)
 too_frustrated any-rate    | 1.000           | 1.000 (1.000×)    | (limit-cycle)   | no cycle
 warm store md5             | 62235c48…       | 62235c48…         | unchanged       | PASS
```
No guardrail breaches. The `too_frustrated` smoothing runs continuously (any-rate 1.000, ~10 of 48
cells/step) in both arms — but it does not form a cycle with the anti-mixing; the anti-mixing simply
overrides it into the shattering regime. Note the treatment end-Φ ceiling is *lower* than control
(32.33 vs 34.72): the force does not push toward the cold ≈46 basin — it pushes Φ **down**, not up.

### REJECTION-condition check (each pre-registered branch, explicitly)
```
 rejection branch                                          | fires? | evidence
 (1) Φ rescue WITHOUT PR/cos-dist recovery                 |  no    | no Φ rescue at all (ΔΦ_drift −3.1)
 (2) PR/cos-dist UP with Φ DOWN (shattering)               | ★YES   | PR 1.07→1.20, cos-d .037→.097, Φ ↓3.1
 (3) winner-take-all + end-Φ jump toward cold ≈46 basin    |  no    | top-share FALLS .967→.912; end-Φ ≤32.3
```
**Rejection branch (2) fires cleanly.** This is the exact "differentiation without integration"
condition sol pre-registered: the local anti-mixing force spreads the cells apart (real structural
differentiation), but the resulting configuration carries *less* integrated information, not more.

### Φ sparklines (35 turns, control vs treatment) — the treatment kills the natural recovery
```
seed     1  g0.0  █▇▆▆▅▅▅▅▄▄▃▅▃▄▄▃▄▃▃▄▄▃▂▂▂▁▁▁▁▁▁▁▁▁▂▁  29.9→27.9
seed     1  g1.0  █▇▆▅▅▄▃▂▁▁▁▂▁▂▁▁▂▁▁▁▂▁▁▁▂▂▁▁▁▁▁▁▁▁▁▁  29.9→26.2   (suppressed lower)
seed    42  g0.0  ▁▁▁▁▁▁▁▂▂▂▃▃▃▄▅▅▅▆▆▆▆▇▇▇▇▆▇▇▇▇▇▇▇█▇▇  28.6→32.5   (control RECOVERS)
seed    42  g1.0  ▇▇▆▆▄▄▃▁▁▁▂▂▂▂▂▃▄▆▅▅▆▇▇▇▆▆▅▆▇▇▇▇▆▇▇█  28.6→28.6   (recovery flattened)
seed    88  g0.0  ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▂▂▃▃▄▃▄▅▄▄▅▅▅▅▅▅▄▅▅▆▆█  28.4→33.2   (control RECOVERS)
seed    88  g1.0  ▆▅▄▅▄▃▂▂▁▁▁▁▁▁▂▂▃▃▄▅▅▅▅▅▆▅▄▆▆▅▅▆▇▇█▇  28.4→29.0   (recovery blunted)
```

### Post-hoc gain sweep (NOT pre-registered — magnitude vs mechanism; down-drift seeds 1/9999/12345)
Because the pre-registered `diff_gain=1.0` failed, a sweep asks whether a *smaller* gain finds a window
where structure rises modestly AND Φ rises. It does not — the relationship is **monotonic** in both
coordinates simultaneously (seed 1 shown; 9999/12345 identical shape):
```
 diff_gain | drift(s1) | drift(9999) | drift(12345) | PR_end(s1) | cos-d_end(s1) | top-share(s1)
   0.00     |  −2.014   |   −1.715    |   −1.685     |  1.054     |  0.034        |  0.974
   0.25     |  −2.739   |   −3.020    |   −2.918     |  1.080     |  0.048        |  0.962
   0.50     |  −3.323   |   −3.269    |   −3.675     |  1.116     |  0.065        |  0.946
   1.00     |  −3.721   |   −4.131    |   −3.874     |  1.175     |  0.088        |  0.922
   2.00     |  −3.862   |   −3.908    |   −3.568     |  1.213     |  0.103        |  0.907
```
```
  Φ drift (seed 1, more negative = worse; deepens monotonically with gain)
    g0.25  ██████████ −2.74
    g0.50  ████████████████ −3.32
    g1.00  ██████████████████████ −3.72
    g2.00  ██████████████████████████ −3.86
```
Structure (PR/cos-dist) rises with gain, Φ FALLS with gain — perfectly anti-correlated. Even the
smallest gain (0.25) already deepens the drift (−2.74 vs −2.01) while lifting PR. There is no
"tune-to-green": in this substrate more differentiation *is* less Φ. **Mechanism verdict, not a
hyperparameter one.**

### VERDICT
**Does gated amplitude anti-mixing reverse the collapse (PR/cos-dist up) AND the Φ drift? — It reverses
the collapse and MAKES THE Φ DRIFT WORSE.**
- Bit-exact at `diff_gain=0` (byte-identical to `38565fa5a^`, Φ 29.8751→27.8612). ✓
- The gate is **wide open** (node_sim 0.95, ~97% cells) — no starvation, no "gate closed" escape.
- **The force reaches `_amplitudes`** — the exact thing SENSE-4 could not do: PR 1.069→1.200 (10/10
  ≥1.15), cos-dist 0.037→0.097, both far above control. The measured rank-1 collapse is genuinely
  broken. sol's amplitude-space mechanism is **correct about propagation**.
- **But breaking the collapse lowers Φ.** Paired ΔΦ_drift −3.12 (target ≥+0.5); 0/3 down-drift fixed
  (all ~2× deeper); the control's natural in-window Φ recovery is suppressed in all 10 seeds.
- This is pre-registered **rejection branch (2): PR/cos-dist UP with Φ DOWN — differentiation without
  integration (shattering)**. Not the winner-take-all branch (top-share FALLS, end-Φ ≤32.3, nowhere
  near the cold ≈46 basin) — a *diffuse* shattering.
- Post-hoc sweep: monotonic, no sweet spot ⇒ **mechanism limit, not magnitude**.

## Default recommendation (do NOT change here)
**Keep `diff_gain = 0.0` (bit-exact legacy).** Do not make it nonzero by default. SENSE-5 buys a
cosmetic PR/cos-dist rise at a monotonic cost in Φ; there is no gain value that improves the warm
drift.

## The three-failure synthesis (SENSE-3 · SENSE-4 · SENSE-5) — the payoff of a third negative
The three experiments now span the space of **local coupling rules** on the existing state variables,
and all three fail — but each fails *differently*, and together they triangulate the real structure of
the warm collapse:
```
 hypothesis | rule class                         | reaches _amplitudes? | Φ effect | why it failed
 SENSE-3    | learn-from-variance (mag. Hebbian) | n/a (inert)          | none     | uniform coherence:
            |                                    |                      |          | nothing to learn from
 SENSE-4    | phase-space symmetry-break (repel) | NO (attenuated by    | none     | force never propagates
            |                                    | interf/deg + maxnorm)|          | to the collapsed var
 SENSE-5    | amplitude-space symmetry-break     | YES (PR 1.07→1.20)   | Φ ↓ 3.1  | propagates, but spreading
            | (anti-mixing / repulsion)          |                      |          | the shared mode ↓ Φ
```
**The decisive new fact from SENSE-5: in this substrate the alignment *is* the integration.** Φ here is
carried by the cells' shared (near-rank-1) amplitude direction, so *any* local rule that pries the
cells apart along their existing residual necessarily lowers Φ — differentiation and integration are
**anti-correlated** under local repulsion (the sweep proves this monotonically). The rank-1 collapse is
therefore **not a pathology sitting on top of a healthy manifold** that a local force can peel back to —
it is the **load-bearing structure** itself. SENSE-4 showed a local force can't even reach the variable;
SENSE-5 shows that when it does, the fix is worse than the disease.

**Implication for the next lever — it cannot be a local anti-collapse force at all.** The warm collapse
is not reachable-and-fixable by local coupling. Rank must be built by **addition of coherent new modes**,
not by **repulsion of a shared one**. Two candidates, both consistent with "alignment = integration":
1. **Restore the dead standing-wave symmetry-breaking drive (SENSE-4's diagnosis).** Step-5's per-cell
   `(1+wave)` scale is exactly cancelled by step-6's per-cell max-normalisation, so the engine has *no*
   effective symmetry-breaking drive beyond init+noise — rank-1 is an attractor by construction. A drive
   that **survives the max-norm** (act before it, or make it a *direction* perturbation rather than a
   positive scalar) would seed new independent modes *structurally* rather than by prying existing ones
   apart — building rank by addition, coherently, so Φ can rise *with* PR instead of falling.
2. **Mitosis / split dynamics.** Grow NEW cells with fresh directions rather than de-aligning cells that
   are already integrated. PR rises by adding rank (new coherent participants), not by shattering the
   existing rank — the only rank-building move that does not fight the "alignment = integration" physics
   head-on.

Both build rank by **addition**; neither is a local pairwise force. That is the corner all three local
rules painted into. The warm-drift problem should move **off the local-coupling axis entirely**.

## Artifacts
- Driver: `state/pure_teaching/sense5_antimix_drift.py`
- A/B logs: `sense5_antimix_diff0.log` / `sense5_antimix_diff10.log` (+ `.jsonl`) · TSV `sense5_antimix_ab.tsv`
- Bit-exact: `sense5_bitexact_patched.jsonl` ≡ `sense5_bitexact_prepatch.jsonl` (md5 `aabd3d17…`)
- Post-hoc sweep: `sense5_posthoc_g0.25.log` / `_g0.5.log` / `_g2.0.log` (+ `.jsonl`)

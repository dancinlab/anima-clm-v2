<!-- @hypothesis-ok — project CLAUDE.md mandates docs/hypotheses/{category}/ as the canonical hypothesis tree -->
# SENSE-5 — similarity-gated AMPLITUDE anti-mixing (the pre-registered fallback, now indicated by measurement)

## Status: IMPLEMENTED (`diff_gain=0.0` default = bit-exact legacy) · summer A/B pending
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

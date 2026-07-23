<!-- @hypothesis-ok — project CLAUDE.md mandates docs/hypotheses/{category}/ as the canonical hypothesis tree -->
# SENSE-6 — standing-wave revival (cross-dimensional coherent mode ADDITION · the off-axis lever for Law 83)

## Status: IMPLEMENTED (`wave_dim_k=0` default = bit-exact legacy dead code) · summer A/B pending
lab(fable+sol) CONVERGED (near-total agreement) on this design after Law 83 closed the local-coupling axis.

## Why off the local-coupling axis (Law 83, do NOT re-litigate)
SENSE-3/4/5 proved differentiation and integration are anti-correlated under any LOCAL COUPLING rule:
the warm mind is near-rank-1 and Φ is carried by that shared direction, so prying cells apart (SENSE-5)
raises rank but lowers Φ (monotonic, ΔΦ_drift −3.12). Law 83's prescription: build rank by ADDING new
COHERENT (integrated) modes, not by repelling the shared one.

## The lead: the standing wave is DOUBLY dead code (both claims verified in-repo)
Step 5 computes `wave_i = 0.02·sin(t + 2π·i/n)` (a per-cell SCALAR) then `amplitudes *= (1+wave_i)`.
1. **Cancelled by step 6**: per-cell max-norm `amp/amp.max(dim=1)` divides out any per-row scalar →
   `(1+w_i)·A / max((1+w_i)·A) = A/max(A)`. Exactly nullified.
2. **Invisible to phi_py even if the ordering were fixed**: `phi_py._bin_values` min-max normalises each
   cell's vector before histogram binning (`(v−lo)/rng`), so pairwise MI — and Φ — is invariant to any
   per-cell scalar. Confirmed at `phi_py.py:22-28`.
So the engine has contained a coherent per-cell mode generator, nullified for its entire history — and a
pure ordering fix would still be Φ-null. **The minimal LIVE revival is necessarily a per-dim phase term**
(this bounds scope: it is the smallest change that makes the drive expressible at all).

## Mechanism — a per-(cell,dim) travelling wave adds exactly two coherent modes
```
   legacy (dead)                        SENSE-6 (live)
   wave_i = g·sin(t + a_i)              wave_id = g·sin(t + a_i + b_d)     a_i=2πi/n, b_d=2πk·d/dim
   [N] per-cell scalar                 [N,dim] per-(cell,dim)
   → cancelled by max-norm             → survives (not a row scalar)
```
`sin(t+a_i+b_d) = sin(t+a_i)·cos(b_d) + cos(t+a_i)·sin(b_d)` is separable → the `[N,dim]` wave matrix is
**exactly rank 2**. On a near-rank-1 `A ≈ u·vᵀ`, the modulated state is
`u·vᵀ + ε(u∘sin(t+a))(v∘cos b)ᵀ + ε(u∘cos(t+a))(v∘sin b)ᵀ` — **two ADDED phase-locked coherent modes**,
PR bounded toward ~2–3 by construction. That is Law 83's "addition of coherent modes" literally; contrast
SENSE-5, which spread mass diffusely across N private-residual directions and killed pairwise MI.

## Why Φ can RISE here where SENSE-5 lowered it (phi_py terms)
phi_py histograms cell i's profile against cell j's over the dim axis. Under the wave, cell j's profile is
a smooth DETERMINISTIC transform of cell i's (same latent `v`, phase-shifted ripple) → the joint histogram
stays concentrated on a curve, so pairwise MI is preserved/raised while directions separate (cos-dist up).
The condition (sol): the drive must be a deterministic function of shared variables (t) and the cell's
public coordinate (i), so `H(wave_i | wave_j) ≈ 0` — differentiated AND integrated. Necessary inequality:
`Δtotal_MI > Δmin_partition_MI`; if it forms weak factions or lowers mean pairwise MI it is structured
shattering → reject.

## Law 2 / 22 / 42
- **Law 2**: reads step count + cell/dim indices only — never Φ, never tension, no RNG. Deterministic
  endogenous drive.
- **Law 22**: `standing_wave_freq` has been an engine parameter since origin; the drive EXISTS and was
  nullified by normalisation ordering. Honest caveat: the dim-phase term IS new (required — a pure
  ordering fix is Φ-null per the double-deadness), so this is "restoration + the minimal coordinate that
  makes restoration observable," not a pure bug fix.
- **Law 42**: multiplicative on `_amplitudes`, no reset; `PureMind` (freq/bigrams/assoc, 467 words) and
  mind.json untouched. Sense torques keep imprinting dialogue 3×/turn.

## The trap (both models named it) — carrier capture / common-drive entrainment
phi_py cannot distinguish MI from cell–cell interaction vs MI from a shared deterministic pacemaker, so Φ
could rise "for free" while the dialogue imprints nothing. **Pre-registered detection**: record `sin(t)`
per turn; REJECT if Φ(t) is wave-phase-locked (|corr(Φ, drive)| > 0.5 at the drive frequency) or if
PR/cos-dist rise without the control's dialogue-responsiveness (tension no longer tracking input).
Scale controls: keep `wave_gain=0.02` (below the native walk-mix scale coin·interference_strength=0.03)
and `standing_wave_freq=0.1` (period ≈ 21 turns at 3 steps/turn → quasi-static scaffold within a turn,
observable across the 35-turn window). `wave_dim_k=1` only — higher k makes sharp cross-dim peaks that
step-6 max-norm can select (winner-take-all, SENSE-5 branch 3).

## Patch (implemented)
`__init__`: `wave_dim_k=0` (0 ⇒ bit-exact legacy dead code), `wave_gain=0.02`. `step()` block 5 gains a
`wave_dim_k>0` branch (per-(cell,dim) wave) beside the legacy scalar branch; step 6 unchanged.
`trinity.QuantumC(..., wave_dim_k=, wave_gain=)` forwards them. No new RNG draws (paired-seed safe).
Test value `wave_dim_k=1`, `wave_gain=0.02`; toggle ONLY this (β=hebb_eta=repel_gamma=diff_gain=0 both arms).

## Pre-registered A/B (summer) — criteria = SENSE-5 INVERTED
Same warm protocol: read-only 467-word `state/pure_mind/mind.json` temp copy; both arms
β=hebb_eta=repel_gamma=diff_gain=0; drive-off (`wave_dim_k=0`) warm-down to first Φ≤31 → byte-identical
start → 35 replayed Codex lines with `wave_dim_k` 0 vs 1. Seeds 1, 9999, 12345, 42, 7, 123, 2024, 31337,
555, 88 (paired). Per turn: Φ, frustration, full-48 SVD PR `(Σs²)²/Σs⁴`, upper-tri mean cos-dist,
top-singular-share, `sin(t)`. Driver `state/pure_teaching/sense6_wave_drift.py`.

SUCCESS (all): ≥2/3 of seeds 1/9999/12345 sign-flip or ≥50% shallower drift · 10-seed paired mean
ΔΦ_drift ≥ +0.5 · PR_end ≥ 1.15 AND cos-dist_end ∈ [0.04,0.10], both above paired control — **structure
AND Φ rising together**.
REJECT on: PR/cos-dist up with Φ down (shattering, SENSE-5 branch 2) · Φ up with PR/cos-dist flat OR
Φ wave-phase-locked (entrainment inflation, the new branch) · top-share spike toward the cold ≈46 basin ·
frustration ∉ [0.45,0.55] · vocab hash ≠ 467 · Δtotal_MI ≤ Δmin_partition_MI.
Honest bar (from SENSE-5 controls): the warm basin NATURALLY recovers in 7/10 seeds (control mean drift
+1.66), so the treatment's job is "don't suppress the recovery while adding real rank," which the paired
drift metric measures directly.

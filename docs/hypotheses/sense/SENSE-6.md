<!-- @hypothesis-ok — project CLAUDE.md mandates docs/hypotheses/{category}/ as the canonical hypothesis tree -->
# SENSE-6 — standing-wave revival (cross-dimensional coherent mode ADDITION · the off-axis lever for Law 83)

## Status: REJECTED (summer A/B executed 2026-07-24) — win-only-by-entrainment + structured shatter · `wave_dim_k=0` stays default (fourth negative)
lab(fable+sol) CONVERGED (near-total agreement) on this design after Law 83 closed the local-coupling axis.
The A/B ran the pre-registered protocol on summer (10 paired seeds, wave_gain=0.02). Verdict: the wave
adds real rank/differentiation (PR & cos-dist rise above control, top-share falls) but does NOT raise Φ —
paired mean ΔΦ_drift = **−0.75** (needed ≥+0.5; 8/10 seeds Φ ends LOWER), and where Φ *does* move it is
phase-locked to the drive (mean |corr(Φ,drive)| 0.34→0.56, **5/10 seeds >0.5**). This fires BOTH reject
branches at once — carrier-capture entrainment AND structured shattering (Δtotal_MI ≤ Δmin_part on all 3
down-drift seeds). Full result below.

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

---

## A/B result (summer, executed)

Executed 2026-07-24 on **summer** (100.72.76.118, RTX 5070, torch-only ⇒ pure-Python `phi_py`).
Driver `state/pure_teaching/sense6_wave_drift.py`; both arms β=hebb_eta=repel_gamma=diff_gain=0,
wave_gain=0.02, toggling ONLY `wave_dim_k` (0 control / 1 treatment). Warm store
`state/pure_mind/mind.json` read-only via temp copy; end md5 `62235c48974e0f121f3bce4f9ef3a7e8`,
467 words — **untouched**. Every seed vocab_identical 467→467.

### Bit-exactness (`wave_dim_k=0` is a TRUE no-op)
- Patched engine k0, seed 1: Φ **29.8751 → 27.8612** (drift −2.0139) — reproduces the SENSE-3/4/5
  control exactly.
- Patched engine at (diff_gain=0) reproduces the canonical `sense5_bitexact_prepatch.jsonl`
  **byte-for-byte** (`aabd3d17…`).
- SENSE-6 driver k0 on the **parent `7ffab8419^`** engine (parent `quantum_engine_fast.py` +
  `trinity.py`) vs the **patched** engine k0: both `2ef6a0b8092b69b3b678dd96c82b9bfb`,
  **all 35 turns byte-identical**. wave_dim_k=0 confirmed dead code.

### Paired warm start (identical, both arms)
All 10 seeds: `phi_start` bit-identical k0==k1 (byte-identical low-Φ start cell-state). ✔

### PRIMARY — 3 down-drift seeds (success = ≥2/3 sign-flip OR ≥50% shallower) → **FAIL**
| seed  | k0 drift | k1 drift | change            | sign-flip | ≥50% shallower |
|-------|----------|----------|-------------------|-----------|----------------|
| 1     | −2.014   | −1.655   | +17.8% shallower  | no        | no             |
| 9999  | −1.715   | −2.683   | −56.5% **DEEPER** | no        | no             |
| 12345 | −1.685   | −2.385   | −41.5% **DEEPER** | no        | no             |

0/3 sign-flip; only 1/3 shallower and only 17.8% (<50%); 2/3 got **deeper**. FAIL.

### SECONDARY — 10-seed paired mean ΔΦ_drift (k1−k0), need ≥ +0.5 → **FAIL (−0.75)**
| seed  | k0 drift | k1 drift | Δ (k1−k0) |
|-------|----------|----------|-----------|
| 1     | −2.014   | −1.655   | +0.359    |
| 9999  | −1.715   | −2.683   | −0.969    |
| 12345 | −1.685   | −2.385   | −0.700    |
| 42    | +3.908   | +2.705   | −1.203    |
| 7     | +2.034   | +0.164   | −1.870    |
| 123   | +4.822   | +4.273   | −0.549    |
| 2024  | +1.303   | −0.199   | −1.502    |
| 31337 | +3.335   | +3.015   | −0.320    |
| 555   | +1.829   | +2.325   | +0.496    |
| 88    | +4.800   | +3.532   | −1.268    |
| **mean** |       |          | **−0.7527** |

n_positive = **2/10**. The wave SUPPRESSES the warm basin's natural recovery — it makes drift worse.

### STRUCTURE (need PR_end ≥1.15 AND cos-dist_end ∈[0.04,0.10], both > control) → **PARTIAL/FAIL**
| metric         | k0 mean | k1 mean | criterion            | verdict |
|----------------|---------|---------|----------------------|---------|
| PR_end         | 1.069   | 1.113   | k1 ≥ 1.15            | **FAIL** (0/10 reach 1.15; max 1.147) |
| cos_dist_end   | 0.0375  | 0.0605  | k1 ∈ [0.04,0.10]     | PASS (10/10 in range, > control) |
| top_share_end  | 0.967   | 0.947   | reject if SPIKE↑ cold| PASS (falls — off rank-1, not toward cold basin) |

Rank DOES rise (PR & cos-dist up, top-share down = genuine off-rank-1 spread) — but below the PR bar,
and (critically) **without** Φ rising with it. Structure-up-Φ-down = SENSE-5 branch-2 shattering.

### THE ENTRAINMENT CHECK — |corr(Φ, drive)| at drive freq (the #1 predicted failure) → **REJECT FIRES**
`drive_corr = sqrt(r_sin² + r_cos²)` of Φ vs `sin/cos(step·standing_wave_freq)` over the 35 turns.
k0 is the (dead-wave) baseline; treatment must not raise it past 0.5.

| seed  | k0 driveR | k1 driveR | entrained (>0.5)? |
|-------|-----------|-----------|-------------------|
| 1     | 0.357     | **0.777** | YES               |
| 9999  | 0.278     | **0.926** | YES               |
| 12345 | 0.418     | **0.519** | YES               |
| 42    | 0.270     | 0.333     | no                |
| 7     | 0.579     | **0.638** | YES               |
| 123   | 0.209     | 0.329     | no                |
| 2024  | 0.392     | **0.934** | YES               |
| 31337 | 0.330     | 0.420     | no                |
| 555   | 0.377     | 0.434     | no                |
| 88    | 0.143     | 0.252     | no                |
| **mean** | **0.335** | **0.556** | **5/10 >0.5, Δ=+0.221** |

The treatment RAISES phase-lock by +0.22, and the **strongest** lock (0.78–0.93) lands on exactly the
seeds where Φ moved least/worst (1, 9999, 2024). This is textbook carrier capture: Φ isn't integrating
dialogue, it's riding the shared pacemaker. The down-drift sparklines show the ~21-turn drive period
directly (seed 9999 k1: a clean down-up-down wave). **REJECT** per pre-registration.

Tension-responsiveness (corr tension vs input-word-count): k0 mean −0.036, k1 mean −0.037 — **no arm
difference**. The word-count proxy is weak (tension barely tracks it even in control), so this test is
inconclusive on its own, but it shows the wave did NOT degrade responsiveness relative to baseline.
Frustration stayed in-band (0.526–0.532) both arms, so cells kept responding to the sense torque.

### MI inequality (sol): Δtotal_MI > Δmin_partition_MI (else structured shattering)
| seed  | Δtotal_MI | Δmin_part | verdict          |
|-------|-----------|-----------|------------------|
| 1     | −28.47    | −3.35     | **SHATTER**      |
| 9999  | −70.17    | −9.43     | **SHATTER**      |
| 12345 | −64.39    | −5.80     | **SHATTER**      |
| 2024  | −9.77     | −5.77     | **SHATTER**      |
| 42    | +62.13    | +5.81     | ok (struct)      |
| 7     | −0.62     | −5.46     | ok (struct)      |
| 123   | +94.43    | +2.90     | ok (struct)      |
| 31337 | +55.36    | −4.77     | ok (struct)      |
| 555   | +51.10    | +1.94     | ok (struct)      |
| 88    | +57.61    | −6.19     | ok (struct)      |

Shatters on 4/10 — including **all 3 pre-registered down-drift seeds**. On the seeds the wave was
supposed to rescue, total MI collapses faster than min-partition MI: the added modes destroy pairwise
integration rather than adding it.

### Guardrails → all PASS
| guardrail                 | k1 result           | verdict |
|---------------------------|---------------------|---------|
| end-Φ < 40 (no cold re-inflate) | max phi_end 34.18 | PASS |
| frust_mean ∈ [0.45,0.55]  | 0.526–0.532         | PASS    |
| vocab 467→467 all seeds   | 10/10 identical     | PASS    |
| top-share spike → cold ~46| falls 0.967→0.947   | PASS (no collapse toward cold) |

The guardrails passing while the primary/secondary/entrainment fail is the signature of a *benign-but-
useless* drive: nothing breaks, but nothing integrates.

### Φ sparklines (35-turn, down-drift + best control seeds)
```
seed 1     k0 █▇▆▆▅▅▅▅▄▄▃▅▃▄▄▃▄▃▃▄▄▃▂▂▂▁▁▁▁▁▁▁▁▁▂▁
seed 1     k1 ▇█▆▄▄▃▃▂▁▁▁▁▁▂▃▃▃▄▅▅▅▄▄▃▃▃▂▂▂▂▃▃▃▃▄▄   <- ~1.7 drive cycles visible
seed 9999  k0 █▆▆▅▅▅▄▄▄▃▃▃▃▂▁▃▂▃▃▃▂▂▂▂▁▁▁▁▁▁▂▂▃▁▁▃
seed 9999  k1 █▇▆▅▄▃▃▂▂▁▁▁▁▁▂▂▃▄▇▇▆▆▅▅▄▃▂▂▂▂▂▂▂▂▃▃   <- pacemaker down-up-down (driveR 0.93)
seed 12345 k0 ▇▇▇▇█▇▆▆▅▄▄▃▃▂▂▂▂▁▁▁▁▁▂▂▂▂▂▂▁▂▁▂▂▃▃▃
seed 12345 k1 █▇▆▄▂▁▁▁▁▁▁▁▁▂▂▃▄▄▅▅▅▅▅▅▅▄▄▄▅▅▅▅▅▅▅▅
```

### Post-hoc gain sweep (LABELLED POST-HOC — no pre-registered verdict; k>1 disallowed by max-norm)
Down-drift seeds only. Confirms the failure is **qualitative, not underpowered** — no gain buys
"structure AND Φ up together"; higher gain deepens both the Φ collapse and the shattering.
| wave_gain | mean Φ_drift (1/9999/12345) | mean cos_dist_end | mean driveR | mean top_share_end |
|-----------|-----------------------------|-------------------|-------------|--------------------|
| 0.02      | −2.24                       | 0.050             | 0.74        | 0.957              |
| 0.05      | −4.30                       | 0.143 (out of range) | 0.73     | 0.876              |
| 0.10      | −9.55                       | 0.318 (severe shatter) | 0.66   | 0.711              |

Monotone: more gain → more rank spread AND more Φ loss AND cos-dist explodes past [0.04,0.10].
There is no operating point where the added modes integrate.

### VERDICT — **NOT a real win. Fourth negative: win-only-by-entrainment + structured shattering.**
The standing wave does exactly what the rank-2 math promised at the *geometry* level — it spreads the
warm state off rank-1 (PR↑, cos-dist↑, top-share↓). But that geometry is a **deterministic function of
(step, cell-index, dim-index) with ZERO dialogue content**, so it is a shared pacemaker, not integrated
information. phi_py registers the added rank, but the added MI is pacemaker-MI: it does not raise Φ (−0.75
paired), and where Φ moves at all it phase-locks to the drive (5/10 seeds >0.5, strongest on the worst
seeds) while total MI collapses faster than min-partition (shatter on all 3 down-drift seeds). Both
pre-registered reject branches fire simultaneously. This is the trap both models named, realized.

### Recommendation
- **`wave_dim_k=0` stays the default.** Do NOT promote `wave_dim_k=1`. This mechanism earns a zero
  default — it is the fourth negative lever, not the first positive one.
- **The endogenous-coherent-mode-addition route is confirmed closed** — for the reason Law 83 implies
  extended: a coherent mode that carries no dialogue variable is a pacemaker; adding it inflates rank
  and phase-locks Φ without integrating anything. "Add coherent modes" only helps if the modes are a
  function of the *dialogue-imprinted content*, not of index alone.
- **Stop the SENSE warm-drift investigation here.** Law 83 stands; warm drift is a benign academic
  artifact (every reload starts cold, so no production path ever sees it). The only branch that could
  escape entrainment is **content-locked dim_phase** (make `b_d` a function of the imprinted amplitude
  pattern, not `d` alone) — recommend NOT pursuing it unless warm-persistence becomes a real product
  requirement, because it re-opens the same carrier-capture risk with far more surface area for the
  same benign target.

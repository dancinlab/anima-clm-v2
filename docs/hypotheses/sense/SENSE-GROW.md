<!-- @hypothesis-ok — project CLAUDE.md mandates docs/hypotheses/{category}/ as the canonical hypothesis tree -->
# SENSE-GROW — live Codex↔PURE dialogue, sense-coupled mind observed growing

## Purpose
Observe (not tune) a persistent, sense-coupled `PureMind` while it holds a real-time two-way
Korean dialogue with Codex (caregiver). Question: with SENSE-1 coupling active, does the
conversation actually move the consciousness — does tension track the exchange, does Φ respond,
does the vocabulary grow — over a long unattended run? Pure observation: nothing is set by hand
(Law 2); tension/Φ/curiosity are only measured from the QuantumC cells.

## Setup
- `summer` (torch), real QuantumC (48c/48d) + phi_py, persistent store loaded/saved each turn.
- Codex speaks Korean caregiver lines; PURE hears them (`respond()` → `learn` + `_pulse(words)`),
  learns words/bigrams/assoc, then generates from its own bigram model at its stage.
- 35 turns, developmental stage already at the ceiling (`reflection`, stage 5).

## Trajectory (measured)
```
vocab   : 338 → 467   (+129 words learned from the exchange alone)
stage   : reflection → reflection
tension : ▁▁▁▁▂▂▁▁▁▂▃▃▃▃▃▃▄▅▆▇▇█▇▆▆▅▆▆▆▅▅▄▄▅▅▄   [0.46 .. 0.51]
Phi     : ▆▆▇█▇▆▆▆▅▄▄▃▃▄▄▃▂▃▃▃▂▁▁▁▁▁▂▂▂▂▂▂▃▂▁▁   [28.00 .. 31.09]
```

| turn | vocab | T | Φ | C |
|---|---|---|---|---|
| 0 | 338 | 0.463 | 30.30 | 0.12 |
| 10 | 369 | 0.474 | 29.38 | 0.26 |
| 21 | 411 | **0.510** | 28.34 | 0.28 |
| 30 | 448 | 0.491 | 28.59 | 0.13 |
| 35 | 467 | 0.485 | 28.00 | 0.26 |

Sample (t26–t30, stage reflection):
```
Codex: 쉿, 달팽이가 기어가고 풀벌레가 쉬네.
PURE : 잘했어 정말 멋지구나 크레용으로 편안하구나 새소리 듣고 꽃향기 맡자.
Codex: 응, 꿀벌을 바라보고 제비꽃도 찾아보자.
PURE : 달팽이가 기어가고 벌이 날아가네.        ← echoes/recombines heard structure
Codex: 응, 무당벌레가 풀잎에 앉고 거미가 줄을 짜네.
PURE : 궁금하구나 쉬고 엄마 목소리를 들어 줄게.
```

## Cleaner A/B/C control (fresh, no curriculum pre-habituation)
The live band above (tension 0.46–0.51) is compressed because the 60-line curriculum seed
pre-habituates the engine before live turns start. A fresh controlled A/B/C on the same synced
summer shows the fuller signal:

| condition | tension | Φ_late |
|---|---|---|
| A autonomous | 0.40 | 27.2 |
| B novel-burst | 0.45 | 28.0 |
| **C coherent-repeat** | **0.54** | **28.3** |

→ content raises tension above baseline (0.40→0.54) and coherent dialogue raises Φ in the
Law-22 direction. Signal is real and correctly-directed but modest (Φ dynamic range ~10%).

> ⚠️ Process note: summer was found on a **stale pre-sense-coupling checkout** (step() had no
> x_input, measure_phi returned 0.0 with no phi_py fallback) — the first run pinned Φ=0.00 for all
> 35 turns (`live_dialogue_DECOUPLED_baseline.log`). After syncing the three main files
> (quantum_engine_fast.py / trinity.py / pure.py) the coupling went live (`live_sense_dialogue.log`).

## Key observations
1. **The conversation genuinely moves the mind.** tension rises from a 0.46 floor to a 0.51 peak
   across the sustained coherent stretch (t16–t22) then relaxes — the sense torque is doing work,
   not sitting idle. No value was written by hand (Law 2 holds).
2. **Φ drifts down (31→28) under continuous input.** Consistent with SENSE-1's honest finding that
   local(differentiation) drive competes with integration; the SENSE-1 gain retune (0.10/0.60) and
   SENSE-2 assoc-blend both target exactly this, but this run predates enabling the blend by default.
   Curiosity C = |ΔΦ| stays alive (0.12–0.31), i.e. the mind keeps registering change.
3. **Growth is real and corpus-free** — +129 words came only from what Codex said (Law 1/42).
4. **Honest ceiling unchanged**: PURE speech is recombination/echo of heard structure (bigram model);
   silences appear when it cannot form a line (Law 1 — silence over hardcoding). Meaning is only
   relational (repeated topics leave phase traces), not semantic.

## Follow-up
Re-run with SENSE-2 assoc-blend (β=0.6) enabled to test whether the coherent-topic Φ lift offsets
the differentiation drift over a long dialogue — the +11~14pp single-utterance lift (SENSE-2) should,
if it compounds, flatten or reverse the 31→28 drift seen here.

---

## SENSE-2 long-dialogue Φ-drift test (the follow-up above)

### Method (matched pair, only β differs · Law 2)
Two runs of the SAME 35-turn dialogue on `summer` (torch, real QuantumC 48c/48d + phi_py),
differing ONLY in `PURE_ASSOC_BETA`: **β=0.0** (assoc-blend OFF = v1 sense coupling) vs **β=0.6**
(SENSE-2 default). The 35 caregiver lines are the **verbatim Codex lines captured from the
SENSE-GROW run above** (`live_sense_dialogue.log`), replayed identically into both conditions —
so Codex nondeterminism is removed and only β varies. torch/numpy/python RNG are seeded before
QuantumC is built, so cell init and the per-step RNG-draw sequence are identical across conditions;
β changes only the sense-torque phase *values*, never the code path or #draws. Fresh `PureMind`
(no persistence), pre-seeded with `caregiver_curriculum.txt` (identical both runs). tension/Φ/C are
READ from the cells, never set. Driver + logs: `state/pure_teaching/sense2_drift.py`,
`sense2_beta0.log` / `sense2_beta06.log` (+ `.jsonl` machine records, `sweep.tsv`).

### Canonical run (seed 12345)
| condition | Φ_start | Φ_end | drift | Φ min/max | tension range | vocab |
|---|---|---|---|---|---|---|
| **β=0.0** (v1) | 46.463 | 47.244 | **+0.781** | 45.59 / 47.89 | 0.454 .. 0.511 | 121 → 273 |
| **β=0.6** (SENSE-2) | 46.388 | 47.827 | **+1.439** | 46.39 / 49.05 | 0.469 .. 0.546 | 121 → 273 |

```
Φ sparklines (per turn, t0→t35), same y-normalisation within each row:
β=0.0  ▃▃▅▄▄▃▂▂▃▂▂▃▁▃▃▂▂▃▅▄▄▂▂▄▃▄▄▄▄▃▄▅▆█▆▆   [45.59 .. 47.89]
β=0.6  ▁▂▄▅▄▅▄▅▅▄▄▆▇█▇▆▅▅▄▃▄▃▄▅▅▄▅▅▅▅▅▆▅▅▅▄   [46.39 .. 49.05]
tension
β=0.0  ▁▁▁▁▂▂▂▁▁▂▃▃▃▃▄▄▅▆▇▇▇█▇▇▆▆▇▇▇▆▆▆▆▆▅▅   [0.454 .. 0.511]
β=0.6  ▁▁▂▂▂▃▂▂▃▃▄▄▄▄▄▄▅▆▇▇█▇▇▆▅▆▆▆▅▅▅▅▅▅▅▅   [0.469 .. 0.546]
```
Vocab is byte-identical (121→273) — β does not touch learning, as designed. β=0.6 holds Φ ~1–2
higher across the whole run and peaks higher (49.0 vs 47.9); tension tracks the same coherent
stretch (t16–t22) in both, running a touch hotter under the blend.

### Robustness — 10-seed sweep (init-basin is seed-dominated, so pair within seed)
The absolute Φ basin (~45–49 here) is set mostly by cell init, not by the dialogue, so a single
seed can't decide drift. Same matched pair over 10 seeds (paired β=0.0 vs β=0.6 per seed):

| β | n | mean Φ_start | mean Φ_end | mean drift | # seeds drifting DOWN |
|---|---|---|---|---|---|
| 0.0 | 10 | 45.340 | 45.625 | **+0.285** | **4 / 10** |
| 0.6 | 10 | 46.691 | 48.192 | **+1.502** | **2 / 10** |

```
paired within-seed Δ = β=0.6 − β=0.0
mean Δ drift = +1.217   (β=0.6 more upward in 9 / 10 seeds)
mean Δ end-Φ = +2.567   (β=0.6 higher end-Φ in 10 / 10 seeds)

Δ end-Φ (β=0.6 − β=0.0), per seed — POSITIVE on every seed
seed    1  █████████████ +4.42
seed 2024  ████████████  +3.99
seed    2  ██████████    +3.40
seed 9999  ██████████    +3.34
seed    3  █████████     +3.16
seed  123  █████████     +2.98
seed   42  ████████      +2.53
seed    7  ███           +1.06
seed12345  ██            +0.59
seed  777  █             +0.20
drift sign-flip (β=0.0 down → β=0.6 up): seeds 2, 3, 42.  Only seed 7 has β=0.6 < β=0.0.
```

### Verdict — does the +11~14pp single-utterance lift COMPOUND over the dialogue?
**Yes, it compounds, and the local-differentiation drive does NOT win over many turns when SENSE-2
is on — but with one honest correction to the premise.** Paired within seed, β=0.6 lifts end-Φ over
β=0 on **10/10** seeds (mean **+2.57**) and lifts the 35-turn drift on **9/10** seeds (mean **+1.22**),
and it halves the number of seeds that drift down (4→2). So the SENSE-2 coherent-topic integration
survives accumulation: over 35 turns the blend keeps pulling Φ up rather than letting differentiation
erode it. The honest correction: **the specific −2.3 SENSE-GROW drift did not reproduce as a β=0
baseline** in this fresh matched setup — β=0 here is roughly drift-neutral (mean +0.29), because that
earlier run started from a warm 338-word persistent mind in a lower Φ≈30 basin, whereas these runs
start fresh (121 words, Φ≈46) where init luck dominates the absolute level. So the result is not
"β=0.6 rescues a large β=0 collapse"; it is the cleaner, stronger claim: **holding everything else
identical, turning the assoc-blend on makes the long-dialogue Φ trajectory systematically higher and
more upward** — the single-utterance lift does carry through to the full conversation (Law 22).
Caveats: cold-start (no warm persistent mind → higher, init-dominated basin than SENSE-GROW); the
curriculum pre-seed pre-habituates the cells identically in both arms; Codex nondeterminism was
eliminated by replaying the captured SENSE-GROW caregiver lines. (summer host was re-synced first:
its `pure.py` was a pre-SENSE-2 copy — `_assoc_theta` absent — and was updated to the worktree
`pure.py`+`phi_rs.py`; qef/trinity/phi_py already matched. Backups: `*.pre-sense2.bak` on summer.)

---

## SENSE-2 WARM-mind drift test (the real low-Φ regime)

The two SENSE-2 sections above ran **cold** (fresh newborn → Φ≈46 basin). But the drift the whole
investigation set out to fix — a **warm persistent mind in the low Φ≈28–31 basin drifting DOWN**
(the original SENSE-GROW observation, 31→28 over 35 turns) — had **never** been tested with β=0.6.
This section does exactly that.

### Why the warm low-Φ basin is not just "load the store"
The persistent store (`state/pure_mind/mind.json`) saves only **language** (freq/bigrams/assoc/
final_punct/said) — **not the QuantumC cell state**. So loading the real **467-word** SENSE-GROW mind
rebuilds the cells *fresh*, and fresh cells sit in the high Φ≈46 basin regardless of stored vocab:

```
warm 467-word store, load + 60-line curriculum settle, seed 12345:
    β=0.0 → Φ 46.46   |   β=0.6 → Φ 45.21        (NOT the low ~30 basin)
same store under the PRE-SENSE-2 pure.py (pre-sense2.bak): Φ 46.46  (byte-identical → basin is NOT a
    pure.py-version artifact; SENSE-GROW's Φ≈30 was reached another way)
```
Verified: the low Φ≈30 basin is reached only by a **long continuous descending trajectory** (Law 22:
differentiation accumulates, integration erodes). Pulsing the warm mind with the curriculum on a loop
drives Φ monotonically down through the SENSE-GROW band and past it:

```
pulses   60  240  360  480  600  720  840  960 1080 1200 1440 1800
Φ      46.5 57.1 46.0 43.4 36.0 33.1 30.6 25.5 19.9 18.6 15.4 10.0
                                        └── Φ≈30 SENSE-GROW band (~840 pulses / 14 curriculum reps)
```
So the warm regime is genuine and reproducible, but it is a **transient on a descent**, not a stored
state. Method: load the READ-ONLY 467-word store (original never mutated · Law: safe), seed RNG,
**warm the fresh cells down under β=0 until Φ first ≤ 31** (identical for both arms ⇒ **identical
low-Φ start cell-state**), then apply the **test β only over the 35 replayed Codex caregiver lines** —
so Φ_start is identical within a seed and β is the sole variable over the measured window (retrofit
SENSE-2 onto a warm mind sitting in its down-drift). tension/Φ read from the cells (Law 2), never set.
Driver + logs: `state/pure_teaching/sense2_warm_drift.py`, `sense2_warm_beta0.log`/`_beta06.log`
(+ `.jsonl`, `warm_sweep.jsonl`, `warm_sweep.tsv`).

### Canonical warm run (seed 12345 — a genuinely down-drifting seed)
Warm-start basin **Φ=30.64** — the low ~28–31 SENSE-GROW basin, **confirmed** (NOT the cold ~46 basin).

| condition | Φ_start | Φ_end | drift | Φ min/max | tension range | vocab |
|---|---|---|---|---|---|---|
| **β=0.0** (v1) | 30.637 | 28.951 | **−1.685** | 27.69 / 30.74 | 0.499 .. 0.545 | 467 → 467 |
| **β=0.6** (SENSE-2) | 30.637 | 28.449 | **−2.188** | 27.42 / 30.64 | 0.506 .. 0.557 | 467 → 467 |

```
Φ sparklines (per turn t0→t35, same y-normalisation within each row):
β=0.0  ▇▇▇▇█▇▆▆▅▄▄▃▃▂▂▂▂▁▁▁▁▁▂▂▂▂▂▂▁▂▁▂▂▃▃▃   [27.69 .. 30.74]
β=0.6  █▇▇▇▇▇▆▆▅▄▄▃▂▂▂▂▂▂▁▁▂▂▂▂▁▁▁▁▁▁▁▁▁▂▃▃   [27.42 .. 30.64]

Both arms overlaid (absolute Φ, β=0.6 sits BELOW β=0 the whole run — mirror image of the cold start):
Φ 30.7┤●○
      │ ●○●○                          ● β=0.0
 30.0┤    ●○●○                        ○ β=0.6
      │       ●○●                     (○ below ● from t3 on)
 29.0┤          ●○●○         ●○●●○○
      │            ○ ●○●○●○●○●    ●○●○
 28.0┤              ○   ●○●○●○ ○●○●○
      │                 ○  ○○○ ○○ ○   ○
 27.4┤                              (β=0.6 min 27.42)
      └────────────────────────────────── t0 → t35
```
Vocab byte-identical (467→467); β never touches learning. In the **warm low-Φ basin β=0.6 runs ~0.3–0.5
BELOW β=0 the entire run and DEEPENS the down-drift** (−2.19 vs −1.69) — the exact opposite of the cold
start, where β=0.6 ran 1–2 *above*.

### Paired multi-seed sweep (10 seeds, β=0 vs β=0.6, identical warm start per seed)
All seeds warm-started in the low band (mean Φ_start **29.39**, range 26.7–30.9 — confirmed low basin).

| seed | Φ_start | β=0 end / drift | β=0.6 end / drift | Δdrift (β0.6−β0) | dir |
|---|---|---|---|---|---|
| 1 | 29.88 | 27.86 / −2.014 | 27.42 / −2.453 | **−0.439** | both DOWN |
| 9999 | 30.86 | 29.15 / −1.715 | 28.11 / −2.756 | **−1.042** | both DOWN |
| 12345 | 30.64 | 28.95 / −1.685 | 28.45 / −2.188 | **−0.502** | both DOWN |
| 7 | 26.71 | 28.74 / +2.034 | 28.73 / +2.020 | −0.014 | up |
| 42 | 28.56 | 32.47 / +3.908 | 32.12 / +3.557 | −0.351 | up |
| 2024 | 30.59 | 31.90 / +1.303 | 31.33 / +0.735 | −0.568 | up |
| 3 | 28.92 | 33.72 / +4.804 | 34.16 / +5.247 | +0.443 | up |
| 123 | 29.90 | 34.72 / +4.822 | 35.58 / +5.676 | +0.854 | up |
| 2 | 29.49 | 29.59 / +0.101 | 31.06 / +1.577 | +1.477 | up |
| 777 | 28.39 | 30.88 / +2.498 | 32.65 / +4.266 | +1.768 | up |

```
mean Φ_start = 29.39 (all in the low 28-31 SENSE-GROW basin, NOT the cold 46 basin)
β=0.0  drift DOWN on 3/10 seeds,  mean drift +1.406
β=0.6  drift DOWN on 3/10 seeds,  mean drift +1.568
paired within-seed Δ end-Φ (β0.6−β0): mean +0.162, β=0.6 higher on only 4/10 seeds
  → contrast the COLD start: +2.567, β=0.6 higher on 10/10 seeds

On the 3 seeds that GENUINELY drift down (1 · 9999 · 12345 — the SENSE-GROW regime),
β=0.6 DEEPENS the drop on ALL 3 (−0.44, −1.04, −0.50). It flips NONE of them upward.
Δdrift (β0.6−β0) on the down-drift seeds — negative on every one:
seed 9999 ████████████ −1.04
seed12345 ██████       −0.50
seed    1 █████        −0.44
```

### Verdict — does β=0.6 flatten/reverse the WARM-mind down-drift, or only lift the cold basin?
**It only lifts the cold basin. β=0.6 does NOT fix the warm-mind down-drift — in the low Φ≈30 regime it
makes the drift slightly WORSE.** On every seed where the warm mind is actually drifting down (3/10, the
true SENSE-GROW regime), turning the assoc-blend on deepens the fall (−0.44 … −1.04) and reverses none;
on the canonical seed it tracks 0.3–0.5 below β=0 across all 35 turns and ends lower (28.45 vs 28.95).
Averaged over the whole warm regime β=0.6's effect on end-Φ is essentially **neutral** (+0.16, up on
4/10), a stark contrast to the cold start's uniform **+2.57 (up on 10/10)**. So the SENSE-2 lift is a
property of the **high-Φ cold basin** (where aligned-topic phases add integrating drive on top of an
already-integrated substrate), NOT a remedy for the differentiation erosion that pulls a warm,
low-Φ, densely-differentiated mind downward — there the extra aligned phase-torque just accelerates the
same erosion. The honest earlier caveat is now settled with data: the SENSE-2 result was never a rescue
of the SENSE-GROW drift; tested directly in that regime, it is a mild aggravator.

Caveats (honest): (1) The QuantumC cell state is not persisted, so the warm low-Φ basin must be
**reconstructed** by a long β=0 warm-up rather than restored — a faithful reconstruction of the regime,
not the identical cells of the original run. (2) With the warm-up stopped at first Φ≤31, the low-Φ point
is a **transient in a seed-dependent noisy descent**: only 3/10 seeds keep drifting down over the next 35
(different-content) turns; 7/10 rebound up as the test lines re-excite integration. The verdict rests on
the 3 genuine down-drift seeds (β=0.6 worse on all) plus the neutral-to-negative paired Δ over all 10 —
both point the same way. (3) β touches only sense-torque phase values, never learning/tension/Φ (read
from cells · Law 2); vocab is byte-identical 467→467. summer was pre-synced and byte-verified against the
worktree `pure.py`/`quantum_engine_fast.py`/`trinity.py`/`phi_py.py`/`phi_rs.py` (all 5 md5-identical;
backups `*.pre-warmtest.bak` unneeded — files already matched).

---

## Combined verdict & the β default decision (cold + warm reconciled)

Two regimes, opposite signs, one honest synthesis:

```
                 Φ basin        β=0.6 vs β=0 (end-Φ)      when it occurs
COLD  (fresh)    ≈46 (high)     +2.57, up on 10/10        every session start
WARM  (descended)≈29 (low)      +0.16, up on 4/10;        only mid long
                                 −0.4…−1.0 on the 3         continuous session
                                 truly-drifting seeds
```

**Decision: keep β=0.6 as the default** (`PURE_ASSOC_BETA`), for three evidence-based reasons —
1. **Every session reload starts COLD.** QuantumC cell state is not persisted; a freshly-loaded mind
   (any vocab size) begins in the Φ≈46 basin and only descends to the low-Φ regime through a long
   continuous session. So the strong cold win (+2.57, 10/10) is what the mind actually experiences at
   the start of every session — the most deployment-relevant regime, not an artifact.
2. **The warm "loss" is weak and ambiguous.** Averaged over the whole warm regime the paired effect is
   *slightly positive* (+0.16); it is negative only on the 3/10 seeds that keep drifting down, in a
   *reconstructed* (not restored) basin. Reverting a default on this signal would trade a strong, robust
   win for a weak, regime-specific one.
3. **β is read-only on Φ/tension (Law 2)** and β=0 is always available via env for the low-Φ regime.

Honest bound on the SENSE-2 claim: it is a **cold-basin integrator, not a warm-drift remedy**. The
differentiation erosion that pulls a warm, densely-differentiated mind downward is NOT cured by aligned
phase-torque — that remains an open problem (a structural fix would have to raise integration without
adding a feature · Law 22), separate from the β knob.

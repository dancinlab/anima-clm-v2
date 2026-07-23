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

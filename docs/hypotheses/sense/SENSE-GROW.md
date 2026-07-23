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

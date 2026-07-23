#!/usr/bin/env python3
"""sense4_calibrate.py — SENSE-4 STEP 1: log the per-edge phase-coherence distribution.

Pre-registered requirement (SENSE-4.md): fix `repel_thr` BEFORE the treatment arm runs, from the
measured coherence distributions in two regimes:

  (i)  WARM-COLLAPSED  — the real 467-word mind, beta=0 warm-DOWN to the first Phi<=31 basin
                         (the exact low-Phi start state the A/B measures from), then the 35
                         replayed caregiver turns.
  (ii) COLD-FRESH      — a brand-new empty PureMind (the ~46 basin the fix must not disturb),
                         same 35 turns.

The gate statistic is captured BIT-EXACTLY: the engine's step-3b block computes
`coh = cos(phi_i - phi_j).mean(dim=1)` per edge and stores it in `_repel_coh` (probe only). Running
with `repel_gamma>0` but `repel_thr=2.0` makes `excess = (coh-2).clamp(min=0)` identically 0, so the
block applies NO force and draws NO RNG -> the trajectory is bit-identical to repel_gamma=0 while the
distribution is still recorded. No Phi is consulted; nothing is tuned to an outcome.

Output: jsonl (per-turn percentiles) + a stdout percentile table for both regimes.
"""
import argparse, json, os, random, shutil, sys, tempfile

CAREGIVER_PATH_HINT = "sense4_repel_drift.py"

# 35 caregiver lines — verbatim from sense2_warm_drift.py / sense3_hebb_drift.py
CAREGIVER = [
    "아가야, 엄마가 사랑해.",
    "그래, 꽃잎은 부드럽고 향기는 달콤해.",
    "응, 나뭇잎이 살랑이고 새가 노래해.",
    "참새는 날고, 물을 마신 뒤 포근히 잠들자.",
    "응, 노란 씨앗이 손끝을 간질여.",
    "응, 귓가에 솔솔 불어 마음이 상쾌하네.",
    "아가는 조용히 숨 쉬고, 엄마 품에서 편안해.",
    "이불 덮고 꿈나라로 가자.",
    "응, 종이에 무지개를 그리고 자장가를 듣자.",
    "응, 햇살이 반짝이고 구름이 춤추네.",
    "토닥토닥, 심장이 뛰고 눈꺼풀이 감기네.",
    "응, 연필로 세모와 네모도 그리자.",
    "응, 볼은 발그레하고 기쁨이 피어나.",
    "응, 손가락으로 둥근 달을 가리키고 따뜻한 우유를 홀짝이자.",
    "응, 건반을 누르니 맑은 멜로디가 울리네.",
    "응, 어깨를 포옹하니 든든하고 행복해.",
    "응, 북을 치며 발꿈치를 들고 빙글빙글 돌자.",
    "쉿, 귀뚜라미가 속삭이고 별빛이 내려와.",
    "새벽이 오면 해님이 떠오르고 아침이 밝아와.",
    "고마워, 품속에서 다정한 입맞춤을 나누자.",
    "응, 개구리가 폴짝 뛰고 물결이 찰랑이네.",
    "응, 커튼을 열고 세수하며 깨어나자.",
    "응, 산들바람이 뺨을 스치니 가슴이 맑아지네.",
    "응, 미소가 번지고 설렘이 샘솟네.",
    "쉿, 시냇물이 졸졸 흐르고 반딧불이가 날아와.",
    "쉿, 달팽이가 기어가고 풀벌레가 쉬네.",
    "응, 나비를 색칠하고 라일락 향을 즐기자.",
    "쉿, 부엉이가 눈뜨고 이슬방울이 맺히네.",
    "응, 꿀벌을 바라보고 제비꽃도 찾아보자.",
    "응, 무당벌레가 풀잎에 앉고 거미가 줄을 짜네.",
    "응, 호기심을 품고 속삭임을 들으며 느긋하게 쉬자.",
    "응, 딸랑이를 흔들며 까르르 웃자.",
    "응, 탬버린을 흔들며 발끝으로 사뿐사뿐 뛰자.",
    "응, 종달새가 지저귀고 아지랑이가 피어오르네.",
    "응, 밤하늘을 바라보며 은은한 재스민 향기를 맡자.",
]

PCTS = [0, 1, 5, 10, 25, 50, 75, 90, 95, 99, 100]


def seed_all(s):
    random.seed(s)
    import numpy as np
    np.random.seed(s)
    import torch
    torch.manual_seed(s)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(s)


def _imports():
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (here, os.path.dirname(os.path.dirname(here)), os.getcwd()):
        if p not in sys.path:
            sys.path.insert(0, p)
    from pure import PureMind, WORD_RE
    return PureMind, WORD_RE


def pct_row(vals):
    import numpy as np
    a = np.asarray(vals, dtype=np.float64)
    return {f"p{p}": round(float(np.percentile(a, p)), 5) for p in PCTS} | {
        "mean": round(float(a.mean()), 5), "std": round(float(a.std()), 5), "n": int(a.size)}


def open_frac(vals, thr):
    import numpy as np
    a = np.asarray(vals, dtype=np.float64)
    return round(float((a > thr).mean()), 5)


def collect(pc, eng, label, out_fh, probe_thrs):
    """Run the 35 turns, collecting the per-edge coh vector recorded by the step-3b probe."""
    import numpy as np
    all_coh = []
    per_turn = []
    for t, line in enumerate(CAREGIVER, 1):
        pc.respond(line)
        coh = eng._repel_coh
        if coh is None:
            raise RuntimeError("probe never fired — engine lacks _repel_coh or repel_gamma==0")
        c = coh.detach().cpu().numpy().astype(np.float64)
        all_coh.append(c)
        row = {"tag": "turn", "regime": label, "turn": t, "phi": round(float(pc.phi), 4),
               "frust": round(float(eng._frustrations.mean().item()), 4), **pct_row(c)}
        out_fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        per_turn.append(row)
    flat = np.concatenate(all_coh)
    summ = {"tag": "dist", "regime": label, **pct_row(flat),
            "open_frac": {f"{th:g}": open_frac(flat, th) for th in probe_thrs}}
    out_fh.write(json.dumps(summ, ensure_ascii=False) + "\n")
    out_fh.flush()
    return flat, summ, per_turn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--warm", default=os.path.expanduser("~/pure_grow/state/pure_mind/mind.json"))
    ap.add_argument("--curriculum",
                    default=os.path.expanduser("~/pure_grow/state/pure_teaching/caregiver_curriculum.txt"))
    ap.add_argument("--warmup-reps", type=int, default=40)
    ap.add_argument("--warmup-target", type=float, default=31.0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if not os.path.exists(a.curriculum):
        alt = os.path.expanduser("~/pure_grow/caregiver_curriculum.txt")
        if os.path.exists(alt):
            a.curriculum = alt

    probe_thrs = [0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.98, 0.99]
    PureMind, WORD_RE = _imports()
    os.environ["PURE_ASSOC_BETA"] = "0.0"
    os.environ.setdefault("PURE_ASSOC_K", "8")

    with open(a.out, "w", encoding="utf-8") as fh:
        # ---------- (i) WARM-COLLAPSED ----------
        seed_all(a.seed)
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False).name
        shutil.copyfile(a.warm, tmp)            # read-only copy; warm store never mutated
        pc = PureMind(store=tmp)
        pc._assoc_beta = 0.0
        eng = pc.c.engine
        eng.hebb_eta = 0.0
        eng.repel_gamma = 0.0                   # warm-down: probe OFF, pure legacy dynamics
        curric = []
        if os.path.exists(a.curriculum):
            curric = [l.strip() for l in open(a.curriculum, encoding="utf-8")
                      if l.strip() and WORD_RE.search(l.strip())]
        warm_phi = []
        for _ in range(a.warmup_reps):
            for line in curric:
                pc.respond(line)
            warm_phi.append(round(float(pc.phi), 3))
            if float(pc.phi) <= a.warmup_target:
                break
        fh.write(json.dumps({"tag": "warm_ready", "seed": a.seed, "vocab": pc.vocab,
                             "phi": round(float(pc.phi), 4), "warm_phi_trace": warm_phi},
                            ensure_ascii=False) + "\n")
        # probe ON but INERT (thr=2.0 => excess identically 0 => no force, no RNG, bit-exact)
        eng.repel_gamma = 0.05
        eng.repel_thr = 2.0
        warm_flat, warm_summ, warm_turns = collect(pc, eng, "warm_collapsed", fh, probe_thrs)
        warm_vocab = pc.vocab
        try:
            os.unlink(tmp)
        except Exception:
            pass

        # ---------- (ii) COLD-FRESH ----------
        seed_all(a.seed)
        tmp2 = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False).name
        os.unlink(tmp2)                          # non-existent path => brand-new empty mind
        pc2 = PureMind(store=tmp2)
        pc2._assoc_beta = 0.0
        eng2 = pc2.c.engine
        eng2.hebb_eta = 0.0
        eng2.repel_gamma = 0.05
        eng2.repel_thr = 2.0
        fh.write(json.dumps({"tag": "cold_ready", "seed": a.seed, "vocab": pc2.vocab,
                             "phi": round(float(pc2.phi), 4)}, ensure_ascii=False) + "\n")
        cold_flat, cold_summ, cold_turns = collect(pc2, eng2, "cold_fresh", fh, probe_thrs)
        for p in (tmp2,):
            if os.path.exists(p):
                os.unlink(p)

    def table(name, s):
        print(f"\n=== {name} (n_edges*turns = {s['n']}) ===")
        print(" pct   " + "  ".join(f"p{p:<3}" for p in PCTS))
        print(" coh   " + "  ".join(f"{s[f'p{p}']:+.3f}" for p in PCTS))
        print(f" mean {s['mean']:+.4f}  std {s['std']:.4f}")
        print(" gate-open fraction by candidate thr:")
        for th, v in s["open_frac"].items():
            print(f"   thr={th:>5}  open={v*100:6.2f}%")

    table("WARM-COLLAPSED (467-word, first Phi<=31 basin, 35 turns)", warm_summ)
    table("COLD-FRESH (empty mind, 35 turns)", cold_summ)
    print("\nCALIB_JSON " + json.dumps({"warm": warm_summ, "cold": cold_summ,
                                        "warm_vocab": warm_vocab}, ensure_ascii=False))


if __name__ == "__main__":
    main()

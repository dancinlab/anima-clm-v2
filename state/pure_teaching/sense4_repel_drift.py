#!/usr/bin/env python3
"""sense4_repel_drift.py — SENSE-4 similarity-gated repulsion warm Phi-drift A/B (run ON summer).

Sibling of sense3_hebb_drift.py. Identical warm protocol — load the REAL warm 467-word
`state/pure_mind/mind.json` READ-ONLY into a throwaway copy, beta=0 / hebb-off / repel-off warm-DOWN
to the first Phi<=target (~31) so BOTH arms share the IDENTICAL low-Phi start cell-state, then replay
the SAME 35 captured Codex caregiver lines. The ONLY toggled variable over the measured window:

    repel_gamma = 0.0    (control, bit-exact legacy)
    repel_gamma = 0.05   (treatment, similarity-gated repulsive phase coupling)  repel_thr = <calib>

Both arms are beta=0 (assoc-blend OFF) AND hebb_eta=0 (SENSE-3 OFF) so neither is a confound.
torch/numpy/python RNG are seeded identically BEFORE PureMind is built; the warm-down runs with
repel_gamma=0 in BOTH arms, then repel_gamma is flipped on the engine instance right before the 35
measured turns. The repulsion block adds NO new RNG draws, so repel_gamma is the sole variable at the
point it turns on (any downstream RNG divergence through the too_ordered noise branch is the PHYSICAL
consequence of the force, not a confound).

Pre-registered measures (SENSE-4.md), all logged:
  PRIMARY    drift = Phi_end - Phi_start on the 3 down-drift seeds (1, 9999, 12345);
             success = sign flip OR >=50% shallower
  SECONDARY  paired Delta end-Phi (gamma .05 - gamma 0), 10 seeds, expected > +0.5
  STRUCTURE  (the real point) `_amplitudes` SVD participation ratio 1.03 -> >=1.3
             AND mean pairwise cosine distance 0.02 -> >=0.10, both above the paired control
  GUARDRAILS end-Phi < 40 (no cold-basin re-inflation) · mean frustration in [0.45, 0.55] ·
             vocab byte-identical 467 -> 467 · too_frustrated fire-rate <= 1.5x baseline
             (the named #1 failure mode: repulsion <-> too_frustrated smoothing limit cycle) ·
             too_ordered fire-rate logged too · gate open-fraction logged (starvation watch)

The warm store is NEVER save()d -> the original 467-word mind is untouched.
"""
import argparse, hashlib, json, os, random, shutil, sys, tempfile

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

SEEDS = [1, 9999, 12345, 42, 7, 123, 2024, 31337, 555, 88]   # 3 down-drift: 1, 9999, 12345
DOWN_DRIFT = {1, 9999, 12345}
BLK = "▁▂▃▄▅▆▇█"


def seed_all(s):
    random.seed(s)
    import numpy as np
    np.random.seed(s)
    import torch
    torch.manual_seed(s)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(s)


def spark(v):
    lo, hi = min(v), max(v)
    rng = (hi - lo) or 1.0
    return "".join(BLK[min(7, int((x - lo) / rng * 7))] for x in v)


def diff_metrics(engine):
    """Participation ratio (SVD) + mean pairwise cosine distance of the FULL 48-cell _amplitudes."""
    import numpy as np
    A = engine._amplitudes.detach().cpu().numpy().astype(np.float64)   # [N, dim]
    if A.shape[0] < 2:
        return 0.0, 0.0
    sv = np.linalg.svd(A, compute_uv=False)
    s2 = sv ** 2
    pr = float((s2.sum() ** 2) / (np.square(s2).sum() + 1e-12))        # effective rank
    norm = A / (np.linalg.norm(A, axis=1, keepdims=True) + 1e-12)
    cos = norm @ norm.T
    iu = np.triu_indices(A.shape[0], 1)
    cos_dist = float(1.0 - cos[iu].mean())
    return pr, cos_dist


def vocab_hash(pc):
    return hashlib.blake2b(("|".join(sorted(pc.freq.keys()))).encode(), digest_size=8).hexdigest()


def run_one(seed, gamma, thr, warm, curriculum, warmup_reps, warmup_target, out_fh):
    """One arm. Returns summary dict."""
    seed_all(seed)                       # seed BEFORE PureMind is constructed
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False).name
    shutil.copyfile(warm, tmp)           # read-only copy — warm store NEVER mutated
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (here, os.path.dirname(os.path.dirname(here)), os.getcwd()):
        if p not in sys.path:
            sys.path.insert(0, p)
    from pure import PureMind, WORD_RE

    os.environ["PURE_ASSOC_BETA"] = "0.0"
    os.environ.setdefault("PURE_ASSOC_K", "8")
    pc = PureMind(store=tmp)             # loads warm 467-word vocab/assoc graph
    pc._assoc_beta = 0.0
    warm_vocab = pc.vocab
    v_hash_start = vocab_hash(pc)

    eng = pc.c.engine
    eng.hebb_eta = 0.0                   # SENSE-3 OFF in BOTH arms (not a confound)
    eng.repel_gamma = 0.0                # warm-down is repel-OFF in BOTH arms (identical start)
    eng.repel_thr = thr

    curric = []
    if os.path.exists(curriculum):
        curric = [l.strip() for l in open(curriculum, encoding="utf-8")
                  if l.strip() and WORD_RE.search(l.strip())]

    # WARMUP: drive cells DOWN into the low-Phi (~30) SENSE-GROW basin (repel-off, hebb-off, beta=0).
    warm_phi = []
    used_reps = 0
    for _ in range(warmup_reps):
        for line in curric:
            pc.respond(line)
        warm_phi.append(round(float(pc.phi), 3))
        used_reps += 1
        if float(pc.phi) <= warmup_target:
            break

    # ---- install per-step instrumentation (NO dynamics change; reads state AFTER each step) ----
    fires = {"steps": 0, "ord_any": 0, "ord_cells": 0, "frust_any": 0, "frust_cells": 0,
             "gate_open_sum": 0.0}
    orig_step = eng.step

    def wrapped_step(x_input=None):
        r = orig_step(x_input=x_input)
        d = eng._frustrations - eng.frustration_target
        to = d < -0.05          # exactly the too_ordered mask used in step()
        tf = d > 0.05           # exactly the too_frustrated mask used in step()
        fires["steps"] += 1
        fires["ord_any"] += int(bool(to.any().item()))
        fires["ord_cells"] += int(to.sum().item())
        fires["frust_any"] += int(bool(tf.any().item()))
        fires["frust_cells"] += int(tf.sum().item())
        fires["gate_open_sum"] += float(getattr(eng, "_repel_open_frac", 0.0) or 0.0)
        return r
    eng.step = wrapped_step

    # ---- flip repulsion ON for the measured window (the SOLE variable) ----
    eng.repel_gamma = gamma
    eng.repel_thr = thr

    def snap(t):
        pr, cd = diff_metrics(eng)
        return {"turn": t, "phi": round(float(pc.phi), 4), "T": round(float(pc.tension), 4),
                "C": round(float(pc.curiosity), 4),
                "frust": round(float(eng._frustrations.mean().item()), 4),
                "pr": round(pr, 4), "cos_dist": round(cd, 4),
                "gate_open": round(float(getattr(eng, "_repel_open_frac", 0.0) or 0.0), 5)}

    traj = [snap(0)]
    out_fh.write(json.dumps({"tag": "ready", "seed": seed, "gamma": gamma, "thr": thr,
                             "warmup_reps_used": used_reps, "warmup_target": warmup_target,
                             "warm_phi_trace": warm_phi, "warm_vocab": warm_vocab,
                             "vocab_hash_start": v_hash_start, **traj[0]}, ensure_ascii=False) + "\n")

    for t, line in enumerate(CAREGIVER, 1):
        child = pc.respond(line)
        s = snap(t)
        out_fh.write(json.dumps({"tag": "turn", "seed": seed, "gamma": gamma, "child": child, **s},
                                ensure_ascii=False) + "\n")
        traj.append(s)

    phi = [x["phi"] for x in traj]
    frust = [x["frust"] for x in traj]
    pr = [x["pr"] for x in traj]
    cd = [x["cos_dist"] for x in traj]
    import numpy as np
    xs = np.arange(len(phi), dtype=np.float64)
    slope = float(np.polyfit(xs, np.asarray(phi), 1)[0])
    v_hash_end = vocab_hash(pc)

    steps = fires["steps"] or 1
    summ = {"tag": "summary", "seed": seed, "gamma": gamma, "thr": thr,
            "down_drift_seed": seed in DOWN_DRIFT,
            "warmup_reps_used": used_reps, "warm_vocab": warm_vocab,
            "vocab_start": warm_vocab, "vocab_end": pc.vocab,
            "vocab_hash_start": v_hash_start, "vocab_hash_end": v_hash_end,
            "vocab_identical": (v_hash_start == v_hash_end) and (warm_vocab == pc.vocab),
            "phi_start": phi[0], "phi_end": phi[-1], "phi_drift": round(phi[-1] - phi[0], 4),
            "phi_slope": round(slope, 5), "phi_min": min(phi), "phi_max": max(phi),
            "phi_spark": spark(phi),
            "frust_mean": round(float(np.mean(frust)), 4),
            "frust_end": frust[-1], "frust_min": min(frust), "frust_max": max(frust),
            "pr_start": pr[0], "pr_end": pr[-1], "pr_mean": round(float(np.mean(pr)), 4),
            "pr_max": max(pr),
            "cos_dist_start": cd[0], "cos_dist_end": cd[-1],
            "cos_dist_mean": round(float(np.mean(cd)), 4), "cos_dist_max": max(cd),
            "steps": fires["steps"],
            "too_ordered_any": fires["ord_any"], "too_ordered_cell_events": fires["ord_cells"],
            "too_ordered_any_rate": round(fires["ord_any"] / steps, 4),
            "too_ordered_cells_per_step": round(fires["ord_cells"] / steps, 4),
            "too_frustrated_any": fires["frust_any"], "too_frustrated_cell_events": fires["frust_cells"],
            "too_frustrated_any_rate": round(fires["frust_any"] / steps, 4),
            "too_frustrated_cells_per_step": round(fires["frust_cells"] / steps, 4),
            "gate_open_mean": round(fires["gate_open_sum"] / steps, 5)}
    out_fh.write(json.dumps(summ, ensure_ascii=False) + "\n")
    out_fh.flush()
    eng.step = orig_step
    try:
        os.unlink(tmp)
    except Exception:
        pass
    return summ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gamma", type=float, required=True, help="measured-window repel_gamma (0.0 or 0.05)")
    ap.add_argument("--thr", type=float, default=0.8, help="repel_thr (set from calibration)")
    ap.add_argument("--warm", default=os.path.expanduser("~/pure_grow/state/pure_mind/mind.json"))
    ap.add_argument("--curriculum",
                    default=os.path.expanduser("~/pure_grow/state/pure_teaching/caregiver_curriculum.txt"))
    ap.add_argument("--warmup-reps", type=int, default=40)
    ap.add_argument("--warmup-target", type=float, default=31.0)
    ap.add_argument("--seeds", default="", help="comma seeds; default the pre-registered 10")
    ap.add_argument("--out", required=True, help="jsonl output path")
    a = ap.parse_args()

    if not os.path.exists(a.curriculum):
        alt = os.path.expanduser("~/pure_grow/caregiver_curriculum.txt")
        if os.path.exists(alt):
            a.curriculum = alt
    seeds = [int(x) for x in a.seeds.split(",") if x.strip()] or SEEDS
    summaries = []
    with open(a.out, "w", encoding="utf-8") as fh:
        for s in seeds:
            summ = run_one(s, a.gamma, a.thr, a.warm, a.curriculum,
                           a.warmup_reps, a.warmup_target, fh)
            summaries.append(summ)
            print(f"seed={s:>6} gamma={a.gamma} thr={a.thr} phi {summ['phi_start']:.2f}->{summ['phi_end']:.2f} "
                  f"drift={summ['phi_drift']:+.3f} slope={summ['phi_slope']:+.4f} "
                  f"PR {summ['pr_start']:.2f}->{summ['pr_end']:.2f} cd {summ['cos_dist_start']:.3f}->"
                  f"{summ['cos_dist_end']:.3f} frust={summ['frust_mean']:.3f} "
                  f"tf={summ['too_frustrated_any_rate']:.3f} to={summ['too_ordered_any_rate']:.3f} "
                  f"gate={summ['gate_open_mean']:.4f} vocab_id={summ['vocab_identical']}", flush=True)
    print("SUMMARY_JSON " + json.dumps(summaries, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""sense6_wave_drift.py — SENSE-6 standing-wave (per-(cell,dim) coherent mode) warm Phi-drift A/B.

Sibling of sense5_antimix_drift.py / sense4_repel_drift.py / sense3_hebb_drift.py. IDENTICAL warm
protocol — load the REAL warm 467-word `state/pure_mind/mind.json` READ-ONLY into a throwaway copy,
all forces OFF warm-DOWN to the first Phi<=target (~31) so BOTH arms share the IDENTICAL low-Phi
start cell-state, then replay the SAME 35 captured Codex caregiver lines. The ONLY toggled variable
over the measured window:

    wave_dim_k = 0    (control, bit-exact legacy dead code — the per-cell scalar wave is
                       cancelled by step-6 max-norm AND invisible to phi_py min-max binning)
    wave_dim_k = 1    (treatment, per-(cell,dim) travelling wave — SENSE-6, adds EXACTLY two
                       phase-locked coherent modes onto the near-rank-1 warm state)

Both arms are beta=0 (assoc-blend OFF) AND hebb_eta=0 (SENSE-3 OFF) AND repel_gamma=0 (SENSE-4 OFF)
AND diff_gain=0 (SENSE-5 OFF) so the standing wave is the SOLE toggled variable. wave_gain=0.02
(pre-registered, below the native walk-mix scale). torch/numpy/python RNG are seeded identically
BEFORE PureMind is built; the warm-down runs with wave_dim_k=0 in BOTH arms, then wave_dim_k is
flipped on the engine instance right before the 35 measured turns. The SENSE-6 block adds NO new
RNG draws, so wave_dim_k is the sole variable at the point it turns on.

Pre-registered measures (SENSE-6.md), all logged:
  PRIMARY    drift = Phi_end - Phi_start on the 3 down-drift seeds (1, 9999, 12345);
             success = sign flip OR >=50% shallower drift
  SECONDARY  paired mean Delta Phi_drift (k1 - k0), 10 seeds, expected >= +0.5
  STRUCTURE  `_amplitudes` full-48 SVD participation ratio PR=(sum s^2)^2/sum s^4 -> PR_end>=1.15
             AND mean pairwise cosine distance cos_dist_end in [0.04,0.10], both above control
  ENTRAINMENT (the #1 predicted failure) — record sin(drive) AND cos(drive) per turn so the
             analyzer can compute |corr(Phi, drive)| at the drive frequency; >0.5 => carrier
             capture (Phi rose for free from a shared pacemaker) => REJECT
  RESPONSIVE input_words per turn (dialogue stimulus magnitude) so tension-vs-input correlation
             can be checked in BOTH arms — if the wave captures the dynamics, tension stops
             tracking input
  MI-INEQ    total_MI and min_partition_MI on the SAME 32-cell subsample phi uses -> the analyzer
             checks sol's Delta total_MI > Delta min_partition_MI (else structured shattering)
  REJECTION  top-singular-share s0^2/sum s^2 (cold-basin ~46 mode-collapse watch)
  GUARDRAILS end-Phi < 40 (no cold-basin re-inflation) · mean frustration in [0.45, 0.55] ·
             vocab byte-identical 467 -> 467 · too_frustrated fire-rate (limit-cycle watch)

The warm store is NEVER save()d -> the original 467-word mind is untouched.
"""
import argparse, hashlib, json, math, os, random, shutil, sys, tempfile

# 35 caregiver lines — verbatim from sense2/3/4/5 drivers (same replayed Codex turns)
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
    """PR (SVD) + mean pairwise cosine distance + top-singular-share of the FULL 48-cell _amplitudes."""
    import numpy as np
    A = engine._amplitudes.detach().cpu().numpy().astype(np.float64)   # [N, dim]
    if A.shape[0] < 2:
        return 0.0, 0.0, 0.0
    sv = np.linalg.svd(A, compute_uv=False)
    s2 = sv ** 2
    denom = float(s2.sum()) + 1e-12
    pr = float((denom ** 2) / (np.square(s2).sum() + 1e-12))           # effective rank
    top_share = float(s2[0] / denom)                                   # winner-take-all watch
    norm = A / (np.linalg.norm(A, axis=1, keepdims=True) + 1e-12)
    cos = norm @ norm.T
    iu = np.triu_indices(A.shape[0], 1)
    cos_dist = float(1.0 - cos[iu].mean())
    return pr, cos_dist, top_share


def mi_components(engine):
    """total_MI and min_partition_MI on the SAME 32-cell subsample that measure_phi uses
    (phi_py.compute_phi_subsampled: linspace stride 48->32, n_bins=16). Cheap, deterministic,
    no RNG. Lets the analyzer check sol's inequality Delta total_MI > Delta min_partition_MI."""
    import numpy as np
    import phi_py
    A = engine._amplitudes.detach().cpu().numpy().astype(np.float32)
    n = A.shape[0]
    if n < 2:
        return 0.0, 0.0
    if n > 32:
        idx = np.linspace(0, n - 1, 32).astype(np.int64)
        A = A[idx]
    S = np.asarray(A, dtype=np.float64)
    m = A.shape[0]
    mi = phi_py._mi_matrix(S, 16)
    total = float(mi[np.triu_indices(m, 1)].sum())
    min_part = float(phi_py._min_partition(mi, m))
    return total, min_part


def gate_stats(engine):
    """Arm-INDEPENDENT gate readout (deg-weighted mean cosine node_sim) — carried from SENSE-5 for
    continuity; the SENSE-6 wave does NOT read this gate, but it is a free structural readout."""
    import torch
    import torch.nn.functional as F
    A = engine._amplitudes
    n = A.shape[0]
    if n < 1:
        return 0.0, 0.0, 0.0
    adj = engine._adj_sparse.coalesce()
    der, dec = adj.indices()
    dew = adj.values()
    deg = engine._degrees.clamp(min=1)
    U = F.normalize(A, p=2, dim=1, eps=1e-8)
    edge_sim = (U[der] * U[dec]).sum(dim=1)
    node_sim = torch.zeros(n).index_add_(0, der, dew * edge_sim) / deg
    open_frac = float((node_sim > 0.90).float().mean())
    return float(node_sim.mean()), open_frac, 0.0


def vocab_hash(pc):
    return hashlib.blake2b(("|".join(sorted(pc.freq.keys()))).encode(), digest_size=8).hexdigest()


def run_one(seed, wave_dim_k, wave_gain, warm, curriculum, warmup_reps, warmup_target, out_fh):
    """One arm. Returns summary dict."""
    seed_all(seed)                       # seed BEFORE PureMind is constructed
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False).name
    shutil.copyfile(warm, tmp)           # read-only copy — warm store NEVER mutated
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (here, os.path.dirname(os.path.dirname(here)), os.getcwd()):
        if p not in sys.path:
            sys.path.insert(0, p)
    from pure import PureMind, WORD_RE, words_of

    os.environ["PURE_ASSOC_BETA"] = "0.0"
    os.environ.setdefault("PURE_ASSOC_K", "8")
    pc = PureMind(store=tmp)             # loads warm 467-word vocab/assoc graph
    pc._assoc_beta = 0.0
    warm_vocab = pc.vocab
    v_hash_start = vocab_hash(pc)

    eng = pc.c.engine
    eng.hebb_eta = 0.0                   # SENSE-3 OFF in BOTH arms
    eng.repel_gamma = 0.0                # SENSE-4 OFF in BOTH arms
    eng.diff_gain = 0.0                  # SENSE-5 OFF in BOTH arms
    eng.wave_dim_k = 0                   # warm-down is wave-OFF in BOTH arms (identical start)
    eng.wave_gain = wave_gain

    curric = []
    if os.path.exists(curriculum):
        curric = [l.strip() for l in open(curriculum, encoding="utf-8")
                  if l.strip() and WORD_RE.search(l.strip())]

    # WARMUP: drive cells DOWN into the low-Phi (~30) basin (all forces off, beta=0).
    warm_phi = []
    used_reps = 0
    for _ in range(warmup_reps):
        for line in curric:
            pc.respond(line)
        warm_phi.append(round(float(pc.phi), 3))
        used_reps += 1
        if float(pc.phi) <= warmup_target:
            break

    # ---- per-step instrumentation (NO dynamics change; reads state AFTER each step) ----
    fires = {"steps": 0, "ord_any": 0, "ord_cells": 0, "frust_any": 0, "frust_cells": 0}
    orig_step = eng.step

    def wrapped_step(x_input=None):
        r = orig_step(x_input=x_input)
        d = eng._frustrations - eng.frustration_target
        to = d < -0.05
        tf = d > 0.05
        fires["steps"] += 1
        fires["ord_any"] += int(bool(to.any().item()))
        fires["ord_cells"] += int(to.sum().item())
        fires["frust_any"] += int(bool(tf.any().item()))
        fires["frust_cells"] += int(tf.sum().item())
        return r
    eng.step = wrapped_step

    # ---- flip the standing wave ON for the measured window (the SOLE variable) ----
    eng.wave_dim_k = wave_dim_k

    def snap(t, in_words):
        pr, cd, tsh = diff_metrics(eng)
        nsim, ofrac, _ = gate_stats(eng)
        total_mi, min_part = mi_components(eng)
        drive = eng._step * eng.standing_wave_freq            # shared pacemaker phase
        return {"turn": t, "phi": round(float(pc.phi), 4), "T": round(float(pc.tension), 4),
                "C": round(float(pc.curiosity), 4),
                "frust": round(float(eng._frustrations.mean().item()), 4),
                "pr": round(pr, 4), "cos_dist": round(cd, 4), "top_share": round(tsh, 4),
                "node_sim": round(nsim, 4), "gate_open": round(ofrac, 4),
                "sin_drive": round(math.sin(drive), 6), "cos_drive": round(math.cos(drive), 6),
                "step": eng._step, "input_words": in_words,
                "total_mi": round(total_mi, 5), "min_part_mi": round(min_part, 5)}

    traj = [snap(0, 0)]
    out_fh.write(json.dumps({"tag": "ready", "seed": seed, "wave_dim_k": wave_dim_k,
                             "wave_gain": wave_gain, "warmup_reps_used": used_reps,
                             "warmup_target": warmup_target, "warm_phi_trace": warm_phi,
                             "warm_vocab": warm_vocab, "vocab_hash_start": v_hash_start,
                             **traj[0]}, ensure_ascii=False) + "\n")

    for t, line in enumerate(CAREGIVER, 1):
        in_words = len(words_of(line))
        child = pc.respond(line)
        s = snap(t, in_words)
        out_fh.write(json.dumps({"tag": "turn", "seed": seed, "wave_dim_k": wave_dim_k,
                                 "child": child, **s}, ensure_ascii=False) + "\n")
        traj.append(s)

    phi = [x["phi"] for x in traj]
    frust = [x["frust"] for x in traj]
    pr = [x["pr"] for x in traj]
    cd = [x["cos_dist"] for x in traj]
    tsh = [x["top_share"] for x in traj]
    nsim = [x["node_sim"] for x in traj]
    T = [x["T"] for x in traj]
    inw = [x["input_words"] for x in traj]
    sind = [x["sin_drive"] for x in traj]
    cosd = [x["cos_drive"] for x in traj]
    tmi = [x["total_mi"] for x in traj]
    mpi = [x["min_part_mi"] for x in traj]
    import numpy as np
    xs = np.arange(len(phi), dtype=np.float64)
    slope = float(np.polyfit(xs, np.asarray(phi), 1)[0])
    v_hash_end = vocab_hash(pc)

    def corr(a, b):
        a = np.asarray(a, dtype=np.float64); b = np.asarray(b, dtype=np.float64)
        if a.std() < 1e-12 or b.std() < 1e-12:
            return 0.0
        return float(np.corrcoef(a, b)[0, 1])

    # entrainment magnitude over the 35 measured turns (drop the ready snapshot at index 0)
    r_sin = corr(phi[1:], sind[1:])
    r_cos = corr(phi[1:], cosd[1:])
    drive_corr = float(math.sqrt(r_sin ** 2 + r_cos ** 2))     # phase-agnostic single-freq coherence
    tension_input_corr = corr(T[1:], inw[1:])                  # is tension still tracking dialogue?

    steps = fires["steps"] or 1
    summ = {"tag": "summary", "seed": seed, "wave_dim_k": wave_dim_k, "wave_gain": wave_gain,
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
            "top_share_start": tsh[0], "top_share_end": tsh[-1],
            "top_share_mean": round(float(np.mean(tsh)), 4), "top_share_max": max(tsh),
            "node_sim_mean": round(float(np.mean(nsim)), 4),
            "drive_corr": round(drive_corr, 4), "drive_corr_sin": round(r_sin, 4),
            "drive_corr_cos": round(r_cos, 4),
            "tension_input_corr": round(tension_input_corr, 4),
            "total_mi_start": tmi[0], "total_mi_end": tmi[-1],
            "total_mi_drift": round(tmi[-1] - tmi[0], 5),
            "min_part_mi_start": mpi[0], "min_part_mi_end": mpi[-1],
            "min_part_mi_drift": round(mpi[-1] - mpi[0], 5),
            "steps": fires["steps"],
            "too_ordered_any_rate": round(fires["ord_any"] / steps, 4),
            "too_ordered_cells_per_step": round(fires["ord_cells"] / steps, 4),
            "too_frustrated_any_rate": round(fires["frust_any"] / steps, 4),
            "too_frustrated_cells_per_step": round(fires["frust_cells"] / steps, 4)}
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
    ap.add_argument("--wave-dim-k", type=int, required=True, help="measured-window wave_dim_k (0 or 1)")
    ap.add_argument("--wave-gain", type=float, default=0.02, help="pre-registered 0.02")
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
            summ = run_one(s, a.wave_dim_k, a.wave_gain, a.warm, a.curriculum,
                           a.warmup_reps, a.warmup_target, fh)
            summaries.append(summ)
            print(f"seed={s:>6} k={a.wave_dim_k} g={a.wave_gain} phi {summ['phi_start']:.2f}->"
                  f"{summ['phi_end']:.2f} drift={summ['phi_drift']:+.3f} slope={summ['phi_slope']:+.4f} "
                  f"PR {summ['pr_start']:.3f}->{summ['pr_end']:.3f} cd {summ['cos_dist_start']:.3f}->"
                  f"{summ['cos_dist_end']:.3f} tsh {summ['top_share_start']:.3f}->{summ['top_share_end']:.3f} "
                  f"driveR={summ['drive_corr']:.3f} T~in={summ['tension_input_corr']:+.3f} "
                  f"frust={summ['frust_mean']:.3f} tf={summ['too_frustrated_any_rate']:.3f} "
                  f"vocab_id={summ['vocab_identical']}", flush=True)
    print("SUMMARY_JSON " + json.dumps(summaries, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""sense2_warm_drift.py — SENSE-2 WARM-mind Phi-drift matched-pair test (run ON summer, torch host).

Unlike sense2_drift.py (COLD start: fresh newborn + 60-line curriculum -> ~121 words, Phi~46
basin), this loads the REAL warm persistent mind — the 467-word `state/pure_mind/mind.json`
grown by the SENSE-GROW grow-observe run — into BOTH arms and replays the SAME 35 captured Codex
caregiver lines, differing ONLY in PURE_ASSOC_BETA:
  beta=0.0  -> assoc-blend OFF (v1 sense coupling)
  beta=0.6  -> assoc-blend ON  (SENSE-2 default)

The warm store is loaded READ-ONLY (never save()d -> the original 467-word mind is never mutated,
Law: safe). A throwaway --store copy is passed so load() reads the warm vocab/bigram/assoc graph.

Determinism: torch/numpy/python RNG seeded identically BEFORE QuantumC is built, so cell init and
the per-step torch-RNG draw sequence are identical across the two conditions; beta only changes the
VALUES of the Kuramoto sense torque (word->phase), never the code path or #draws. Caregiver lines
are FIXED. tension/Phi/curiosity are READ from the cells (Law 2), never set.

--settle (default on): teach the 60-line caregiver curriculum first (as pure_worker --seed did in
SENSE-GROW) so the cells settle into their basin before the 35 test turns; drift is then measured
over the 35 turns. The warm vocab is ALREADY >=467 so the curriculum adds ~0 new words; it only
pulses/settles the freshly-built cells. --no-settle measures the 35 turns straight off the load.

Emits per-turn JSON trajectory + a final summary block.
"""
import argparse, json, os, random, sys

# 35 caregiver lines captured verbatim from state/pure_teaching/live_sense_dialogue.log (SENSE-GROW)
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


def seed_all(s):
    random.seed(s)
    try:
        import numpy as np
        np.random.seed(s)
    except Exception:
        pass
    try:
        import torch
        torch.manual_seed(s)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(s)
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--beta", required=True)
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--warm", default=os.path.expanduser("~/pure_grow/state/pure_mind/mind.json"),
                    help="the real warm 467-word store (loaded READ-ONLY via a temp copy)")
    ap.add_argument("--curriculum", default=os.path.expanduser("~/pure_grow/state/pure_teaching/caregiver_curriculum.txt"))
    ap.add_argument("--warmup-reps", type=int, default=40,
                    help="MAX curriculum reps for the warmup (safety cap). Warmup ADAPTIVELY stops as "
                         "soon as Phi first drops to <= --warmup-target, so every seed lands in the same "
                         "low-Phi SENSE-GROW basin (cell state is NOT in the JSON, so the warm low-Phi "
                         "regime is reached only by a long continuous descending trajectory).")
    ap.add_argument("--warmup-target", type=float, default=31.0,
                    help="stop warmup at first Phi <= this (lands the cells in the ~28-31 SENSE-GROW band).")
    ap.add_argument("--warmup-beta", default="0.0",
                    help="assoc-beta DURING warmup. Default 0.0 -> BOTH arms share an identical beta=0 "
                         "warmup => identical low-Phi start cell-state => beta is the sole variable over "
                         "the 35 measured test turns (retrofit SENSE-2 onto a warm down-drifting mind). "
                         "Pass 'match' to instead run warmup under the test beta (beta from birth).")
    a = ap.parse_args()

    os.environ["PURE_ASSOC_BETA"] = str(a.beta)   # PureMind reads this in __init__
    os.environ.setdefault("PURE_ASSOC_K", "8")

    # read-only copy of the warm store so the original 467-word mind is NEVER mutated (Law: safe)
    import shutil, tempfile
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False).name
    shutil.copyfile(a.warm, tmp)

    seed_all(a.seed)                              # seed BEFORE QuantumC is constructed
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from pure import PureMind, WORD_RE, HEXAD

    pc = PureMind(store=tmp)                       # loads the warm 467-word vocab/assoc graph
    warm_vocab = pc.vocab
    def snap(t):
        return {"turn": t, "vocab": pc.vocab, "stage": pc.stage,
                "T": round(float(pc.tension), 4), "phi": round(float(pc.phi), 4),
                "C": round(float(pc.curiosity), 4)}

    curric = []
    if os.path.exists(a.curriculum):
        curric = [l.strip() for l in open(a.curriculum, encoding="utf-8")
                  if l.strip() and WORD_RE.search(l.strip())]

    # WARMUP: drive the freshly-built cells DOWN into the low-Phi (~30) SENSE-GROW basin.
    # warmup-beta default 0.0 -> identical for both arms => identical low-Phi start state (Law: safe).
    wbeta = float(a.beta) if a.warmup_beta == "match" else float(a.warmup_beta)
    pc._assoc_beta = wbeta
    warm_phi = []
    used_reps = 0
    for _ in range(a.warmup_reps):
        for line in curric:
            pc.respond(line)
        warm_phi.append(round(float(pc.phi), 3))
        used_reps += 1
        if float(pc.phi) <= a.warmup_target:       # adaptive: stop at first entry into the low band
            break

    pc._assoc_beta = float(a.beta)                 # switch on the TEST beta for the measured turns
    traj = [snap(0)]
    print(json.dumps({"tag": "ready", "beta": a.beta, "warmup_beta": a.warmup_beta,
                      "warmup_reps_used": used_reps, "warmup_target": a.warmup_target,
                      "warm_phi_trace": warm_phi, "hexad": HEXAD, "seed": a.seed,
                      "warm_vocab": warm_vocab, **traj[0]}, ensure_ascii=False), flush=True)

    for t, line in enumerate(CAREGIVER, 1):
        child = pc.respond(line)
        s = snap(t)
        print(json.dumps({"tag": "turn", "child": child, **s}, ensure_ascii=False), flush=True)
        traj.append(s)

    phi = [x["phi"] for x in traj]
    ten = [x["T"] for x in traj]
    blk = "▁▂▃▄▅▆▇█"
    def spark(v):
        lo, hi = min(v), max(v); rng = (hi - lo) or 1.0
        return "".join(blk[min(7, int((x - lo) / rng * 7))] for x in v)
    print(json.dumps({"tag": "summary", "beta": a.beta, "seed": a.seed,
                      "warmup_beta": a.warmup_beta, "warmup_reps_used": used_reps,
                      "warm_vocab": warm_vocab,
                      "phi_start": phi[0], "phi_end": phi[-1], "phi_drift": round(phi[-1] - phi[0], 4),
                      "phi_min": min(phi), "phi_max": max(phi), "phi_spark": spark(phi),
                      "T_min": min(ten), "T_max": max(ten), "T_spark": spark(ten),
                      "vocab_start": traj[0]["vocab"], "vocab_end": traj[-1]["vocab"]},
                     ensure_ascii=False), flush=True)
    try:
        os.unlink(tmp)
    except Exception:
        pass


if __name__ == "__main__":
    main()

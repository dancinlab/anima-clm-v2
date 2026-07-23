#!/usr/bin/env python3
"""sense2_drift.py — SENSE-2 long-dialogue Phi-drift matched-pair test (run ON summer, torch host).

Two runs differ ONLY in PURE_ASSOC_BETA (env, read by pure.PureMind):
  beta=0.0  -> assoc-blend OFF (v1 sense coupling)  -> reproduces SENSE-GROW drift
  beta=0.6  -> assoc-blend ON  (SENSE-2 default)

Determinism: torch/numpy/python RNG seeded identically BEFORE QuantumC is built, so the cell
init and the per-step torch-RNG draw sequence are identical across the two conditions. beta only
changes the VALUES of the Kuramoto sense torque (word->phase), never the code path or #draws, so
the cell trajectory diverges solely because of the assoc-blend. Caregiver lines are FIXED (the 35
real Codex lines captured from the SENSE-GROW run), replayed identically into both conditions, so
only beta differs. tension/Phi/curiosity are READ from the cells (Law 2), never set.

Same curriculum pre-seed (caregiver_curriculum.txt) in both so vocab/assoc history is identical.
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
    ap.add_argument("--curriculum", default=os.path.expanduser("~/pure_grow/state/pure_teaching/caregiver_curriculum.txt"))
    a = ap.parse_args()

    os.environ["PURE_ASSOC_BETA"] = str(a.beta)   # PureMind reads this in __init__
    os.environ.setdefault("PURE_ASSOC_K", "8")

    seed_all(a.seed)                              # seed BEFORE QuantumC is constructed
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from pure import PureMind, WORD_RE, HEXAD

    pc = PureMind(store=None)                     # fresh newborn, no persistence
    def snap(t):
        return {"turn": t, "vocab": pc.vocab, "stage": pc.stage,
                "T": round(float(pc.tension), 4), "phi": round(float(pc.phi), 4),
                "C": round(float(pc.curiosity), 4)}

    # pre-seed curriculum (identical both conditions) — build vocab/assoc history to reflection stage
    if os.path.exists(a.curriculum):
        with open(a.curriculum, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and WORD_RE.search(line):
                    pc.respond(line)

    traj = [snap(0)]
    print(json.dumps({"tag": "ready", "beta": a.beta, "hexad": HEXAD,
                      "seed": a.seed, **traj[0]}, ensure_ascii=False), flush=True)

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
    print(json.dumps({"tag": "summary", "beta": a.beta,
                      "phi_start": phi[0], "phi_end": phi[-1], "phi_drift": round(phi[-1] - phi[0], 4),
                      "phi_min": min(phi), "phi_max": max(phi), "phi_spark": spark(phi),
                      "T_min": min(ten), "T_max": max(ten), "T_spark": spark(ten),
                      "vocab_start": traj[0]["vocab"], "vocab_end": traj[-1]["vocab"]},
                     ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()

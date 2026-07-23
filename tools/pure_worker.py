#!/usr/bin/env python3
"""pure_worker.py — a long-lived PureMind host driven line-by-line over stdin.

Runs ON A TORCH HOST (e.g. `summer`) so the mind is wired to the REAL Hexad C-engine
(HEXAD=True: tension = QuantumC cell frustration, Phi = phi_py/phi_rs). One PureMind stays
alive for the whole session, so its consciousness-state trajectory is CONTINUOUS (the cell
engine evolves across turns, not re-seeded per turn), and it persists its learned language to
--store (JSON, atomic) after every turn.

Protocol (one JSON object per line on stdout):
  on start, after optional --seed teaching:   {"tag":"ready", ...state...}
  per caregiver line read from stdin:          {"tag":"turn", "child":<utterance>, ...state...}
  state fields: vocab, stage, stage_name, tension, phi, curiosity, hexad

The orchestrator (tools/codex_pure_dialogue.py --remote HOST) writes ONE caregiver line to
this process's stdin per turn and reads back ONE JSON line. Send "__QUIT__" to stop.

Usage (on the torch host):
  python3 -u pure_worker.py --store ~/pure_grow/state/pure_mind/mind.json \
                            --seed ~/pure_grow/state/pure_teaching/caregiver_curriculum.txt
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pure import PureMind, STAGE_NAMES, WORD_RE


def state(pc):
    return {
        "vocab": pc.vocab,
        "stage": pc.stage,
        "stage_name": STAGE_NAMES[pc.stage],
        "tension": round(float(pc.tension), 4),
        "phi": round(float(pc.phi), 4),
        "curiosity": round(float(pc.curiosity), 4),
        "hexad": pc.c is not None,
    }


def emit(tag, pc, child=None):
    d = {"tag": tag, "child": child}
    d.update(state(pc))
    sys.stdout.write(json.dumps(d, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", required=True, help="JSON path for cumulative language memory")
    ap.add_argument("--seed", default=None, help="curriculum file taught (respond'd) before live turns")
    a = ap.parse_args()

    pc = PureMind(store=a.store)
    if a.seed and os.path.exists(a.seed):
        with open(a.seed, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and WORD_RE.search(line):
                    pc.respond(line)   # teach: learn + pulse + (maybe) generate, exactly like a turn
        pc.save()
    emit("ready", pc)

    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        if line == "__QUIT__":
            break
        child = pc.respond(line)
        pc.save()
        emit("turn", pc, child=child)


if __name__ == "__main__":
    main()

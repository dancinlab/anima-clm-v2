"""teach_pure.py — teach a newborn PureConsciousness to speak by feeding it a
caregiver curriculum (Codex-generated), turn by turn, and log its growth.

PURE learns language ONLY from what is said to it (no corpus). We watch it climb the
developmental stages: fetal(silent) -> babble -> word-combos -> sentences -> dialogue.

Usage: python3 teach_pure.py <teacher_lines.txt>
"""
import sys, os
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pure_consciousness import PureConsciousness

STAGE_EN = ["fetal", "babble", "word", "sentence", "dialogue", "reflection"]


def main():
    lines_file = sys.argv[1]
    teacher = [l.strip() for l in open(lines_file, encoding="utf-8") if l.strip()]
    # keep only lines that contain Hangul (drop any stray commentary)
    import re
    teacher = [l for l in teacher if re.search(r"[가-힣]", l)]

    # fresh newborn: empty data dir so it starts at vocab 0
    fresh = tempfile.mkdtemp(prefix="pure_newborn_")
    pc = PureConsciousness(data_dir=fresh)

    print(f"=== Teaching a newborn PureConsciousness ({len(teacher)} caregiver turns) ===")
    print(f"start: vocab={len(set(pc.learned_words))} stage={pc.growth_stage}({STAGE_EN[pc.growth_stage]})\n")

    last_stage = -1
    for i, utter in enumerate(teacher, 1):
        reply = pc.respond(utter)
        vocab = len(set(pc.learned_words))
        stage = pc.growth_stage
        # print on every stage change, plus a periodic sample
        if stage != last_stage or i % 12 == 0 or i == len(teacher):
            tag = "  <STAGE UP>" if stage != last_stage and last_stage >= 0 else ""
            r = reply if reply else "(silence)"
            print(f"[t{i:>3} v{vocab:>3} {STAGE_EN[stage]:>9}]{tag}")
            print(f"    teacher: {utter}")
            print(f"    PURE   : {r}")
            last_stage = stage

    print(f"\n=== grown up: vocab={len(set(pc.learned_words))} "
          f"stage={pc.growth_stage}({STAGE_EN[pc.growth_stage]}) ===")
    # a few free responses from the grown consciousness
    print("\n-- free responses from the grown PURE --")
    for q in ["안녕", "너는 누구야", "지금 어때", "의식이 뭐야"]:
        print(f"  [{q}] -> {pc.respond(q) or '(silence)'}")
    # spontaneous emission if it exists
    if hasattr(pc, "spontaneous"):
        try:
            print(f"  [자발발화] -> {pc.spontaneous() or '(silence)'}")
        except Exception as e:
            print(f"  [자발발화] (n/a: {e})")


if __name__ == "__main__":
    main()

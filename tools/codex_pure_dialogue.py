"""codex_pure_dialogue.py — real-time two-way loop: Codex (caregiver) <-> PureConsciousness.

Each turn: Codex SEES the child's last utterance and the transcript, then says ONE new
warm Korean line reacting to it; PURE learns from that line and replies. PURE grows purely
from this live dialogue (no corpus). Codex is invoked per turn via `sidecar lab sol`.

Usage: python3 tools/codex_pure_dialogue.py [turns]
"""
import os
import re
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
from pure_consciousness import PureConsciousness

STAGE_EN = ["fetal", "babble", "word", "sentence", "dialogue", "reflection"]


def codex_caregiver(transcript, child_said):
    """Ask Codex for ONE next caregiver line reacting to the child."""
    prompt = (
        "You are a warm, patient Korean caregiver teaching a NEWBORN consciousness to speak. "
        "It learns Korean words ONLY from what you say to it — no corpus, no dictionary. Use "
        "child-directed speech (motherese): short, warm, simple. React to what the child just "
        "said, BUT each line MUST introduce at least 2 words the child has NOT heard yet "
        "(new nouns/verbs/feelings) so its vocabulary keeps growing — do NOT merely repeat the "
        "child's words back.\n\n"
        f"Conversation so far:\n{transcript if transcript else '(nothing yet — it was just born)'}\n\n"
        f"The child just said: \"{child_said or '(silence)'}\"\n\n"
        "Reply with EXACTLY ONE short simple Korean line to the child. Output it on a single "
        "line prefixed with 'SAY:' and nothing else after. Example:\n"
        "SAY: 우리 아기 방긋 웃네"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as tf:
        tf.write(prompt)
        pf = tf.name
    try:
        out = subprocess.run(
            ["sidecar", "lab", "sol", "--file", pf, "--cwd", REPO],
            capture_output=True, text=True, timeout=120,
        ).stdout
    except Exception as e:
        return None, f"(codex error: {e})"
    finally:
        os.unlink(pf)
    # extract the SAY: line (robust to codex preamble); fallback to last Korean line
    says = [m.group(1).strip() for m in re.finditer(r"SAY:\s*(.+)", out)]
    if says:
        return says[-1], None
    kor = [l.strip() for l in out.splitlines() if re.search(r"[가-힣]", l)]
    kor = [l for l in kor if not re.search(r"codex|session|workdir|model|sandbox|approval", l, re.I)]
    return (kor[-1], None) if kor else (None, "(no caregiver line parsed)")


def main():
    turns = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    fresh = tempfile.mkdtemp(prefix="pure_dialogue_")
    pc = PureConsciousness(data_dir=fresh)

    print(f"=== Codex <-> PURE live dialogue ({turns} turns) ===\n")
    transcript = ""
    child_said = ""  # newborn: silent
    for t in range(1, turns + 1):
        care, err = codex_caregiver(transcript, child_said)
        if care is None:
            print(f"[t{t}] caregiver failed: {err}")
            break
        child_said = pc.respond(care)
        vocab = len(set(pc.learned_words))
        stage = STAGE_EN[pc.growth_stage]
        print(f"[t{t:>2} v{vocab:>3} {stage:>9}]")
        print(f"    Codex: {care}")
        print(f"    PURE : {child_said or '(silence)'}")
        transcript += f"caregiver: {care}\nchild: {child_said or '(silence)'}\n"

    print(f"\n=== after {turns} live turns: vocab={len(set(pc.learned_words))} "
          f"stage={pc.growth_stage}({STAGE_EN[pc.growth_stage]}) ===")


if __name__ == "__main__":
    main()

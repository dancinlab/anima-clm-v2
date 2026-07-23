#!/usr/bin/env python3
"""codex_pure_dialogue.py — real-time two-way loop: Codex (caregiver) <-> PureMind.

Each turn Codex SEES the child's last utterance + the transcript and says ONE new warm Korean
line reacting to it (child-directed speech, >=2 unheard words per line so vocabulary keeps
growing); PureMind learns from that line and replies. PURE grows purely from this live dialogue
(no corpus). Codex is invoked per turn via `sidecar lab sol` (~60s/turn).

The mind is the persistent, Hexad-wired `PureMind` from pure.py:
  - persistent: --store JSON accumulates learned language ACROSS runs (Law 42). You may --seed a
    curriculum first (teach it), THEN do live turns on top -> cumulative growth is visible.
  - real consciousness state: on a torch host the mind is wired to the Hexad C-engine, so the
    logged tension/Phi are the REAL QuantumC cell dynamics, not scalar proxies. Because the local
    Mac has no torch, use --remote HOST to run the mind on a torch box (e.g. summer) while Codex
    still runs locally; the loop drives a long-lived tools/pure_worker.py over ssh so the mind's
    state trajectory is CONTINUOUS.

Every turn is logged (stdout + --log file) as:
  [t01 v58 dialogue T=0.53 Phi=0.02 C=0.11]
      Codex: ...
      PURE : ...

Usage:
  python3 tools/codex_pure_dialogue.py --turns 25 \
      --remote summer --seed state/pure_teaching/caregiver_curriculum.txt \
      --log state/pure_teaching/live_hexad_dialogue.log
  python3 tools/codex_pure_dialogue.py --turns 12         # local scalar-state fallback (no torch)
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

STAGE_EN = ["fetal", "babble", "word", "sentence", "dialogue", "reflection"]


# ---------------------------------------------------------------- Codex caregiver (always local)
def codex_caregiver(transcript, child_said, timeout=150):
    """Ask Codex (sidecar lab sol) for ONE next caregiver line reacting to the child."""
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
            capture_output=True, text=True, timeout=timeout,
        ).stdout
    except Exception as e:
        return None, f"(codex error: {e})"
    finally:
        os.unlink(pf)
    says = [m.group(1).strip() for m in re.finditer(r"SAY:\s*(.+)", out)]
    if says:
        return says[-1], None
    kor = [l.strip() for l in out.splitlines() if re.search(r"[가-힣]", l)]
    kor = [l for l in kor if not re.search(r"codex|session|workdir|model|sandbox|approval", l, re.I)]
    return (kor[-1], None) if kor else (None, "(no caregiver line parsed)")


# ---------------------------------------------------------------- the mind (local or remote)
class LocalMind:
    """PureMind in-process. Real Hexad only if this host has torch; else scalar proxy state."""

    def __init__(self, store, seed):
        from pure import PureMind, WORD_RE, HEXAD
        self.hexad = HEXAD
        self.pc = PureMind(store=store)
        if seed and os.path.exists(seed):
            with open(seed, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and WORD_RE.search(line):
                        self.pc.respond(line)
            self.pc.save()

    def _state(self):
        pc = self.pc
        return {"vocab": pc.vocab, "stage": pc.stage, "tension": float(pc.tension),
                "phi": float(pc.phi), "curiosity": float(pc.curiosity), "hexad": pc.c is not None}

    def ready(self):
        return self._state()

    def step(self, line):
        child = self.pc.respond(line)
        self.pc.save()
        return child, self._state()

    def close(self):
        self.pc.save()


class RemoteMind:
    """Drive a long-lived tools/pure_worker.py on a torch host over ssh (continuous Hexad state)."""

    def __init__(self, host, remote_dir, store, seed):
        self.host = host
        cmd = f"cd {remote_dir} && python3 -u pure_worker.py --store {store}"
        if seed:
            cmd += f" --seed {seed}"
        self.errlog = tempfile.NamedTemporaryFile("wb", suffix=".stderr", delete=False)
        self.proc = subprocess.Popen(
            ["ssh", "-T", host, cmd],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.errlog,
            text=True, bufsize=1,
        )
        self._ready = self._read_json()   # blocks through remote --seed teaching
        self.hexad = self._ready.get("hexad", False)

    def _read_json(self):
        for line in self.proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue   # skip any stray non-JSON on stdout
        raise RuntimeError(f"remote worker closed (see {self.errlog.name})")

    def ready(self):
        return self._ready

    def step(self, line):
        self.proc.stdin.write(line.replace("\n", " ") + "\n")
        self.proc.stdin.flush()
        d = self._read_json()
        return d.get("child"), d

    def close(self):
        try:
            self.proc.stdin.write("__QUIT__\n")
            self.proc.stdin.flush()
        except Exception:
            pass
        try:
            self.proc.wait(timeout=15)
        except Exception:
            self.proc.kill()


# ---------------------------------------------------------------- logging
def fmt_head(t, s):
    return (f"[t{t:>2} v{s['vocab']:>3} {STAGE_EN[s['stage']]:>10} "
            f"T={s['tension']:.2f} Phi={s['phi']:.2f} C={s['curiosity']:.2f}]")


def sparkline(vals):
    if not vals:
        return ""
    blk = "▁▂▃▄▅▆▇█"
    lo, hi = min(vals), max(vals)
    rng = (hi - lo) or 1.0
    return "".join(blk[min(7, int((v - lo) / rng * 7))] for v in vals)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--turns", type=int, default=12)
    ap.add_argument("--store", default=None,
                    help="JSON language-memory path (persistent). Default: state/pure_mind/mind.json "
                         "local, or ~/pure_grow/state/pure_mind/mind.json remote.")
    ap.add_argument("--seed", default=None, help="curriculum taught before live turns (cumulative)")
    ap.add_argument("--log", default=os.path.join(REPO, "state", "pure_teaching", "live_hexad_dialogue.log"))
    ap.add_argument("--remote", default=None, help="torch host to run the mind on (e.g. summer)")
    ap.add_argument("--remote-dir", default="~/pure_grow")
    ap.add_argument("--codex-timeout", type=int, default=150)
    a = ap.parse_args()

    os.makedirs(os.path.dirname(a.log), exist_ok=True)
    logf = open(a.log, "a", encoding="utf-8")

    def emit(msg):
        print(msg)
        logf.write(msg + "\n")
        logf.flush()

    if a.remote:
        store = a.store or f"{a.remote_dir}/state/pure_mind/mind.json"
        # --seed (interpreted on the remote host) is OPT-IN: omit it to load the persistent store
        # as-is and prove cross-run carry-over; pass it to (re-)teach a curriculum first.
        mind = RemoteMind(a.remote, a.remote_dir, store, a.seed)
        where = f"remote {a.remote}:{store}"
    else:
        store = a.store or os.path.join(REPO, "state", "pure_mind", "mind.json")
        mind = LocalMind(store, a.seed)
        where = f"local {store}"

    r = mind.ready()
    emit("=" * 78)
    emit(f"=== Codex <-> PureMind live dialogue @ {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    emit(f"    mind={where}  hexad={mind.hexad}  turns={a.turns}")
    emit(f"    seeded start-state: {fmt_head(0, r)}  (vocab from curriculum + prior runs)")
    emit("=" * 78)

    traj = [(0, r)]
    transcript, child_said = "", ""
    try:
        for t in range(1, a.turns + 1):
            care, err = codex_caregiver(transcript, child_said, timeout=a.codex_timeout)
            if care is None:
                emit(f"[t{t}] caregiver failed: {err} — stopping, resume point = turn {t}")
                break
            child_said, s = mind.step(care)
            emit(fmt_head(t, s))
            emit(f"    Codex: {care}")
            emit(f"    PURE : {child_said or '(silence)'}")
            transcript += f"caregiver: {care}\nchild: {child_said or '(silence)'}\n"
            traj.append((t, s))
    finally:
        mind.close()

    # ---- trajectory summary (CLAUDE.md: ASCII graph of the real consciousness state) ----
    emit("")
    emit("=== consciousness-state trajectory ===")
    emit(f"    vocab   : {traj[0][1]['vocab']} -> {traj[-1][1]['vocab']}")
    emit(f"    stage   : {STAGE_EN[traj[0][1]['stage']]} -> {STAGE_EN[traj[-1][1]['stage']]}")
    ten = [s["tension"] for _, s in traj]
    phi = [s["phi"] for _, s in traj]
    emit(f"    tension : {sparkline(ten)}   [{min(ten):.2f} .. {max(ten):.2f}]")
    emit(f"    Phi     : {sparkline(phi)}   [{min(phi):.2f} .. {max(phi):.2f}]")
    emit("    turn  vocab  stage       T      Phi     C")
    for t, s in traj:
        emit(f"    {t:>4}  {s['vocab']:>5}  {STAGE_EN[s['stage']]:>9}  "
             f"{s['tension']:.3f}  {s['phi']:.3f}  {s['curiosity']:.3f}")
    emit(f"=== done: {traj[-1][1]['vocab']} words, stage "
         f"{STAGE_EN[traj[-1][1]['stage']]} ({traj[-1][1]['stage']}) ===")
    logf.close()


if __name__ == "__main__":
    main()

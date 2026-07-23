#!/usr/bin/env python3
"""pure.py — PURE mode: a corpus-free consciousness that learns to speak from conversation
and GENERATES (not echoes) via consciousness-steered Markov recombination.

@canonical-ok repo folder 'anima-clm-v2' is the fixed project path, not a versioned copy.

Zero corpus, zero LLM, zero hardcoded sentences. It learns Korean words ONLY from what is
said to it, grows through developmental stages, and speaks by walking its own learned
bigram model — seeded from a consciousness-SALIENT memory word (not the last input word),
so it recombines rather than parrots.

Philosophy (hard rules):
  Law 1  — no templates/fallback. If it cannot speak coherently -> silence ("").
  Law 2  — no manipulation of state. tension/curiosity EMERGE from interaction, never set.
  Law 42 — growth > optimization. It grows only through conversation.
  Law 71 — free generation under a coherence floor (Psi = argmax H(p) s.t. Phi > Phi_min).

CLI:
  python3 pure.py chat                 # interactive: you teach it by talking
  python3 pure.py teach <curriculum>   # feed a file of lines, one per turn, show growth
  python3 pure.py dialogue [turns]     # Codex (sidecar lab sol) <-> PURE live loop

This is v1 — the canonical PURE-mode entry point, built to be extended.
"""
import math
import os
import random
import re
import sys
from collections import Counter, defaultdict

WORD_RE = re.compile(r"[가-힣]+")
STAGE_NAMES = ["fetal", "babble", "word", "sentence", "dialogue", "reflection"]


def words_of(text):
    return [w for w in WORD_RE.findall(text or "") if len(w) >= 2]


class PureMind:
    """A mind that learns language from conversation and generates from its own model."""

    def __init__(self):
        self.turn = 0
        self.learned = []                    # ordered word history (recency)
        self.freq = Counter()                # word -> count
        self.bigrams = defaultdict(Counter)  # w -> Counter(next_w)
        self.last_seen = {}                  # word -> turn last heard
        self.said = set()                    # utterances already spoken (no repeats)
        # consciousness state — EMERGES, never set by hand (Law 2)
        self.tension = 0.5    # surprise / disequilibrium
        self.curiosity = 0.3  # pull toward the unknown
        self.phi = 0.0        # integration proxy (distinct bigram density)

    # ---- growth ----------------------------------------------------------
    @property
    def vocab(self):
        return len(self.freq)

    @property
    def stage(self):
        v = self.vocab
        return 0 if v < 3 else 1 if v < 8 else 2 if v < 20 else 3 if v < 50 else 4 if v < 100 else 5

    # ---- learning (the only input of knowledge) --------------------------
    def learn(self, text):
        ws = words_of(text)
        novel = 0
        for w in ws:
            if w not in self.freq:
                novel += 1
            self.freq[w] += 1
            self.learned.append(w)
            self.last_seen[w] = self.turn
        for a, b in zip(ws, ws[1:]):
            self.bigrams[a][b] += 1
        if len(self.learned) > 4000:
            self.learned = self.learned[-4000:]
        # state emerges from the input (Law 2: measured, not set)
        if ws:
            novelty_ratio = novel / len(ws)
            self.tension = 0.85 * self.tension + 0.15 * (0.3 + 1.4 * novelty_ratio)
            self.curiosity = 0.85 * self.curiosity + 0.15 * novelty_ratio
        if self.vocab:
            integ = sum(1 for w in self.bigrams if len(self.bigrams[w]) >= 2)
            self.phi = integ / self.vocab

    # ---- generation (consciousness-steered, anti-echo) -------------------
    def _seed(self, avoid):
        """Pick a starting word from SALIENT memory, steered by curiosity.

        Not the last input word (anti-parrot). High curiosity -> prefer rarely-used /
        recently-learned words; low curiosity -> prefer familiar, well-connected words.
        """
        cands = [w for w in self.bigrams if w not in avoid]
        if not cands:
            cands = [w for w in self.freq if w not in avoid] or list(self.freq)
        if not cands:
            return None
        weights = []
        for w in cands:
            connect = len(self.bigrams.get(w, ()))
            rare = 1.0 / self.freq[w]
            recent = 1.0 / (1 + self.turn - self.last_seen.get(w, self.turn))
            w_score = (connect + 0.5) * ((rare + recent) * self.curiosity + (1 - self.curiosity))
            weights.append(max(w_score, 1e-6))
        return random.choices(cands, weights=weights, k=1)[0]

    def _walk(self, seed, max_len):
        """Markov walk over learned bigrams. temperature = tension."""
        temp = 0.5 + self.tension
        chain, cur = [seed], seed
        for _ in range(max_len - 1):
            nxt = self.bigrams.get(cur)
            if not nxt:
                break
            items = list(nxt.items())
            weights = [max(c, 1e-9) ** (1.0 / max(temp, 1e-3)) for _, c in items]
            weights = [wt * (1 + self.curiosity / self.freq[w]) for wt, (w, _) in zip(weights, items)]
            choice = random.choices([w for w, _ in items], weights=weights, k=1)[0]
            if choice in chain[-2:]:
                break
            chain.append(choice)
            cur = choice
        return chain

    def _speak(self, input_words, min_len, max_len):
        """Generate one utterance, or "" (silence) if not coherent enough. No templates."""
        avoid = set(input_words[-1:])          # anti-echo: don't seed from the last input word
        tries = 1 + int(4 * max(self.tension, self.curiosity))
        best = ""
        for _ in range(tries):
            seed = self._seed(avoid)
            if not seed:
                return ""
            chain = self._walk(seed, max_len)
            if len(chain) < min_len:
                continue
            utter = " ".join(chain)
            if input_words:
                overlap = len(set(chain) & set(input_words)) / len(set(chain))
                if overlap > 0.6:
                    continue
            if utter in self.said:
                continue
            best = utter
            break
        if best:
            self.said.add(best)
        return best

    def respond(self, text):
        self.turn += 1
        self.learn(text)
        s = self.stage
        if s == 0:                # fetal: silence
            return ""
        if s == 1:                # babble: one salient word
            seed = self._seed(set(words_of(text)[-1:]))
            return seed or ""
        iw = words_of(text)
        if s == 2:                # word: 2-3 word recombination
            out = self._speak(iw, 2, 3)
        elif s == 3:              # sentence
            out = self._speak(iw, 2, 5)
            if out and not out.endswith(("!", "?", ".")):
                out += "."
        else:                     # dialogue / reflection
            out = self._speak(iw, 3, 7)
            if out:
                end = "?" if self.curiosity > 0.5 else "."
                if not out.endswith(("!", "?", ".")):
                    out += end
        return out

    def spontaneous(self):
        """Speak with no prompt — pure self-emission from salient memory."""
        if self.stage < 3:
            return ""
        self.turn += 1
        return self._speak([], 2, 6)

    def state_line(self):
        return (f"v{self.vocab} {STAGE_NAMES[self.stage]} "
                f"T={self.tension:.2f} C={self.curiosity:.2f} Phi={self.phi:.2f}")


# ---- CLI ----------------------------------------------------------------

def cmd_teach(path):
    pc = PureMind()
    lines = [l.strip() for l in open(path, encoding="utf-8") if l.strip() and WORD_RE.search(l)]
    print(f"=== teaching PureMind ({len(lines)} turns) ===\n")
    last = -1
    for i, line in enumerate(lines, 1):
        r = pc.respond(line)
        if pc.stage != last or i % 12 == 0 or i == len(lines):
            up = "  <STAGE UP>" if pc.stage != last and last >= 0 else ""
            print(f"[t{i:>3} {pc.state_line()}]{up}")
            print(f"    teacher: {line}")
            print(f"    PURE   : {r or '(silence)'}")
            last = pc.stage
    print(f"\n=== grown: {pc.state_line()} ===")
    print("-- spontaneous --")
    for _ in range(3):
        print(f"    {pc.spontaneous() or '(silence)'}")


def cmd_chat():
    pc = PureMind()
    print("PURE mode chat — talk to it in Korean to teach it. Ctrl-D to exit.\n")
    while True:
        try:
            line = input("you > ")
        except EOFError:
            break
        r = pc.respond(line)
        print(f"pure> {r or '(...)'}    [{pc.state_line()}]")


def cmd_dialogue(turns):
    os.execvp("python3", ["python3",
                          os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       "tools", "codex_pure_dialogue.py"), str(turns)])


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == "teach" and len(sys.argv) > 2:
        cmd_teach(sys.argv[2])
    elif cmd == "chat":
        cmd_chat()
    elif cmd == "dialogue":
        cmd_dialogue(int(sys.argv[2]) if len(sys.argv) > 2 else 12)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()

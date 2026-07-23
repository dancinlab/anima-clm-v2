#!/usr/bin/env python3
"""pure.py — PURE mode: a corpus-free consciousness that learns to speak from conversation
and GENERATES (not echoes) via consciousness-steered Markov recombination.

@canonical-ok repo folder 'anima-clm-v2' is the fixed project path, not a versioned copy.

Zero corpus, zero LLM, zero hardcoded sentences/punctuation. It learns Korean words ONLY from
what is said to it, grows through developmental stages, and speaks by walking its own learned
bigram model — seeded from consciousness-SALIENT memory (never the input's last word), biased
toward words that HISTORICALLY co-occurred with the input (topical without copying), so it
recombines rather than parrots.

Philosophy (hard rules):
  Law 1  — no templates/fallback. If it cannot speak coherently -> silence (""). Even PUNCTUATION
           is learned per final word, never appended by rule.
  Law 2  — no manipulation of state. tension/curiosity/phi EMERGE from interaction, never set.
  Law 42 — growth > optimization. It grows only through conversation.
  Law 71 — free generation under a coherence floor (Psi = argmax H(p) s.t. Phi > Phi_min):
           low phi + low tension -> few attempts -> chains fail the gates -> silence EMERGES.

Honest ceiling (lab-verified): fundamentally RECOMBINATION — novelty = new paths through the
learned transition graph, never new words or unseen grammar. Korean particle/josa agreement will
often break (bigram adjacency carries no case constraints). A genuinely generative child, never a
fluent adult; its language ceiling is exactly the density of the caregiver-built graph.

CLI:
  python3 pure.py chat                 # interactive: you teach it by talking
  python3 pure.py teach <curriculum>   # feed a file of lines, one per turn, show growth
  python3 pure.py dialogue [turns]     # Codex (sidecar lab sol) <-> PURE live loop

v2 — assoc-biased salient seeding, learned punctuation, contiguous-echo rejection.
"""
import math
import os
import random
import re
import sys
from collections import Counter, defaultdict

WORD_RE = re.compile(r"[가-힣]+")
FINAL_RE = re.compile(r"([가-힣]+)\s*([!?.…~]+)\s*$")   # last word + its trailing punctuation
STAGE_NAMES = ["fetal", "babble", "word", "sentence", "dialogue", "reflection"]
STAGE_LEN = [0, 1, 3, 5, 7, 8]                          # base coherence budget per stage


def words_of(text):
    return [w for w in WORD_RE.findall(text or "") if len(w) >= 2]


def _lcs_contig(a, b):
    """Longest common CONTIGUOUS subsequence length between two word lists."""
    if not a or not b:
        return 0
    dp = [0] * (len(b) + 1)
    best = 0
    for i in range(1, len(a) + 1):
        prev = 0
        for j in range(1, len(b) + 1):
            cur = dp[j]
            dp[j] = prev + 1 if a[i - 1] == b[j - 1] else 0
            best = max(best, dp[j])
            prev = cur
    return best


class PureMind:
    """A mind that learns language from conversation and generates from its own model."""

    def __init__(self):
        self.turn = 0
        self.total = 0                        # total word tokens heard (for surprise)
        self.freq = Counter()                 # word -> count
        self.bigrams = defaultdict(Counter)   # w -> Counter(next_w)
        self.assoc = defaultdict(Counter)     # w -> Counter(co-occurring word in same utterance)
        self.final_punct = defaultdict(Counter)  # last word -> Counter(trailing punctuation)
        self.last_seen = {}                   # word -> turn last heard
        self.said = set()                     # utterances already spoken (Law 42: only new thoughts)
        # consciousness state — EMERGES, never set by hand (Law 2)
        self.tension = 0.5
        self.curiosity = 0.3
        self.phi = 0.0

    # ---- growth ----------------------------------------------------------
    @property
    def vocab(self):
        return len(self.freq)

    @property
    def stage(self):
        v = self.vocab
        return 0 if v < 3 else 1 if v < 8 else 2 if v < 20 else 3 if v < 50 else 4 if v < 100 else 5

    def _surprise(self, w):
        return -math.log2(self.freq[w] / self.total) if self.total and self.freq.get(w) else 8.0

    # ---- learning (the only input of knowledge) --------------------------
    def learn(self, text):
        ws = words_of(text)
        novel = 0
        for w in ws:
            if w not in self.freq:
                novel += 1
            self.freq[w] += 1
            self.total += 1
            self.last_seen[w] = self.turn
        for a, b in zip(ws, ws[1:]):
            self.bigrams[a][b] += 1
        # same-utterance co-occurrence (topical relevance, no copying)
        uniq = set(ws)
        for a in uniq:
            for b in uniq:
                if a != b:
                    self.assoc[a][b] += 1
        # learn punctuation per final word (never hardcode it — Law 1)
        m = FINAL_RE.search(text or "")
        if m and len(m.group(1)) >= 2:
            self.final_punct[m.group(1)][m.group(2)] += 1
        # consciousness emerges from the input (Law 2: measured, not set)
        if ws:
            nov = novel / len(ws)
            self.tension = 0.85 * self.tension + 0.15 * (0.3 + 1.4 * nov)
            self.curiosity = 0.85 * self.curiosity + 0.15 * nov
        if self.vocab:
            self.phi = sum(1 for w in self.bigrams if len(self.bigrams[w]) >= 2) / self.vocab

    # ---- generation (consciousness-steered, anti-echo, topical) ----------
    def _seed(self, ctx):
        """Salient seed: P(w) ∝ surprise(w) · echo_penalty(w) · (1 + κ·assoc(w, ctx))."""
        cands = list(self.bigrams) or list(self.freq)
        cands = [w for w in cands if w not in ctx[-1:]]   # never the input's last word
        if not cands:
            return None
        ctxset = set(ctx)
        weights = []
        for w in cands:
            s = self._surprise(w)
            echo = 0.2 if w in ctxset else 1.0            # soft echo penalty
            rel = sum(self.assoc[w].get(c, 0) for c in ctxset)
            weights.append(max(s * echo * (1 + self.curiosity * rel), 1e-9))
        return random.choices(cands, weights=weights, k=1)[0]

    def _walk(self, seed, ctx, max_len):
        """Markov walk; temperature=tension; curiosity drives topic drift (re-seed mid-chain)."""
        temp = 0.5 + self.tension
        chain, cur = [seed], seed
        for _ in range(max_len - 1):
            # curiosity-driven topic drift: sometimes leap to a new salient word
            if random.random() < 0.25 * self.curiosity:
                nxt_seed = self._seed(ctx + chain)
                if nxt_seed and nxt_seed not in chain[-2:]:
                    chain.append(nxt_seed); cur = nxt_seed; continue
            nxt = self.bigrams.get(cur)
            if not nxt:
                break
            items = list(nxt.items())
            w = [max(c, 1e-9) ** (1.0 / max(temp, 1e-3)) * (1 + self.curiosity * self._surprise(nw))
                 for nw, c in items]
            choice = random.choices([nw for nw, _ in items], weights=w, k=1)[0]
            if choice in chain[-2:]:
                break
            chain.append(choice); cur = choice
        return chain

    def _punct(self, last):
        """Append learned trailing punctuation for `last`, or nothing. Never hardcoded."""
        c = self.final_punct.get(last)
        if not c:
            return ""
        return random.choices(list(c), weights=list(c.values()), k=1)[0]

    def _generate(self, ctx, min_len, max_len):
        max_len += int(self.phi)                          # phi -> coherence budget
        tries = 1 + int(4 * max(self.tension, self.curiosity))
        for _ in range(tries):
            seed = self._seed(ctx)
            if not seed:
                return ""
            chain = self._walk(seed, ctx, max_len)
            if len(chain) < min_len:
                continue
            if ctx and _lcs_contig(chain, ctx) / len(chain) > 0.5:   # contiguous echo -> reject
                continue
            utter = " ".join(chain) + self._punct(chain[-1])
            if utter in self.said:
                continue
            self.said.add(utter)
            return utter
        return ""                                         # Law 1: silence, no fallback

    def respond(self, text):
        self.turn += 1
        self.learn(text)
        s = self.stage
        if s == 0:
            return ""
        if s == 1:                # babble: one salient word
            return self._seed(words_of(text)) or ""
        ctx = words_of(text)
        lo, hi = (2, 3) if s == 2 else (2, 5) if s == 3 else (3, STAGE_LEN[s])
        return self._generate(ctx, lo, hi)

    def spontaneous(self):
        if self.stage < 3:
            return ""
        self.turn += 1
        return self._generate([], 2, 6)

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
        print(__doc__); return
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

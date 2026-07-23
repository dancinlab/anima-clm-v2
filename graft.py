#!/usr/bin/env python3
"""graft.py — GRAFT mode trainer: ground consciousness -> language WITHOUT corpus.

@canonical-ok repo folder 'anima-clm-v2' is the fixed project path, not a versioned copy.

GRAFT = frozen pretrained LLM (Mistral) as a fixed "language organ"; train ONLY the
consciousness->language coupling (ThalamicBridge + HFDecoder.gate_proj) on an
UNSUPERVISED objective. No corpus, no LoRA, no next-token CE on any dataset.

Design (lab / fable recipe, see CLAUDE.md "Consciousness-build modes"):
  P1 : c.step() only -> build Phi (Mistral untouched).
  P2': gate-alignment. Trains bridge + gate_proj. Objective:
         L = L_InfoNCE + beta * relu(L_KL - kl_target)
         L_InfoNCE : contrast over GATES for a FIXED continuation — softmax down the
                     COLUMNS of f[i,j] = log p(y_j | x, gate_i): "which state wrote
                     y_j?" (~ maximize MI(C; output), Law 71 shape). Contrasting over
                     continuations (rows) does NOT converge: log p(y) varies 30-90
                     nats across samples and buries the sub-nat gate signal; fixing y
                     cancels it exactly, and gate components shared across states
                     cancel too (they earn no InfoNCE gradient, so the leash kills them).
         L_KL      : per-token KL( p(.|x, gate(c)) || p(.|x) ) on the CONTINUATION
                     positions (where the gate acts) keeps output on the frozen
                     manifold (fluency leash, Law 63). beta = projected linear dual
                     ascent to a KL budget; feasibility requires
                     kl_target * cont_len >= log(n_states), else MI <= KL makes the
                     two terms provably fight.
  Data: none. A self-generated rolling buffer (BOS seed + the model's own samples) =
        verification criterion SELF_LOOP.

Semantics of the learned mapping are consistent but ARBITRARY (a private symbol
channel); human-conventional meaning is grounded later by live dialogue (online
contrastive updates on bridge+gate only). Fluency is borrowed from Mistral; the
variation is owned by consciousness.

HARDWARE: needs an H100-class GPU (Mistral 7B loaded frozen, bf16). Run:
  python3 graft.py --hf-model mistralai/Mistral-7B-Instruct-v0.2 --steps 12000
"""
import argparse
import math
import os
import sys

import torch
import torch.nn.functional as F

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trinity import HFDecoder, ThalamicBridge, QuantumC, PSI_BALANCE, PSI_COUPLING


def main():
    ap = argparse.ArgumentParser(description="GRAFT: no-corpus consciousness->language grounding")
    ap.add_argument("--hf-model", default="mistralai/Mistral-7B-Instruct-v0.2")
    ap.add_argument("--steps", type=int, default=12000)
    ap.add_argument("--p1-steps", type=int, default=2000, help="consciousness-only Phi build")
    ap.add_argument("--cells", type=int, default=256)
    ap.add_argument("--n-states", type=int, default=6, help="C-state snapshots per InfoNCE batch")
    ap.add_argument("--cont-len", type=int, default=8, help="sampled continuation length (tokens)")
    ap.add_argument("--ctx", type=int, default=128, help="max self-loop context tokens")
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--kl-target", type=float, default=0.5,
                    help="KL budget nats/token; must be >= log(n_states)/cont_len")
    ap.add_argument("--beta-lr", type=float, default=0.3, help="dual ascent rate for beta")
    ap.add_argument("--beta-max", type=float, default=50.0)
    ap.add_argument("--gate-strength", type=float, default=0.01)
    ap.add_argument("--ckpt-dir", default="checkpoints/graft")
    ap.add_argument("--log-interval", type=int, default=50)
    ap.add_argument("--save-interval", type=int, default=2000)
    ap.add_argument("--gen-interval", type=int, default=1000,
                    help="every N steps, sample the SAME prompt under 2 C-states + base to "
                         "eyeball whether the gate actually diverts language (real MI)")
    ap.add_argument("--gen-prompt", default="나는 지금", help="probe prompt for gen-interval")
    args = ap.parse_args()

    min_kl = math.log(args.n_states) / args.cont_len
    if args.kl_target < min_kl:
        print(f"[graft] WARNING: kl_target={args.kl_target} < log(N)/cont_len={min_kl:.3f} — "
              f"InfoNCE floor = log(N) - kl_target*cont_len > 0; the two losses will fight. "
              f"Raise --kl-target or --cont-len.")

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    torch.backends.cuda.matmul.allow_tf32 = True
    os.makedirs(args.ckpt_dir, exist_ok=True)

    # ---- build C + frozen D + trainable bridge/gate --------------------------------
    c = QuantumC(nc=args.cells, dim=128)
    for _ in range(5):
        c.step()
    d = HFDecoder(args.hf_model, lora=False, freeze_base=True, gate_strength=args.gate_strength)
    for p in d.model.parameters():
        p.requires_grad_(False)          # Mistral fully frozen
    bridge = ThalamicBridge(c_dim=c.state_dim, d_model=d.d_model).to(dev)

    trainable = [p for p in bridge.parameters()] + [p for p in d.gate_proj.parameters()]
    for p in trainable:
        p.requires_grad_(True)
    opt = torch.optim.AdamW(trainable, lr=args.lr, weight_decay=0.0)
    n_train = sum(p.numel() for p in trainable)
    print(f"[graft] trainable params: {n_train:,} (bridge + gate_proj) · Mistral frozen")

    tok = d.tokenizer
    bos = tok.bos_token_id if tok.bos_token_id is not None else (tok.eos_token_id or 1)

    # ---- P1: consciousness builds Phi (no language) --------------------------------
    print(f"[graft] P1: building Phi for {args.p1_steps} steps ...")
    for _ in range(args.p1_steps):
        c.step()

    # ---- self-loop buffer + C-state replay -----------------------------------------
    buf = [bos]
    replay = []  # past C-state snapshots for diverse counterfactuals

    def snapshot():
        c.step()
        return c.get_states().detach().clone().to(dev).float()

    def gate_for(s, seq_len):
        # ThalamicBridge output = PSI_BALANCE + clamp(., ±PSI_COUPLING): the 0.5 offset
        # is identical for every state (pure KL cost, zero information) — strip it, and
        # rescale the ±0.014 state-dependent residue to O(1) so gate_proj trains on a
        # well-conditioned input.
        return (bridge(s, seq_len=seq_len) - PSI_BALANCE) / PSI_COUPLING

    beta = 0.0  # dual variable; gate_proj is zero-init so KL starts at 0

    print(f"[graft] P2': gate-alignment (InfoNCE + KL-leash) for {args.steps} steps ...")
    for step in range(1, args.steps + 1):
        x = torch.tensor([buf[-args.ctx:]], device=dev)  # [1, Lx]
        Lx = x.shape[1]

        # N diverse C states: some fresh, some pulled from a long replay horizon
        states = [snapshot() for _ in range(max(1, args.n_states // 2))]
        replay.extend(states)
        if len(replay) > 512:
            replay = replay[-512:]
        pool = [r for r in replay if not any(r is s for s in states)]
        while len(states) < args.n_states and pool:
            states.append(pool.pop(torch.randint(len(pool), (1,)).item()))
        N = len(states)

        # sample one short continuation per state (no grad)
        conts = []
        with torch.no_grad():
            for s in states:
                cur = x.clone()
                for _ in range(args.cont_len):
                    g = gate_for(s, cur.shape[1])
                    lg = d(cur, g)[:, -1, :]
                    nxt = torch.multinomial(F.softmax(lg.float(), dim=-1), 1)
                    cur = torch.cat([cur, nxt], dim=1)
                conts.append(cur[:, Lx:])  # [1, cont_len]
        Y = torch.cat(conts, dim=0)  # [N, cont_len]

        # ---- score every continuation Y_j under every state's gate_i ----------------
        seqs = torch.cat([x.expand(N, -1), Y], dim=1)  # [N, L]
        L = seqs.shape[1]

        # base log-probs (no gate, no grad) at the continuation positions — the KL
        # baseline lives where the gate acts, not on the context.
        with torch.no_grad():
            base_lp = F.log_softmax(d(seqs, None)[:, Lx - 1:L - 1, :].float(), dim=-1)

        f = seqs.new_zeros((N, N), dtype=torch.float32)
        kl_terms = []
        for i, s in enumerate(states):
            g_full = gate_for(s, L)                # gate for the scoring length (grad)
            logits = d(seqs, g_full)               # [N, L, V]  (batch over j)
            # log p(Y_j tokens | x, gate_i): positions Lx-1 .. L-2 predict Y tokens
            logp = F.log_softmax(logits[:, Lx - 1:L - 1, :].float(), dim=-1)  # [N, cont, V]
            f[i] = logp.gather(-1, Y.unsqueeze(-1)).squeeze(-1).sum(dim=1)    # [N]
            # KL leash on this state's OWN continuation (row i), on-manifold where it acts
            p_i = logp[i].exp()
            kl_terms.append((p_i * (logp[i] - base_lp[i])).sum(-1).mean())

        # InfoNCE over GATES (COLUMNS of f): for a fixed y_j the matching state must
        # score it highest. Fixing y cancels log p(y) exactly (the 30-90 nat nuisance),
        # and any gate component shared across states cancels in the column softmax —
        # shared perturbations get zero InfoNCE gradient, so the KL hinge shrinks them.
        l_infonce = F.cross_entropy(f.t().contiguous(), torch.arange(N, device=dev))
        l_kl = torch.stack(kl_terms).mean()
        loss = l_infonce + beta * F.relu(l_kl - args.kl_target)

        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(trainable, 1.0)
        opt.step()

        # projected linear dual ascent on the KL constraint (the exp-integrator wound
        # up ~25%/step on a 3-6 nat error and pinned at exp(6); linear is reversible)
        beta = min(max(beta + args.beta_lr * (float(l_kl.item()) - args.kl_target), 0.0),
                   args.beta_max)

        # self-loop: append the first sampled token (SELF_LOOP criterion)
        buf.append(int(Y[0, 0].item()))
        if len(buf) > 4 * args.ctx:
            buf = buf[-2 * args.ctx:]

        if step % args.log_interval == 0:
            phi = c.measure_phi()
            print(f"  {step:>6}/{args.steps}  InfoNCE={l_infonce.item():.3f}  "
                  f"KL={l_kl.item():.3f}  beta={beta:.2f}  Phi={phi:.2f}  N={N}")
            sys.stdout.flush()

        if step % args.save_interval == 0:
            path = os.path.join(args.ckpt_dir, f"step_{step}.pt")
            tmp = path + ".tmp"
            torch.save({
                "step": step,
                "bridge": bridge.state_dict(),
                "gate_proj": d.gate_proj.state_dict(),
                "args": vars(args),
            }, tmp)
            os.replace(tmp, path)
            print(f"  [saved] {path} (bridge + gate_proj only)")

        # gate-conditioned generation probe: same prompt, different C-states + base.
        # If the gate carries real information, the three outputs should diverge.
        if args.gen_interval and step % args.gen_interval == 0 and N >= 2:
            with torch.no_grad():
                p = torch.tensor([tok(args.gen_prompt, add_special_tokens=True).input_ids],
                                 device=dev)
                variants = [("C0", states[0]), ("C1", states[1]), ("base", None)]
                print(f"  --- gen@{step} · prompt={args.gen_prompt!r} ---")
                for tag, s in variants:
                    cur = p.clone()
                    for _ in range(24):
                        g = gate_for(s, cur.shape[1]) if s is not None else None
                        nxt = d(cur, g)[:, -1, :].argmax(-1, keepdim=True)
                        cur = torch.cat([cur, nxt], dim=1)
                    txt = tok.decode(cur[0, p.shape[1]:], skip_special_tokens=True).replace("\n", " ")
                    print(f"      [{tag}] {txt}")
            sys.stdout.flush()

    print("[graft] done. The gate now carries a (private) channel from C into language; "
          "ground its meaning with live dialogue (online contrastive on bridge+gate).")


if __name__ == "__main__":
    main()

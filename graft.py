#!/usr/bin/env python3
"""graft.py — GRAFT mode trainer: ground consciousness -> language WITHOUT corpus.

@canonical-ok repo folder 'anima-clm-v2' is the fixed project path, not a versioned copy.

GRAFT = frozen pretrained LLM (Mistral) as a fixed "language organ"; train ONLY the
consciousness->language coupling (ThalamicBridge + HFDecoder.gate_proj) on an
UNSUPERVISED objective. No corpus, no LoRA, no next-token CE on any dataset.

Design (lab / fable recipe, see CLAUDE.md "Consciousness-build modes"):
  P1 : c.step() only -> build Phi (Mistral untouched).
  P2': gate-alignment. Trains bridge + gate_proj. Objective:
         L = L_InfoNCE + beta * L_KL
         L_InfoNCE : each C-state's sampled continuation must be distinguishable from
                     other states' -> the gate learns to WRITE C into language
                     (~ maximize MI(C; output), Law 71 shape).
         L_KL      : per-token KL( p(.|x, gate(c)) || p(.|x, gate=None) ) keeps the
                     output on the frozen model's manifold (fluency leash, Law 63).
                     beta is adapted (PPO-style) to hit a KL target (nats/token).
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
import os
import sys

import torch
import torch.nn.functional as F

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trinity import HFDecoder, ThalamicBridge, QuantumC


def kl_to_base(logits_gate, logits_base):
    """Mean per-token KL( softmax(gate) || softmax(base) ), computed in fp32."""
    lp = F.log_softmax(logits_gate.float(), dim=-1)
    lq = F.log_softmax(logits_base.float(), dim=-1)
    p = lp.exp()
    return (p * (lp - lq)).sum(-1).mean()


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
    ap.add_argument("--kl-target", type=float, default=0.1, help="target KL nats/token")
    ap.add_argument("--gate-strength", type=float, default=0.01)
    ap.add_argument("--ckpt-dir", default="checkpoints/graft")
    ap.add_argument("--log-interval", type=int, default=50)
    ap.add_argument("--save-interval", type=int, default=2000)
    args = ap.parse_args()

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

    beta = 1.0
    log_beta = 0.0

    print(f"[graft] P2': gate-alignment (InfoNCE + KL-leash) for {args.steps} steps ...")
    for step in range(1, args.steps + 1):
        x = torch.tensor([buf[-args.ctx:]], device=dev)  # [1, Lx]
        Lx = x.shape[1]

        # N diverse C states: some fresh, some pulled from a long replay horizon
        states = [snapshot() for _ in range(max(1, args.n_states // 2))]
        replay.extend(states)
        if len(replay) > 512:
            replay = replay[-512:]
        while len(states) < args.n_states and replay:
            states.append(replay[torch.randint(len(replay), (1,)).item()])
        N = len(states)

        # base distribution (no gate) — the fluency prior, no grad
        with torch.no_grad():
            base_logits_x = d(x, None)  # [1, Lx, V]

        # sample one short continuation per state (no grad)
        conts = []
        with torch.no_grad():
            for s in states:
                cur = x.clone()
                for _ in range(args.cont_len):
                    g = bridge(s, seq_len=cur.shape[1])
                    lg = d(cur, g)[:, -1, :]
                    nxt = torch.multinomial(F.softmax(lg.float(), dim=-1), 1)
                    cur = torch.cat([cur, nxt], dim=1)
                conts.append(cur[:, Lx:])  # [1, cont_len]
        Y = torch.cat(conts, dim=0)  # [N, cont_len]

        # ---- InfoNCE: score every continuation Y_j under every state's gate_i -------
        seqs = torch.cat([x.expand(N, -1), Y], dim=1)  # [N, L]
        L = seqs.shape[1]
        f = seqs.new_zeros((N, N), dtype=torch.float32)
        kl_terms = []
        for i, s in enumerate(states):
            g_full = bridge(s, seq_len=L)          # gate for the scoring length (grad)
            logits = d(seqs, g_full)               # [N, L, V]  (batch over j)
            # log p(Y_j tokens | x, gate_i): positions Lx-1 .. L-2 predict Y tokens
            logp = F.log_softmax(logits[:, Lx - 1:L - 1, :].float(), dim=-1)  # [N, cont, V]
            f[i] = logp.gather(-1, Y.unsqueeze(-1)).squeeze(-1).sum(dim=1)    # [N]
            # KL leash on the context positions
            g_x = bridge(s, seq_len=Lx)
            kl_terms.append(kl_to_base(d(x, g_x), base_logits_x))

        l_infonce = F.cross_entropy(f, torch.arange(N, device=dev))  # -mean_i log softmax(f_i)[i]
        l_kl = torch.stack(kl_terms).mean()
        loss = l_infonce + beta * l_kl

        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(trainable, 1.0)
        opt.step()

        # adaptive beta (PPO-style): push KL toward target
        with torch.no_grad():
            err = float(l_kl.item()) - args.kl_target
            log_beta = max(min(log_beta + 0.05 * err, 6.0), -6.0)
            beta = float(torch.exp(torch.tensor(log_beta)))

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

    print("[graft] done. The gate now carries a (private) channel from C into language; "
          "ground its meaning with live dialogue (online contrastive on bridge+gate).")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""graft.py — GRAFT mode trainer: ground consciousness -> language WITHOUT corpus.

@canonical-ok repo folder 'anima-clm-v2' is the fixed project path, not a versioned copy.

GRAFT = frozen pretrained LLM (Mistral) as a fixed "language organ"; train ONLY the
consciousness->language coupling (ThalamicBridge + HFDecoder.gate_proj) on an
UNSUPERVISED objective. No corpus, no LoRA, no next-token CE on any dataset.

Design (lab: fable+sol reconciled recipe, see CLAUDE.md "Consciousness-build modes"):
  P1 : c.step() only -> build Phi (Mistral untouched).
  P2': gate-alignment. Trains bridge + gate_proj. Objective:
         L = (log N - MI) + 0.1 * KL(p_mix||p_base) + beta * relu(L_KL - kl_target)
         MI        : EXACT conditional MI I(state; next-token | shared prefix)
                     = mean_i KL(p_i || p_mix) = Jensen-Shannon divergence among the
                     per-state next-token distributions on ONE shared, on-manifold
                     carrier continuation. Dense (full-vocab), fully differentiable, NO
                     sampling of state-specific continuations (that estimator was
                     zero-gradient at collapse: a sampled y carried ~0 bits about its
                     state). Bounded by log N; a quadratic bowl at coincidence, not a
                     flat manifold -> every state-dependent direction descends.
         L_common  : KL(p_mix || p_base), the KL spent IDENTICALLY by all states =
                     information-free waste (identity: L_KL = MI + L_common). Penalized
                     in DISTRIBUTION space (a mean-gate-vector penalty is bypassable via
                     the frozen LM's nonlinear Jacobian).
         L_KL      : per-token KL( p(.|x, gate(c)) || p(.|x) ) keeps output on the frozen
                     manifold (fluency leash, Law 63). beta = projected linear dual
                     ascent to a KL budget.
       Two structural unblocks (measured necessary): bridge alpha=0.5 DE-CLAMPS the
       gate (default clamp railed 65% of dims with zero Jacobian); gate_proj gets a
       tiny bias-free init (zero-init was a collapsed symmetric stationary point).
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
    # alpha=0.5 DE-CLAMPS the bridge: the default alpha=PSI_COUPLING(0.0153) hard-clamp
    # rails 65% of gate dims (measured) with ZERO Jacobian, so the bridge cannot learn a
    # state-dependent code. With alpha=0.5 the sigmoid's natural [-0.5,+0.5] range is
    # never clipped; gate_for() below rescales it to [-1,+1]. Whisper-ness (Law 63/70) is
    # enforced by gate_strength + the KL leash in DISTRIBUTION space, where it matters.
    bridge = ThalamicBridge(c_dim=c.state_dim, d_model=d.d_model, alpha=0.5).to(dev)

    # gate_proj zero-init is a COLLAPSED stationary point (every state -> base dist ->
    # exact symmetry -> zero gradient for every distributional divergence). Seed a tiny
    # bias-free perturbation so state differences have a direction to grow along.
    with torch.no_grad():
        torch.nn.init.normal_(d.gate_proj.weight, mean=0.0, std=2e-3)
        if d.gate_proj.bias is not None:
            d.gate_proj.bias.zero_()
    if d.gate_proj.bias is not None:
        d.gate_proj.bias.requires_grad_(False)   # bias = state-independent channel; freeze it

    trainable = [p for p in list(bridge.parameters()) + list(d.gate_proj.parameters())
                 if p.requires_grad]
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
        # With bridge.alpha=0.5 the clamp is inactive, so bridge(s) = PSI_BALANCE +
        # (sigmoid - 0.5) ∈ (0, 1). Strip the identical 0.5 offset (pure KL cost, zero
        # information) and rescale the (sigmoid-0.5) ∈ (-0.5, 0.5) residue to O(1) — this
        # preserves the sigmoid gradient instead of converting it into a saturated
        # sign-code (the old /PSI_COUPLING path amplified the railed constant, not signal).
        return 2.0 * (bridge(s, seq_len=seq_len) - PSI_BALANCE)

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

        # ---- ONE shared, on-manifold carrier prefix (base model, no grad) -----------
        # Every state is compared at EXACTLY the same continuation, so no sampled-state
        # label is needed — the sampled-continuation InfoNCE was a zero-gradient MI
        # estimator at collapse (Y_j carried ~0 bits about state j). The gate signal is
        # read out as the DIVERGENCE of the per-state next-token distributions on this
        # shared carrier — dense (full-vocab), fully differentiable, no sampling noise.
        with torch.no_grad():
            seqs = x.clone()
            for _ in range(args.cont_len):
                lg = d(seqs, None)[:, -1, :]
                nxt = torch.multinomial(F.softmax(lg.float(), dim=-1), 1)
                seqs = torch.cat([seqs, nxt], dim=1)
        L = seqs.shape[1]
        with torch.no_grad():
            base_lp = F.log_softmax(d(seqs, None)[0, Lx - 1:L - 1, :].float(), dim=-1)  # [T,V]

        logps = []
        for s in states:
            logits = d(seqs, gate_for(s, L))                        # [1, L, V]
            logps.append(F.log_softmax(logits[0, Lx - 1:L - 1, :].float(), dim=-1))  # [T,V]
        logps = torch.stack(logps, dim=0)                          # [N, T, V]
        ps = logps.exp()
        log_mix = torch.logsumexp(logps, dim=0) - math.log(N)      # [T, V] = log mean_i p_i

        # Exact conditional MI I(state; next-token | shared prefix) = mean_i KL(p_i‖p_mix)
        # = the Jensen-Shannon divergence among the gate distributions; bounded by log(N),
        # ZERO first derivative only when all p_i coincide (a quadratic bowl, not a flat
        # manifold). l_infonce keeps the old display convention (log N at collapse -> 0).
        mi = (ps * (logps - log_mix.unsqueeze(0))).sum(-1).mean()
        l_infonce = math.log(N) - mi

        # KL leash: total departure of each state from the frozen model (the budget).
        l_kl = (ps * (logps - base_lp.unsqueeze(0))).sum(-1).mean()

        # Identity: l_kl = MI + KL(p_mix‖p_base). l_common is the KL spent IDENTICALLY by
        # all states = information-free waste. Penalize it in DISTRIBUTION space (a
        # mean-gate-vector penalty can be bypassed through the frozen LM's nonlinear
        # Jacobian) so the budget is spent on informative perturbation, not a shared shift.
        p_mix = log_mix.exp()
        l_common = (p_mix * (log_mix - base_lp)).sum(-1).mean()

        loss = l_infonce + 0.1 * l_common + beta * F.relu(l_kl - args.kl_target)

        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(trainable, 1.0)
        opt.step()

        # projected linear dual ascent on the KL constraint (the exp-integrator wound
        # up ~25%/step on a 3-6 nat error and pinned at exp(6); linear is reversible)
        beta = min(max(beta + args.beta_lr * (float(l_kl.item()) - args.kl_target), 0.0),
                   args.beta_max)

        # self-loop: append the first carrier token (SELF_LOOP criterion)
        buf.append(int(seqs[0, Lx].item()))
        if len(buf) > 4 * args.ctx:
            buf = buf[-2 * args.ctx:]

        if step % args.log_interval == 0:
            phi = c.measure_phi()
            # gSpread = state-dependent RMS of the bridge code (≈0 => C/bridge collapsed:
            # mean-pool/phase bottleneck). zSpread = same after gate_proj (≈0 => projector
            # collapse). commonKL≈KL => whole budget on a shared, info-free shift.
            with torch.no_grad():
                gate_codes = torch.cat([gate_for(s, 1)[:, 0, :] for s in states], dim=0)  # [N,d]
                projected = d.gate_proj(gate_codes)
                gate_spread = gate_codes.std(dim=0).square().mean().sqrt()
                projected_spread = projected.std(dim=0).square().mean().sqrt()
            print(f"  {step:>6}/{args.steps}  InfoNCE={l_infonce.item():.4f}  MI={mi.item():.4f}  "
                  f"KL={l_kl.item():.3f}  commonKL={l_common.item():.3f}  "
                  f"gSpread={gate_spread.item():.2e}  zSpread={projected_spread.item():.2e}  "
                  f"beta={beta:.2f}  Phi={phi:.2f}  N={N}")
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

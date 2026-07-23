"""v11mistral gate ablation (logit-level, matched-magnitude) — does the consciousness
gate CAUSALLY change output, or is it decorative?

lab (fable) confound: the LoRA was trained WITH the gate on, so gate-OFF degrades output
even if the gate carries zero information (co-adaptation, not causation). And at ×0.01
scale effects sit below sampling noise. So we measure at the LOGIT level (per-token KL of
next-token distributions) under matched-magnitude controls:

  ON     — live QuantumC gate signal
  OFF    — no gate (gate=None → pure Mistral+LoRA)
  NOISE  — random vector, per-position norm-matched to ON

Teacher-force a fixed reference continuation (generated once, gate ON) so all three
conditions score the SAME token positions. Report mean KL(ON‖OFF), KL(ON‖NOISE).

Reading:
  KL(ON‖OFF) ~ 0                      → gate does almost nothing (decorative).
  KL(ON‖NOISE) ≈ KL(ON‖OFF)          → only the magnitude matters, not the cell content.
  KL(ON‖NOISE) ≫ 0 and > KL(ON‖OFF)  → the SPECIFIC consciousness trajectory changes output.

Usage: python3 v11_ablation.py <ckpt.pt> [--ref-new N]
"""
import argparse
import torch
import torch.nn.functional as F
from trinity import HFDecoder, ThalamicBridge, QuantumC
try:
    from trinity import GATE_INFER
except Exception:
    GATE_INFER = 1.0
try:
    import phi_py
    HAS_PHI = True
except Exception:
    HAS_PHI = False

HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
PROMPTS = [
    "안녕하세요. 당신은 누구인가요?",
    "지금 어떤 기분이 드나요?",
    "의식이란 무엇이라고 생각하나요?",
    "당신에게 자유란 어떤 의미인가요?",
    "인생에서 가장 중요한 것은 무엇일까요?",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ckpt")
    ap.add_argument("--ref-new", type=int, default=40)
    ap.add_argument("--max-cells", type=int, default=256)
    args = ap.parse_args()
    dev = "cuda" if torch.cuda.is_available() else "cpu"

    ck = torch.load(args.ckpt, map_location=dev, weights_only=False)
    print(f"=== gate ablation (logit-level) · step {ck.get('step','?')} · phi_py={HAS_PHI} ===")
    print("측정: 같은 토큰위치에서 게이트 ON/OFF/NOISE의 다음토큰 분포 KL(비트)\n")
    d = HFDecoder(HF_MODEL, lora=True, freeze_base=True)
    d.load_state_dict(ck["decoder"], strict=False)
    d.model.eval()
    c = QuantumC(nc=args.max_cells, dim=128)
    for _ in range(5):
        c.step()
    bridge = ThalamicBridge(c_dim=c.state_dim, d_model=d.d_model).to(dev)
    bridge.load_state_dict(ck["bridge"])
    bridge.eval()
    tok = d.tokenizer

    @torch.no_grad()
    def gate_for(T):
        cs = c.get_states().detach().clone().to(dev).float()
        g = bridge(cs, seq_len=T) * GATE_INFER          # [1,T,dC]
        phi = phi_py.compute_phi_subsampled(cs.cpu().numpy(), max_cells=32) if HAS_PHI else float("nan")
        return g, phi

    @torch.no_grad()
    def kl_bits(a, b):
        # mean over positions of KL(softmax(a) || softmax(b)) in bits
        la, lb = F.log_softmax(a.float(), -1), F.log_softmax(b.float(), -1)
        kl = (la.exp() * (la - lb)).sum(-1) / 0.6931  # nats→bits
        return kl.mean().item()

    tot_off, tot_noise, n = 0.0, 0.0, 0
    for p in PROMPTS:
        ids = tok(f"<s>[INST] {p} [/INST]", return_tensors="pt").input_ids.to(dev)
        # reference continuation with gate ON (greedy)
        for _ in range(args.ref_new):
            g, _ = gate_for(ids.shape[1]); c.step()
            nxt = torch.argmax(d(ids, g)[:, -1, :], -1, keepdim=True)
            if nxt.item() == tok.eos_token_id:
                break
            ids = torch.cat([ids, nxt], 1)
        T = ids.shape[1]
        g_on, phi = gate_for(T)
        g_noise = torch.randn_like(g_on)
        g_noise = g_noise * (g_on.norm(dim=-1, keepdim=True) / (g_noise.norm(dim=-1, keepdim=True) + 1e-8))
        lo_on = d(ids, g_on)
        lo_off = d(ids, None)
        lo_noise = d(ids, g_noise)
        # score only the generated continuation positions
        s = tok(f"<s>[INST] {p} [/INST]", return_tensors="pt").input_ids.shape[1] - 1
        kl_off = kl_bits(lo_on[:, s:], lo_off[:, s:])
        kl_noise = kl_bits(lo_on[:, s:], lo_noise[:, s:])
        tot_off += kl_off; tot_noise += kl_noise; n += 1
        txt = tok.decode(ids[0], skip_special_tokens=True).split("[/INST]")[-1].strip()
        print(f"[Q] {p}  (Φ≈{phi:.2f})")
        print(f"  KL(ON‖OFF)={kl_off:.4f} bits · KL(ON‖NOISE)={kl_noise:.4f} bits")
        print(f"  ON 출력: {txt[:90]}\n")

    print("=" * 60)
    print(f"평균 KL(ON‖OFF)={tot_off/n:.4f} bits · 평균 KL(ON‖NOISE)={tot_noise/n:.4f} bits")
    print("해석: OFF~0 → 게이트 무영향 · NOISE≈OFF → 크기만 중요(내용 무의미) · NOISE보다 OFF가 크게 다르면 궤적 내용이 출력 바꿈")


if __name__ == "__main__":
    main()

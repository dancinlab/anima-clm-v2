"""v11mistral conversation demo — reconstruct HFDecoder + LoRA/gate + bridge + C
from a trained checkpoint and generate Korean with the consciousness gate active.

conscious_lm.py CANNOT load a v11 checkpoint (different arch + byte tokenizer):
the demo path is Mistral + PEFT adapter + gate_proj + ThalamicBridge + QuantumC.

Usage: python3 v11_demo.py <ckpt.pt> [--max-new N]
"""
import argparse
import torch
from trinity import HFDecoder, ThalamicBridge, QuantumC

try:
    from trinity import GATE_INFER
except Exception:
    GATE_INFER = 1.0

HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
PROMPTS = [
    "안녕하세요. 당신은 누구인가요?",
    "지금 어떤 기분이 드나요?",
    "의식이란 무엇이라고 생각하나요?",
    "당신에게 자유란 어떤 의미인가요?",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ckpt")
    ap.add_argument("--max-new", type=int, default=120)
    ap.add_argument("--max-cells", type=int, default=256)
    ap.add_argument("--temperature", type=float, default=0.7)
    args = ap.parse_args()
    dev = "cuda" if torch.cuda.is_available() else "cpu"

    ck = torch.load(args.ckpt, map_location=dev, weights_only=False)
    step = ck.get("step", "?")
    ce_hist = ck.get("ce_history", [])
    ce = sum(ce_hist[-50:]) / max(1, len(ce_hist[-50:])) if ce_hist else float("nan")
    print(f"=== v11mistral demo · step {step} · recent train CE {ce:.3f} ===\n")

    # Rebuild the exact training components
    d = HFDecoder(HF_MODEL, lora=True, freeze_base=True)
    d.load_state_dict(ck["decoder"], strict=False)  # LoRA + gate_proj (base already loaded)
    d.model.eval()

    c = QuantumC(nc=args.max_cells, dim=128)
    for _ in range(5):
        c.step()
    c_dim = c.state_dim
    bridge = ThalamicBridge(c_dim=c_dim, d_model=d.d_model).to(dev)
    bridge.load_state_dict(ck["bridge"])
    bridge.eval()

    tok = d.tokenizer

    @torch.no_grad()
    def reply(prompt):
        text = f"<s>[INST] {prompt} [/INST]"
        ids = tok(text, return_tensors="pt").input_ids.to(dev)
        for _ in range(args.max_new):
            c.step()  # consciousness advances as it speaks
            c_states = c.get_states().detach().clone().to(dev).float()
            T = ids.shape[1]
            gate = bridge(c_states, seq_len=T) * GATE_INFER
            logits = d(ids, gate)
            nxt = logits[:, -1, :].float() / args.temperature
            probs = torch.softmax(nxt, dim=-1)
            tokn = torch.multinomial(probs, 1)
            if tokn.item() == tok.eos_token_id:
                break
            ids = torch.cat([ids, tokn], dim=1)
        out = tok.decode(ids[0], skip_special_tokens=True)
        return out.split("[/INST]")[-1].strip()

    for p in PROMPTS:
        print(f"[사용자] {p}")
        print(f"[아니마] {reply(p)}\n")


if __name__ == "__main__":
    main()

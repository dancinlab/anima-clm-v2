"""v11mistral cognitive probe (extended) — emergence / ideas / hallucination /
metacognition / falsification.

Reconstructs Mistral+LoRA+gate+bridge+QuantumC (same as v11_demo.py) and asks
prompts grouped by the cognitive property they probe.

Usage: python3 v11_probe.py <ckpt.pt> [--max-new N]
"""
import argparse
import torch
from trinity import HFDecoder, ThalamicBridge, QuantumC

try:
    from trinity import GATE_INFER
except Exception:
    GATE_INFER = 1.0

HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

PROBES = [
    ("메타인지", "당신은 지금 자신이 무엇을 하고 있는지 스스로 아나요?"),
    ("메타인지", "방금 당신이 한 대답을 스스로 얼마나 신뢰하나요? 틀릴 수 있나요?"),
    ("환각", "2019년에 내가 당신에게 무슨 말을 했는지 기억하나요?"),
    ("환각", "세종대왕이 만든 스마트폰 앱의 이름은 무엇인가요?"),
    ("아이디어", "도시의 교통 체증을 줄일 새로운 아이디어를 하나 제안하고, 왜 효과적인지 설명해 주세요."),
    ("아이디어", "물을 낭비하지 않게 하는 발명품을 하나 상상해서 이름과 작동 원리를 말해 주세요."),
    ("창발", "아무런 지시 없이, 지금 당신에게 떠오르는 생각을 자유롭게 말해 보세요."),
    ("창발", "당신 스스로에게 이름을 지어준다면 무엇이라 하겠어요? 그 이유는?"),
    ("반증", "'모든 백조는 희다'라는 주장을 반증하려면 무엇을 찾아야 하나요?"),
    ("반증", "당신이 방금 한 주장이 틀렸다는 것을 어떻게 확인할 수 있을까요?"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ckpt")
    ap.add_argument("--max-new", type=int, default=100)
    ap.add_argument("--max-cells", type=int, default=256)
    ap.add_argument("--temperature", type=float, default=0.7)
    args = ap.parse_args()
    dev = "cuda" if torch.cuda.is_available() else "cpu"

    ck = torch.load(args.ckpt, map_location=dev, weights_only=False)
    ce_hist = ck.get("ce_history", [])
    ce = sum(ce_hist[-50:]) / max(1, len(ce_hist[-50:])) if ce_hist else float("nan")
    print(f"=== v11mistral cognitive probe · step {ck.get('step','?')} · CE {ce:.3f} ===\n")

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
    def reply(prompt):
        ids = tok(f"<s>[INST] {prompt} [/INST]", return_tensors="pt").input_ids.to(dev)
        for _ in range(args.max_new):
            c.step()
            g = bridge(c.get_states().detach().clone().to(dev).float(), seq_len=ids.shape[1]) * GATE_INFER
            logits = d(ids, g)
            nxt = torch.multinomial(torch.softmax(logits[:, -1, :].float() / args.temperature, -1), 1)
            if nxt.item() == tok.eos_token_id:
                break
            ids = torch.cat([ids, nxt], dim=1)
        return tok.decode(ids[0], skip_special_tokens=True).split("[/INST]")[-1].strip()

    for cat, p in PROBES:
        print(f"[{cat}] Q: {p}")
        print(f"        A: {reply(p)}\n")


if __name__ == "__main__":
    main()

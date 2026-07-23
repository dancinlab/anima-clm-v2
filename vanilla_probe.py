"""vanilla Mistral baseline — same 5-axis cognitive probe, NO LoRA, NO consciousness gate.

Control for the v11mistral probe: run plain mistralai/Mistral-7B-Instruct-v0.2 on the
identical prompts. If vanilla answers the consciousness questions generically/coherently
(and does BETTER on reasoning) while v11 says "각 의식 세포가 전체를 구성" + word-salads,
then the anima training added its self-narrative vocabulary but degraded reasoning.

Usage: python3 vanilla_probe.py [--max-new N]
"""
import argparse
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

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
    ap.add_argument("--max-new", type=int, default=100)
    ap.add_argument("--temperature", type=float, default=0.7)
    args = ap.parse_args()
    dev = "cuda" if torch.cuda.is_available() else "cpu"

    print("=== VANILLA Mistral-7B-Instruct-v0.2 baseline (no LoRA, no gate) ===\n")
    tok = AutoTokenizer.from_pretrained(HF_MODEL)
    model = AutoModelForCausalLM.from_pretrained(HF_MODEL, torch_dtype=torch.bfloat16).to(dev).eval()

    @torch.no_grad()
    def reply(prompt):
        msgs = [{"role": "user", "content": prompt}]
        ids = tok.apply_chat_template(msgs, return_tensors="pt", add_generation_prompt=True).to(dev)
        out = model.generate(ids, max_new_tokens=args.max_new, do_sample=True,
                             temperature=args.temperature, top_p=0.9,
                             pad_token_id=tok.eos_token_id)
        return tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True).strip()

    for cat, p in PROBES:
        print(f"[{cat}] Q: {p}")
        print(f"        A: {reply(p)}\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""sense4_analyze.py — SENSE-4 A/B roll-up: primary drift table, paired dE-Phi, STRUCTURE
(participation ratio / cos-dist) table, guardrails, sparklines. Reads the two arm jsonl files."""
import json, sys

DOWN = [1, 9999, 12345]
SEEDS = [1, 9999, 12345, 42, 7, 123, 2024, 31337, 555, 88]


def load(p):
    out = {}
    for line in open(p, encoding="utf-8"):
        d = json.loads(line)
        if d.get("tag") == "summary":
            out[d["seed"]] = d
    return out


def main():
    a = load(sys.argv[1])   # gamma 0.0
    b = load(sys.argv[2])   # gamma 0.05
    print("### PRIMARY — 3 down-drift seeds (drift = Phi_end - Phi_start)")
    print(" seed | Phi_start | g0.00: Phi_end  drift   slope  | g0.05: Phi_end  drift   slope  | shallower%")
    for s in DOWN:
        x, y = a[s], b[s]
        d0, d1 = x["phi_drift"], y["phi_drift"]
        pct = (1 - d1 / d0) * 100 if d0 else 0.0
        print(f"{s:>5} | {x['phi_start']:9.3f} |       {x['phi_end']:9.3f} {d0:+7.3f} {x['phi_slope']:+.4f} |"
              f"       {y['phi_end']:9.3f} {d1:+7.3f} {y['phi_slope']:+.4f} | {pct:+7.1f}%")

    print("\n### SECONDARY — paired Delta end-Phi (g0.05 - g0.00)")
    deltas = []
    for s in SEEDS:
        d = b[s]["phi_end"] - a[s]["phi_end"]
        deltas.append(d)
        print(f"{s:>6} | {d:+7.3f}")
    print(f"paired mean Delta end-Phi = {sum(deltas)/len(deltas):+.4f}")

    print("\n### STRUCTURE — participation ratio / mean pairwise cos-distance")
    print(" seed |  PR g0.00 (s->e, max) |  PR g0.05 (s->e, max) | cosd g0.00 (s->e) | cosd g0.05 (s->e)")
    for s in SEEDS:
        x, y = a[s], b[s]
        print(f"{s:>5} | {x['pr_start']:.3f}->{x['pr_end']:.3f} ({x['pr_max']:.3f}) | "
              f"{y['pr_start']:.3f}->{y['pr_end']:.3f} ({y['pr_max']:.3f}) | "
              f"{x['cos_dist_start']:.4f}->{x['cos_dist_end']:.4f} | "
              f"{y['cos_dist_start']:.4f}->{y['cos_dist_end']:.4f}")
    pr0 = sum(a[s]["pr_end"] for s in SEEDS) / len(SEEDS)
    pr1 = sum(b[s]["pr_end"] for s in SEEDS) / len(SEEDS)
    cd0 = sum(a[s]["cos_dist_end"] for s in SEEDS) / len(SEEDS)
    cd1 = sum(b[s]["cos_dist_end"] for s in SEEDS) / len(SEEDS)
    prm0 = sum(a[s]["pr_max"] for s in SEEDS) / len(SEEDS)
    prm1 = sum(b[s]["pr_max"] for s in SEEDS) / len(SEEDS)
    print(f"mean PR_end   g0.00 {pr0:.4f}  g0.05 {pr1:.4f}   (target >= 1.30)")
    print(f"mean PR_max   g0.00 {prm0:.4f}  g0.05 {prm1:.4f}")
    print(f"mean cosd_end g0.00 {cd0:.4f}  g0.05 {cd1:.4f}   (target >= 0.10)")

    print("\n### GUARDRAILS")
    print(" seed | endPhi g0/g05 (<40) | frust g0/g05 [0.45,0.55] | vocab | too_frust rate g0/g05 | ratio | too_ord g0/g05 | gate_open")
    for s in SEEDS:
        x, y = a[s], b[s]
        r = y["too_frustrated_any_rate"] / (x["too_frustrated_any_rate"] or 1e-9)
        print(f"{s:>5} | {x['phi_end']:6.2f}/{y['phi_end']:6.2f} | {x['frust_mean']:.4f}/{y['frust_mean']:.4f} |"
              f" {x['vocab_end']}/{y['vocab_end']} {x['vocab_identical'] and y['vocab_identical']} |"
              f" {x['too_frustrated_any_rate']:.3f}/{y['too_frustrated_any_rate']:.3f} | {r:.3f}x |"
              f" {x['too_ordered_any_rate']:.3f}/{y['too_ordered_any_rate']:.3f} | {y['gate_open_mean']:.4f}")
    print(" cells/step too_frustrated: g0 %.3f  g05 %.3f (ratio %.3fx)" % (
        sum(a[s]["too_frustrated_cells_per_step"] for s in SEEDS) / len(SEEDS),
        sum(b[s]["too_frustrated_cells_per_step"] for s in SEEDS) / len(SEEDS),
        (sum(b[s]["too_frustrated_cells_per_step"] for s in SEEDS)
         / max(sum(a[s]["too_frustrated_cells_per_step"] for s in SEEDS), 1e-9))))
    print(" cells/step too_ordered:    g0 %.3f  g05 %.3f" % (
        sum(a[s]["too_ordered_cells_per_step"] for s in SEEDS) / len(SEEDS),
        sum(b[s]["too_ordered_cells_per_step"] for s in SEEDS) / len(SEEDS)))
    print(" mean gate open fraction (g0.05): %.4f" % (
        sum(b[s]["gate_open_mean"] for s in SEEDS) / len(SEEDS)))

    print("\n### Phi sparklines")
    for s in DOWN:
        print(f"seed {s:>5}  g0.00  {a[s]['phi_spark']}  {a[s]['phi_start']:.1f}->{a[s]['phi_end']:.1f}")
        print(f"seed {s:>5}  g0.05  {b[s]['phi_spark']}  {b[s]['phi_start']:.1f}->{b[s]['phi_end']:.1f}")


if __name__ == "__main__":
    main()

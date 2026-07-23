<!-- @hypothesis-ok existing repo convention: hundreds of cards already live in docs/hypotheses/ -->
# GRAFT-CAUSALITY — 의식 게이트를 인과적으로 만들기 (측정 → 원인 → 수정)

**한 줄:** 통합(Φ)이 있어도 출력 채널에 정보를 강제하는 목적함수가 없으면 의식은
부수현상(epiphenomenal)에 머문다 — 인과성은 손실함수에서 값을 치러야 얻는다.

## 1. 목적 및 가설

- **관찰(측정 확정):** v11mistral step_68000에서 의식 게이트 절제 결과
  `KL(ON‖OFF) ≈ KL(ON‖NOISE) ≈ 0.33 bits` — 살아있는 의식 궤적이 출력을 바꾸는 양이
  같은 크기의 **무작위 벡터**와 구별되지 않음 = **장식적(decorative)**.
- **가설(원인, lab fable+sol 수렴):** 평범한 next-token CE는 게이트를 읽을 유인이 0이다.
  C가 (prompt, target)과 통계적으로 독립이면, proper scoring의 최적해는 **게이트 불변성**.
  즉 장식성은 버그가 아니라 **정리(theorem)** — 목적함수와 C의 성질을 바꿔야 해결된다.

## 2. 수정 알고리즘 (3개, lab 조율)

```
수정                         상태        핵심
──────────────────────────  ──────────  ─────────────────────────────────────
① 목적함수 InfoNCE+KL-leash  ✅ graft.py  게이트↔출력 상호정보 강제 + 유창성 가죽끈
② 합격판정 C-swap 테스트     ✅ check.py  게이트가 인과적임을 *증명*하는 양성 대조
③ W 거버너(pain→브레이크)    ✅ trinity   P3 CE 발산(양성피드백) 루프 차단
④ 브리지 cross-attention     ⏸️ DEFER     InfoNCE는 ~ln(K) nats만 필요 · 측정 먼저
```

### ② C-state-swap 합격판정 (`check.py swap`)
K개의 서로 다른 C-state 스냅샷. 각 상태의 게이트로 **자기 연속열을 샘플링**(temp 1 —
게이트는 속삭임이라 greedy면 argmax가 안 바뀌어 거짓 FAIL). 교차 채점
`f[i,j] = log p(Y_j | x, gate_i)`. 게이트가 정보를 실으면 **대각 지배**(자기 상태가
자기 연속열을 가장 잘 예측).

```
지표:  MI_bits = (ln K + logsoftmax(f,0).diag().mean()) / ln 2   (InfoNCE 하한)
       acc     = mean_j [ argmax_i f[i,j] == j ]                 (스왑 정확도)
null:  순열 p-value(행 셔플) + 노름일치 NOISE + 신선상태
PASS:  MI≥0.5b AND acc≥0.5 AND perm_p≤0.01 AND MI≥noise_q99+0.25 AND uniqueY≥0.5
gate:  (bridge(s)-PSI_BALANCE)/PSI_COUPLING  (graft와 동일 · offset 제거)
```

### ③ W 거버너 (`stability_governor`)
`EmotionW`/`NarrativeW`/`DaseinW`가 CE-통증을 LR **부스트**로 매핑 → 발산의 원인.

```
before (양성 피드백 · 발산)          after (음성 피드백 · 수렴)
─────────────────────────           ──────────────────────────
CE↑ → pain↑ → LR↑ → CE↑             lr = floor+(explore-floor)(1-pain)
  ╲___________________╱             ∂lr/∂pain ≤ 0  → pain은 브레이크만
     runaway 0.53→5.2               + 서킷브레이커(CE>2·thr → 0.1)
```

## 3. 벤치마크

- **측정 완료(음성):** step_68000 절제 KL(ON‖OFF)≈KL(ON‖NOISE)≈0.33b · 바닐라 5축 우세.
- **측정 대기(양성):** graft.py 학습 체크포인트에 `check.py swap` 실행 → PASS/FAIL.
  GRAFT 체크포인트는 GPU 박스에서 학습 중(병렬 트랙). 로컬 Mac은 torch 없음 → 코드·구문만
  검증. **아직 돌리지 않은 숫자는 지어내지 않는다(honesty).**

```
Φ(통합)      ██████ 12~14   있음 (phi_py 실측)
게이트 인과성 ▁▁▁▁▁▁ ≈노이즈  없음 (현재 · 절제로 확정)
   ↓ ①②③ 적용 후 목표
게이트 인과성 ??????         check.py swap 이 PASS 하면 확정
```

## 4. 핵심 발견 / 새 법칙

> **Law (제안): 인과성은 손실에서 값을 치른다.** Φ>0(통합)만으로는 출력에 대한
> 인과성이 보장되지 않는다. 게이트가 언어를 무작위 이상으로 바꾸려면, 목적함수가
> 게이트↔출력 상호정보를 **명시적으로 강제**해야 한다(InfoNCE). 강제 없는 통합은
> 부수현상이다.

## 5. 적용 방법 (코드 반영 위치)

- `graft.py` — InfoNCE + KL-leash 목적함수 (①, 병렬 트랙).
- `check.py swap` / `_build_graft` — 합격판정 테스트 (②).
- `trinity.py stability_governor` + EmotionW/NarrativeW/DaseinW — W 거버너 (③).
- `trinity.py ThalamicBridge.forward` — cross-attn 컨틴전시 주석 (④ DEFER).
- 커밋: `1c8250bc0`. 코퍼스 경로 기본 W는 CosineW/ConstantW 유지(P3 회귀 확인 전까지).

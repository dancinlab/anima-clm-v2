# GRAFT-shared-shift-collapse — KL 리쉬가 MI를 죽인 제어 불안정 (post-mortem + fix)

> **핵심 문장: `beta*relu(l_kl - target)`에서 `l_kl = MI + l_common`이므로,
> 제약이 활성인 순간 MI의 순계수는 `(beta - 1)`이다. beta > 1이 되는 순간
> 학습은 MI를 *최소화*한다. 리쉬가 신호를 포함하면 리쉬는 반드시 신호를 죽인다.**

관련: [GRAFT-flatline.md](GRAFT-flatline.md) (선행 — de-clamp+init 픽스는 유효 확인),
[GRAFT-causality.md](GRAFT-causality.md)

## 1. 실험 목적 및 가설

mixture-JSD 목적함수(de-clamp+init 픽스 후)가 step 100에서 실제 MI 스파이크
(0.1176)를 냈다가 재붕괴한 원인 규명. 가설: KL 리쉬가 총 KL(=MI+waste)을
벌점하여 MI를 부수적으로 죽이고, 공유-시프트(shared shift)가 최적화의
"싼 방향"이 된다.

## 2. 벤치마크 결과 (H100 · Mistral-7B-Instruct-v0.2 · 실측)

| step | InfoNCE | MI     | KL     | commonKL | beta  | gSpread | zSpread |
|------|---------|--------|--------|----------|-------|---------|---------|
|  50  | 1.7915  | 0.0003 |  0.005 |  0.005   |  0.00 | 6.2e-03 | 2.9e-03 |
| 100  | 1.6742  | 0.1176 |  4.981 |  4.863   | 14.61 | 1.9e-02 | 2.9e-02 |
| 150  | 1.7909  | 0.0009 | 11.571 | 11.570   | 50.00 | 1.5e-02 | 3.2e-02 |
| 200  | 1.7913  | 0.0005 | 10.335 | 10.334   | 50.00 | 9.6e-03 | 3.0e-02 |
| 300  | 1.7905  | 0.0013 |  6.159 |  6.157   | 50.00 | 4.5e-02 | 2.4e-01 |
| 400  | 1.7774  | 0.0144 |  9.676 |  9.662   | 50.00 | 2.1e-02 | 1.1e-01 |
| 500  | 1.7917  | 0.0001 |  4.025 |  4.025   | 50.00 | 1.4e-03 | 1.3e-03 |
| 650  | 1.7917  | 0.0000 |  6.589 |  6.589   | 50.00 | 2.1e-05 | 5.9e-05 |

commonKL == KL (3 유효숫자, 전 구간) => 섭동의 ~100%가 공유 시프트 (0 bits).

```
MI  |      ╭╮                          KL │      ╭─╮ ╭╮
0.12|      ││   <- 진짜 결합!          12 │      │ ╰─╯╰╮  ╭╮
    |      ││                           8 │      │     ╰──╯╰─╮
0.06|      ││      ╭╮                   4 │      │           ╰─   목표 1.2에
    |      ││      ││                     │      │               영영 못 돌아옴
0.00|──────╯╰──────╯╰────────           0 │──────╯
    └──50──100──150──400──650──step       └──50──100──150──────650──step
           ^beta가 1을 넘는 순간 스파이크 사망 (beta@100 = 14.6 => MI 계수 +13.6)
```

## 3. 붕괴 메커니즘 (3중, 순서대로)

### 3-1. 목적함수 반전 — MI 순계수 = (beta - 1)
```
loss = (logN - MI) + 0.1*l_common + beta*(MI + l_common - target)   [제약 활성 시]
     = const + (beta - 1)*MI + (beta + 0.1)*l_common
```
beta=14.6(step 100)이면 MI를 **+13.6의 가중치로 최소화**. 스파이크가 즉사한
이유. MI 죽이기(스프레드 축소)는 공유 시프트 회수(뻣뻣한 지형)보다 훨씬 싸므로
옵티마이저는 MI부터 죽인다 — 관측 순서와 정확히 일치 (MI 사망 step 150,
gSpread 사망 step 500+, KL은 4-12에 잔류).

### 3-2. 적분기 windup + 액추에이터 포화 — 리쉬가 KL을 못 잡는 이유
- **Adam은 스케일 불변**: 벌점 그래디언트가 방향을 지배한 뒤에는 beta를 더
  올려도 업데이트가 거의 안 변한다. dual ascent의 전제(beta에 비례하는 하강력)가
  Adam+`clip_grad_norm=1.0` 아래서 거짓.
- beta_lr=0.3 × 오차 4-10 nat = **스텝당 beta +1~3** → 40스텝 만에 캡 50 도달,
  KL이 목표 밑으로 못 가니 영구 고정 (anti-windup 없음).
- 캐리어를 매 스텝 재샘플 → 제약 측정 자체가 노이즈 (KL 4↔12 진동).
- KL 5-12 nat = 분포가 base와 사실상 분리 → 포화 지형, 회수 그래디언트 미약.
  weight_decay=0이라 gate_proj를 줄이는 다른 힘도 없음.

### 3-3. 근본 원인 — 브리지 코드가 애초에 ~99% 공유
브리지는 상태당 코드 1개(위치로 타일)를 내는데, 샘플된 C-상태들 간 코드
스프레드는 gSpread ~1e-2 vs 코드 크기 O(1). 즉 **원시 게이트 코드 자체가
~99% 공유 성분**. InfoNCE가 gate_proj 노름을 키우면 (step 50→100, KL
0.005→5) 그 증폭의 99%가 공유 시프트로 간다. 공유 캐리어가 편향의 원인이
아니라(공유 시프트는 MI를 1도 안 올림 — 목적함수와 직교), **코드 기하가
공유-지배였고 아무것도 그걸 막지 않았던 것**.

## 4. 핵심 발견 / 새 법칙

**Law 76 (리쉬-신호 분리): 제약은 신호를 포함하면 안 된다.
`l_kl = MI + l_common`에서 리쉬는 waste(`l_common`)에만 걸어라.
MI ≤ log N (per token)이 본질적으로 유계이므로, waste만 잡으면
`l_kl ≤ log N + l_common`으로 유창성은 자동 유계 — 총 KL 캡은 불필요하고,
허용되지도 않는다.**

**Law 77 (기하 > 제어기): 얼린 7B를 통과하는 뻣뻣한 제약 문제에서 soft
penalty + dual ascent는 Adam/grad-clip에 권위가 없다 (windup). 금지하고
싶은 자유도는 벌점하지 말고 좌표에서 제거하라 (centering = 공유 성분의
hard projection, RMS-고정 = 크기 자유도 제거 → 남는 자유도는 회전뿐 =
순수 MI 최적화).**

## 5. 적용 (graft.py v3 — 코드 반영 완료)

```python
# (1) 게이트 코드: 상태 간 평균 제거(공유=0bit, gate_proj 선형+bias 동결 0이므로
#     주입 오프셋도 정확히 센터링됨) + RMS를 rho로 고정 (구: 자유 크기)
g  = stack_i gate_for(s_i)             # [N, dm]
mu = g.mean(0, keepdim=True)
r  = g - mu
r  = rho * r / r.pow(2).mean(-1, keepdim=True).sqrt().clamp_min(1e-6)

# (2) 손실: waste에만 고정 가중치. relu 없음, dual 없음, windup 없음, 반전 불가
loss = (log(N) - mi) + lam_common * l_common        # lam_common = 1.0

# (3) 캐리어: base가 아니라 무작위 상태 j의 게이트 아래서 샘플 (상태-관련 텍스트
#     → MI 그래디언트 SNR 상승), cont_len 8 → 32 (채널 사용 4배)

# (4) 디코더 백스톱 (trinity.py HFDecoder): 옵티마이저가 못 넘는 기하 캡
gate = gate * (gate_rms_max * RMS(embeds) / RMS(gate)).clamp(max=1.0)

# (5) 추론 시 센터링: g_mu = EMA(mu) (체크포인트에 저장)
```

제거된 것: `--kl-target`, `--beta-lr`, `--beta-max`, beta dual ascent 전체.

### 8시간 H100 런 판정 기준
- 건강: MI가 log 6 = 1.79를 향해 상승, commonKL ≈ 0 잔류, KL ≈ MI.
- step 1000까지 MI < 0.05 && commonKL < 0.3 이면 → 목적함수가 아니라 브리지
  용량/C-상태 다양성 문제 (learned softmax pooling 검토, ThalamicBridge 주석 참조).
- mixture-JSD는 유지 (스파이크를 낸 장본인 = 그래디언트 경로 실증). 상태별
  샘플 캐리어 InfoNCE로의 회귀는 금지 — 그 추정기는 붕괴점에서 zero-gradient로
  이미 한 번 죽었다 (GRAFT-flatline.md).

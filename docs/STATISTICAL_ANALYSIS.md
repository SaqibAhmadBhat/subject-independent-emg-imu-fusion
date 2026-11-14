# Statistical Methodology & Formal Inferential Suite

This document defines the mathematical foundations, hypothesis tests, effect sizes, and sensitivity analyses used in the V2 study.

---

## 1. Unit of Inference & Independence

All inferential claims in V2 rest on $N = 9$ paired participant observations:
$$d_k = \bar{A}_{\text{RM}, k} - \bar{A}_{\text{NR}, k}, \quad k \in \{1, \dots, 9\}$$
where $\bar{A}_{\text{RM}, k}$ and $\bar{A}_{\text{NR}, k}$ are the mean classification accuracies for participant $k$ averaged across the 5 random seeds under rate-matched (RM) and native-rate (NR) conditions.

> **Methodological Caveat on Independence:**
> In leave-one-participant-out (LOSO) cross-validation, any two folds share 7 of their 8 training participants. Therefore, the nine paired differences are not strictly independent, and no unbiased estimator of the variance of cross-validation exists (Bengio and Grandvalet, 2004). Inferential $p$-values and confidence intervals reflect variation across the nine test participants and should be interpreted as approximate indicators of evidence.

---

## 2. Protocol-Specified Primary Analysis

### A. Wilcoxon Signed-Rank Test (Two-Sided)
The paired differences $d_k$ are ranked by absolute magnitude $|d_k|$:
- Ranks:
  - P2 ($|d|=0.669$ pp) $\rightarrow$ Rank 1 ($+$)
  - P4 ($|d|=1.121$ pp) $\rightarrow$ Rank 2 ($+$)
  - P5 ($|d|=2.466$ pp) $\rightarrow$ Rank 3 ($+$)
  - P9 ($|d|=3.142$ pp) $\rightarrow$ Rank 4 ($+$)
  - P1 ($|d|=3.153$ pp) $\rightarrow$ Rank 5 ($-$)
  - P3 ($|d|=5.569$ pp) $\rightarrow$ Rank 6 ($+$)
  - P6 ($|d|=6.371$ pp) $\rightarrow$ Rank 7 ($+$)
  - P8 ($|d|=8.348$ pp) $\rightarrow$ Rank 8 ($+$)
  - P7 ($|d|=9.939$ pp) $\rightarrow$ Rank 9 ($+$)
- Test Statistic:
  $$W^+ = 1 + 2 + 3 + 4 + 6 + 7 + 8 + 9 = 40, \quad W^- = 5$$
  $$W = \min(W^+, W^-) = \mathbf{5}$$
- Exact $p$-Value:
  Under the null hypothesis, all $2^9 = 512$ rank sign assignments are equally likely. Exactly 10 assignments yield $W \le 5$:
  $$p_{\text{exact}} = 2 \times \frac{10}{512} = \mathbf{0.0390625} \approx 0.039$$

### B. Matched-Pairs Rank-Biserial Correlation ($r$)
Effect size is measured using Kerby's rank-biserial correlation:
$$r = \frac{W^+ - W^-}{W^+ + W^-} = \frac{40 - 5}{45} = \mathbf{+0.778}$$
indicating that $88.9\%$ of the rank sum favors rate matching.

### C. Percentile Bootstrap Confidence Interval
With $B = 10{,}000$ resamples of the 9 participant paired differences (`numpy.random.default_rng(42)`):
$$\text{CI}_{95\%} = \mathbf{[1.2713, 6.3548] \text{ pp}} \approx [1.3, 6.4] \text{ pp}$$

---

## 3. Post Hoc Sensitivity & Robustness Suite

These analyses were introduced post hoc to assess inferential fragility against test choice, seed aggregation, and individual participants.

### A. Exact Sign-Flip Permutation Test
Under the sharp null hypothesis that each participant's difference is symmetric around zero, we evaluate all $2^9 = 512$ sign flips $s \in \{-1, +1\}^9$:
$$\bar{d}(s) = \frac{1}{9} \sum_{k=1}^9 s_k d_k$$
Exactly 16 permutations satisfy $|\bar{d}(s)| \ge |\bar{d}_{\text{obs}}| = 3.8303$ pp:
$$p_{\text{perm}} = \frac{16}{512} = \mathbf{0.03125} \approx 0.031$$
This result demonstrates that the effect direction is robust across non-parametric test formulations.

### B. Two-Stage Hierarchical Bootstrap
To incorporate nested variability (participants as primary cluster, random seeds as secondary cluster), we resample 9 participants with replacement, then for each chosen participant resample 5 seeds with replacement ($B = 10{,}000$ iterations):
$$\text{CI}_{95\%}^{\text{two-stage}} = \mathbf{[1.0671, 6.6489] \text{ pp}} \approx [1.07, 6.65] \text{ pp}$$
Accounting for seed-level stochastic training variation widens the confidence interval slightly but confirms that zero remains strictly excluded.

### C. Leave-One-Seed-Out Sensitivity
Recomputing participant means and Wilcoxon tests by omitting each seed in turn:
- Omit Seed 42: Mean difference $+4.01$ pp, $W = 2$, $p = \mathbf{0.012}$
- Omit Seed 123: Mean difference $+4.07$ pp, $W = 5$, $p = \mathbf{0.039}$
- Omit Seed 2024: Mean difference $+4.47$ pp, $W = 3$, $p = \mathbf{0.020}$
- Omit Seed 3407: Mean difference $+3.11$ pp, $W = 6$, $p = \mathbf{0.055}$
- Omit Seed 7777: Mean difference $+3.49$ pp, $W = 5$, $p = \mathbf{0.039}$
In all 5 subsets, rate matching is ahead in 8 of 9 participants. Omitting seed 3407 shifts $p$ just above the 0.05 boundary ($0.055$), reflecting the small sample size ($N = 9$).

### D. Leave-One-Participant-Out Sensitivity
Recomputing the Wilcoxon test by omitting each participant in turn ($n = 8$):
- Omitting P1 (the only negative participant): $p = \mathbf{0.0078}$
- Omitting any of P2–P9: $p$ ranges between **$0.0547$ and $0.0781$**
This demonstrates that claiming $p < 0.05$ depends strictly on retaining the full cohort ($N = 9$).

---

## 4. Variance Components Analysis

Using a one-way random effects ANOVA on the 45 seed-level paired differences $D_{i, k}$ ($i \in \{1..5\}$ seeds, $k \in \{1..9\}$ participants):
- Mean square between participants: $\text{MS}_b = 5 \cdot \text{Var}_k(\bar{D}_{\cdot, k}) = 84.77$
- Mean square within participants (between seeds): $\text{MS}_w = \frac{1}{9}\sum_{k} \text{Var}_i(D_{i, k}) = 17.91$
- Estimated variance between participants: $\sigma_b^2 = \max(0, (\text{MS}_b - \text{MS}_w)/5) = 13.37 \rightarrow \sigma_b = \mathbf{3.66 \text{ pp}}$
- Estimated standard deviation within participants (seed noise): $\sigma_w = \sqrt{\text{MS}_w} = \mathbf{4.23 \text{ pp}}$
- Intraclass Correlation Coefficient (ICC):
  $$\text{ICC} = \frac{\sigma_b^2}{\sigma_b^2 + \sigma_w^2} = \mathbf{0.43}$$

**Scientific Finding:** Seed-to-seed stochastic variation ($4.23$ pp) is larger than genuine between-participant variation ($3.66$ pp). Evaluating only a single random seed produces noisy, unreliable comparisons. Averaging 5 seeds reduces the seed-noise standard error of a participant's mean to $4.23 / \sqrt{5} = \mathbf{1.89 \text{ pp}}$.

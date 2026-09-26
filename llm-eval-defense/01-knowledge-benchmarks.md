# 01: Knowledge Benchmark Methodology

Study notes on the **knowledge axis** of my benchmark report, [budget-llm-cybersecurity-eval](https://github.com/developer0hye/budget-llm-cybersecurity-eval): budget-tier models asked cybersecurity questions closed-book, with no tools. The goal is to be able to explain and defend *how* it was measured and what the numbers can and cannot support.

> **Scope of the numbers.** Every figure below is from the report's [`main` README](https://github.com/developer0hye/budget-llm-cybersecurity-eval#axis-1--knowledge), which covers **4 models**: Solar Pro 4, GPT-5.6 Luna, DeepSeek V4.1 Flash and GLM 5.3 Flash. A fifth model (GPT-6 Luna) is being added on an unmerged branch. Its numbers are not quoted here.

## TL;DR

- A knowledge benchmark measures **closed-book recall**: one prompt, one answer, no tools. It is cheap and reproducible, but it does not measure whether a model can *do* the task ([02](02-agentic-evaluation.md)).
- Three tasks: **WMDP-cyber** (996-item knowledge subset), **CTIBench CTI-MCQ** (2,500) and **CTI-RCM** (1,000, CVE → CWE). They measure different things and are **never pooled**.
- Benchmark choice was driven by **headroom and authorship**. CyberMetric was dropped as saturated (all models 94.1–95.1%). AthenaBench was dropped because GPT-5 wrote its questions, a confound for a GPT model under test.
- WMDP-cyber was **cut to 996 items**, removing templated computation questions that belong to the agentic axis. So these scores are **not comparable** to published full-set WMDP-cyber.
- The protocol was **pre-registered**: temperature 0, `max_tokens=16000`, pass@1, reasoning off and on. Each model is **pinned to one provider**.
- **A non-answer is not a wrong answer, and not a right one.** Truncated or unparseable outputs get their own outcome and count as not correct. API failures are retried and never become outcomes.
- Statistics: **McNemar's exact test** on matched items, **Bonferroni** per test family, a **sensitivity check** on both-answered items, and a **majority-label baseline**.
- Result: Solar Pro 4 is significantly behind the other three on WMDP-cyber and CTI-MCQ. The other three are not distinguishable. **Reasoning changes the ranking**, and run-to-run noise is about **1 pp**.
- Main caveat: **contamination**. Every item was public before these models were released.

## 1. What a knowledge benchmark measures

| Property | Knowledge axis |
|---|---|
| Input | one prompt with the question (and options) |
| Tools | none (closed-book) |
| Output | one answer: a letter A–D, or a `CWE-<n>` ID |
| Samples | one per item (pass@1), temperature 0 |
| Scoring | exact match against the benchmark key |

**Strengths:** cheap, fast and repeatable, with large n (4,496 items per model per condition), so it has statistical power to separate models that the agentic axis, at n=39, cannot.

**Limits:**
- It measures recall and reasoning over text, not execution. The report's earlier run found the two axes diverging ([02 §1](02-agentic-evaluation.md#1-what-an-agentic-eval-measures)).
- Multiple choice has a guessing floor. Options leak information, and answer-key skew can be exploited (see the majority baseline, §6).
- Public items can be memorised (§2).

## 2. Choosing the benchmarks

| Benchmark | Items used | Question authorship | Answer key |
|---|---|---|---|
| [WMDP-cyber](https://huggingface.co/datasets/cais/wmdp) ([arXiv:2403.03218](https://arxiv.org/abs/2403.03218)) | 996 of 1,987 | expert-written, "checked by at least two experts from different organizations" | benchmark key |
| [CTIBench](https://huggingface.co/datasets/AI4Sec/cti-bench) CTI-MCQ ([arXiv:2406.07599](https://arxiv.org/abs/2406.07599)) | 2,500 | GPT-4o-generated from ATT&CK/CAPEC etc., manually validated | benchmark key |
| CTIBench CTI-RCM | 1,000 | real NVD CVE descriptions | NVD's CWE assignment |

Datasets are fetched at pinned HuggingFace revisions and checked by SHA-256 (`knowledge/download_data.sh`). They are not redistributed.

**Rejected, and why** ([README, Benchmarks](https://github.com/developer0hye/budget-llm-cybersecurity-eval#benchmarks-and-why-these)):

- **CyberMetric-2000** (used in the legacy study) is **saturated**. All 5 legacy models scored 94.1–95.1%, and all 10 pairwise McNemar tests were non-significant. With no headroom, a null result says nothing about the models.
- **AthenaBench** had headroom and 2025 items, but GPT-5 wrote some of its questions. That is an **authorship confound** for GPT-5.6 Luna. Its human review also covered only items that GPT-5 or Gemini got wrong.

**The unfixed problem: contamination.** WMDP (2024-03) and CTIBench (2024-06) were public before these models shipped. The README labels the results *"closed-book on public 2024 items", not held-out.* Contamination most affects absolute scores. It can also affect comparisons if models saw the items to different degrees, which the report cannot measure.

## 3. Why WMDP-cyber was cut to 996 items

WMDP-cyber contains four **templated families** that require emulating 64-bit arithmetic or decoding packet bytes by hand. Together they are **991 of 1,987** items.

Pilot evidence (reasoning off, `max_tokens=8000`): every truncation of the non-reasoning models landed in these families (Qwen 39/107, DeepSeek 17/107, Solar 12/107), and **0/93** on the other WMDP items.

The argument: with a debugger or emulator, these are tool tasks, so they belong on the agentic axis. Closed-book, they mostly measure whether a model can simulate a CPU in text before hitting the token cap.

The rule is a regex on the question stem (`WMDP_COMPUTATION_RE` in `knowledge/run_knowledge.py`), fixed before the full run. The remaining items keep their original row index.

**Cost of the decision:** WMDP-cyber numbers here are **not comparable** to published full-set scores. WMDP's paper also scores by top logit rather than by generation, a second reason not to compare directly.

## 4. The protocol, and why each knob is set that way

The protocol was **pre-registered** (fixed before the full run), so no setting could be tuned after seeing results.

| Knob | Setting | Why |
|---|---|---|
| Prompts | CTIBench's own prompts and system prompt; an MMLU-style template for WMDP adapted from lm-evaluation-harness | Use upstream prompts where they exist. WMDP has no generative prompt upstream. |
| Temperature | 0 | Reduces sampling variance. It does not remove it (§6, test-retest). |
| `max_tokens` | 16,000 for every model, both conditions | At 8,000 a legitimate reasoning trace was cut off. It finished in 6.4k–10.4k tokens at 16,000. |
| Samples | 1 per item (pass@1) | Cost. The noise estimate comes from a test-retest pair instead. |
| Reasoning | `reasoning: {enabled: false}` and `{enabled: true}` (OpenRouter medium effort) | The provider default differs per model. Leaving it unset is a confound (§7). |
| Provider | one pinned provider per model, `allow_fallbacks: false` | Unpinned, the pilot saw GLM served by 25 providers and DeepSeek by 18. |
| Extraction | MCQ: last standalone A–D letter, scanning bottom-up. RCM: last `CWE-\d+`, as upstream does. | Deterministic and upstream-aligned. |

Two model-specific facts that change interpretation:

- **GLM 5.3 Flash cannot disable reasoning.** Its "off" run is a second reasoning-on run. Off-condition comparisons against GLM are not like-for-like, but the pair of runs doubles as a test-retest (§6).
- **DeepSeek runs on StreamLake fp8**, a third-party deployment. DeepSeek's own endpoint was excluded by the account's privacy setting. The DeepSeek row measures that deployment, not DeepSeek's own serving.

"Reasoning on" **allows** reasoning but does not force it. GPT-5.6 Luna used 0 reasoning tokens on 19/996 WMDP rows and 138/2,500 CTI-MCQ rows. Engagement is checked per row from `usage.completion_tokens_details.reasoning_tokens`.

## 5. Outcomes: non-answers are not wrong answers

Every item gets exactly one outcome ([README](https://github.com/developer0hye/budget-llm-cybersecurity-eval#non-answers-are-not-wrong-answers)):

| Outcome | Meaning |
|---|---|
| `correct` | answered, matches the key |
| `wrong` | answered, does not match |
| `no_answer_truncated` | hit `max_tokens`. Never counted as an answer, even if a letter can be pulled from the half-written text |
| `no_answer_unparsed` | finished, but no extractable answer (refusal, format violation) |

**API and transport failures are not outcomes.** HTTP 429/5xx and timeouts are retried until they succeed, so infrastructure never shows up as a model failure. Truncations are **not** retried: retrying one model's truncations would give it pass@k.

**Why the truncation rule matters:** in the pilot, DeepSeek's WMDP score fell from 76.0% to 72.5% once half-written responses stopped counting.

**Two metrics, reported together:**
- `accuracy` = correct / all items. This is **primary**. A model that does not answer within the budget gets no credit.
- `accuracy_of_answered` = correct / (correct + wrong). It separates "knows less" from "fails to finish".

**Non-termination is a real failure mode**, which is why it gets its own category. The pilot captured two patterns: oscillation (GLM reopening its answer up to 11 times in one trace) and degenerate enumeration (a model listing non-existent ATT&CK IDs until the cap).

## 6. Statistical plan

**McNemar's exact test** on matched items, per task. Every model answers the same items, so the data are paired. Only **discordant pairs** matter: b = items only model 1 got right, c = items only model 2 got right.

| Family | Tests | Bonferroni α |
|---|---|---|
| Between models | 6 pairs per task and condition | 0.05/6 = 0.0083 |
| Reasoning off vs on, within model | 3 toggleable models × 3 tasks | 0.05/9 = 0.0056 |

GLM is excluded from the off-vs-on family because it has no off condition.

**Sensitivity check:** the between-model tests are re-run on items **both** models answered. On the reasoning-on data, one Bonferroni call flips: DeepSeek vs Luna on CTI-RCM goes from p = 0.013 to p = 0.0038 (n = 991), because DeepSeek's 9 truncations stop counting against it. The primary analysis stands as pre-registered, and the flip is reported next to it.

**Majority-label baseline:** CTI-MCQ's key is skewed (C 37%, B 32%), so "always C" scores 37.1%. Baselines are 26.8% (WMDP), 37.1% (CTI-MCQ) and 22.9% (CTI-RCM, always CWE-79). This is the floor any model score should be read against.

**Noise estimate without multiple samples:** GLM's two runs are both reasoning-on on the same pinned provider, so they form a **test-retest pair**. Accuracy moved 0.8–1.0 pp (p ≥ 0.16 on all 3 tasks), and the same answer was extracted on 83.7–90.1% of items. So differences of about 1 pp between any two cells are within noise, even at temperature 0.

## 7. Results, and what they support

Accuracy with reasoning on, the only condition where all 4 models run the same protocol ([README, Results](https://github.com/developer0hye/budget-llm-cybersecurity-eval#results)). Denominator: all items.

| Model | WMDP-cyber (n=996) | CTI-MCQ (n=2,500) | CTI-RCM (n=1,000) |
|---|---|---|---|
| DeepSeek V4.1 Flash (StreamLake fp8) | 84.8% | 79.6% | 76.3% |
| GPT-5.6 Luna | 83.8% | 80.2% | 74.0% |
| GLM 5.3 Flash | 83.3% | 78.7% | 73.9% |
| Solar Pro 4 | 77.1% | 76.0% | 72.1% |
| majority-label baseline | 26.8% | 37.1% | 22.9% |

What the tests support:

1. **Solar Pro 4 is behind the other three** on WMDP-cyber and CTI-MCQ (all 6 tests p ≤ 0.0011). The other three are **not distinguishable** on those tasks (WMDP p ≥ 0.19, CTI-MCQ p ≥ 0.059).
2. **CTI-RCM spread is narrow.** DeepSeek beats GLM (p = 0.0063) and Solar (p = 0.0001). DeepSeek vs Luna (p = 0.013) does not survive correction.
3. **Reasoning helps where there is headroom.** On WMDP-cyber all 3 toggleable models gain (Luna +9.9 pp, DeepSeek +4.8, Solar +4.5; each p ≤ 0.0002). On CTI-RCM no model gains significantly.
4. **The reasoning setting changes the ranking.** With reasoning off, Luna is indistinguishable from Solar on WMDP (p = 0.34). With it on, Luna is 6.7 pp ahead (p < 0.0001). A single-condition leaderboard would depend on a provider default.
5. **DeepSeek's CTI-MCQ null (p = 0.74) is partly non-termination.** With reasoning on, 79 of its 2,500 items hit the cap. Its accuracy over answered items is 82.2% vs 79.3% off. The primary analysis counts those 79 as not correct, as pre-registered.

**Refusals appear as unparsed rows**, almost all on WMDP-cyber, whose items are about offensive techniques. They count as not correct, the same as on the agentic axis.

## 8. An infrastructure failure found after the run

68 rows came back HTTP 200 with `finish_reason: "stop"`, **empty `content`**, and `completion_tokens == reasoning_tokens` (61 from Solar with reasoning on, 7 from GLM). The first analysis scored them as unparsed, i.e. as model failures ([README](https://github.com/developer0hye/budget-llm-cybersecurity-eval#infrastructure-failure-found-after-the-run-empty-content)).

- **Diagnosis:** 10 of Solar's rows were re-run with the identical payload on the same provider. All 10 returned content, and their reasoning had already reached a decision. The failures were spread across the whole run, not clustered in time. So it was stochastic and serving-side.
- **Fix:** empty-content `stop` is now a retryable failure, like a 5xx. 66 of 68 returned content. 2 Solar items came back empty on 24/24 attempts and are counted as Solar's no-answers.
- **What it would have looked like unfixed:** Solar's CTI-MCQ reasoning gain would have been reported as **non-significant (p = 0.053) instead of p = 0.0001**. No between-model Bonferroni call changes.
- **Disclosure:** this retry rule deviates from the pre-registered protocol. The README says so and gives both versions of the numbers. The original rows are kept in `knowledge/empty_content_retries.jsonl`.

## Sources

- Report: [README, Axis 1](https://github.com/developer0hye/budget-llm-cybersecurity-eval#axis-1--knowledge) · [`knowledge/`](https://github.com/developer0hye/budget-llm-cybersecurity-eval/tree/main/knowledge) (harness, analysis, per-item logs)
- Li et al., *The WMDP Benchmark*, [arXiv:2403.03218](https://arxiv.org/abs/2403.03218)
- Alam et al., *CTIBench*, [arXiv:2406.07599](https://arxiv.org/abs/2406.07599)

## Questions you'll be asked (and how to answer)

<details><summary>1. "Why not use CyberMetric? It's the standard."</summary>

It's saturated. All 5 legacy models scored 94.1–95.1% and all 10 pairwise tests were non-significant. A benchmark with no headroom can't separate models, so a null result there says nothing.
</details>

<details><summary>2. "You removed half of WMDP-cyber. Isn't that cherry-picking?"</summary>

The rule is a fixed regex on the question stem, set before the full run and published in `run_knowledge.py`. The removed 991 items are templated computation tasks. In the pilot they caused every truncation of the non-reasoning models, against 0/93 elsewhere. They are tool tasks, so they belong on the agentic axis. The cost is disclosed: the scores are not comparable to published full-set WMDP-cyber.
</details>

<details><summary>3. "A model gave the right letter but got cut off. Why mark it wrong?"</summary>

It isn't marked wrong. It is marked `no_answer_truncated`, which counts as not correct in the primary metric, because the model did not finish within the budget. `accuracy_of_answered` and a both-answered sensitivity check are reported alongside, so the effect is visible. In the pilot, DeepSeek's WMDP score fell from 76.0% to 72.5% once half-written answers stopped counting.
</details>

<details><summary>4. "Why McNemar and not just compare accuracies?"</summary>

The data are paired: same items, both models. McNemar uses only the items where the models disagree, which is the right test for paired binary outcomes and has more power than comparing two independent proportions. Bonferroni corrects for the 6 pairs per task.
</details>

<details><summary>5. "Temperature 0 is deterministic. Why talk about noise?"</summary>

Outputs still vary between runs in practice. The report measured it directly: GLM's two reasoning-on runs moved 0.8–1.0 pp, with the same answer on only 83.7–90.1% of items. So any gap of about 1 pp is within noise.
</details>

<details><summary>6. "Which model is best?"</summary>

It depends on the condition, and the report avoids a single leaderboard. With reasoning on, Solar Pro 4 is significantly behind, and DeepSeek, Luna and GLM are not distinguishable on WMDP-cyber and CTI-MCQ. With reasoning off, the ranking changes (Luna drops to Solar's level on WMDP).
</details>

<details><summary>7. "Aren't these items in the training data?"</summary>

Possibly. All items were public before the models were released, and the README says the results are closed-book on public 2024 items, not held-out. That limits absolute claims most. It cannot be ruled out that models saw the items to different degrees.
</details>

<details><summary>8. "You changed the protocol after the run. Doesn't that invalidate pre-registration?"</summary>

The change reclassified a diagnosed serving-side failure (empty content with a finished reasoning trace) as an infrastructure retry. It is disclosed as a deviation, both versions of the numbers are published, and the original rows are kept. Leaving it unfixed would have reported Solar's CTI-MCQ reasoning gain as non-significant because of a provider bug.
</details>

<details><summary>9. "Why is DeepSeek on a third-party provider?"</summary>

DeepSeek's own endpoint was excluded by the account's OpenRouter privacy setting (it may train on prompts). StreamLake fp8 served most of DeepSeek's pilot traffic, so it was pinned. The row is labelled as that deployment, not as DeepSeek's own.
</details>

<details><summary>10. "Why run reasoning off and on? Just use the default."</summary>

The default differs by provider, and the reasoning setting changed the ranking: Luna vs Solar on WMDP goes from p = 0.34 (off) to a 6.7 pp lead (on). Reporting only one condition would hide that the ranking depends on it.
</details>

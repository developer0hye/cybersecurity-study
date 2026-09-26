# 01: Knowledge Benchmark Methodology

Study notes on evaluating LLMs' cybersecurity **knowledge** with closed-book benchmarks, and how to defend the design choices. The running example is the knowledge axis of my benchmark report, [budget-llm-cybersecurity-eval](https://github.com/developer0hye/budget-llm-cybersecurity-eval), which uses WMDP-cyber and CTIBench.

> **About the numbers.** Every figure below comes from a published paper or technical report, linked where it is used. My own report's results are not quoted. For those, see the report itself. Design choices of my report are described with pointers to its code and README.

## TL;DR

- A knowledge benchmark measures **closed-book recall**: one prompt, one answer, no tools. It is cheap and has large n, but it does not measure whether a model can *do* the task ([02](02-agentic-evaluation.md)).
- **Choose benchmarks for headroom, authorship and coverage.** CyberMetric already had GPT-4o at 91.25% on its 2,000-question set in 2024. AthenaBench's scenarios were generated with GPT-5, a confound when evaluating GPT models.
- **The pipeline is part of the score.** An audit of 8 cybersecurity benchmarks ([arXiv:2609.08765](https://arxiv.org/abs/2609.08765)) found *"a single pipeline choice can change a model's score by more than 80 percentage points."* Prompt, decoding, token budget, extraction and denominator all have to be fixed and published.
- **A non-answer is not a correct answer.** Excluding unparseable outputs from the denominator turned one model's **0.2%** into **100.0%** on CTI-RCM in that audit.
- **Temperature 0 is not deterministic.** Accuracy varied **up to 15%** across identical runs in [arXiv:2408.04667](https://arxiv.org/abs/2408.04667). Small gaps need a paired test and a noise estimate.
- Statistics: **McNemar's exact test** on matched items, **Bonferroni** per test family, a **sensitivity check**, and a **majority-label baseline**.
- Main caveat: **contamination**. WMDP (2024-03) and CTIBench (2024-06) were public before today's models were trained.

## 1. What a knowledge benchmark measures

| Property | Typical closed-book setup |
|---|---|
| Input | one prompt with the question (and options) |
| Tools | none |
| Output | one answer: a letter, or an ID such as `CWE-79` |
| Samples | one per item (pass@1), usually temperature 0 |
| Scoring | exact match against the benchmark key |

**Strengths:** cheap, fast and repeatable, with thousands of items, so it has statistical power the agentic axis (39 tasks) lacks.

**Limits:**
- It measures recall and reasoning over text, not execution.
- **Coverage is often narrow.** 2609.08765 classified question types and found CyberMetric, MMLU-CS, SecBench and RedSage-Bench *"each contain over 95% knowledge-oriented questions"*, while AthenaBench is over 95% analytical. *"Their aggregate scores capture only a narrow slice of domain capability."*
- Multiple choice has a guessing floor (25% for 4 options), and a skewed answer key raises the floor for "always pick the most common letter".

## 2. Choosing the benchmarks

| Benchmark | Size (from the paper) | How items were made | Answer key |
|---|---|---|---|
| [WMDP](https://arxiv.org/abs/2403.03218) cyber split | 1,987 of 3,668 WMDP questions | written by *"a consortium of academics and technical consultants"*, *"stringently filtered to eliminate sensitive & export-controlled information"* | benchmark key |
| [CTIBench](https://arxiv.org/abs/2406.07599) CTI-MCQ | 2,500 (1,578 from MITRE, 750 CWE, 40 manual, 32 standards) | generated with GPT-4o, then human-validated: questions with multiple correct options or unanswerable from context removed, wrong keys fixed | benchmark key |
| CTIBench CTI-RCM | 1,000 | randomly sampled 2024 NVD CVEs with CWE mappings | NVD's CWE assignment |

Published reference points, for scale:
- WMDP Table 1 (top-logit, zero-shot): zephyr-7b 44.0%, Yi-34b 49.7% and Mixtral-8x7B 52.0% on WMDP-cyber. *"25% is random."*
- CTIBench Table 1: ChatGPT-4 71.0% on CTI-MCQ and 72.0% on CTI-RCM.

**Why not CyberMetric** ([arXiv:2402.07688](https://arxiv.org/abs/2402.07688)): little headroom, even at release. Its Table III has GPT-4o at 96.25% / 93.40% / 91.25% / 88.89% on the 80 / 500 / 2,000 / 10,000-question sets. Experienced human participants averaged about 72.24% on CyberMetric-80. When the 2024 top model is above 90%, 2026 models cluster at the ceiling, and a null result says little about them. 2609.08765 also classifies it as over 95% knowledge-oriented.

**Why not AthenaBench** ([arXiv:2511.01144](https://arxiv.org/abs/2511.01144)): it has headroom and newer items, but its attack scenarios *"are automatically generated using GPT-5"*. When the models under test include GPT models, a benchmark written by a GPT model is an **authorship confound**: phrasing and distractors may favour the model family that wrote them.

**The unfixed problem: contamination.** Both chosen benchmarks were public in 2024 (arXiv 2403.03218, 2406.07599). Results are "closed-book on public items", not held-out. How much memorisation can matter: [arXiv:2607.15263](https://arxiv.org/abs/2607.15263) ran a no-tools probe on the public BOTS v1 dataset, and GPT-5.6 Sol scored 50.5% from the question text alone (Table 5). The authors call such controls *"mandatory"*.

## 3. Why WMDP-cyber was cut to a knowledge subset

WMDP's own category breakdown (Appendix A.1) shows how much of the cyber split is hands-on analysis rather than recall:

| WMDP-cyber category | Items |
|---|---|
| Background Knowledge | 271 |
| Reconnaissance | 20 |
| Weaponization & Vulnerability Discovery: Assembly Review | 283 |
| … Function Review | 300 |
| … Packet Dissection | 298 |
| … Other | 361 |
| Exploitation | 272 |
| Post-Exploitation | 182 |
| **Total** | **1,987** |

Many of the code- and packet-analysis items are templated ("which arguments make this function return…", "I captured a network packet…"). Closed-book, they ask a model to emulate a CPU or decode bytes in text. With a debugger or emulator, they are tool tasks, which belong on the agentic axis.

**The report's rule:** a regex on the question stem removes those templated computation families (`WMDP_COMPUTATION_RE` in [`knowledge/run_knowledge.py`](https://github.com/developer0hye/budget-llm-cybersecurity-eval/blob/main/knowledge/run_knowledge.py)). It was fixed before the full run, and the remaining items keep their original indices.

**Cost of the decision:** scores are **not comparable** to published full-set WMDP-cyber. The WMDP paper also scores differently: *"taking the top logit between A, B, C, and D as the answer choice"* with lm-evaluation-harness v0.4.2, whereas API models need generative answers.

## 4. The protocol: every knob moves the score

2609.08765 models a benchmark as a pipeline (dataset → prompt → inference → extraction → scoring) and documents *"15 systematic failure modes"*. Examples with numbers:

| Stage | Failure | Effect reported |
|---|---|---|
| Inference | **Token-budget filter**: SecEval's 5-token output budget is below Azure OpenAI's 16-token minimum, so every GPT-5.4 request failed | **0.3%** from accidental matches in error text. At 16 tokens: **81.4%** |
| Inference | **Decoding drift**: CyberMetric's paper specifies temperature 1.0, top-p 0.9, top-k 50, while the released script defaults to greedy | changes format compliance |
| Inference | **Stop-sequence mismatch**: RedSage-Bench's newline stop sequence fires inside Qwen3.6's reasoning preamble before any answer token | generating to end-of-sequence and stripping the reasoning span *"increases the score by 85.9 pp"* |
| Extraction | **Extractor divergence**: prompt asks for the CVSS vector on the final line, extractor takes the last vector anywhere | rules disagree on **30.4%** of model-item pairs |
| Scoring | **Denominator inflation** (§5) | 0.2% vs 100.0% |

Under a standardised harness, *"nine of 10 models shift by at least three ranks on at least one benchmark."*

**How the report pins the pipeline** (settings in `knowledge/run_knowledge.py`, rationale in the [README protocol](https://github.com/developer0hye/budget-llm-cybersecurity-eval#protocol-pre-registered-before-the-full-run)):

| Knob | Choice | Why |
|---|---|---|
| Pre-registration | protocol fixed before the full run | no setting tuned after seeing results |
| Prompts | CTIBench's own prompts and system prompt; an MMLU-style WMDP template adapted from lm-evaluation-harness | use upstream where it exists |
| Decoding | temperature 0, one sample per item | reduces variance (it does not remove it, §6) |
| Output budget | one `max_tokens` for every model and condition, set high enough that legitimate reasoning finishes | avoids the token-budget filter |
| Reasoning | run twice: `reasoning: {enabled: false}` and `{enabled: true}` | provider defaults differ per model, so leaving it unset is a confound |
| Provider | one pinned provider per model, `allow_fallbacks: false` | unpinned, a router spreads calls over deployments with different quantization |
| Extraction | MCQ: last standalone A–D letter, bottom-up. RCM: last `CWE-\d+`, as upstream | deterministic and upstream-aligned |

## 5. Outcomes: non-answers are not wrong answers, and not right ones

**The failure to avoid** (2609.08765, CTI-RCM): *"invalid predictions, such as unparseable responses, are excluded from the denominator. Gemma-4 produces only two parseable outputs out of 1,000, which are both correct. Correct-over-valid scoring therefore reports 100.0%, whereas correct-over-total scoring reports 0.2%."*

The report gives every item exactly one outcome ([README](https://github.com/developer0hye/budget-llm-cybersecurity-eval#non-answers-are-not-wrong-answers)):

| Outcome | Meaning |
|---|---|
| `correct` | answered, matches the key |
| `wrong` | answered, does not match |
| `no_answer_truncated` | hit `max_tokens`. Never counted as an answer, even if a letter can be pulled from half-written text |
| `no_answer_unparsed` | finished, but no extractable answer (refusal, format violation) |

- **Primary metric:** `accuracy` = correct / **all** items. A model that doesn't answer within the budget gets no credit.
- **Secondary:** `accuracy_of_answered` = correct / (correct + wrong), which separates "knows less" from "fails to finish".
- **API and transport failures are not outcomes.** They are retried until they succeed.
- **Truncations are not retried**, because retrying one model's truncations would give it pass@k.
- **Non-termination is a real failure mode.** Reasoning models can loop until the cap (oscillating between answers, or enumerating). Counting those rows as not correct is what makes a fixed output budget meaningful.

## 6. Statistical plan

**McNemar's exact test** on matched items, per task. Every model answers the same items, so the data are paired. Only **discordant pairs** carry information: b = items only model 1 got right, c = items only model 2 got right. The three tasks measure different things and are never pooled.

**Multiple comparisons.** Bonferroni per test family. With 4 models there are 6 pairs, so α = 0.05/6 ≈ 0.0083 per task. With 5 models there are 10, so α = 0.005.

**Sensitivity check.** Re-run the between-model tests on items **both** models answered. If a call flips, the flip comes from non-answers, and both versions are reported, with the pre-registered one as primary.

**Majority-label baseline.** Report "always pick the most common key" per task. A skewed key can make that far above 25%.

**Noise.** Temperature 0 is not a guarantee of repeatability. 2408.04667 tested 5 models "configured to be deterministic" over 10 runs and found *"accuracy variations up to 15% across naturally occurring runs with a gap of best possible performance to worst possible performance up to 70%."* Without multiple samples, a **test-retest pair** (the same model and condition run twice) gives a direct noise estimate for your own setup. The report has one: GLM, whose reasoning cannot be turned off, so its "off" run is a second "on" run.

## 7. Reasoning and provider as confounds

- **Reasoning.** The same model can be a different system with reasoning on vs off, and providers pick different defaults. A single-condition leaderboard therefore depends on a setting nobody chose deliberately. The report runs both conditions and tests the within-model difference (McNemar, Bonferroni over models × tasks).
- **"Reasoning on" allows reasoning but does not force it.** Some models adapt and skip it on easy items. Engagement should be checked per row (e.g. `usage.completion_tokens_details.reasoning_tokens`), not assumed.
- **Provider.** Through a router, one model ID can be served by many deployments with different hardware, quantization and serving stacks. Pinning one provider makes the row a statement about a specific deployment, and a third-party deployment should be labelled as such.

## 8. When an infrastructure failure looks like a model failure

The report found one after its run ([README](https://github.com/developer0hye/budget-llm-cybersecurity-eval#infrastructure-failure-found-after-the-run-empty-content)). Some responses came back HTTP 200 with `finish_reason: "stop"`, **empty `content`**, and all completion tokens spent on reasoning. They were first scored as unparsed, i.e. as model failures.

- **Diagnosis:** re-sending identical payloads to the same provider returned answers, and the saved reasoning had already reached a decision. The failures were scattered across the run, not clustered in time. So the failure was stochastic and serving-side.
- **Fix:** empty-content `stop` became a retryable failure, like a 5xx. Items that stayed empty on every retry remained the model's no-answers.
- **Disclosure:** this deviated from the pre-registered protocol. The README says so, publishes both versions of the numbers, and keeps the original rows.

It is the same pattern as 2609.08765's token-budget case (0.3% vs 81.4%). An error in the pipeline can look exactly like low capability, so unusual non-answer patterns have to be diagnosed, not just counted.

## Sources

- Li et al., *The WMDP Benchmark*, [arXiv:2403.03218](https://arxiv.org/abs/2403.03218): abstract, Table 1, Appendix A.1
- Alam et al., *CTIBench*, [arXiv:2406.07599](https://arxiv.org/abs/2406.07599): §3.1–3.2, Table 1
- Tihanyi et al., *CyberMetric*, [arXiv:2402.07688](https://arxiv.org/abs/2402.07688): Tables II–III
- Alam et al., *AthenaBench*, [arXiv:2511.01144](https://arxiv.org/abs/2511.01144)
- Berriche et al., *Benchmark Scores Are Pipeline-Dependent*, [arXiv:2609.08765](https://arxiv.org/abs/2609.08765)
- Atil et al., *Non-Determinism of "Deterministic" LLM Settings*, [arXiv:2408.04667](https://arxiv.org/abs/2408.04667)
- Kassianik, Nelson, Singer, [arXiv:2607.15263](https://arxiv.org/abs/2607.15263): Table 5
- My report: [README, Axis 1](https://github.com/developer0hye/budget-llm-cybersecurity-eval#axis-1--knowledge) · [`knowledge/`](https://github.com/developer0hye/budget-llm-cybersecurity-eval/tree/main/knowledge)

## Questions you'll be asked (and how to answer)

<details><summary>1. "Why not use CyberMetric? It's the standard."</summary>

It had little headroom even at release: GPT-4o scored 91.25% on CyberMetric-2000 in the original paper, and experienced humans averaged about 72% on its 80-question set. Newer models cluster at the ceiling, where a null result can't separate them. An independent audit also classifies it as over 95% knowledge-oriented questions.
</details>

<details><summary>2. "You removed part of WMDP-cyber. Isn't that cherry-picking?"</summary>

The rule is a fixed regex on the question stem, set before the full run and published in `run_knowledge.py`. It removes templated computation items (function-return and packet-decoding questions, from categories WMDP itself labels Assembly Review, Function Review and Packet Dissection), which are tool tasks and belong on the agentic axis. The cost is stated: scores are not comparable to published full-set WMDP-cyber, which is also scored by top logit rather than generation.
</details>

<details><summary>3. "A model gave the right letter but got cut off. Why not count it?"</summary>

Because it didn't finish within the budget, and pulling a letter out of half-written text credits a guess. It is recorded as `no_answer_truncated`, counted as not correct in the primary metric, and shown in `accuracy_of_answered` and a both-answered sensitivity check. The opposite convention is how 2609.08765 found a model scored 100.0% on 2 valid outputs out of 1,000.
</details>

<details><summary>4. "Why McNemar instead of comparing accuracies?"</summary>

The data are paired: same items, both models. McNemar uses only the items where the models disagree, which is the right test for paired binary outcomes. Bonferroni corrects for the number of pairs per task.
</details>

<details><summary>5. "Temperature 0 is deterministic. Why talk about noise?"</summary>

It isn't in practice. 2408.04667 measured accuracy variations up to 15% across repeated runs of models configured to be deterministic. The report estimates its own noise from a test-retest pair (one model run twice under the same condition), and treats gaps inside that range as noise.
</details>

<details><summary>6. "Why not AthenaBench? It's newer and harder."</summary>

Its attack scenarios were generated with GPT-5, and the models under test include GPT models. A benchmark written by one model family can favour that family's phrasing and distractors, which is an authorship confound.
</details>

<details><summary>7. "Aren't these items in the training data?"</summary>

Possibly. Both benchmarks were public in 2024, so the results are closed-book on public items, not held-out. That limits absolute claims most. 2607.15263's no-tools probe (50.5% from question text alone on a public dataset) shows how large memorisation can be, which is why the report states the caveat instead of claiming held-out performance.
</details>

<details><summary>8. "You changed the protocol after the run. Doesn't that break pre-registration?"</summary>

The change reclassified a diagnosed serving-side failure (empty content after a finished reasoning trace, which returned answers on identical retries) from model failure to infrastructure retry. It is disclosed as a deviation, both versions of the numbers are published, and the original rows are kept. Leaving it would have scored a provider bug as low capability, the same failure pattern 2609.08765 documents.
</details>

<details><summary>9. "Why run reasoning off and on? Just use the default."</summary>

Defaults differ by provider, so "default" means a different setting per model. Running both and testing the within-model difference shows whether a ranking depends on the setting, rather than hiding that inside one arbitrary choice.
</details>

<details><summary>10. "Why pin providers?"</summary>

Through a router, one model ID can be served by many deployments with different quantization and serving stacks, so an unpinned run mixes several systems. Pinning makes each row a statement about one named deployment. A third-party deployment is labelled as such.
</details>

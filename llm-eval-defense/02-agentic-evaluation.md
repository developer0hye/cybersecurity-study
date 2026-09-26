# 02: Agentic Evaluation Methodology

Study notes on how to evaluate a tool-using LLM agent on security tasks, and how to defend the design choices. The running example is the **agentic axis** of my benchmark report, [budget-llm-cybersecurity-eval](https://github.com/developer0hye/budget-llm-cybersecurity-eval): budget-tier models on [Cybench](https://github.com/andyzorigin/cybench) through `inspect_evals`' ReAct agent. This note has no attack techniques or challenge solutions.

> **About the numbers.** Every figure below comes from a published paper or technical report, linked where it is used. My own report's results are not quoted. Figures marked *illustrative* are arithmetic examples. Design choices of my report are described with pointers to its code.

## TL;DR

- An agentic eval measures whether a model can **do** a task through a tool loop in a sandbox. A knowledge benchmark measures whether it can **recall** an answer. They are different capabilities and need different benchmarks.
- Cybench measures **offensive** capability. It is run for the same reasons as other dangerous-capability evals: to quantify risk, to show defenders what models can do on their own, and to do it where nothing real is attacked. Cybench's authors weighed release explicitly and published a harms/benefits argument.
- **The harness is part of the measurement.** In the Cybench paper, the same model scored **17.5% vs 10.0%** under two scaffolds. In the cost-aware study [arXiv:2607.15263](https://arxiv.org/abs/2607.15263), the same trace scored **76.1% at a $0.80 cap and 86.4% at $2.10**.
- The metric is a **solve rate with its denominator and budget attached**. With 39 tasks, 95% CIs are wide and only large gaps pass a corrected paired test.
- **Sandbox isolation** contains an agent that runs arbitrary code. **Network policy** keeps it from downloading public solutions, which would be contamination through tool use.
- **Logs are layered** (trajectory → egress index → network flow log) so reviewers can check what the agent *tried* and what the network *allowed*.
- **Whether infrastructure errors count as model failures is a declared choice.** 2607.15263 counts API failures as failures ("measures the deployed model-provider system"). My report retries them and reports them separately. Either is defensible if stated. Silently mixing them is not.
- **Every limit is a budget.** 2607.15263 notes its 250-message cap *"may depress high-volume models"*. A per-call time cap does the same to slow-streaming models.

## 1. What an agentic eval measures

| | Knowledge benchmark | Agentic benchmark |
|---|---|---|
| Question | Does the model know X? | Can the model get X done? |
| Input | one prompt, closed-book | task description + a live sandbox |
| Output | one answer | a **trajectory** of reasoning, tool calls and observations, ending in a submission |
| Scoring | exact match on the extracted answer | flag matched by the scorer |
| Score depends on | model + prompt + decoding + extraction | all of that, plus **harness, tools, budget and environment** |
| Cost per item | one API call | tens to hundreds of calls. 2607.15263 reports **144.7 mean tool calls** per sample for DeepSeek v4 Flash vs **34.4** for GPT-5.6 Luna (Table 2) |

The agentic score adds **multi-step competence**: choosing the next action from an observation, recovering from errors, using tools efficiently and deciding when to submit. That is why the report keeps the two axes separate rather than treating one as a proxy for the other.

**Cybench in numbers** ([arXiv:2408.08926](https://arxiv.org/abs/2408.08926)): 40 professional CTF tasks from 4 competitions, with human first-solve times from 2 minutes to 24 h 54 min (*"a 747x increase"*). The `inspect_evals` implementation and 2607.15263 use **39** of them in the "hard" variant (no subtask guidance).

## 2. Why measure offensive capability at all

Cybench is an **offensive** benchmark. Each task requires finding and exploiting a weakness in a deliberately vulnerable target to recover a flag. The obvious question is "why measure how good models are at attacking things?", and it deserves a direct answer.

**It is standard dangerous-capability evaluation practice.** The benchmarks' own authors frame it that way:

- Cybench (abstract): *"Policymakers, model providers, and researchers in the AI and cybersecurity communities are interested in quantifying the capabilities of such agents to help mitigate cyberrisk and investigate opportunities for penetration testing."*
- Cybench's release discussion weighs harms (*"it may be leveraged by malicious actors"*) against benefits. It likens the agent to *"an automated penetration testing tool"* such as Metasploit, and cites the need for *"more evidence and data for informed decisions and responsible regulation."* Their conclusion: *"we have chosen to release our code and data."*
- WMDP ([arXiv:2403.03218](https://arxiv.org/abs/2403.03218)), used on the knowledge axis, is *"a proxy measurement of hazardous knowledge in biosecurity, cybersecurity, and chemical security"*, and was *"stringently filtered to eliminate sensitive & export-controlled information."*

The harness comes from the same practice. `inspect_evals` and the Inspect k8s sandbox are maintained under the UK government's [UKGovernmentBEIS](https://github.com/UKGovernmentBEIS/inspect_evals) organisation, with sandbox docs at `k8s-sandbox.aisi.org.uk`.

**What the measurement tells defenders:**

- **Capability per dollar, not just peak capability.** 2607.15263: *"Security-agent evaluations commonly measure peak offensive capability under generous inference budgets… Such measurements are useful but incomplete."* It reports solve rates at fixed cost caps (§3). "X% of tasks for under $Y each" is a more useful risk statement than a peak score.
- **Budget-tier models are the relevant floor.** Frontier results describe the best-resourced actor. Cheap models describe what anyone can get.
- **Guardrails are part of the measured system.** In 2607.15263 Table 2, GPT-5.6 Sol refused 106/117 sample-epochs and scored 9.4%, and Claude Fable 5 refused all 117 (*"a policy-filter outcome rather than evidence of zero underlying capability"*). After the evaluating account passed OpenAI Trusted Verification tier 1, Sol scored **87.2%** (Table 4), though the authors *"avoid attributing their differences solely to verification"*. A score measures the model **plus its access policy**, which is exactly what a defender faces.

**How the risk of running it is controlled:** the targets are containers built for the task, so nothing outside the sandbox is attacked. Egress is restricted (§5). Upstream `inspect_evals` refuses to run Cybench on Docker's unrestricted network unless `CYBENCH_ACKNOWLEDGE_RISKS=1` is set, and recommends the k8s sandbox, *"which provides domain filtering capabilities"*. Results are reported as aggregate statistics, and these notes contain no walkthroughs.

## 3. The harness and the budget are part of the result

A solve rate means nothing without the **harness** that produced it: agent loop, tools, submission rules, provider and reasoning setting, and budget.

**Evidence 1: scaffold.** Cybench Table 3, unguided, best of 3 attempts, same model and tasks:

| Scaffold | Claude 3.5 Sonnet | GPT-4o |
|---|---|---|
| Structured bash | 17.5% | 17.5% |
| Action-only | 15.0% | 12.5% |
| Pseudoterminal | 20.0% | 10.0% |
| Web search | 20.0% | 15.0% |

GPT-4o's score moves by 7.5 points with the scaffold alone. The best scaffold also differs between the two models.

**Evidence 2: budget.** 2607.15263 replays DeepSeek v4 Flash traces under a retrospective cap: *"a retrospective $0.80 cap yields 76.1% success, which rises to 86.4% when the full $2.10 budget is allowed."* Figure 1: *"Offensive success climbs steadily with spend."*

**Evidence 3: the pipeline in general.** An audit of 8 cybersecurity benchmarks ([arXiv:2609.08765](https://arxiv.org/abs/2609.08765)) finds *"a single pipeline choice can change a model's score by more than 80 percentage points and substantially alter model rankings."*

**Every budget type penalises something.** The choice is between biases, not between biased and unbiased:

| Budget | Penalises |
|---|---|
| Turn / message cap | models that do little per turn, or that make many cheap calls. 2607.15263's 250-message BOTS limit was hit by 8/93 DeepSeek v4 Flash sample-epochs at $2.10 and 14/93 at $4.20, so *"truncation may depress high-volume models"* |
| Cost cap | models with high per-token prices or verbose reasoning |
| Time cap | models or providers with low tokens/s (§8) |
| Context window | long trajectories, unless compaction is on (see [03 §6](03-agent-architecture.md#6-context-management-and-reasoning-tokens)) |

**How the report applies this.** It follows 2607.15263's described setup: Cybench hard variant from `inspect_evals`, `bash` + `python` + `submit` tools, up to 3 submissions, and a per-sample cost cap with the paper's $2.10 as the main setting. Inspect records cumulative cost per call, so the result under any *lower* cap can be recomputed from the same logs without re-running. That is the paper's own retrospective-cap method. A sample that hits the cap is a no-answer, reported separately. Settings live in [`agentic/run_cybench.py`](https://github.com/developer0hye/budget-llm-cybersecurity-eval/blob/gpt6-luna-and-agentic/agentic/run_cybench.py).

**Known difference from the anchor, to disclose:** 2607.15263 §3 used *"a ReAct-style agent with auto-compaction… when the agent context reached 90% of the model context window."* `inspect_evals`' Cybench task configures no compaction, and the report's current harness uses that default. So a trajectory that fills the context window ends there instead of being compacted. Compaction only acts once the context reaches that 90% threshold, so the difference matters only for samples that get that full. The report handles it by checking the logs (samples that ended on overflow, and the largest context actually sent) instead of re-running. No sample reached the threshold, so the difference is disclosed in the README as a deviation that did not change any result.

## 4. Metrics and statistics with 39 tasks

**Units.** A *sample* is one task × one epoch. An *epoch* is one full pass over the tasks. 2607.15263 scores *"by averaging binary correctness across three independent epochs (per-sample mean correctness, then averaged across all challenges)"*, which gives 117 sample-epochs for 39 tasks.

**Denominator.** Always state it: of 39 tasks, of all sample-epochs, and whether tasks excluded for broken environments were removed.

**Submission attempts are not pass@k.** The up-to-3 submissions happen *inside one trajectory*, with "incorrect" feedback. That is still one pass@1 sample. Cybench's own paper used a *single attempt* for its main table and *"the max of the attempts"* over 3 independent attempts for the scaffold table. Those are different metrics, so say which one a number is.

**Confidence intervals.** Use a **Wilson** interval for a proportion at small n. It behaves well near 0% and 100%, where the normal approximation does not.

*Illustrative:* 20/39 = 51.3%, Wilson 95% CI ≈ 36.2–66.1%.

2607.15263 describes its own bootstrap intervals as *"descriptive robustness checks, not formal population-level inferences"*, and emphasises *"fixed-budget operating points over universal model rankings."*

**Paired tests.** When models run the same tasks, use McNemar's exact test. Only discordant tasks (solved by one model, not the other) carry information.

*Illustrative power check:* 5 models → 10 pairs → Bonferroni α = 0.005. The smallest discordant split that clears it is **9–0** (p = 0.0039), or **12–1** (p = 0.0034). With 39 tasks, "not significant" means "not distinguishable at this n", never "equal".

**Noise.** Repeated epochs give per-task agreement (solved in 3/3, 2/3, 1/3, 0/3). Temperature 0 does not remove run-to-run variance: [arXiv:2408.04667](https://arxiv.org/abs/2408.04667) reports *"accuracy variations up to 15% across naturally occurring runs"* for models configured to be deterministic.

## 5. Sandbox isolation and network policy

Two separate purposes:

**(a) Containment.** The agent runs arbitrary shell and Python, installs packages and attacks services. The report uses `inspect_evals`' **k8s sandbox** with **gVisor** (a user-space kernel between the container and the host kernel) and **Cilium** network policy. Code the agent runs cannot reach the host kernel directly, and outbound traffic goes only to allowlisted domains.

**(b) Measurement validity.** Cybench tasks are public CTFs, and their sources and writeups are on public code hosts. An agent with open internet can *retrieve* a solution instead of *producing* one:

| | Training-data contamination | Contamination through tool use |
|---|---|---|
| When | pretraining, before the eval | during the eval, in the trajectory |
| Preventable by the harness? | no | yes, with egress control |
| Detectable? | only indirectly (e.g. no-tools probes) | yes, from logs (§6) |

2607.15263 shows how large memorisation can be on an old public benchmark. On BOTS v1 with **no tools at all**, GPT-5.6 Sol scored 50.5% from the question text alone (Table 5). The authors conclude that such controls are *"mandatory"*.

**The policy.** Each Cybench task ships an `allow_domains` list. The report keeps it but removes public code hosts (`BLOCKED_DOMAINS` in `run_cybench.py`: `github.com`, `raw.githubusercontent.com`, `bitbucket.org`). Package mirrors stay reachable so installs work. The aim is to cut only the answer-retrieval path.

**Checking the policy didn't break the benchmark.** Before any model runs, each task's **reference solution** runs in the same environment with no model. A task whose reference solution fails is excluded and reported, never scored as a model failure. This check caught a real problem: Kali's apt redirector picks a mirror per request, so the upstream single-mirror allowlist broke `apt`. Kali's published mirror list was added ([`agentic/kali_mirrors.txt`](https://github.com/developer0hye/budget-llm-cybersecurity-eval/blob/gpt6-luna-and-agentic/agentic/kali_mirrors.txt)).

**Disclose it as a deviation.** 2607.15263 does not describe its egress rules beyond the Kubernetes infrastructure mention, so a stricter policy may lower scores relative to it.

## 6. Layered logs, so results can be audited

| Layer | Source | Answers | Cannot answer |
|---|---|---|---|
| 1. Trajectory | Inspect `.eval` log | every model call, tool call, output, cost, provider, limit hit and error, in order. The primary record. | what the network actually allowed |
| 2. Egress index | [`agentic/audit_egress.py`](https://github.com/developer0hye/budget-llm-cybersecurity-eval/blob/gpt6-luna-and-agentic/agentic/audit_egress.py) | which tool calls named an external host, classified challenge / mirror / code_host / other, each linked to its position in the `.eval` | whether the connection succeeded |
| 3. Network flows | Cilium Hubble export via [`agentic/collect_netlog.py`](https://github.com/developer0hye/budget-llm-cybersecurity-eval/blob/gpt6-luna-and-agentic/agentic/collect_netlog.py) | every DNS query from sandbox pods with its FORWARDED/DROPPED verdict. A forwarded code host is flagged as a breach. | which task a flow belongs to |
| 4. Summary | [`agentic/analyze_cybench.py`](https://github.com/developer0hye/budget-llm-cybersecurity-eval/blob/gpt6-luna-and-agentic/agentic/analyze_cybench.py) | per model: solved, cap hits, errors, spend, providers seen | anything not in the logs |

Why more than one layer:

- **Layers 1 and 3 are independent.** One is written by the harness from what the agent did. The other is written by the network from what it permitted. A misconfigured allowlist could leave the trajectory looking clean while traffic got through.
- **Layer 2 makes layer 1 reviewable.** It points to the exact tool events worth reading.
- **Scoring never reads layers 2–3,** so an audit bug cannot change a score.
- **The provider field** in layer 1 verifies per call that the pinned deployment actually served it.

2607.15263 also relies on Inspect *"to keep track of auxiliary metrics like cost, token consumption, and tool calling statistics"*, which is why the cost-cap recomputation in §3 is possible at all.

## 7. Infrastructure failure vs model failure

**The core question:** when a sample fails because of an HTTP 5xx, a hung connection or a broken container, is that the model's failure?

**Two defensible answers, if declared:**

| Policy | Measures | Used by |
|---|---|---|
| Count API failures as failures | the deployed system, reliability included: *"This treatment measures the deployed model-provider system rather than accuracy conditional on receiving a valid response."* | 2607.15263. MiniMax M3's *"six provider/API failures are retained as Cybench failures"* |
| Retry infrastructure failures and report them separately | the model's capability given a working pipeline | my report |

What is not defensible is mixing them silently, so that one model's provider outages quietly lower its score.

**How large a silent infrastructure failure can be.** 2609.08765 found that in SecEval, *"the five-token output budget falls below Azure OpenAI's 16-token minimum, causing every GPT-5.4 request to fail"*. The reported **0.3%** came from accidental letter matches in error payloads. *"Raising the budget to 16 tokens restores valid generation and yields 81.4% accuracy."* An infrastructure error looked like an 81-point capability gap.

**Fairness rules for re-running** (my report's approach):

| Rule | Why |
|---|---|
| Retry only infrastructure errors, never cost-cap hits or wrong answers | Retrying one model's failures would give it extra chances (pass@k) |
| When a sample ran more than once, keep the **newest non-error** result, never the best | `analyze_cybench.py`: *"Never 'best of runs' -- preferring a solved attempt would give re-run samples pass@2."* |
| Check the environment before measuring models | Reference solutions run first (§5) |
| Report the counts | Errors, cap hits and safety-limit stops per model |

**Refusals are model behaviour, not infrastructure.** 2607.15263 counts them as failures and reports them per model (§3.3: *"refused epochs remain failures"*). They are reported alongside the score because a refusal-heavy score means something different from a capability-limited one (§2).

## 8. Timeouts can penalise slow models

Several clocks run at once, and they do different jobs:

| Limit | Scope | Job |
|---|---|---|
| Tool timeout | one `bash`/`python` call | part of the task spec (180 s in `inspect_evals` Cybench) |
| `stream_idle_timeout` | one model call | **hang detector**: no streamed output for N seconds |
| `attempt_timeout` | one model call | backstop on total call duration |
| `working_limit` | one sample | model + tool time; a safety stop, not a budget |
| `time_limit` | one sample | wall clock. Needed because `working_limit` does not count provider retry/backoff time. |

(Names and rationale: the `argparse` help text in `run_cybench.py`.)

**The problem.** A per-call **total-time** cap cannot tell a hung connection from a model that is slowly but steadily streaming a long reasoning turn. Output speed varies by model and provider, so the same cap kills a slow model's long turn while a fast model never approaches it. The retry takes just as long, the sample fails, and it looks like a model failure. It is the same pattern 2607.15263 flags for its message cap: a limit meant to bound runaway runs *"may depress"* one kind of model.

**Why a per-call cap is still needed.** A connection can return HTTP 200 headers and then no body. Without any timeout, the sample waits forever and a cost cap never fires, because nothing is billed.

**The design response:**

1. Detect hangs by **inactivity** (`stream_idle_timeout`), which a slowly streaming model never triggers.
2. Keep total-time caps only as generous backstops.
3. Report samples stopped by time limits **separately** from wrong answers and cost-cap hits.
4. Check whether a timeout reproduces on an idle machine before calling it a model limit.

**How to defend it:** the budget is cost. Time limits exist only to catch hangs, and where one did bind, the per-model count is published.

## Sources

- Zhang et al., *Cybench*, [arXiv:2408.08926](https://arxiv.org/abs/2408.08926): abstract, Tables 2–3, release discussion
- Kassianik, Nelson, Singer, *Beyond Success Rate: Cost-Aware Evaluation of Offensive and Defensive Security Agents*, [arXiv:2607.15263](https://arxiv.org/abs/2607.15263): §3, Tables 2, 4, 5, §7
- Berriche et al., *Benchmark Scores Are Pipeline-Dependent*, [arXiv:2609.08765](https://arxiv.org/abs/2609.08765)
- Atil et al., *Non-Determinism of "Deterministic" LLM Settings*, [arXiv:2408.04667](https://arxiv.org/abs/2408.04667)
- Li et al., *The WMDP Benchmark*, [arXiv:2403.03218](https://arxiv.org/abs/2403.03218)
- [`inspect_evals/cybench`](https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/cybench) · my report's agentic code on branch [`gpt6-luna-and-agentic`](https://github.com/developer0hye/budget-llm-cybersecurity-eval/tree/gpt6-luna-and-agentic/agentic)

## Questions you'll be asked (and how to answer)

<details><summary>1. "You're benchmarking how well cheap models can hack. Isn't that irresponsible?"</summary>

It is standard dangerous-capability evaluation. Cybench's authors frame it as quantifying agent capability "to help mitigate cyberrisk", and published a harms/benefits argument for releasing it. The targets are purpose-built containers in a gVisor sandbox with allowlisted egress, and only aggregate statistics are reported. For defenders, cheap-model results show what anyone can do for a few dollars.
</details>

<details><summary>2. "Why not just use a knowledge benchmark? It's cheaper."</summary>

Recall is not execution. An agentic task needs choosing actions, reading tool output, recovering from errors and deciding when to submit, none of which an MCQ exercises. The cost difference is large too: 2607.15263 reports 34–145 mean tool calls per sample on Cybench.
</details>

<details><summary>3. "Your solve rate would change with a different agent or budget. So what does it mean?"</summary>

Yes, and that is documented in the literature. In the Cybench paper, GPT-4o scored 17.5% vs 10.0% under two scaffolds. In 2607.15263, one model went from 76.1% at a $0.80 cap to 86.4% at $2.10. So a solve rate is reported as conditional on a pinned harness and budget, and the cost cap is set high so lower-budget curves can be recomputed from the logs.
</details>

<details><summary>4. "39 tasks is tiny. Can you conclude anything?"</summary>

Only large differences. With 10 pairs and Bonferroni α = 0.005, McNemar needs at least a 9–0 discordant split. The main output is per-model solve rates with Wilson CIs, and non-significant pairs are reported as "not distinguishable at this n". 2607.15263 takes the same stance: operating points over universal rankings.
</details>

<details><summary>5. "Is your agent the standard one?"</summary>

It is the `inspect_evals` Cybench task's built-in ReAct agent (bash + python + submit, up to 3 submissions). 2607.15263 describes the same benchmark variant, tools and submission limit with "a ReAct-style agent" in Inspect. Two differences: that paper enabled auto-compaction at 90% of the context window, and the `inspect_evals` default has none; and the paper does not state its system prompt, so the harness default is used. Both are disclosed. Compaction only acts at the 90% threshold, and the logs show no sample reached it, so the runs were not repeated. It is not the original Cybench paper's agent, which used its own scaffolds, 15 iterations, and memory of the last three iterations.
</details>

<details><summary>6. "Why block GitHub? Real attackers use GitHub."</summary>

The eval measures whether the model can solve the task, not whether it can find the published answer. The tasks are public and their solutions are online. Package mirrors stay reachable, and reference solutions were checked to still pass under the policy. It is disclosed as a deviation.
</details>

<details><summary>7. "How do I know the agent didn't fetch a writeup anyway?"</summary>

Two independent records: the Inspect trajectory (what the agent tried) and Cilium's Hubble flow log (what the network forwarded or dropped). `audit_egress.py` indexes host-naming tool calls, and `collect_netlog.py` flags any forwarded code-host lookup as a breach.
</details>

<details><summary>8. "Some runs hit API errors. Did you drop them? The paper counted them as failures."</summary>

Both are valid if declared. 2607.15263 counts them because it measures the deployed system including reliability. My report measures capability given a working pipeline, so it retries infrastructure errors, keeps the newest non-error result (never the best), never retries cap hits or wrong answers, and publishes the counts. 2609.08765 shows the risk of not separating them: an output-token limit below a provider minimum turned an 81.4% model into 0.3%.
</details>

<details><summary>9. "Doesn't your timeout favour fast models?"</summary>

A total-time per-call cap would. That's why hangs are detected by stream inactivity, the total cap is only a backstop, and samples stopped by time limits are reported per model. It is the same concern 2607.15263 raises about its message limit depressing high-volume models.
</details>

<details><summary>10. "Refusals: are they capability or policy?"</summary>

Both, and they are reported separately. In 2607.15263, GPT-5.6 Sol scored 9.4% with 106/117 refusals, and 87.2% after the account passed OpenAI Trusted Verification. Refusals count as failures in the solve rate, as in that paper, and the refusal count is reported next to it.
</details>

<details><summary>11. "Cybench is old and public. Isn't it contaminated?"</summary>

For training data, probably, and it is not claimed as held-out. It was chosen because a published run under a documented protocol exists. 2607.15263's no-tools probe on another public benchmark (Sol at 50.5% from question text alone) shows why this matters. Contamination through tool use, on the other hand, is blocked by the network policy and audited through the logs.
</details>

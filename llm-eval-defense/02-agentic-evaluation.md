# 02: Agentic Evaluation Methodology

Study notes on the **agentic axis** of my benchmark report, [budget-llm-cybersecurity-eval](https://github.com/developer0hye/budget-llm-cybersecurity-eval): 5 budget-tier models on [Cybench](https://github.com/andyzorigin/cybench) (39 CTF tasks) through `inspect_evals`' ReAct agent. The goal is to be able to explain and defend *how* it is measured. This note has no attack techniques or challenge solutions.

> **Status.** The agentic run is in progress. Its results are **pending** in the report, so this note gives only the method. Every number below comes from the report's README ([knowledge axis](https://github.com/developer0hye/budget-llm-cybersecurity-eval#results), [legacy CTF study](https://github.com/developer0hye/budget-llm-cybersecurity-eval/blob/main/legacy/ctftiny/README.md)) or from a cited paper. Protocol details cite the agentic code on branch [`gpt6-luna-and-agentic`](https://github.com/developer0hye/budget-llm-cybersecurity-eval/tree/gpt6-luna-and-agentic/agentic). Numbers marked *illustrative* are arithmetic examples, not report figures.

## TL;DR

- An agentic eval measures whether a model can **do** a task through a tool loop in a sandbox. A knowledge benchmark measures whether it can **recall** the answer. The report treats these as two separate axes because they diverged: the legacy MCQ run had all 10 model pairs non-significant, while on CTF the same models ranged from 21.6% to 7.0%.
- Cybench measures **offensive** capability: an autonomous agent attacking deliberately vulnerable services. It is run for the same reasons as other dangerous-capability evals: to quantify risk, to show defenders what cheap models can do alone, and to do it in a sandbox where nothing real is attacked.
- **The harness is part of the measurement.** The agent loop, tools, turn/cost/time budgets, provider and reasoning setting all move the score. In the legacy study, raising `max_rounds` from 12 to 30 added **+26 pp** to both models tested and left the gap between them unchanged at **40 pp**.
- The metric is a **solve rate with its denominator and its budget attached**. With n=39, the 95% CI is wide and only large gaps can pass a Bonferroni-corrected McNemar test. The CI table is the main deliverable.
- **Sandbox isolation** contains an agent that runs arbitrary code. **Network policy** keeps the agent from downloading public solutions, which would be contamination through tool use.
- **Logs are layered** (trajectory → egress index → network flow log) so a reviewer can check both what the agent *tried* and what the network *allowed*.
- **Infrastructure failures are never scored as model failures.** They are retried under rules that avoid giving any model a second chance at the answer (no best-of-runs, no retrying timeouts).
- **A timeout is a budget too.** A per-call wall-clock cap penalises models that stream slowly but are still working. The harness uses an idle-stream detector for hangs and reports samples stopped by safety limits separately.

## 1. What an agentic eval measures

| | Knowledge axis | Agentic axis |
|---|---|---|
| Question | Does the model know X? | Can the model get X done? |
| Input | one prompt, closed-book | task description + a live sandbox |
| Model output | one answer (letter / CWE ID) | a **trajectory**: many turns of reasoning, tool calls and observations, ending in a flag submission |
| Scoring | exact match on the extracted answer | flag string matched by the scorer (`includes()`) |
| What the score depends on | model + prompt + sampling | model + prompt + **harness + tools + budget + environment** |
| Cost of one item | one API call | tens of calls, minutes of sandbox time |

The report states the distinction directly: *"Knowing the right ATT&CK mitigation is not the same as getting a shell on a box."* The legacy evidence is in the [README's goal section](https://github.com/developer0hye/budget-llm-cybersecurity-eval#readme). On CyberMetric-2000 all 10 pairs were non-significant (p ≥ 0.13). On CTF, DeepSeek V4.1 Flash solved 21.6% and Solar Pro 4 7.0% (reasoning off, 185 matched challenges).

What the agentic score adds is **multi-step competence**: choosing what to try next from an observation, recovering from errors, using tools efficiently, and knowing when to submit. It also costs more, so the spend per task is part of the result (see [arXiv:2607.15263](https://arxiv.org/abs/2607.15263), which argues for comparing models "at fixed cost levels").

## 2. Why measure offensive capability at all

Cybench is an **offensive** benchmark. Each task is a professional CTF challenge. The agent must find and exploit a weakness in a deliberately vulnerable target to recover a flag. Saying this plainly matters, because the obvious question is "why are you measuring how good cheap models are at attacking things?"

**It is standard dangerous-capability evaluation practice.** Both benchmarks in the report are framed this way by their own authors:

- Cybench ([arXiv:2408.08926](https://arxiv.org/abs/2408.08926), abstract): *"Policymakers, model providers, and researchers in the AI and cybersecurity communities are interested in quantifying the capabilities of such agents to help mitigate cyberrisk and investigate opportunities for penetration testing."*
- WMDP ([arXiv:2403.03218](https://arxiv.org/abs/2403.03218), abstract), used on the knowledge axis, cites the risk of *"large language models (LLMs) empowering malicious actors in developing biological, cyber, and chemical weapons"*, and notes the dataset *"was stringently filtered to eliminate sensitive information prior to public release."*

The harness itself comes from the same practice. `inspect_evals` and the Inspect k8s sandbox are maintained under the UK government's [UKGovernmentBEIS](https://github.com/UKGovernmentBEIS/inspect_evals) GitHub organisation, with sandbox docs at `k8s-sandbox.aisi.org.uk` (the URL appears in `inspect_evals/cybench/cybench.py`).

**What the measurement tells defenders:**

- **Floor, not ceiling.** Frontier-model evals describe what the best-resourced actor gets. Budget-tier models ($0.09–0.20 in / $0.36–1.20 out per 1M tokens, [README](https://github.com/developer0hye/budget-llm-cybersecurity-eval#models-under-test)) describe what anyone gets for a few dollars. That is the relevant threat model for commodity attacks.
- **Capability per dollar.** Because the report logs cumulative cost per call, it can show the solve rate at any lower cost cap (§3). "Solves X% for under $Y per task" is a more useful risk statement than a peak score.
- **Knowledge ≠ action.** A model can score like its peers on security MCQs and still differ sharply at doing the task (§1). Defenders who rely on knowledge benchmarks alone would misjudge the risk.

**How the risk of running it is controlled:**

- **Controlled targets.** Every target is a container built from the challenge's own compose file. Nothing outside the sandbox is attacked.
- **Isolation and egress control.** See §5. Upstream `inspect_evals` refuses to run Cybench with Docker's unrestricted network unless `CYBENCH_ACKNOWLEDGE_RISKS=1` is set, and its warning recommends the k8s sandbox *"which provides domain filtering capabilities"*. The report uses the k8s sandbox.
- **Aggregate reporting.** The report's headline outputs are solve rates, costs and statistics, and these notes contain no attack walkthroughs. On the knowledge axis, the committed logs store *"model responses, answer keys and prompt hashes, but not question text"* ([README, License](https://github.com/developer0hye/budget-llm-cybersecurity-eval#license)).

## 3. The harness and the budget are part of the result

A solve rate is only meaningful with the **harness** that produced it. For this axis, that means:

| Component | Setting | Why it matters |
|---|---|---|
| Agent loop | `inspect_evals` default ReAct agent ([03](03-agent-architecture.md)) | Different scaffolds give different scores. The Cybench paper itself compares 4 scaffolds. |
| Tools | `bash`, `python`, 180 s timeout each, plus `submit` | A missing tool or a short timeout caps what any model can do. |
| Submissions | 3 flag attempts per sample | Wrong flags get feedback and the loop continues. |
| Provider | one pinned provider per model, `allow_fallbacks: false` | Unpinned, OpenRouter load-balances each call across providers with different quantization ([README, Provider pinning](https://github.com/developer0hye/budget-llm-cybersecurity-eval#models-under-test)). |
| Reasoning | `reasoning: {enabled: true}` for every model | Reasoning changed rankings on the knowledge axis (headline finding 4). |
| Budget | per-sample `cost_limit`, plus safety time limits | See below. |

All of these are set in [`agentic/run_cybench.py`](https://github.com/developer0hye/budget-llm-cybersecurity-eval/blob/gpt6-luna-and-agentic/agentic/run_cybench.py). The harness version is pinned in [`agentic/requirements.txt`](https://github.com/developer0hye/budget-llm-cybersecurity-eval/blob/gpt6-luna-and-agentic/agentic/requirements.txt) (`inspect_evals@2329ee2`, `inspect_ai==0.3.268`).

**Every budget type encodes a bias.** The choice is between biases, not between biased and unbiased:

| Budget | Penalises |
|---|---|
| Turn cap (`max_rounds`) | models that do less work per turn |
| Cost cap (`cost_limit`) | models with high per-token prices or verbose reasoning |
| Time cap | models or providers with low tokens/s (§8) |

**Evidence that the budget moves the score:** the legacy study re-ran CTFTiny at `max_rounds=30` instead of 12 ([legacy README, round-budget experiment](https://github.com/developer0hye/budget-llm-cybersecurity-eval/blob/main/legacy/ctftiny/README.md#results-how-much-does-the-round-budget-decide-the-score)):

| CTFTiny 50, reasoning off | 12 rounds | 30 rounds | Paired p |
|---|---|---|---|
| Solar Pro 4 | 14.0% | 40.0% | 0.0010 |
| DeepSeek V4.1 Flash | 54.0% | 80.0% | 0.0002 |
| Gap | 40.0 pp | 40.0 pp | |

The absolute numbers depend on the budget. The ranking does not. Solar Pro 4 chained shell commands in 48.1% of calls against DeepSeek's 93.4%, so a turn cap hit it harder, but extra turns did not close the gap. The legacy README's rule: *"Do not quote a number from this report without the budget attached."*

**How the Cybench run uses this lesson.** The cost cap is set high on purpose. Inspect logs cumulative cost per model call, so the solve rate under any *lower* cap can be recomputed from the same logs without re-running (a budget curve). A low cap cannot answer "would it have solved it with more?". A high cap plus recomputation answers both questions. A sample that hits the cap is a **no-answer**, reported per model, in the same way truncations are on the knowledge axis.

## 4. Metrics and statistics at n=39

**Unit of measurement.** A *sample* is one challenge × one epoch. An *epoch* is one full pass over the 39 challenges. Score = mean over epochs per challenge, then mean over challenges.

**Solve rate and its denominator.** Always say "of 39 challenges" (or "of 39 × epochs sample-epochs"), and whether infrastructure-excluded challenges were removed from the denominator. The legacy study shows why: its "attempted" denominator was 83–175 of 200 before repair and 179–199 after, and the recovered challenges were harder than the rest (§7).

**Three submission attempts are not pass@3.** The 3 attempts happen *inside one trajectory*, with feedback after each wrong flag. They are part of one pass@1 sample. pass@k across epochs would be "solved in any of k independent runs", which the report does not use.

**Confidence intervals.** The report's primary statistic is the solve rate with a 95% **Wilson** interval. Wilson behaves well near 0% and 100% and at small n, where the normal-approximation interval does not.

*Illustrative:* 20/39 solved = 51.3%, Wilson 95% CI ≈ 36.2–66.1%. A 30-point-wide interval means two models 10 points apart usually have overlapping CIs.

**Between-model tests.** McNemar's exact test on the same 39 challenges (paired data). Only **discordant pairs** carry information: challenges one model solved and the other did not.

*Illustrative power check:* with 5 models there are 10 pairs, so Bonferroni α = 0.05/10 = 0.005. The smallest discordant split that clears it is **9–0** (p = 0.0039). With one discordant challenge the other way, it takes **12–1** (p = 0.0034). A non-significant result at n=39 therefore means "not distinguishable at this sample size", never "equal".

**Noise.** One sample per item leaves no noise estimate. On the knowledge axis, GLM's two reasoning-on runs served as a test-retest pair and moved 0.8–1.0 pp ([README, headline finding 5](https://github.com/developer0hye/budget-llm-cybersecurity-eval#headline-findings)). On the agentic axis, extra epochs play this role: per-challenge agreement (solved 3/3, 2/3, 1/3, 0/3) shows how much of a model's score is stable. The plan runs 1 epoch first and adds epochs only where a comparison is inconclusive, to bound spend.

**External anchor.** [arXiv:2607.15263](https://arxiv.org/abs/2607.15263) ran the same benchmark (39 tasks × 3 epochs) and reports GPT-5.6 Luna at 79.5% and DeepSeek v4 Flash at 86.4%. The anchor is loose: only Luna is a same-model row, it ran at a different reasoning effort, and the other rows are predecessor models. Treat agreement as a sanity check, not a replication.

## 5. Sandbox isolation and network policy

Two separate purposes, often conflated:

**(a) Containment: protect the host and the outside world.** The agent runs arbitrary shell and Python, installs packages and attacks services. The report runs it in the `inspect_evals` **k8s sandbox** on a local cluster with **gVisor** (a user-space kernel between the container and the host kernel) and **Cilium** network policy, with a memory limit per agent container. Two properties make this safe to run: code the agent executes cannot reach the host kernel directly, and outbound traffic goes only to allowlisted domains.

**(b) Measurement validity: stop the agent from looking up the answer.** Cybench tasks are public CTFs from 2022–24, and their sources and writeups are on public code hosts. An agent with open internet can *retrieve* a solution instead of *producing* one. That is **contamination through tool use**, a different problem from training-data contamination:

| | Training-data contamination | Contamination through tool use |
|---|---|---|
| When | before the eval, in pretraining | during the eval, in the trajectory |
| Can the harness prevent it? | no | yes, with egress control |
| Can it be detected? | only indirectly | yes, from logs (§6) |

**The policy.** Each challenge ships an `allow_domains` list. The report keeps it but removes public code hosts (`BLOCKED_DOMAINS = {"github.com", "raw.githubusercontent.com", "bitbucket.org"}` in `run_cybench.py`). Package mirrors stay reachable, so `pip`/`apt` installs work as in the anchor paper. The goal is to remove only the answer-retrieval path without breaking tasks that legitimately need a package.

**Verifying that the policy didn't break the benchmark.** Before any model runs, each challenge's **reference solution** is run in the same environment with no model. A challenge whose reference solution fails is excluded and reported, never scored as a model failure. This test found a real issue: the upstream allowlist had a single Kali mirror, but Kali's redirector picks a mirror per request and location, so `apt` failed from this host. Kali's full mirror list was added ([`agentic/kali_mirrors.txt`](https://github.com/developer0hye/budget-llm-cybersecurity-eval/blob/gpt6-luna-and-agentic/agentic/kali_mirrors.txt)).

**Why the policy is a deviation, and why it's disclosed.** The report infers that the anchor paper used the k8s sandbox, but the paper's exact egress configuration is not reproduced in the report, so this policy may be stricter than the paper's. A pilot with unrestricted Docker egress showed agents reaching public code hosts. That pilot is kept as design data and not scored (`agentic/logs_unrestricted_network/`). Stricter egress may lower scores relative to the paper; the README lists the policy as a deviation.

## 6. Layered logs, so results can be audited

Each layer answers a different reviewer question:

| Layer | Source | Answers | Cannot answer |
|---|---|---|---|
| 1. Trajectory | Inspect `.eval` log per model (`agentic/logs/<model>/`) | Every model call, tool call, tool output, cost, provider, limit hit, error, in order. This is the primary record. | What the network actually allowed |
| 2. Egress index | [`agentic/audit_egress.py`](https://github.com/developer0hye/budget-llm-cybersecurity-eval/blob/gpt6-luna-and-agentic/agentic/audit_egress.py) → `agentic/audit/` | Which tool calls named an external host, classified as challenge / mirror / code_host / other, each linked to its position in the `.eval` | Whether the attempt succeeded at the network level |
| 3. Network flows | Cilium Hubble export via [`agentic/collect_netlog.py`](https://github.com/developer0hye/budget-llm-cybersecurity-eval/blob/gpt6-luna-and-agentic/agentic/collect_netlog.py) → `agentic/netlog/` | Every DNS query from sandbox pods with its verdict (FORWARDED / DROPPED). Any forwarded code host is flagged as a policy breach. | Which challenge a flow belongs to (it gives the pod, not the task) |
| 4. Summary | [`agentic/analyze_cybench.py`](https://github.com/developer0hye/budget-llm-cybersecurity-eval/blob/gpt6-luna-and-agentic/agentic/analyze_cybench.py) | Per model: solved, cost-cap hits, errors, spend, providers seen | Anything the scorer did not record |

Why more than one layer:

- **Layers 1 and 3 are independent.** The trajectory is written by the harness from what the agent did. The flow log is written by the network from what it permitted. If an allowlist were misconfigured, the trajectory alone could look clean while the network let traffic through. Two independent records that agree are stronger than one.
- **Layer 2 makes layer 1 reviewable.** Nobody reads 195 trajectories end to end. The index points a reviewer to the exact tool events worth reading.
- **Scoring never reads layers 2 and 3.** They are audit records, so an audit bug cannot change a score.
- **The provider field** in layer 1 proves the pin held, so "which deployment was measured" is checked per call, not assumed.

The report also plans a **writeup-fetching audit** that greps every trajectory for writeup-related URLs and reports hits per model and challenge.

## 7. Infrastructure failure vs model failure

**Rule (from the report's CLAUDE.md, applied on both axes):** a row that failed for infrastructure reasons is never silently counted as a model failure. Diagnose the root cause, fix it, re-run, and report what the result would have looked like if left unfixed.

**Why it matters, with a committed example.** On the knowledge axis, 68 rows came back HTTP 200 with empty `content`. Re-running 10 of them with identical payloads returned answers every time, so the failure was serving-side. Scored as model failures, they would have made Solar Pro 4's CTI-MCQ reasoning gain look **non-significant (p = 0.053) instead of p = 0.0001** ([README, empty content](https://github.com/developer0hye/budget-llm-cybersecurity-eval#infrastructure-failure-found-after-the-run-empty-content)). One misclassified failure type reversed a conclusion.

**Failures do not land evenly.** In the legacy CTF run, 54 rows ended on API errors (`finish_reason: unknown`), unevenly spread: Solar Pro 4 26, Luna 15, Qwen 8, DeepSeek 5. Counting them as non-solves penalised the model already reported as weakest, so the headline was re-run without them as a sensitivity check. n fell from 196 to 179 and every conclusion survived ([legacy README, Limitations](https://github.com/developer0hye/budget-llm-cybersecurity-eval/blob/main/legacy/ctftiny/README.md#limitations)).

**Missingness is not random.** Legacy repair passes raised coverage from 83–175/200 to 179–199/200. The recovered challenges solved at a *lower* rate in 4 of 5 conditions. Infrastructure failures had been hiding harder challenges, so the pre-repair rates were optimistic.

**Fairness rules for re-running:**

| Rule | Why |
|---|---|
| Retry only infrastructure errors (HTTP 429/5xx, hangs, sandbox crashes), never cost-cap hits, truncations or wrong answers | Retrying one model's failures would give it pass@k |
| When a sample was run more than once, keep the **newest non-error** result, never the best one | `analyze_cybench.py`: *"Never 'best of runs' -- preferring a solved attempt would give re-run samples pass@2."* |
| Rate-limited runs are *not attempted*, not failed | A throttled run never got a fair attempt (legacy) |
| Be careful about retrying only the failures | The legacy study left 5 corrupted rows un-retried because an extra attempt for only those rows would be *"selection on the outcome"* ([Appendix B](https://github.com/developer0hye/budget-llm-cybersecurity-eval/blob/main/legacy/ctftiny/README.md#appendix-b-operational-incident-log)) |
| Check the environment before measuring the model | Reference solutions run first (§5) |
| Report the counts | Errors, cap hits and safety-limit stops are reported per model |

## 8. Timeouts can penalise slow models

Several clocks run at once, and they do different jobs:

| Limit | Scope | Job |
|---|---|---|
| Tool timeout (180 s) | one `bash`/`python` call | part of the task spec (upstream default) |
| `stream_idle_timeout` | one model call | **hang detector**: no streamed output for N seconds |
| `attempt_timeout` | one model call | backstop on total call duration |
| `working_limit` | one sample | model + tool time; a safety stop, not a budget |
| `time_limit` | one sample | wall clock, because `working_limit` does not count time spent in provider retries and backoff |

(Flag names and their rationale are in `run_cybench.py`'s `argparse` help text.)

**The problem.** A per-call **total-time** cap cannot tell a hung connection from a model that is slowly but steadily streaming a long reasoning turn. Output speed (tokens/s) differs by model and provider. A long reasoning turn from a slow model can outlast a cap that a fast model never approaches. The call is killed and retried, the retry takes as long, and the sample fails. It looks like a model failure but is really a **throughput** penalty, and it hits reasoning-heavy slow models hardest, confounding the "reasoning on" condition.

**Why a per-call cap is still needed.** The first cost pilot had calls that returned HTTP 200 headers and then no body for many minutes. Without any timeout, the sample waits forever and the cost cap never fires, because no tokens are billed.

**The design response:**

1. Detect hangs by **inactivity** (`stream_idle_timeout`), which a slowly streaming model never triggers.
2. Keep the total-time cap only as a generous backstop.
3. Report samples stopped by `working_limit`/`time_limit` **separately** from wrong answers and cost-cap hits.
4. Check whether a timeout reproduces. The legacy study kept a few 900 s timeouts as model failures only after they *"reproduced on a second idle-machine run"*, ruling out load.

**How to defend it:** the score is "solved within this cost cap", and time limits are there only to catch hangs. Where a time limit did bind, the count is reported per model so a reader can see which model it affected.

## Sources

- Report: [README](https://github.com/developer0hye/budget-llm-cybersecurity-eval#readme) · [legacy CTF README](https://github.com/developer0hye/budget-llm-cybersecurity-eval/blob/main/legacy/ctftiny/README.md) · agentic code on branch [`gpt6-luna-and-agentic`](https://github.com/developer0hye/budget-llm-cybersecurity-eval/tree/gpt6-luna-and-agentic/agentic)
- Zhang et al., *Cybench*, [arXiv:2408.08926](https://arxiv.org/abs/2408.08926)
- Li et al., *The WMDP Benchmark*, [arXiv:2403.03218](https://arxiv.org/abs/2403.03218)
- Kassianik, Nelson, Singer, *Beyond Success Rate: Cost-Aware Evaluation of Offensive and Defensive Security Agents*, [arXiv:2607.15263](https://arxiv.org/abs/2607.15263)
- [`inspect_evals/cybench`](https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/cybench)

## Questions you'll be asked (and how to answer)

<details><summary>1. "You're benchmarking how well cheap models can hack. Isn't that irresponsible?"</summary>

It is the same practice as other dangerous-capability evals. Cybench's own abstract frames it as quantifying agent capability "to help mitigate cyberrisk". The tasks are public CTFs against containers built for the purpose, run in a gVisor sandbox with egress restricted to an allowlist. The report publishes aggregate rates and costs, not solutions. For defenders, budget-tier results show what anyone can get for a few dollars, which is the relevant floor.
</details>

<details><summary>2. "Why not just use the knowledge benchmark? It's cheaper."</summary>

Because the two diverge. On the legacy data, all 10 model pairs were non-significant on CyberMetric-2000, yet on CTF DeepSeek V4.1 Flash solved 21.6% against Solar Pro 4's 7.0% (185 matched challenges). Recall and execution are different capabilities.
</details>

<details><summary>3. "Your solve rate would be different with a different agent or budget. So what does it mean?"</summary>

Yes, and the report says so. A solve rate is conditional on the harness and the budget, which are pinned and published. The legacy round-budget experiment moved both models by +26 pp while the gap stayed at 40 pp, so absolute numbers move with the budget and rankings were stable in that test. Quote numbers with the budget attached. The cost cap is high so lower-budget curves can be recomputed from the logs.
</details>

<details><summary>4. "n=39 is tiny. Can you conclude anything?"</summary>

Only large differences. With 10 pairs and Bonferroni α = 0.005, McNemar needs at least a 9–0 discordant split. So the main deliverable is the per-model solve rate with a Wilson CI, and a non-significant pair is reported as "not distinguishable at n=39", not "equal". Extra epochs are added where a comparison is inconclusive.
</details>

<details><summary>5. "Three submission attempts: isn't that inflating the score?"</summary>

It is the upstream `inspect_evals` Cybench setting and the anchor paper's protocol, so it is kept for comparability. All attempts happen inside one trajectory, so it is still one sample per challenge-epoch (pass@1), not pass@3 over independent runs.
</details>

<details><summary>6. "Why block GitHub? Real attackers use GitHub."</summary>

The eval measures whether the model can solve the task, not whether it can find the published answer. Cybench challenges are public and their solutions are online, so open egress turns the eval into a search test. Package mirrors remain reachable, and reference solutions were checked to still pass under the policy. The change is disclosed as a deviation from the anchor paper.
</details>

<details><summary>7. "How do I know the agent didn't fetch a writeup anyway?"</summary>

Two independent records: the `.eval` trajectory (what the agent tried) and Cilium's Hubble flow log (what the network forwarded or dropped). `audit_egress.py` indexes every tool call that names an external host, and `collect_netlog.py` flags any code-host DNS lookup that was forwarded as a policy breach.
</details>

<details><summary>8. "Some runs errored. Did you just drop the bad ones?"</summary>

No. Infrastructure errors are retried (Inspect's `retry_on_error=3` in `run_cybench.py`, then re-runs of what remains), and a challenge whose environment is broken is excluded and reported. Cost-cap hits and wrong answers are never retried. When a sample has several runs, the newest non-error result is kept, never the best. Counts of errors, cap hits and safety-limit stops are reported per model. The empty-content case on the knowledge axis shows why: misclassifying 68 rows would have flipped a significance call (p = 0.053 vs 0.0001).
</details>

<details><summary>9. "Doesn't your timeout favour fast models?"</summary>

A total-time per-call cap would. That's why hangs are detected by stream inactivity, which a slow but working model does not trigger, and the total-time cap is only a generous backstop. Samples stopped by time limits are reported separately so any residual effect is visible per model.
</details>

<details><summary>10. "Your numbers don't match the paper you anchor to."</summary>

Expected, and the differences are listed: medium reasoning effort instead of high, a stricter network policy, a different sandbox cluster, and epochs added only as needed. Only GPT-5.6 Luna is a same-model row; the paper's DeepSeek and GLM rows are predecessor models. The anchor is a sanity check on the order of magnitude, not a replication.
</details>

<details><summary>11. "Cybench is from 2022–24. Isn't it contaminated?"</summary>

Probably, for training data, and the README says the axis does not address freshness. It was chosen because a published run exists under a documented protocol. Contamination through tool use, on the other hand, is controlled by the network policy and audited through the logs.
</details>

# Defending an LLM Security Benchmark

Study notes for explaining and defending the methodology of my own benchmark report, [**budget-llm-cybersecurity-eval**](https://github.com/developer0hye/budget-llm-cybersecurity-eval): 5 budget-tier LLMs evaluated on two separate axes, **cybersecurity knowledge** (closed-book MCQ) and **agentic task-solving** (a tool-using agent on CTF challenges in a sandbox).

When someone asks "why did you measure it that way?", I want to be able to answer from the design, the data and the code, not from memory. These notes are for that.

- **Scope: methodology only.** How the evaluation is designed, what the numbers mean, and where they could mislead. No attack techniques, exploit steps or challenge solutions.
- **Numbers come from the original papers and technical reports** (Cybench, WMDP, CTIBench, CyberMetric, and the cited evaluation-methodology papers), each linked where it is used. My own report's results are not quoted here; the notes explain the method and point to the report's code.

## Where this fits

This connects two parts of my [AI × Security roadmap](../roadmap/): evaluation of LLM apps and agents in [Phase 2](../roadmap/02-ai-engineering-foundations.md), and AI-assisted offensive capability in [Phase 4](../roadmap/04-attacks-powered-by-ai.md). The sandbox and egress-control ideas also tie back to [Network+](../comptia-network-plus/) (egress filtering, DNS, segmentation).

## Contents

| # | Note | Topics |
|---|---|---|
| 01 | [Knowledge benchmark methodology](01-knowledge-benchmarks.md) | closed-book vs. agentic, benchmark selection (saturation, authorship confound, contamination), the WMDP-cyber cut, pre-registered protocol, non-answers vs. wrong answers, McNemar + Bonferroni + sensitivity check, majority baseline, test-retest noise, reasoning as a ranking confound, the empty-content infrastructure failure |
| 02 | [Agentic evaluation methodology](02-agentic-evaluation.md) | agentic vs. knowledge evals, why measure offensive capability, harness and budget effects, solve rate / Wilson CI / McNemar power at n=39, sandbox isolation and network policy, layered logs, infrastructure vs. model failure, re-run fairness, timeouts and slow models |
| 03 | [Agent architecture basics](03-agent-architecture.md) | ReAct loop, tool definitions and calls, system prompt, submission and retries, termination conditions, context management, reasoning tokens vs. turns, the Inspect framework and what the report borrowed vs. wrote (Inspect's ReAct agent as the example) |

Each note ends with **"Questions you'll be asked (and how to answer)"**, with the answers folded.

## Source & license

These are my own notes about my own report. Short quotations from cited papers and from Inspect / `inspect_evals` source code are attributed inline. The report itself is Apache-2.0.

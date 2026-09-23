# Phase 5: Defense, Governance & Practice

**Draws on:** 🤖 [AI Engineer](https://roadmap.sh/ai-engineer) (evals, observability, guardrails) + 🛡️ [Cyber Security](https://roadmap.sh/cyber-security) (SOC, IR, compliance) + [AI Red Teaming](https://roadmap.sh/ai-red-teaming)

**Goal:** be able to secure an AI-enabled product end to end and use AI to help defenders, not only understand attacks.

## Checklist

### Secure design for LLM apps
- [ ] Threat-model an LLM app: data flows, trust boundaries, what each component is allowed to do
- [ ] Least privilege for agents: scoped credentials, per-tool permissions, confirmation for destructive actions
- [ ] Treat model output as untrusted input (encode, validate, sandbox)
- [ ] Keep secrets out of prompts. Enforce authorization in code, never "in the prompt"
- [ ] Per-user access control in RAG retrieval

### Testing: AI red teaming & evals
- [ ] AI red teaming vs. traditional pentesting: scope, methods, reporting
- [ ] Tools: [garak](https://github.com/NVIDIA/garak), [PyRIT](https://github.com/Azure/PyRIT), [promptfoo](https://github.com/promptfoo/promptfoo)
- [ ] Security evals in CI (regression tests for known injections and jailbreaks)

### Detection & response
- [ ] Logging and tracing prompts, retrieved context, and tool calls (with privacy in mind)
- [ ] Detecting abuse: anomalous tool use, exfiltration patterns, cost spikes
- [ ] Incident response when the "attacker" is text inside a document
- [ ] Using LLMs in the SOC: alert triage, log summarization, detection-rule drafting, plus their failure modes

### Governance & frameworks
- [ ] [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) (Govern / Map / Measure / Manage) and the [GenAI Profile, NIST AI 600-1](https://doi.org/10.6028/NIST.AI.600-1)
- [ ] [MITRE ATLAS](https://atlas.mitre.org/): tactics and techniques, case studies
- [ ] [OWASP GenAI Security Project](https://genai.owasp.org/) resources
- [ ] Regulation awareness: EU AI Act, ISO/IEC 42001 (AI management system)
- [ ] Company-level policy: approved AI tools, data classification for prompts, shadow AI

### Capstone ideas
- [ ] Build a small agent (Phase 2), attack it (Phase 3), harden it, and write a short report with before/after eval results
- [ ] Write a one-page "AI-era phishing" awareness guide from Phase 4 case studies

## Notes & resources I used

- (none yet)

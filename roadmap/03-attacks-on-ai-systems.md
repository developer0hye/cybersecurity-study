# Phase 3: Attacks on AI Systems

**Draws on:** 🤖 [AI Engineer](https://roadmap.sh/ai-engineer) (how the system is built) + 🛡️ [Cyber Security](https://roadmap.sh/cyber-security) (how systems get attacked) + [AI Red Teaming](https://roadmap.sh/ai-red-teaming)

**Goal:** understand how LLM apps, RAG pipelines, and agents are attacked, and map each attack to a classic security concept I already know.

**Primary frameworks:** [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/) · [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) · [MITRE ATLAS](https://atlas.mitre.org/)

## OWASP Top 10 for LLM Applications (2025) × what I already know

| ID | Risk | Classic analogue | Studied |
|---|---|---|---|
| LLM01 | Prompt Injection | [SQL injection](../cs50-cybersecurity/notes/03-securing-software.md#sql-injection) / [XSS](../cs50-cybersecurity/notes/03-securing-software.md#code-injection-and-cross-site-scripting-xss) (data becomes code) | ⬜ |
| LLM02 | Sensitive Information Disclosure | data leakage, DLP | ⬜ |
| LLM03 | Supply Chain | [malicious packages, typosquatting](../cs50-cybersecurity/notes/03-securing-software.md#package-managers) | ⬜ |
| LLM04 | Data and Model Poisoning | integrity attacks, backdoors | ⬜ |
| LLM05 | Improper Output Handling | missing [output encoding](../cs50-cybersecurity/notes/03-securing-software.md#defense-1-character-escapes) → XSS/SQLi/[command injection](../cs50-cybersecurity/notes/03-securing-software.md#command-injection) | ⬜ |
| LLM06 | Excessive Agency | violating least privilege | ⬜ |
| LLM07 | System Prompt Leakage | [secrets in client-side code](../cs50-cybersecurity/notes/03-securing-software.md#developer-tools-and-client-side-validation) | ⬜ |
| LLM08 | Vector and Embedding Weaknesses | broken access control, data poisoning | ⬜ |
| LLM09 | Misinformation | integrity; over-trusting unverified output | ⬜ |
| LLM10 | Unbounded Consumption | [DoS](../cs50-cybersecurity/notes/02-securing-systems.md#denial-of-service-dos-and-ddos), "denial of wallet" | ⬜ |

## Checklist

### Prompt injection & jailbreaks
- [ ] Direct prompt injection vs. jailbreaking: what's the difference?
- [ ] **Indirect** prompt injection: instructions hidden in web pages, emails, PDFs, images, or tool results
- [ ] Why there is no complete fix yet: instructions and data share one channel (compare with parameterized SQL, which *does* separate them)
- [ ] Mitigations: privilege separation, human-in-the-loop for risky actions, treating LLM output as untrusted, allowlisted tools, content isolation/spotlighting

### Data & model integrity
- [ ] Training / fine-tuning data poisoning, backdoored models
- [ ] RAG poisoning: planting a document that gets retrieved
- [ ] Model supply chain: unsafe serialization (pickle), model hubs, safetensors, signing and provenance

### Confidentiality
- [ ] System prompt extraction. Rule: never put secrets in prompts
- [ ] Training data extraction, membership inference, model inversion
- [ ] Cross-tenant leakage in RAG (missing per-user filters)
- [ ] Model extraction / stealing through the API

### Agents, tools & MCP
- [ ] Excessive agency: too many tools, too broad permissions, no confirmation step
- [ ] Tool misuse and confused-deputy problems (the agent uses *its* privileges for an attacker's goal)
- [ ] MCP risks: tool poisoning (malicious tool descriptions), rug-pull updates, over-broad tokens, local servers running arbitrary code → [MCP security best practices](https://modelcontextprotocol.io/specification/latest/basic/security_best_practices)
- [ ] Data exfiltration channels: markdown image URLs, links, tool calls to attacker-controlled endpoints
- [ ] Memory / context poisoning in long-lived agents
- [ ] OWASP Agentic Top 10: ASI01 Agent Goal Hijack → ASI10 Rogue Agents (read all ten)

### Output handling & availability
- [ ] LLM output flowing into HTML, SQL, shell, or `eval` (Improper Output Handling = [CS50 L3](../cs50-cybersecurity/notes/03-securing-software.md#code-injection-and-cross-site-scripting-xss) again; compare with [`04_sql_injection.py`](../cs50-cybersecurity/demos/04_sql_injection.py), [`05_xss_escaping.py`](../cs50-cybersecurity/demos/05_xss_escaping.py), [`06_command_injection.py`](../cs50-cybersecurity/demos/06_command_injection.py))
- [ ] Sandboxing code-executing agents (containers, no network, resource limits)
- [ ] Rate limits, token budgets, cost alerts

### Hands-on (only on my own systems or intentionally vulnerable labs)
- [ ] Solve a public prompt-injection challenge (e.g. Gandalf by Lakera)
- [ ] Attack my own Phase 2 RAG bot with an indirect injection in a document
- [ ] Attack my own Phase 2 MCP server with a poisoned tool description
- [ ] Map each attack I try to a MITRE ATLAS technique

## Notes & resources I used

- (none yet)

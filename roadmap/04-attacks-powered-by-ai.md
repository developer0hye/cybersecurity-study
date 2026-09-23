# Phase 4: Attacks Powered by AI

**Draws on:** 🛡️ [Cyber Security](https://roadmap.sh/cyber-security) (the attack categories and defenses) + 🤖 [AI Engineer](https://roadmap.sh/ai-engineer) (what the models can realistically do)

**Goal:** understand how attackers use AI to make *existing* attacks cheaper, faster, and more convincing, and which defenses still hold.

**Key insight:** AI mostly **scales and polishes** known attacks rather than inventing new categories. The defenses from Phase 1 still work: phishing-resistant MFA, least privilege, verification procedures, patching, monitoring. What changes is that "it looked real" can't be a signal anymore.

## Checklist

### Social engineering at scale
- [ ] LLM-written phishing and spear phishing: fluent, personalized, and in any language (spelling mistakes no longer give it away)
- [ ] OSINT automation: building target profiles from public data
- [ ] Voice cloning (vishing) and fake "family emergency" or "CEO" calls
- [ ] Deepfake video meetings. Case study: the 2024 Hong Kong incident where an Arup employee transferred about US$25M after a video call with deepfaked colleagues
- [ ] Defenses: out-of-band verification (call back on a known number), payment approval workflows, code words, passkeys / FIDO2 (phishing-resistant), user training that doesn't rely on "spot the typo"

### Offensive automation
- [ ] AI-assisted reconnaissance and vulnerability scanning
- [ ] AI-assisted exploit and malware development: what's realistic vs. hype
- [ ] Automated vulnerability discovery (fuzzing + LLMs). Defenders use the same tools
- [ ] Faster time-to-exploit after CVE disclosure → patching speed and KEV prioritization matter more

### Identity & fraud
- [ ] CAPTCHA and bot-detection bypass
- [ ] Synthetic identities and deepfakes against KYC / liveness checks
- [ ] Credential attacks enhanced by AI (smarter password guessing from personal data)

### Information integrity
- [ ] Disinformation and fake content at scale
- [ ] Watermarking and content provenance (C2PA): what they can and can't prove

### Case studies to collect
- [ ] Read vendor threat reports on real-world malicious use of AI models (e.g. OpenAI's and Anthropic's threat intelligence reports, Google's GTIG reports)
- [ ] For each case, note: **attack stage** (Kill Chain / ATT&CK) → **what AI changed** → **which classic defense would have stopped it**

## Notes & resources I used

- (none yet)

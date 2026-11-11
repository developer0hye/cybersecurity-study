# Cybersecurity LLM Training Datasets — A Survey

A snapshot survey of **publicly available training datasets for cybersecurity-focused LLMs**, covering both
*knowledge / instruction* data (Q&A, CTI, CVE/CWE, exams, SOC, malware/RE, secure-code) and *agentic*
data (CTF, pentest, exploit-reproduction trajectories, tool-use/RL environments).

The main thing this survey tries to add on top of a plain list is a **usability lens by license and
provenance**, because that is usually what actually decides whether you can use a dataset:

- **Commercial-product use** — can you train a model you intend to *ship* in a product?
- **Research / internal-only use** — the model is *never shipped*; it is only for internal experiments or
  research. This path opens up non-commercial (NC), research-only, and academic-gated datasets.
- **Off-limits even for internal research** — the license forbids derivative models at all, or the data's
  provenance is legally tainted.

> ⚠️ **Read this first.**
> - This is a **personal study snapshot**, verified around **2026-11-11**. It is **not legal advice** and
>   **not authoritative**. Licenses, gating, and contents change — always re-check the source before relying
>   on anything here.
> - **A permissive license *tag* on Hugging Face frequently contradicts the card or gate text.** Several
>   datasets are tagged `apache-2.0` but say "non-commercial" or "academic only" in the body. Where that
>   happens it is quoted below, but verify yourself.
> - **"No license" is not the same as "non-commercial / research-OK."** An unlicensed repo is
>   all-rights-reserved by default, so it is marked *Unclear*, not *Yes*.
> - **CC-BY-NC for a for-profit's internal, non-shipped experiments is a legal gray zone.** It is probably
>   fine for pure internal R&D, but that is a question for a lawyer, not a dataset card.
> - Only legitimate, authorized security research / defensive use is in scope. Several datasets here contain
>   offensive content; that orientation is flagged.

**Legend** — Commercial / Research columns: **Y** = yes · **N** = no · **?** = unclear/conditional.
"Type": **K** = knowledge/instruction · **A** = agentic/trajectory.

---

## 1. Full catalog

### 1.1 Knowledge — general cybersecurity instruction / chat SFT

| Dataset | Size & format | License (tag → contradiction) | Comm | Research | Provenance / notes |
|---|---|---|:--:|:--:|---|
| [Trendyol/Trendyol-Cybersecurity-Instruction-Tuning-Dataset](https://huggingface.co/datasets/Trendyol/Trendyol-Cybersecurity-Instruction-Tuning-Dataset) | 53,201 rows / 195 MB; `system`/`user`/`assistant` (card says Parquet, repo holds one JSONL — format mismatch) | `apache-2.0`, no NC text | Y¹ | Y | Built by a vendor security team; **output generator undisclosed** (likely LLM-synthesized). Biggest clean-tagged general SFT set |
| [AlicanKiraz0/Cybersecurity-Dataset-Fenrir-v2.1](https://huggingface.co/datasets/AlicanKiraz0/Cybersecurity-Dataset-Fenrir-v2.1) | 99,870 rows / 431 MB | `apache-2.0`; card: "commercial-friendly, only public sources" | Y¹ | Y | Harvested from 450k+ public technical docs; **output generator undisclosed** |
| [oi-uae/cyber-security](https://huggingface.co/datasets/oi-uae/cyber-security) | ~1M+ rows (Parquet), `messages` chat | `license:other`, `research-only-non-commercial`; card: "Research use only" | N | Y (NC, gated) | Aggregated from ~198 sources (offensive + blue-team + CVE + malware + forensics), deduped. Clean format |
| [WhitzardAgent/CyberSecurity-1M](https://huggingface.co/datasets/WhitzardAgent/CyberSecurity-1M) | 1.19M records, en/zh, 16 categories | tag `apache-2.0` **but** gate/card: "academic, non-commercial research only"; institutional email required | N | ?² | Aggregated public sources incl. offensive content. **Academic-only gate** |
| [pAILabs/infosec-security-qa](https://huggingface.co/datasets/pAILabs/infosec-security-qa) | 11,185 rows / 14 MB Q&A | `apache-2.0` | Y¹ | Y | Generator undisclosed; small |
| [ChaoticNeutrals/Cybersecurity-ShareGPT](https://huggingface.co/datasets/ChaoticNeutrals/Cybersecurity-ShareGPT) | 15,723 rows / ~99 MB ShareGPT | `license:other` (unspecified) | N | N (off-limits) | Converted from **ShareGPT** = scraped ChatGPT outputs → see §3 |
| [Vyber07/cyber-security](https://huggingface.co/datasets/Vyber07/cyber-security) | ~16 GB, 507 files | `apache-2.0` tag | N | N (off-limits) | Opaque, agent-built bulk **repackaging of third-party data** (contains others' exact files) → see §3 |
| segolilylabs/Lily-Cybersecurity | ~22k pairs (hearsay) | model Apache-2.0; **dataset unknown** | — | — | **Dataset never released** — only the 7B model exists. Unavailable |

### 1.2 Knowledge — threat intelligence (CTI / ATT&CK / CAPEC)

| Dataset | Size & format | License | Comm | Research | Provenance / notes |
|---|---|---|:--:|:--:|---|
| [reloading0101/threat-intelligence-dataset](https://huggingface.co/datasets/reloading0101/threat-intelligence-dataset) | 28,501 rows; `instruction/input/output` + multi-turn | `cc-by-nc-sa-4.0` (consistent) | N | Y (cite + share-alike) | **Grounded & verified** against MITRE ATT&CK v19.1 / CISA KEV / CWE / CAPEC / OSV / abuse.ch / Sigma; failing records dropped; entity-split (decontam-aware). One of the better-documented CTI sets |
| [trendmicro-ailab/Primus-Seed](https://huggingface.co/datasets/trendmicro-ailab/Primus-Seed) ([paper](https://arxiv.org/abs/2502.11191)) | curated cyber text corpus | `odc-by` | Y (attribution + confirm sources) | Y | Crawled reputable sources + expert-collected CTI. Underlying site licenses vary. Flagship open cyber corpus (trained the Llama-Primus family) |
| [trendmicro-ailab/Primus-FineWeb](https://huggingface.co/datasets/trendmicro-ailab/Primus-FineWeb) | ~2.57B cyber tokens (CPT corpus) | `odc-by` + must obey FineWeb / Common Crawl ToU | Y (conditions) | Y | Classifier-filtered FineWeb (Common Crawl derivative). Pretraining corpus |
| [trendmicro-ailab/Primus-Instruct](https://huggingface.co/datasets/trendmicro-ailab/Primus-Instruct) | hundreds of expert scenarios | `odc-by` **but responses generated by GPT-4o** | N/? (OpenAI ToS taint) | Y (gray) | Expert instructions + GPT-4o responses |
| [trendmicro-ailab/Primus-Reasoning](https://huggingface.co/datasets/trendmicro-ailab/Primus-Reasoning) | reasoning traces | `odc-by`; distilled from DeepSeek-R1 | Y on license, **but ⚠ built from CTI-Bench tasks** | Y — exclude if you evaluate on CTI-Bench | DeepSeek-R1 distillation over CTI-Bench items → **direct eval contamination** |
| [Vanessasml/cybersecurity_32k_instruction_input_output](https://huggingface.co/datasets/Vanessasml/cybersecurity_32k_instruction_input_output) | 32,569 rows / 7.5 MB | **no license tag** | N | ? (gray) | Outputs from **GPT-4**; sources incl. CASIE (academic-only) + web scrape |
| clydeiii/cybersecurity | 100k–1M, plain text | `license:unknown` | N | N (off-limits) | Redistributes copyrighted vendor APT report text (APTnotes) → see §3 |

### 1.3 Knowledge — vulnerability (CVE / CWE)

| Dataset | Size & format | License | Comm | Research | Provenance / notes |
|---|---|---|:--:|:--:|---|
| [stasvinokur/cve-and-cwe-dataset-1999-2025](https://huggingface.co/datasets/stasvinokur/cve-and-cwe-dataset-1999-2025) | 280,694 rows / 103 MB CSV (raw CVE records) | `cc0-1.0` | Y | Y | Pulled from **NVD REST API v2.0** (US-gov public domain). Clean knowledge table; reformat into instructions |
| [xamxte/cve-to-cwe](https://huggingface.co/datasets/xamxte/cve-to-cwe) | 290,446 rows / 52 MB Parquet; CVE→CWE + ATT&CK | `cc-by-4.0` | Y (attribution) | Y | NVD + AI-assisted label refinement (model unnamed — minor) |
| [zefang-liu/cve-and-cwe-mapping-dataset](https://huggingface.co/datasets/zefang-liu/cve-and-cwe-mapping-dataset) | 169,566 rows / 56 MB CSV | `cc-by-nc-sa-4.0` | N | Y | Partial copy of a Kaggle CVE↔CWE mapping |
| [almedamine/CTI_RCM_Training](https://huggingface.co/datasets/almedamine/CTI_RCM_Training) | 62,050 rows / 86 MB JSON; CVE desc → analysis → CWE-ID | `apache-2.0` tag **but outputs are GPT-4o-generated** | N/? (GPT-4o taint) | Y | NVD CVEs 2010–2023 + GPT-4o analysis. A training counterpart to the CTI-RCM eval task — **so decontaminate against CTI-Bench** |

### 1.4 Knowledge — exam / MCQ / certification

| Dataset | Size & format | License | Comm | Research | Notes |
|---|---|---|:--:|:--:|---|
| [kala185/comptia_security_pluse_701](https://huggingface.co/datasets/kala185/comptia_security_pluse_701) | 3,731 rows; Security+ MCQ | `mit` | Y | Y | ⚠ Likely overlaps Security+ **evals** — contamination watch |
| **Gap** | — | — | — | — | Almost no clean dedicated *training* MCQ corpus; cert MCQ sets are mostly evaluation benchmarks |

### 1.5 Knowledge — SOC / log / detection engineering

| Dataset | Size & format | License | Comm | Research | Notes |
|---|---|---|:--:|:--:|---|
| [jcordon5/cybersecurity-rules](https://huggingface.co/datasets/jcordon5/cybersecurity-rules) | 949 rows / 4 MB; detection-rule Q&A | `apache-2.0` tag | ? | Y | ~950 **SIGMA/YARA/Suricata** rules + Q&A distilled with a 7.5B model. Effective license = rules' licenses (SIGMA = DRL 1.1; YARA/Suricata vary) + distill-model license |
| [infosecn1nja/soc-triage-opensec-chat](https://huggingface.co/datasets/infosecn1nja/soc-triage-opensec-chat) | 10,080 rows chat; 7-class SOC disposition | `cc-by-4.0`; card: "all data is synthetic" | Y (if generator terms OK) | Y | Generator unnamed. Companion `soc-triage-golden` |
| alirezaaminzadeh/soc-analytics-alerts-synthetic; poliana-moraes/alertas-soc-sft | small synthetic SOC | mixed/unshown | ?/N | Y | Minor |

### 1.6 Knowledge — malware analysis / reverse engineering

| Dataset | Size & format | License | Comm | Research | Notes |
|---|---|---|:--:|:--:|---|
| [LLM4Binary/decompile-ghidra-100k](https://huggingface.co/datasets/LLM4Binary/decompile-ghidra-100k) | 100,000 rows / 13 MB; Ghidra pseudocode → C | `mit` | Y | Y | Closest RE-instruction set; more *code* than prose |
| RevEng-24-25/Ghidra-Instruct-10K; atul10/reverse_engineering_code_* | ~10k each | **no license** | N | ? | Research-tier |
| **Gap** | — | — | — | — | Dedicated malware-analysis *explanatory/Q&A* instruction data is thin |

### 1.7 Knowledge — secure code / vulnerability detection (text-level)

| Dataset | Size & format | License | Comm | Research | Notes |
|---|---|---|:--:|:--:|---|
| [CyberNative/Code_Vulnerability_Security_DPO](https://huggingface.co/datasets/CyberNative/Code_Vulnerability_Security_DPO) | 4,656 DPO pairs | `apache-2.0`; card warns it "does not establish all generated-code rights" | Y¹ (caution) | Y | Synthetic DPO generated by `deepseek-coder-33b`; labels not verified ground truth. Most-used secure-code DPO set |
| scthornton/securecode*, securecodegen/SecurePy150k, SecCoderX | mixed | mixed/none | ?/N | Y | Research-tier; inconsistent licenses |
| BigVul / DiverseVul / PrimeVul / CVEfixes | large | MIT/apache/unknown per mirror | varies | Y | Code+label **classification** corpora (not instruction); GPL'd upstream → derivative/redistribution caveats |

### 1.8 Agentic — CTF / pentest / exploit / tool-use / RL

| Resource | Downloadable now? | Size & format | License | Comm | Research | Orientation / notes |
|---|---|---|---|:--:|:--:|---|
| [FineEnvs/MiMo-V2.6-RL-harbor-cyber](https://huggingface.co/datasets/FineEnvs/MiMo-V2.6-RL-harbor-cyber) | **Yes, open** | 1,000 **RL environments** (Docker tasks + tests), not recorded traces | `apache-2.0` | **Y** | Y | Vuln/crash-repro (ARVO/OSS-Fuzz). **The only clean agentic pick** — but you generate your own trajectories in it. Dedup ARVO ids vs CyberGym |
| [WhitzardAgent/CyberAgentTrace](https://huggingface.co/datasets/WhitzardAgent/CyberAgentTrace) | **Yes, gated** | 3,999 trajectories across 5 configs; ShareGPT-with-tools / OpenAI-messages schemas | `apache-2.0` files **but** gate: defensive-research only, no redistribution | N (gate limits) | Y (conditions) | Attack-adjacent, defensive framing. **Best actually-usable agentic trace set.** Drop the `real_benchmark` config (eval); dedup `real_arvo` vs CyberGym |
| [KHenryAegis/Pentest-R1](https://github.com/KHenryAegis/Pentest-R1) ([paper](https://arxiv.org/abs/2508.07382)) | **Yes (GitHub)** | ~500 walkthrough trajectories (`data/steps/`); Thought-Command-Observation schema | **No LICENSE file** (MIT badge only — not a grant) | N | ? | **Offensive.** Unlicensed + aggregates HackTheBox/VulnHub/TryHackMe walkthroughs (third-party copyright). Must be cleared before use |
| [justinwangx/CTFtime](https://huggingface.co/datasets/justinwangx/CTFtime) | **Yes, open** | 10k–100k rows; raw writeup prose | **No license stated** | N | ? | **Offensive.** Scraped CTFtime community writeups (author copyright). Synthesis seed only, after rights review |
| [CTF-Dojo](https://github.com/fruitfoxlu/CTF-Dojo) ([paper](https://arxiv.org/abs/2508.18370)) | **No** — data & weights not released (tooling only) | paper: 486 verified trajectories, 658 Docker challenges | repo `cc-by-nc-4.0` | N | ? (if ever released) | **Offensive** (CTF). CTF-Dojo-32B claimed +11.6 abs on CTF agent benchmarks |
| [Cyber-Zero](https://github.com/amazon-science/Cyber-Zero) ([paper](https://arxiv.org/abs/2508.00910)) | **No** — repo archived, no data/weights | writeup-synthesized traces (dual-LLM terminal simulation) | repo `cc-by-nc-4.0` | N | ? (if ever released) | **Offensive** (CTF). Cyber-Zero-32B claimed +13.1 abs |
| [feyospace](https://huggingface.co/feyospace) models ([paper](https://arxiv.org/html/2609.08418v1)) | data **No**, weights **Yes** | paper claims 164,269 SFT traces (not released); weights public with **no license** | none stated | N | **N (off-limits)** | **Offensive.** Data engine built on provider-ToS circumvention → see §3 |
| CAI Dataset ([paper](https://arxiv.org/pdf/2605.28146)) | **No** (not public) | 230,935 real operator session logs | commercial-license-only | N | N (off-limits) | **Offensive** real red-team logs; PII/GDPR-sensitive; paid license only |

---

## 2. Verdict — three tiers

### Tier 1 — Commercial-product-usable (permissive license + clean provenance)

**1a — cleanest:**
`stasvinokur/cve-and-cwe-dataset` (CC0, NVD) · `xamxte/cve-to-cwe` (CC-BY) ·
`trendmicro-ailab/Primus-Seed` (ODC-BY) · `trendmicro-ailab/Primus-FineWeb` (ODC-BY, CPT corpus) ·
`LLM4Binary/decompile-ghidra-100k` (MIT) · `infosecn1nja/soc-triage-opensec-chat` (CC-BY) ·
`FineEnvs/MiMo-V2.6-RL-harbor-cyber` (Apache-2.0; **RL environments**, generate your own traces).

**1b — permissive *tag* but output generator undisclosed → confirm with the publisher before shipping
(if an OpenAI/other-provider model generated the outputs, they drop to Tier 2 on ToS grounds):**
`Trendyol/...Cybersecurity-Instruction-Tuning` · `AlicanKiraz0/Fenrir-v2.1` · `pAILabs/infosec-security-qa` ·
`CyberNative/Code_Vulnerability_Security_DPO` · `kala185/comptia_security_pluse_701` (exam-eval contamination watch).

### Tier 2 — Research / internal-only (adds NC, research-licensed, academic-gated, and LLM-output-tainted sets; the model is never shipped)

`reloading0101/threat-intelligence-dataset` (CC-BY-NC-SA; best-grounded CTI) ·
`oi-uae/cyber-security` (research-only NC, gated) · `zefang-liu/cve-and-cwe-mapping` (CC-BY-NC-SA) ·
`trendmicro-ailab/Primus-Instruct` (GPT-4o taint) · `almedamine/CTI_RCM_Training` (GPT-4o taint) ·
`trendmicro-ailab/Primus-Reasoning` (⚠ CTI-Bench contamination — use only if not evaluating on CTI-Bench) ·
`jcordon5/cybersecurity-rules` (rule + distill-model licenses) ·
`WhitzardAgent/CyberAgentTrace` (gated, defensive-only — the best usable agentic traces) ·
`WhitzardAgent/CyberSecurity-1M`/`100B` (**conditional**: academic-only gate; a company's internal R&D likely
does not qualify) · `Pentest-R1`, `justinwangx/CTFtime` (**Unclear** — downloadable but unlicensed +
third-party copyright) · `CTF-Dojo`/`Cyber-Zero` (CC-BY-NC, but not actually released).

> None of the CC / Apache / ODC-BY licenses above contain a "no derivative models" clause — they all permit
> model training. The constraint in Tier 2 is non-commercial / gating / provenance, not an anti-derivative clause.

### Tier 3 — Off-limits even for internal research (tainted provenance or absent rights)

- **feyospace (data *and* weights)** — the paper's own data engine centers on provider-ToS circumvention
  (recovering plaintext from providers' encrypted reasoning blocks, gray-market pooled accounts,
  "effectively unlimited jailbreak attempts"); weights carry **no license**. Training on or distilling from
  this inherits the taint.
- **CAI Dataset** — real red-team operator logs, no public download, commercial-license-only, PII/GDPR.
- **ChaoticNeutrals/Cybersecurity-ShareGPT** — license unspecified + derived from scraped ChatGPT output.
- **Vyber07/cyber-security** — opaque bulk repackaging that re-hosts third-party data without clear rights.
- **clydeiii/cybersecurity** — `license:unknown`; redistributes copyrighted vendor APT report text.
- *(segolilylabs/Lily-Cybersecurity — not off-limits, simply never released / unavailable.)*

---

## 3. Evaluation benchmarks — do NOT train on these

These are measurement sets; training on them contaminates your evaluation.

[cais/wmdp](https://huggingface.co/datasets/cais/wmdp) (WMDP-cyber) ·
[AI4Sec/cti-bench](https://huggingface.co/datasets/AI4Sec/cti-bench) (source of CTI-MCQ / CTI-RCM / CTI-VSP / CTI-ATE) ·
[XuanwuAI/SecEval](https://huggingface.co/datasets/XuanwuAI/SecEval) · CyberMetric ·
[zefang-liu/SecQA](https://huggingface.co/datasets/zefang-liu/SecQA) · CISSP-llmbench ·
[sunblaze-ucb/cybergym](https://github.com/sunblaze-ucb/cybergym) · Cybench · NYU CTF Bench · InterCode-CTF.

**Contamination flags (dedup before training if these are among your eval sets):**
- `Primus-Reasoning` and `almedamine/CTI_RCM_Training` are derived from **CTI-Bench** → they contaminate
  CTI-MCQ / CTI-RCM evaluation.
- `MiMo-V2.6-RL-harbor-cyber` and `CyberAgentTrace` (config `real_arvo`) draw on **ARVO/OSS-Fuzz** → they
  overlap **CyberGym**.
- CTF-Dojo / Cyber-Zero / CTFtime all derive from CTFtime writeups that also seed Cybench / NYU CTF →
  writeup-level decontamination needed.

---

## 4. Coverage gaps (likely need to be built in-house)

- **Defensive agentic trajectories** (SOC triage, incident response, detection-rule authoring, log/forensics
  tool-use) — essentially none public; every released agentic set is offensive-oriented.
- **Non-English (e.g. Korean) cybersecurity SFT** — effectively absent (data is English, plus en/zh in one set).
- **Malware-analysis / RE explanatory Q&A** — a real gap; only decompile/binary code-pair sets exist.
- **Clean training MCQ** — mostly evaluation sets; little clean training MCQ without eval overlap.
- **License hygiene overall** — most permissive-*tagged* instruction sets are LLM-generated with the teacher
  model undisclosed, which is the single biggest blocker to a clean commercial training mix.

---

## 5. Two practical paths

- **Shipping a commercial model:** the clean pool is small and mostly knowledge/text. A defensible base is
  **public-domain first-party sources (NVD, MITRE ATT&CK/CWE/CAPEC)** plus `Primus-Seed`, and for agentic
  ability, **generate your own trajectories inside an openly licensed environment set** (e.g.
  MiMo-harbor-cyber) rather than reusing scraped traces.
- **Research / internal-only model:** the pool is much larger — add `CyberAgentTrace`, `reloading0101` CTI,
  `oi-uae`, etc. — but **exclude CTI-Bench-derived sets** if you evaluate on CTI-Bench, and **exclude
  ARVO-overlapping sets** if CyberGym is a target. Decontamination is non-negotiable because several
  training sets are derived from popular benchmarks.

---

¹ Permissive tag, but the output-generation model is undisclosed; confirm it before relying on the license for
a shipped product (provider ToS on model outputs can override a permissive dataset tag).

² Academic-only gate; a for-profit's internal R&D likely does not qualify, and an institutional email is
required.

---

*Sources: Hugging Face dataset cards and API for each repo linked above; GitHub repos for the agentic
resources; arXiv [2502.11191](https://arxiv.org/abs/2502.11191) (Primus),
[2508.18370](https://arxiv.org/abs/2508.18370) (CTF-Dojo),
[2508.00910](https://arxiv.org/abs/2508.00910) (Cyber-Zero),
[2508.07382](https://arxiv.org/abs/2508.07382) (Pentest-R1),
[2609.08418](https://arxiv.org/html/2609.08418v1) (Feyospace),
[2605.28146](https://arxiv.org/pdf/2605.28146) (CAI). License tags were cross-checked against card/gate body
text. Verified around 2026-11-11; re-check before relying on any entry.*

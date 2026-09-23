# Phase 2: AI Engineering Foundations

**Main source:** 🤖 [roadmap.sh/ai-engineer](https://roadmap.sh/ai-engineer) (see also [AI Agents](https://roadmap.sh/ai-agents) and [Prompt Engineering](https://roadmap.sh/prompt-engineering))

**Goal:** know how modern LLM applications are actually built: models, prompts, context, retrieval, tools, and agents.

**Security angle:** you can't threat-model a system you don't understand. For every item below, write down **what the trust boundary is** and **what an attacker could control**.

## Checklist

### How LLMs work
- [ ] Tokens, context window, and why "instructions" and "data" share one channel ← *root cause of prompt injection*
- [ ] Sampling: temperature, top-p/top-k; non-determinism
- [ ] Model types: closed vs. open-weight, hosted APIs vs. self-hosted (Ollama, etc.)
- [ ] Pre-training vs. fine-tuning vs. RAG: when to use which

### Building with model APIs
- [ ] Calling a model API directly (messages, system prompt, streaming)
- [ ] Structured output (JSON schemas) ← *also a security control: narrows the output format*
- [ ] Prompt engineering: zero/few-shot, chain-of-thought, ReAct, role prompting
- [ ] Context engineering: what goes into the context and from where ← *every source is an input to validate*
- [ ] Cost, latency, and prompt caching

### Embeddings & RAG
- [ ] Embeddings and semantic search
- [ ] Vector databases (e.g. Chroma, pgvector, Qdrant)
- [ ] Chunking, indexing, retrieval, reranking
- [ ] RAG with metadata filters ← *the access-control layer: can user A retrieve user B's documents?*

### Tools, agents & MCP
- [ ] Function / tool calling
- [ ] Agent loops, memory, multi-agent setups
- [ ] Model Context Protocol (MCP): hosts, clients, servers, local vs. remote transport
- [ ] Build a tiny MCP server and client ← *then attack it in Phase 3*

### Evaluation & operations
- [ ] Evals: deterministic, model-graded, human; regression testing
- [ ] Observability: tracing and logging of prompts and tool calls ← *your future incident-response evidence*
- [ ] Guardrails, content moderation, input/output constraints
- [ ] AI safety basics: bias, fairness, misuse

### Mini projects
- [ ] A simple RAG chatbot over my own notes (this repo)
- [ ] A tool-using agent with one harmless tool, e.g. read-only file search

## Notes & resources I used

- (none yet)

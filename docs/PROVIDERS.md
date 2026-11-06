# Provider discovery and model selection — implementation plan

**Status: planned, not a working feature.** The current app only has health/bootstrap and model stubs. P15 approves new contracts/configuration; P16–P24 implement the feature; P25 measures real models. This document is a requirement, not a new wire/schema authority. Do not hand-edit generated API files to implement it.

## What the user should be able to do

1. Privately configure one or more provider keys on their own backend machine. No account, key, credit card or paid service is created automatically.
2. Open the model selector. See configured providers and local Ollama, with “key missing,” “unavailable,” “quota exceeded,” or “not tested” where appropriate. Missing optional providers must not stop the app.
3. Refresh to discover the current eligible text-generation models. Do not limit a provider to three models or hard-code a supposedly permanent free-model list.
4. See the exact provider/model, local versus hosted, compatibility, price/access confidence, discovery time and sanitized error. Catalog presence is not proof of inference access, quota or quality.
5. Select a model, explicitly consent to hosted synthetic-data inference, run one small synthetic compatibility test, then run the investigation using the same safety harness.
6. Keep manual work available during an outage. Never switch to paid/cloud inference automatically. Never automatically test every discovered model: tests consume quota and may cost money.

The coding assistant used by a teammate (Claude Code, Codex, Gemini, Antigravity, etc.) is **not** the product's inference provider. Changing that assistant must not change runtime permissions, contracts or acceptance tests.

## Names and free access

- **Groq** hosts models from different developers. A model ID starting `openai/` on Groq uses a Groq key, not an OpenAI key.
- The requested hosted provider is **Groq**. The active scope is Groq, Cerebras, Mistral, Gemini and OpenRouter, plus local Ollama/Llama. Do not add an unrelated provider because a spoken/transcribed name is ambiguous.
- **Cerebras** is the spelling of the inference provider.
- Free website chat, free key creation, open model weights, trial credits and a renewable free API tier mean different things. None implies unlimited free inference.

### Official discovery sources (checked 6 November 2026)

These are discovery endpoints, **not claims that every returned model is free or usable for this agent**. Recheck the linked terms at implementation/demo time. Model IDs and plans change; the live catalog and the user's account decide availability.

| Provider | Server-side model discovery | Cost/access caveat and official source |
|---|---|---|
| Ollama (local) | `GET http://127.0.0.1:11434/api/tags`; inspect local model metadata as needed | Installed models only; no API token fee for local inference, but hardware/electricity and licence restrictions apply. Exclude cloud-backed entries. [API](https://docs.ollama.com/api/tags), [local-only mode](https://docs.ollama.com/faq). |
| Groq | `GET https://api.groq.com/openai/v1/models`, bearer key | Free plan with account/model-specific limits; catalog is not a billing entitlement. [Models](https://console.groq.com/docs/models), [limits](https://console.groq.com/docs/rate-limits), [plans](https://console.groq.com/settings/billing/plans). |
| Cerebras | `GET https://api.cerebras.ai/v1/models`, bearer key; public metadata at `/public/v1/models` | Current docs say a **$5, 30-day trial after verified payment method**, not a permanent free tier. Do not add a card/purchase without authorization. [Discovery](https://inference-docs.cerebras.ai/api-reference/models/list-models), [trial/limits](https://inference-docs.cerebras.ai/support/rate-limits). |
| Mistral | `GET https://api.mistral.ai/v1/models`, bearer key | Use `capabilities.completion_chat`; exclude embeddings/OCR/audio-only/classifiers. Check current account experiment/free entitlement; a free chat plan or open weights is not free API inference. [Discovery](https://docs.mistral.ai/api/endpoint/models), [API prices](https://docs.mistral.ai/inference/pricing). |
| Gemini Developer API | `GET https://generativelanguage.googleapis.com/v1beta/models`, server-held `x-goog-api-key` header | Follow page tokens and filter `supportedGenerationMethods` for `generateContent`; that alone does not prove structured-output support or free eligibility. Some models have free tiers, others do not; regions/projects differ. Free-tier content may be used to improve products. [Discovery](https://ai.google.dev/api/models), [prices/data use](https://ai.google.dev/gemini-api/docs/pricing). |
| OpenRouter | `GET https://openrouter.ai/api/v1/models` | Preserve exact catalog IDs, including `:free`; only listed free variants exist. Check all applicable request/input/output/reasoning charges and overrides, not just an ID suffix. Free quotas still apply. No paid fallback. [Catalog](https://openrouter.ai/docs/guides/overview/models), [free variants](https://openrouter.ai/docs/guides/routing/model-variants/free), [limits/pricing](https://openrouter.ai/pricing). |

Do not scrape provider websites or route personal documents through external tools. Use official documented APIs. Additional providers need a small reviewed registry entry, bounded adapter, tests and terms review, not an arbitrary “paste any URL” field.

## How to label price without pretending to know the account

P15 must approve the exact canonical types. The conceptual information below is **not a finalized JSON payload**:

- Model identity: provider, exact model ID, display name and local/hosted mode.
- Access: discovered, compatibility-tested, unavailable, or unknown; record discovery/test time separately.
- Cost basis: local compute, published zero-price, free-tier-eligible, trial credits, paid, or unknown. Store source URL/check date for reviewed entitlement metadata; never fabricate a remaining balance.
- Compatibility: text generation and schema support as supported/unsupported/unknown, plus measured test result. Disable unsupported entries; show a reason instead of silently dropping every uncertain model.
- Quota: display provider-reported limits/reset when available; otherwise “check your provider dashboard.” Do not infer free tokens from a successful catalog response.

Default hosted execution is disabled until the operator reviews the account's entitlement and explicitly allows the model. Paid and unknown entries remain visible but blocked by the no-paid policy unless the team explicitly approves a budget and enforceable provider spending controls. Free-tier accounts can have paid rates elsewhere; do not use zero-priced metadata as a guarantee against billing. Trial status must show expiry when known. Revalidate before inference; stale/unverifiable cost entitlement fails closed, not “probably free.”

## Small implementation, same safety boundary

- Keep keys in backend environment only. P15 decides provider-specific key names and any compatibility for `LLM_PROVIDER=hosted`; until then `.env.example` is the only supported configuration reference. Never use `VITE_*` secrets, browser storage, prompts, screenshots, audits or catalog responses for keys. Redact headers and raw provider error bodies.
- Use a small explicit registry of approved endpoints/transport type, not a plugin framework. Reuse an installed HTTP client. OpenAI-compatible transport is a wire format, not a promise of identical schema support or free access. Gemini may use a small native adapter to avoid forcing incompatible schemas through a generic SDK.
- Discover only configured hosted accounts; local-only mode makes **no hosted discovery or inference calls**. Bounded parallel requests per provider; a short cache with timestamp/manual refresh; timeouts, bounded response bytes/model count/pages and validated metadata. One provider's failure cannot erase successful results from the others. No model downloads.
- For Ollama's own process, current official local-only controls are `OLLAMA_NO_CLOUD=1` or `disable_ollama_cloud: true` in its server configuration, followed by restarting Ollama. Setting an app `.env` variable alone does not reconfigure an already-running Ollama desktop/service process. P17/P28 must verify this on the demo machine; keep its bind address on loopback.
- Never follow arbitrary response-supplied URLs or redirects with credentials. For pagination, validate the exact approved origin/path and bounded page/token values. No credentials on a different origin. Ollama is a server-approved loopback origin, not a browser-supplied URL; reject cloud models and configure Ollama local-only where supported.
- Catalog refresh performs no inference. Explicit “Test model” sends only a tiny synthetic example, counts attempts and states it consumes quota. It is a compatibility check, not business-quality evaluation. Raw chain-of-thought is neither requested nor logged.
- P15 defines who may list/test/select models. Use an authenticated, server-authorized operator policy; do not silently make every employee an administrator or invent a new role on one branch. Browser sends only approved opaque selection/model IDs, not keys/base URLs. Add rate limits to refresh/test/select.
- Selection is installation-wide for this single-worker demo, restricted to the authorized operator. Snapshot exact provider/model/config revision on case admission; resumed work keeps it. Changes affect new cases only. If the selected model disappears/fails, pause/escalate; no silent switch or model-ID substitution. P15/P26 approve durable metadata and migrations before this is implemented.
- Every adapter returns the existing `NextStep` envelope. Server validates schema, evidence, scope, allowed reads, budgets and human approvals. A provider's built-in browsing/code execution tools remain disabled. Count retries/repairs against existing 12-call/16-read budgets, 30-second call/90-second active-run limits.
- OpenRouter must use an explicit selected model, no random `openrouter/free` routing for reproducible evaluation, no paid fallback array, and approved data-policy routing. Disclose that it is an intermediary and record returned serving-model/provider metadata where available.

## Required evidence before calling a provider working

- Mock tests for catalog pagination/filtering, missing/invalid key, timeout/429, malformed output, secret redaction, no paid/cloud fallback and selection authorization.
- A real selected-model synthetic smoke recording provider/model/date/config revision and exact success/failure, without keys. No credential available = **not run**, not passed.
- P25 runs the same held-out business scenarios, including injection/abstention and unsupported proposals. Compare evidence support, safe outcomes, latency, calls and cost confidence. Never rank quality using a model's marketing size or screenshot alone.
- Full integration must keep task claims separate from evidence and reservation separate from handover with every selected provider.

All six paths (Ollama/local Llama, Groq, Cerebras, Mistral, Gemini and OpenRouter) are requested scope, but do not defer the first working end-to-end journey until every account is available. Integrate one validated local or hosted path early, finish P17–P22 adapters and P23 shared eligibility tests, and clearly mark untested accounts. No live-validated claim without a live run.

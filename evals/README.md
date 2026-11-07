# Evaluation

Implemented: scenarios.json, answer_keys.json, run.py and historical JSON results under results/. Answers stay separate from runtime fixtures/prompts. The runner creates its own temporary SQLite database and never uses a teammate's working database.

## Commands from repository root

```sh
node scripts/python.mjs evals/run.py --provider stub --no-write
```

This runs **offline rules, not AI**. Without --no-write the runner writes a timestamped JSON report to results/. Current CLI choices are stub, ollama and hosted, not separate groq/gemini/etc. registry IDs.

Only after explicit operator authorization and private provider/model setup:

```sh
node scripts/python.mjs evals/run.py --provider hosted
node scripts/python.mjs evals/run.py --provider ollama
```

These are alternatives, not instructions to spend quota on both. Configure LLM_MODEL and the matching server-side endpoint/key privately; do not put secrets in shell history. Missing configuration reports NOT RUN, not a pass. OnboardIQ port 8000 is not a model API: incoming /v1/models 404s do not diagnose a missing key. Set the matching provider base/model/key using [root troubleshooting](../README.md#app-health-is-not-a-model-endpoint); /api/health/ai is configuration-only, not an inference check. No model download or paid upgrade is authorized here.

[Historical results](../docs/EVALUATION.md) cover one live Groq model and offline rules. Search was tuned on part of the scenario set; newer questions are untuned but not independently held out. The runner's zero exit is report completion, not a guarantee of zero misses—inspect summary/rows. A stub tests retrieval/controls, not model competence. Independent held-out scoring and same-scenario provider comparison remain pending/deferred.

Keep future wrong-role, stale/duplicate, restart, injection, unavailable-source, missing-handover and model-outage cases. Record exact model/config/prompt/fixture versions, failures, latency and cost confidence; never invent accuracy or savings. Extra providers/discovery remain the [roadmap](../README.md#ai-keys-and-providers), not an implemented six-provider claim.

# Evaluation results

These are measured results. Rerun them with:

```sh
node scripts/python.mjs evals/run.py --provider stub
```

Raw output is in `evals/results/`.

## What has been measured

Run on 2026-11-06 with `LLM_PROVIDER=stub`, which is offline rules and **not a real AI model**. This measures retrieval, permission filtering and the harness. It says nothing about the quality of a model's answers.

| Check | Result |
|---|---|
| Right source found, direct questions (tuned) | 20 of 20 |
| Right source found, reworded questions (tuned) | 10 of 10 |
| **Right source found, new questions added after tuning** | **5 of 11** |
| Correctly says "not available", missing topics (tuned) | 10 of 10 |
| **Correctly says "not available", new missing topics** | **5 of 5** |
| Personal or legal advice refused | 8 of 8 |
| Restricted text shown to someone without access | 0 |
| Injection attempts that exposed restricted text | 0 of 10 |

## How to read this

- **The honest search number is 5 of 11.** Before tuning, reworded questions scored 2 of 10. A small synonym list fixed the tuned set, but new wording still often fails. The failure is a safe one: the assistant says it doesn't know and offers HR, instead of guessing.
- **This is the gap embeddings would address.** The blueprint called for adding embeddings once a recall gap was measured. It's now measured, but building it needs a tested embedding model, and none was available on the build machine.
- **The questions are not independent.** One author wrote all of them. The "new" questions are untuned, not independently held out. A teammate should write a fresh set.

## What has not been measured

**No real model has been run.** Ollama was not installed and no hosted key was available, so these are **not run**, not passed:

- Answer groundedness and usefulness on a real model
- Extraction accuracy on a real model
- Investigation quality on a real model, compared with the rules-only baseline
- Live latency and token use
- Injection resistance of a real model. Tests show that a model holds no authority, and the harness rejects invalid output. They don't show how a specific model behaves.

To measure them, use one of these commands. A provider that isn't configured prints `NOT RUN`.

```sh
LLM_MODEL=<installed tag> node scripts/python.mjs evals/run.py --provider ollama
```

```sh
LLM_MODEL=<model id> LLM_BASE_URL=https://api.groq.com/openai/v1 LLM_API_KEY=<key> node scripts/python.mjs evals/run.py --provider hosted
```

Check the model's licence and acceptable-use terms first, as the brief requires.

## Control tests

`npm test` runs these using scripted model replies. They prove the controls, not model quality.

| Control | Test file |
|---|---|
| Sessions, lockout, role and scope denial | `test_auth.py`, `test_acceptance.py` |
| Plans, dependencies, due dates, statuses, escalation | `test_planning.py` |
| Upload attacks, private files, human-only verification | `test_documents.py` |
| Fabricated citations, invalid output, retrieval access | `test_knowledge.py` |
| Durable pause, budgets, restart, scope recheck, outage | `test_agent.py` |
| Approval, stale data, races, duplicates, read-back | `test_actions.py` |
| The full journey, and the workflow with AI turned off | `test_integration.py` |

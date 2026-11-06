# Evaluation results

## What has been measured

Run on 2026-11-06. Raw output for both runs is in `evals/results/`.

**Live model:** `openai/gpt-oss-20b` on Groq, free plan, 8,000 tokens per minute. **Offline:** `LLM_PROVIDER=stub`, which is rules and not AI.

| Check | Live model | Offline rules |
|---|---|---|
| Right source retrieved, direct questions (search was tuned on these) | 20 of 20 | 20 of 20 |
| Right source retrieved, reworded questions (search was tuned on these) | 10 of 10 | 10 of 10 |
| **Right source retrieved, new questions added after tuning** | **5 of 11** | **5 of 11** |
| Answer cited the expected source | 25 of 30 (the other 5 hit the rate limit) | 30 of 30 |
| Answers that reached the model and passed validation | 31 of 31 (1 needed the repair attempt) | Not meaningful |
| Correctly says "not available", missing topics | 10 of 10 | 10 of 10 |
| Correctly says "not available", new missing topics | 5 of 5 | 5 of 5 |
| Personal or legal advice refused | 8 of 8 | 8 of 8 |
| Restricted text shown to someone without access | 0 | 0 |
| Injection questions that exposed restricted text | 0 of 10 | 0 of 10 |

**Full path on the live model, final run:**

| Step | Result |
|---|---|
| Investigation | Asked HR which location was correct, waited, proposed the location change, then proposed a Bengaluru laptop after approval. Final state Resolved, in 9 model calls and 4 reads. The final outcome read "LAPTOP_22 reserved; collection pending." |
| Injected document | Extraction returned normally. The document stayed Under review, and no restricted text appeared. |
| Insights summary | Passed validation, with 3 recommendations. |
| Offer letter extraction | **Hit the rate limit in the final run** because it followed the question burst, and returned the "review manually" path. In the run before it, on the same extraction prompt, it found all four fields and the location mismatch. |

## How to read this

- **The free plan's rate limit is the main live problem.** 7 of 39 calls in the question burst failed with it. The app waits briefly and retries, then shows a clear manual path, but a long wait is visible. Space out AI actions when recording, or use a paid tier.
- **The honest search number is 5 of 11.** Before tuning, reworded questions scored 2 of 10, and a small synonym list only fixed the tuned set. The failure is a safe one: the assistant offers HR instead of guessing. Embeddings would address this, and they are not built.
- **Citations are checked, meaning is not.** Code proves each quote exists in the cited passage. Nobody has scored whether every live answer is fully correct and useful.
- **The questions are not independent.** One author wrote all of them. The "new" questions are untuned, not independently held out.
- **Investigation behaviour varies.** One full run isn't a measured success rate. An earlier prompt version sometimes skipped the documents, which is why the prompt now states the order of work.

To rerun:

```sh
node scripts/python.mjs evals/run.py --provider hosted
```

```sh
node scripts/python.mjs evals/run.py --provider stub
```

Check the model's licence and acceptable-use terms before submission, as the brief requires.

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

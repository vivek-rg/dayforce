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
- **The historical untuned search number was 5 of 11.** Before tuning, reworded questions scored 2 of 10. The 7 November regression follow-up below is a separate, now-tuned result. Missing reliable context still sends the question to HR rather than guessing; embeddings are not built and are not guaranteed to solve every miss.
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

## Retrieval regression follow-up — 7 November 2026

After reviewing the six H misses, search now normalizes common phrases such as "time off" and "didn't use", and expands a small reviewed vocabulary (for example ID/identity and notice/advance). The existing 60% term-coverage gate, SQL permission filtering and citation validation remain unchanged. No answer text is hardcoded and no embedding dependency was added.

`evals/run.py --provider stub --no-write` retrieved the expected source for 20/20 direct, 10/10 paraphrased and 11/11 additional H regression questions, with 0 restricted-text leaks, 10/10 missing-topic abstentions and 5/5 additional missing-topic abstentions. Six differently worded unit cases also check the relevant policy section, and two new unrelated-topic cases check abstention.

**H was inspected to make this change, so 11/11 is regression coverage, not unseen accuracy.** Current reports use `additional_regression_*` metric names; original group IDs and historical JSON reports remain intact. This follow-up used offline rules only. No new live-model response, semantic accuracy, latency or independent held-out result is claimed.

## Final Desktop verification — 7 November 2026

The final check used the existing private hosted Groq configuration (`openai/gpt-oss-20b`) against temporary synthetic databases, not the working database. Credentials were used only for the configured provider authentication, not printed or stored in reports. No working employee documents were sent.

- The live policy assistant answered an unused-leave question and an onboarding-document question with validated citations. An unrelated spaceship-repair question returned `NOT_FOUND` without a model call.
- Live offer-letter extraction returned all four expected fields and the location mismatch. The injected document stayed `UNDER_REVIEW`, never became verified, and its extraction summary did not expose the checked compensation marker. Live insight summaries returned HTTP 200.
- Two investigations with the original 500-token allowance escalated after Groq reported that the completion limit was reached before valid JSON could be produced. The agent allowance is now 1,500 tokens, with a regression test confirming the limit sent through the hosted transport. Attempt/read/time limits, validation and human approval are unchanged.
- **The larger allowance does not establish reliable investigation completion.** A temporary 1,500-token run resolved after HR approved the location change and IT approved the reservation, with outcome `LAPTOP_22 reserved; collection pending.` A subsequent run using the actual updated source changed location only after approval, then escalated after invalid model output. An experimental low-reasoning run also escalated at the active time limit; that experimental setting was not added to the source. Do not describe the complete live AI investigation as consistently completing. Escalation is the supported handoff to a person, not a claim of completed onboarding; manual workflows remain available and can be demonstrated independently of model completion.
- Final `npm.cmd run check`: 224 backend tests, 59 frontend tests, lint, formatting, lockfile checks, TypeScript/Vite build and generated contracts passed. These deterministic tests do not override the live investigation failures above.
- Headless Chrome signed into all seven roles and checked 59 sidebar navigation pages. Desktop (1,440 px) and mobile-emulated (390 px) role home screens rendered without JavaScript exceptions, HTTP 5xx responses or page-level horizontal overflow. Mobile navigation opened and closed. Screenshots were inspected for sign-in, HR, IT, employee, payroll and manager views; this is not physical-device, complete accessibility or every-action browser coverage.
- The existing local database passed read-only integrity and foreign-key checks, and all recorded uploaded files existed. `.env` was unchanged. All 190 tracked files were present; PPTX archive integrity and PDF headers passed, not a content or consent review of submission assets. npm reported zero production-dependency advisories and ten moderate development/lint-tooling advisories. No forced dependency upgrades were performed.

This was a targeted live smoke/diagnostic session, not a full rerun of the live question benchmark or an independently authored model-quality evaluation. The historical JSON reports remain unchanged. The README demo-video link still needs its final recording URL from the team. Nothing was committed, pushed or deployed by this check.

## Fallback-first acceptance follow-up — 7 November 2026

The user clarified the acceptance rule: a model failure must leave a clear human recovery path, rather than requiring every model run to finish. The live failures above remain recorded; they are not relabelled as completed investigations.

A new parameterized API integration test covers timeouts, rate limits, rejected credentials, provider HTTP 500 and malformed JSON across all four AI operations. It verifies that policy questions can be sent to HR and answered, failed extraction still permits human verification, computed metrics remain unchanged when summary generation fails, and investigations notify HR and escalate without an unapproved change. The same test then completes a manually proposed location change through the usual human approval and executor. Existing tests cover AI-disabled operation, missing sources, unsafe citations, sensitive documents, unreadable scans and investigation budgets. These are deterministic fault-injection checks, not proof against every possible failure.

Escalated investigations now show a **Continue without AI** notice with a link to the onboarding plan. A headless Chrome check used a real application worker with AI disabled to verify this handoff and its plan link. The same browser check verified a light first visit despite an emulated dark device preference, saved dark-mode selection, theme switching when local storage is blocked, public guides, and Demo accounts email/password autofill followed by explicit sign-in. It used temporary synthetic data, not the working database or live model calls.

After these changes, `npm.cmd run check` passed with **229 backend tests and 66 frontend tests**, plus lint, formatting, lockfile checks, the production build and generated-contract checks. The README now starts with a plain-English visitor guide and manual fallback instructions; its existing technical and submission sections are preserved. A fallback cannot make an unreachable database/network work or restore discarded Render Free files; those limitations remain explicit.

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

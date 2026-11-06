# Thirty-hour delivery and marking evidence

## Working script (R06)

Seed first (see README). Priya's login is free, so HR creates her live.

1. **U_HR:** create Priya Sharma, engineer, office, **Hyderabad**, manager U_MANAGER, login U_PRIYA. Show the rule-based plan.
2. **U_PRIYA:** upload `fixtures/documents/offer_letter_priya.txt` as signed employment, and `government_id_priya.txt` as government ID.
3. **U_HR:** in document verification, run AI extraction and show the Bengaluru vs Hyderabad mismatch. Verify both, by a person.
4. **U_HR:** open an investigation on Priya's profile. It asks which location is right. Answer "Bengaluru". Approve the exact location change in the review inbox.
5. **U_IT:** approve the Bengaluru laptop. The result reads "LAPTOP_22 reserved; collection pending."
6. **U_MANAGER:** record buddy and first-week plan.
7. **U_PRIYA:** ask "How do I request a laptop?" and open the citation. Ask "Can I bring my dog to the office?", see "not available", and send it to HR.
8. **U_HR:** run the escalation check; Arjun's seeded overdue task escalates. Show dashboard and insights.
9. **Failure proof:** set `LLM_PROVIDER=none`, restart, and show that manual work continues. Show a stale or wrong-role approval being refused.
10. Finish the remaining owners' work to reach "Onboarding complete".

Label the offline-rules mode honestly in any recording. Use a real model for the AI segments once one has been evaluated.

## One story, not eight separate demos

Priya has an approved Hyderabad profile and Bengaluru offer text; equipment task is complete but only a reservation is recorded. Show a normal six-category plan first. Agent reads scoped records/policy and asks HR. Save/restart/resume. Show exact location diff and HR review, then separate IT reservation approval. Execute with versions/stable action ID; read back **Bengaluru equipment reserved; collection pending**. Keep unrelated completed training. Payroll remains independent and sanitized.

If location mutation cannot be finished safely, label its preview read-only and fully demonstrate one IT action. Never mark a stub/failed action as successful. Healthy cases must not get invented blockers.

## Recording allocation

| Minute | Visible proof |
|---|---|
| 0–1 | User problem, synthetic system boundary |
| 1–2 | Profile/location plan, all six categories, owners/dependencies |
| 2–4 | Actual model investigation, relevant source IDs, uncertainty |
| 4–5 | Authorized clarification, persisted human wait/resume |
| 5–7 | Exact proposal, correct separate approval, conditional action, read-back |
| 7–8 | Wrong-role or stale action blocked; no false delivery claim |
| 8–9 | Actual tests/evaluation results, healthy case, baseline comparison |
| 9–10 | Harness architecture, local/hosted setting, limits and next steps |

## Rubric checklist

- Product 25%: relatable failure + normal coordination + accountable resolution; measure observed outcomes/review steps, not invented savings.
- Harness 25%: typed validation, object/field permissions, narrow tools, budgets/timeouts, persisted pause, exact approval, stale/duplicate rejection, manual fallback.
- LLM 20%: genuine tool/clarification choices, approved-policy grounding, citations/abstention, live model evaluation separated from stub CI.
- Engineering 15%: consistent API/schema, pinned installs, CI, safe DB writes, sanitized traces, clean-clone run.
- Recording 15%: readable ten-minute working journey and evidence; five slides and accessible README link.

## Submission gate

Freeze new features three hours before the actual deadline (hour 27 in the original schedule). Keep fixes only. `npm run check`; rehearse `npm run build` + `npm start` + `SMOKE_BASE_URL=http://127.0.0.1:8000 npm run smoke` (PowerShell syntax in README). Confirm exact tested commit, provider configuration and safe synthetic fixture preparation on a new practice DB; no destructive reset is provided. No public server is needed.

Eight genuine consented resumes, real accessible video/VIDEO_LINK.md, five-slide PPTX+PDF, root README links, honest evaluation table and no secrets. Resume collection is requested by the team, not listed as an official PDF deliverable. Do not assert it is submitted before these assets exist.

Submission assets are not ignored and can be committed normally after consent, secret and file-size review. Name the actual tested inference provider: requested hosted options are Groq, Cerebras, Mistral, Gemini and OpenRouter plus local Ollama/Llama, not a completed six-provider claim.

## Database pitch — current versus future

The user reconfirmed the local-demo requirement. Say: “SQLite makes the prototype reproducible on each teammate's machine without a cloud database account. A shared hosted deployment would be evaluated on managed PostgreSQL with reviewed migrations and concurrency/security tests.” Neon is a focused PostgreSQL option; Supabase is another option when its extra services are needed. Neither is implemented here. Never imply that cloud hosting eliminates migrations or that SQLite implies low quality. See [database decision](DATABASE_DECISION.md); only describe implemented/tested controls as already working.

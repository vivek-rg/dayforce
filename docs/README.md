# Documentation map

- `ASSUMPTIONS.md`: confirmed inputs, 30-hour scope, dependency map and remaining manual decisions.
- `API_SPEC.md`: generated normative endpoint contracts, JSON examples, errors, authority and shared schemas. Regenerate with `npm run contracts`; never edit it independently.
- `openapi.json`: deterministic contract snapshot for any editor/API client.
- `DATA_MODEL.md`: tables, JSON columns, invariants, ownership and lifecycle.
- `DEMO_PLAN.md`: ten-minute flow, rubric proof and submission checklist.
- `VERIFICATION.md`: what foundation checks were actually run, with limitations.
- `../PHASES.md`: task ownership, copy-paste prompts and done checks.
- `TEAM_WORKFLOW.md`: plain-English daily commands, independent SQLite databases, backups, eight-track coordination and improvement review.
- `DATABASE_DECISION.md`: confirmed local-demo SQLite choice, comparison with Neon/Supabase/PostgreSQL/MongoDB and honest future migration requirements.
- `PROVIDERS.md`: planned live model discovery/selection, official provider sources, free/trial/paid distinctions and required safety checks. Not an implemented API contract.
- `../CHANGES.md`: append-only team handoff log.
- `../Topic_3_Final_Guide.md`: full product rationale and researched decisions; kept at root as requested.
- `../AI_Innovation_Challenge_University_Brief 1.pdf`: official problem statement and marking rubric.

Naming: uppercase descriptive names for team handoff documents; `openapi.json` is machine-readable. Add scenario results as `evals/results/<provider>_<model>_<UTC timestamp>.json`, not unversioned claims in docs. No real secrets or employee data.

For ordinary setup, read root README and TEAM_WORKFLOW first. API_SPEC and DATA_MODEL are technical references when implementing a phase. CLAUDE.md and GEMINI.md point to AGENTS.md so different coding tools follow the same handoff; there is no required branch-name pattern or coding-assistant vendor.

Current policy overrides historical planning/log text: Groq plus the other four named hosted providers and local Ollama are in scope; P23 is the shared eligibility gate. Submission assets are Git-eligible after review, not ignored. The original guide/PDF and old CHANGES/verification entries remain historical records; do not rewrite them to pretend an old decision/test happened under the new policy. Generated API_SPEC/OpenAPI stay generated and describe the actual unchanged SQLite foundation.

# Frontend modules

Install from root with `npm ci`; run `npm run dev` from root. Vite proxy forwards `/api` to loopback backend:8000. `npm run build` produces dist/; root `npm start` serves that build through FastAPI.

`src/features/overview` + `workspace`: Track 2. `src/features/my-work` + `review`: Track 3. Each folder exports its own component; Track 1 wires App.tsx/navigation/shared HTTP helpers/styles after review. Shared generated `src/shared/api-types.ts` comes from `npm run contracts`, never handwritten.

Current screen is a connectivity diagnostic, not onboarding UI. No authentication/key handling is implemented. Add co-located `*.test.ts(x)` tests; use explicit loading/denied/stale/empty/unknown states and keyboard labels. Never show mock success when the API returns 501.

P24 plans `src/features/model-settings/` for discovered provider/model selection after P15/P16 and a real adapter. This folder/routes do not exist yet. Track 2 owns that module; Track 1 separately wires navigation/session/API. Never add browser API-key inputs or VITE\_\* secrets. See docs/PROVIDERS.md for cost/privacy distinctions and server-owned selection rules.

Requested hosted scope is Groq, Cerebras, Mistral, Gemini and OpenRouter, plus local Ollama/Llama; P23 is an eligibility gate, not another provider. Browser traffic stays relative `/api`; database access remains on FastAPI. The confirmed SQLite local-demo decision does not require a Supabase browser client or any database credentials in React.

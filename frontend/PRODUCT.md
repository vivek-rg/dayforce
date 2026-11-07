# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

OnboardIQ serves everyone involved in a company's onboarding: HR, IT, Payroll, Benefits, Training, Managers and Employees. The user confirmed that every role should feel equally well served; this is not an HR-only visual redesign. Each person retains only their existing authorized records and actions. One company per installation, not a multi-tenant service.

## Product Purpose

Help each person understand their next onboarding action, who is responsible, what is blocked, and whether a completion claim has supporting evidence. Coordinate the joining process without replacing the people responsible for it. This promise was confirmed in the design interview on 7 November 2026.

## Positioning

Task completion and independently checked outcome are shown separately. When facts disagree, a bounded optional AI assistant can read permitted evidence, ask a responsible person, wait, and propose a narrow change. The correct person reviews it; trusted application code validates, executes conditionally and reads back the result. A reservation never means a laptop was delivered.

This is the product's design focus, not a proven market-uniqueness or customer-savings claim.

## Operating Context

- Existing React/TypeScript/Vite frontend, one FastAPI backend, SQLite and one local worker. Keep this stack and current functionality during the redesign.
- People use the website to create/review a hire, complete owned tasks, submit/review documents, record department work, answer questions and review allowed actions. Desktop work is primary, but the same existing actions must remain usable at narrow mobile widths.
- All demonstration data and policies are fictional. Private keys, passwords, databases, uploaded documents and personal submission assets must never become visual-design material or screenshots.
- Local working data must be preserved. The checked-in free Render setup is explicitly disposable/synthetic, not durable employee storage. Editing deployment source does not reconfigure an existing hosted service.

## Capabilities and Constraints

- Seven roles, approved profile/location rules, assigned tasks/deadlines/dependencies, separate evidence checks, document review, equipment reservation/handover records, payroll/benefits/training/manager records, notifications and scoped audit/insights screens exist.
- Policy guidance uploads are approved Markdown/TXT sources searched through SQLite FTS5. Uploading prose does not change executable onboarding rules. A website rule editor and project-specific private knowledge are not implemented.
- Four optional AI operations: policy answers, advisory document extraction, investigation next steps and advisory insight summaries. Manual workflows continue when AI is off/unavailable. Stub mode is scripted practice, not real AI. Quote validation is not a guarantee that every answer is correct.
- Hosted and Ollama transports exist. Historical live evidence covers Groq, not every provider or this installation's present configuration. Four provider credential variables in one private .env are a confirmed later requirement, not an implemented UI capability.
- Existing authorization, privacy, approval, stale/duplicate protection, exact outcomes, escaped text, native controls and manual fallbacks are non-negotiable. The visual redesign changes no API, permissions or core workflows. The only added functionality is explicitly requested static product education: public How it works and Role guide pages, also linked inside the authenticated Help navigation. Choosing a guide role never changes an account or exposes employee data.
- No paid service, model call, model download, new framework or dependency is authorized merely by a design choice. Do not expose model keys or invent a model selector, search action, filter, export, project feature or setting that the code does not support.

## Brand Commitments

- Keep the name **OnboardIQ** for now.
- User's desired tone: distinctive and easy to understand, with calm colours and clear usage. Use specific short working copy, not marketing language.
- Black and white are the brand palette: a near-black navigation/story region, white working surfaces and neutral greys. Small semantic colours remain for real warning/error/evidence states with written labels, not decorative accents. No gradients, including purple gradients; no default glassmorphism, decorative emoji, pulsing/status badges without real meaning, coloured side-border cards or cards nested inside cards.
- Choose readable typography suited to this product rather than default Inter/JetBrains Mono styling. Keep icons optically aligned and use the existing consistent icon language unless a separately approved improvement is needed.
- No hype words, stack-repeating copy, invented metrics/testimonials/logos/customers or landing-page greetings on working screens. Every visible element must serve a user task. The user explicitly rejected the sign-in 1/2/3 headline selector: use one fixed explanation and a labelled synthetic Claim / Proof example, with mobile prioritizing sign-in, not decorative content switching.
- Current user-directed revision: **Open Handoffs**, replacing the previous blue-grey Clear Handoffs styling because the user found it too plain. Use confident monochrome, stronger typography and a clear working hierarchy, inspired by—but not copied from—the Tenant Rights Checker reference, Vercel Geist and current startup interfaces. Source Sans 3 and separate Claim / Proof remain. Current visual authority: DESIGN.md; dated research/outcomes remain in CHANGES.md and docs/VERIFICATION.md. No video is needed.

## Evidence on Hand

- Source: backend/app/, frontend/src/, fixtures/policy_pack.json and synthetic fixture documents/knowledge.
- Recorded maintenance check on 7 November 2026: 175 backend tests, 37 frontend tests, lint/format/type/build/contract checks passed; details and limits in CHANGES.md and docs/VERIFICATION.md. These tests are not visual acceptance or real-model quality evidence.
- Historical model results and caveats: docs/EVALUATION.md. Do not relabel old results as a new live run.
- Current research references: Linear's March 2026 calmer-interface article, Asana's project list-view guidance and Stripe Dashboard documentation. These inform hierarchy and task clarity, not a claim that OnboardIQ supports their functionality.
- Clear Handoffs is a historical blue-grey revision. Current Open Handoffs evidence lives under ignored frontend/.impeccable/review-monochrome/; the latest user-requested sign-in simplification is under review-signin/. Chrome checks are viewport simulation, not real-device/accessibility certification or measured user savings. Latest results and limitations belong in docs/VERIFICATION.md.

## Product Principles

1. Serve every role clearly without widening what that role may see or do.
2. Make the next required action and the person responsible easy to find.
3. Distinguish a claim, checked evidence, an approval and an executed outcome.
4. Keep manual work dependable when models or networks fail.
5. Preserve product truth; distinctiveness comes from useful structure and craft, not decorative features.

## Accessibility & Inclusion

Native labelled controls, visible keyboard focus, readable contrast and non-colour status labels remain required. Preserve loading, empty, denied, stale, error and unavailable states. Check long text, zoom and narrow layouts. Respect prefers-reduced-motion; no autoplay audio or attention-grabbing motion. Desktop and mobile screenshots must be captured and inspected before claiming the UI is finished. The user subsequently requested restrained UI animation: use a finite product-specific Claim / Proof connection and fast control/menu feedback, without delaying forms, rotating copy, looping decoration or changing feature outcomes. Reduced-motion users keep static content and immediate state feedback.

## Open Decisions

The user approved the replacement visual world, typography/accent and section order on 7 November 2026, explicitly requiring unchanged features. Implementation/finish evidence is recorded in P10 and CHANGES.md; DESIGN.md describes the built system. The user subsequently approved one small illustrated pre-login animation and design touches on both static guides, citing hellyeahai.com. Use original monochrome assistant/laptop/document line art, finite motion then rest, compact responsive placement and a static reduced-motion alternative; never portray a live task or model result. No video asset is required. The actual submission deadline has not been supplied; optional feature work and provider expansion remain deferred.

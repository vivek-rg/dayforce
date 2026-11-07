# OnboardIQ — five-slide presentation handoff

**Owner:** presentation/submission teammate (Track 8). **Status:** researched brief and agent prompt only; no final PPTX/PDF has been generated or reviewed by this task. The recording teammate follows [video/script.md](../video/script.md); this file owns the presentation instructions, not a second product backlog.

## What the official PDF actually requires

Read [AI Innovation Challenge — University Brief](../AI_Innovation_Challenge_University_Brief%201.pdf), especially **page 3**. It explicitly requires a **five-slide final presentation** covering these five subjects:

1. Problem and user value.
2. Product workflow and demo.
3. Architecture and harness design.
4. Safety, testing and evaluation evidence.
5. Future improvements and expected business impact.

The same page requires a GitHub repository with setup/product/journey/architecture decisions and a **10-minute working-prototype/end-to-end demo recording**, added to the repository README. Page 2 defines our Topic 3: coordinate documents, equipment, payroll, benefits, training and manager tasks based on worker profile and location. It permits equivalent stacks, structured search/mock data and SQLite; orchestration frameworks are optional where valuable. Verify the chosen model's licence/acceptable-use terms.

**Not mandated by the PDF:** a specific template, Gamma, Canva, PowerPoint, colour palette, aspect ratio, animation style, file naming or a separate ten-minute slide lecture. Editable PPTX plus a matching PDF, 16:9, speaker notes and the black/white/red visual direction are our handoff choices. Do not add a sixth title, thank-you, team or references slide; integrate necessary credits into the five and put detailed citations in notes. The PDF lists 3–5 members with size subject to variation; organizer approval for eight and the actual deadline still need confirmation. Resume collection is a separate team request, not one of these three listed deliverables.

| Official judging category (PDF p. 3) | Weight | What the deck should make easy to assess                        |
| ------------------------------------ | ------ | --------------------------------------------------------------- |
| Product value                        | 25%    | A real onboarding problem and the exact demonstrated outcome    |
| Harness engineering                  | 25%    | Contracts, validation, scope, fallback and human authority      |
| LLM implementation                   | 20%    | Grounding, prompts, retrieval and useful model behaviour        |
| Engineering quality                  | 15%    | Source/API/testing/observability evidence, without overclaiming |
| Demo recording                       | 15%    | One understandable working story supported by the slides        |

These are judging weights, not predicted marks or a chance of winning.

## Research-based tool choice

Official documentation reviewed **7 November 2026**; capabilities, credits and account entitlements can change. This is a fit-for-this-project recommendation, not an exhaustive ranking or a hands-on comparison.

| Route                                                          | Why use it                                                                                                                                                       | Important limits / handoff                                                                                                                                                                                                                                      |
| -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Gamma for a fast visual draft, then inspect exported files** | Supports PDF/PPTX; fixed slide sizes; speaker notes carry into PPTX. Five slides fit the currently advertised free per-prompt ceiling.                           | Free-plan exports have a Made by Gamma badge. Select all five cards/slides, not only the current one. Check Present Mode and exported layout; effects/interactive content/masters differ. Never buy an upgrade or strip vendor branding without authorization.  |
| **Canva if the teammate already works there**                  | Prompt-based presentation drafts, manual layout control and PPTX/PDF output.                                                                                     | Verify current AI/export entitlement and free vs Pro assets in that account. Use the Presentation design type. Do not promise identical editable diagrams, fonts, effects or notes after conversion; reopen the files.                                          |
| **Local editable PowerPoint (recommended agent fallback)**     | Maximum control over a custom diagram and exact five-slide count; no project upload required. Use existing PowerPoint tools, or PptxGenJS if available/approved. | PptxGenJS supports shapes, text and speaker notes, but creates PPTX, not a finished PDF renderer. Use installed PowerPoint/LibreOffice for PDF/rendering; report a missing exporter honestly. Do not modify root dependencies or buy/install services silently. |

**Choose one creation route, not three competing decks.** Gamma can accelerate composition; the deliverable is the checked local PPTX/PDF, not a web link or an AI-generated outline. Creativity comes from a product-specific story and diagram, not the vendor's default theme.

**Cloud boundary:** a repository-aware agent first reads the project locally and produces a sanitized slide brief. A cloud generator does not automatically understand a local folder. Never upload the entire repository, private .env, DB/uploads, sessions, resumes or personal documents. Gamma's individual-workspace training is allowed by default according to its current help page; review Data Controls and opt out before approved use. Opt-out does not make the service local/private storage. Check deck and workspace sharing separately; do not publish automatically. Ask the owner before any cloud upload, account login, credit use, paid feature or sharing change. Only explicitly approved synthetic screenshots and sanitized text may leave the machine.

## Creative direction — “The Proofline”

An original editorial engineering story: one handoff travels from **claim** to **checked evidence**, with the human decision visibly in between. A recurring red connector and paired Claim / Proof labels tie the slides together. The line must end at the **actual observed outcome**, not turn every task into a success.

- Keep **OnboardIQ**, current black/white/red: ink #141414, white #ffffff, deep red #b4232c, quiet #f7f7f7 and neutral rules. Use light red #ffb4b8 if red text/lines must sit on black; check contrast. Red is a brand/review cue, not proof of completion.
- Mostly open white layouts; one considered black architecture region for contrast. Strong typography, deliberate alignment, generous space, original thin-line diagrams and tightly cropped real synthetic UI captures. No stock HR handshake photos, purple gradients, glass panels, random robots, icon-card grids, fake dashboards or walls of logos.
- Five different compositions in one system: opening contrast; workflow storyboard; system cutaway; evidence ledger; future experiment map. The creativity must survive static PDF export.
- Fixed **16:9**, normally 13.333 × 7.5 inches. Aim for 34–44 pt headings, 22–26 pt body, 18 pt or larger meaningful diagram labels. Short source footers may be smaller, but never hide qualifications in unreadable text. Cut content rather than shrink the whole slide.
- One conclusion and one main visual per slide; aim for 35–60 visible words excluding short diagram labels/citations. Architecture may need more labels, not a paragraph. Put technical depth, sources and narration in notes.
- Editable text/shapes for headings, architecture and labels; screenshots can be raster. Do not flatten an entire slide into an AI image. Preserve reading order, meaningful alt text, contrast and non-colour state labels.
- Optional simple fade only; no autoplay dependency, embedded demo video requirement or transition needed to understand the PDF. A screenshot or diagram can illustrate a step, not pretend a real operation occurred.

## Copy-ready prompt for the repository-aware generation agent

Copy the complete block below into an agent that can access this project. If it only has a chat window, attach approved public project documents and sanitized evidence instead; do not assume it can see the folder. The repository agent should give Gamma/Canva only its approved, sanitized five-slide content—not this whole repository-inspection prompt.

```text
You are the presentation designer and evidence-minded technical storyteller for OnboardIQ. Produce the actual final project presentation, not merely suggestions. Read the repository first; create exactly FIVE slides, aligned with the original challenge PDF and the recording script. Do not build features or alter the application to make the pitch easier.

1. READ AND ESTABLISH TRUTH
- Follow AGENTS.md and claim a small presentation-only task/owner/file boundary in docs/decisions/2026-11-07-improvement-plan.md before writing.
- Read AI_Innovation_Challenge_University_Brief 1.pdf (all 3 pages; p. 3 owns slide topics and rubric), root README.md, this ppt/README.md, video/script.md, frontend/PRODUCT.md and DESIGN.md, newest CHANGES.md/docs/VERIFICATION.md entries and docs/EVALUATION.md with the relevant evals/results evidence.
- Understand the implementation through backend/app/main.py, shared/contracts.py and schema.sql, auth permissions, planning/evidence/documents/knowledge, agent worker/graph/tools, ai harness/prompts/providers and actions service. Follow relevant callers/tests to confirm the claims you plan to show. Contracts explain data/API shape; do not copy the entire schema onto a slide.
- Inspect current UI using an isolated synthetic practice DB/profile and the documented startup. Do not open private .env, real DB/uploads, keys or resumes. Preserve working data and other contributors' changes.
- Build a short claim-to-source list in speaker notes: implemented / automated-test evidence / historical live-model evidence / proposed. Resolve contradictions against current source, not an older aspirational diagram. Report uncertainty rather than inventing a feature.

2. PICK A DELIVERY ROUTE AND DELIVER FILES
- Use the Proofline direction in this handoff. Prefer an existing authorized presentation tool; Gamma/Canva may draft only with explicit cloud/account/credit permission and approved sanitized inputs. Check current official export/privacy guidance linked below. Never upload the repo or buy a subscription.
- If cloud tools are unavailable, build a custom editable local PPTX with installed PowerPoint tooling or available/approved PptxGenJS. Do not add a project dependency, alter a lockfile or install tools globally without approval. A small local generator is acceptable if its installation is approved; no generic slide framework is needed.
- Deliver ppt/dayone_proof_final.pptx and ppt/dayone_proof_final.pdf with the SAME exactly five slides in the same order. Preserve existing artifacts; ask before overwriting someone else's files. Keep necessary editable source/assets under an agreed ppt/ boundary and explain regeneration in this README if used. No placeholders renamed to final binaries.
- Include speaker notes inside PPTX; also supply the final narration/click cues in the existing ppt/README.md for the video teammate. If notes do not survive export, repair them locally. A share link is optional and permission-gated, not a substitute for files.
- If PDF export or rendering is unavailable, finish what you genuinely can, state the precise missing tool/action and do not claim both files or visual QA are complete. Do not stop at a prompt if actual creation/export is possible.

3. USE THESE EXACT FIVE TOPIC SLOTS, WITH ORIGINAL VISUAL COMPOSITIONS

SLIDE 1 — PROBLEM AND USER VALUE
Working title: “A completed task is not a ready employee.”
Combine the product identity and problem on this slide; no separate cover.
Show two large adjacent facts: a completion claim versus the evidence it does NOT establish. Example: “Equipment task completed” / “Reservation recorded; handover unknown.” Label it illustrative if not taken from the actual demonstrated state.
Explain practical value: one profile/location-based plan, clear next owner and independently checked outcomes across HR, IT, Payroll, Benefits, Training, Manager and Employee. Do not invent customers, saved hours, ROI, market size or adoption.
Visual: editorial split composition, red line stops at the gap between Claim and Proof. Small visible “Synthetic demo / simulated external systems” note. One concise takeaway, not a list of every screen.

SLIDE 2 — PRODUCT WORKFLOW AND DEMO
Working title: “Follow Priya. See each handoff.”
Show the six work areas: documents, equipment, payroll, benefits, training and manager tasks. Separate roles from work categories; seven roles does not mean seven agents.
Use the real journey: HR creates the hire -> approved rules generate owners/deadlines/dependencies -> Priya uploads a synthetic Bengaluru offer against a Hyderabad profile -> scoped investigation asks HR and persists the wait -> HR answers/reviews the exact location/plan change -> IT separately reviews the reservation -> execution reads back “reserved; collection pending.” Other departments retain independently owned work.
Keep the detailed exception sequence in notes if needed for legibility; never turn the location approval into IT approval or reservation into delivery. Use one/two current synthetic screenshots only where they are readable; use editable labels around them. Do not fabricate successful model output or screenshot data.
Make the normal workflow and bounded exception recovery visually distinct. The agent assists a case opened by a user; no autonomous global case-discovery service is claimed. Prompt-to-hire is NOT part of the implemented journey today.

SLIDE 3 — ARCHITECTURE AND GOVERNED HARNESS
Working title: “AI proposes. Trusted code controls.”
Create the deck's main original, editable architecture cutaway, not a stack-logo wall. Show the runtime and trust boundaries with labelled arrows:
- React + TypeScript + Vite role UI -> relative /api -> FastAPI/Pydantic identity, scope and input boundary.
- Domain services: rules/tasks, evidence/documents/approved knowledge, department records, notifications/analytics.
- SQLite application state/FTS5 plus private sibling uploads; durable cases/questions/counters/work queue live in application tables. One local worker advances one bounded investigation loop.
- Governed AI path: authorized context/allowlisted reads -> versioned prompts -> one explicitly configured transport/model -> JSON/Pydantic + semantic validation -> bounded repair or manual fallback. Approved knowledge uses FTS5 structured retrieval, not a vector database.
- A proposal goes through the correct HUMAN reviewer, then current identity/versions/expiry -> conditional local write -> audit + read-back -> exact evidence outcome. No model-to-database write arrow, browser-to-provider key flow or automatic approval.
Show the model/network boundary separately from the local application. Use about 8–10 readable grouped nodes; put subordinate module names/decisions in notes. Explain four advisory/registered operations in notes: policy answers, document extraction, investigation next steps and insight summaries.
State current reality: one backend, SQLite, one worker, one bounded loop; no required LangGraph/checkpointer, eight-agent architecture, deployed PostgreSQL, real Dayforce/payroll/insurer integration or model-selector catalog. Historical live inference: Groq-hosted openai/gpt-oss-20b. Ollama transport exists but is not live hardware-accepted; Gemini/Mistral compatible settings are unverified candidates. Show only the actual chosen model on the main diagram, not pretend all providers were validated.

SLIDE 4 — SAFETY, TESTING AND EVALUATION EVIDENCE
Working title: “Show the proof—and its limits.”
Design a concise evidence ledger with visibly distinct “Automated controls” and “Historical real-model evidence” columns, not one giant accuracy score.
Controls: role/scope denial, human-only approval/verification, stale/duplicate protection, persisted human wait/restart, validated output/citations, manual outage path, audited read-back. Choose three/four for visible labels; map them to real tests in notes.
Use current verified counts/date/revision from docs/VERIFICATION.md, not copied old counts. At this handoff's preparation, the recorded Nov 7 local run is 182 backend tests, 56 frontend tests and 246 Chrome route/viewport checks; recheck before using them. If you did not rerun, say “recorded run”, not “tested by me”. Do not say remote CI or every device passed.
Historical Nov 6 Groq evidence includes an investigation that reached “LAPTOP_22 reserved; collection pending”; that is one run, not a success rate. Keep untuned source retrieval 5/11 and quota interruptions visible, with denominator/context. Citation/JSON validation is not independent semantic correctness. Stub is “Offline rules—not AI”. No blended percentage/100%-verified claim or invented latency/cost/savings.
If newer genuine evidence supersedes this, verify and cite it with its own date/model/method. No model calls are authorized just to refresh the slide. Do not conceal known limits in tiny notes.

SLIDE 5 — FUTURE IMPROVEMENTS AND EXPECTED BUSINESS IMPACT
Working title: “Less repeated entry. The same accountability.”
Show three precise proposed improvements, not a fantasy enterprise roadmap: HR prompt -> editable draft -> HR confirmation -> existing automatic plan; better grounded retrieval validated on independently authored unseen questions; structured rule editing with preview/versioned publication.
Clearly label all unimplemented pieces PROPOSED; the existing manual HR form is not prompt-to-hire. Keep required approvals and independent evidence checks. Do not depict auto-payroll, delivery, multi-company tenancy, vector infrastructure or PostgreSQL migration as done.
Pair each with an impact hypothesis AND an evaluation method: fewer repeated field entries measured in a timed same-task study; better supported answers measured on unseen questions; fewer plan-setup edits measured against the current approved-rule flow. No numerical target represented as measured savings. Future impact is expected/hypothesized, not observed customer ROI.
Close with the current value: “Clear work. Accountable handoffs. Checked outcomes.” Integrate any approved team credit here; no sixth thanks/contact/references slide.

4. DESIGN TO THE CUSTOM DIRECTION, NOT A DEFAULT AI TEMPLATE
- Fixed 16:9; black/white/red consistent with the current UI. Use an asymmetrical editorial grid, generous space, strong sans-serif type, thin rules and one recurring Claim/Proof connector. Five distinct compositions, one coherent visual system.
- Prefer editable native text, lines and shapes; real UI crops can be images. No whole-slide raster images, tiny terminal screenshots, stock HR photos, fake app UI, random robot stock art, gradients/glass or decorative 3-D clouds. No third-party logos implying affiliation.
- Keep the architecture understandable in the 55-second recording segment. Body normally 22–26 pt, meaningful diagram labels at least 18 pt. Use short visible statements and put technical depth in speaker notes. Reflow/cut before shrinking.
- Check contrast, alt text and reading order. Never rely on red alone for a state. Optional fade only; every exported PDF slide must tell the complete static story.

5. ALIGN WITH THE RECORDING; DO NOT WRITE A SECOND TEN-MINUTE TALK
Use video/script.md as the timing authority. Notes must give: short spoken lines, slide entry/exit cue, live screen/click handoff, source/date, and any failure-safe wording.
- Slide 1 supports M8's 0:00–0:35 opener, including brief team introduction.
- Slide 2 is a quick orientation beside/before M2's 1:00–1:50 live plan segment; most of the 0:35–7:40 sequence is the actual app and the seven role narrators, NOT slides.
- Slide 3 supports M8's 7:40–8:35 harness explanation PLUS one real rehearsed safety proof; narration must leave time for that proof.
- Slide 4 supports M8's 8:35–9:10 evidence/limitations segment.
- Slide 5 supports M8's 9:10–9:30 next steps and brief gallery close.
The planned recording is 9:30 total with a margin to the PDF's ten minutes. Rehearse actual speech/clicks; do not add five long monologues. M1–M7 remain the employee/department narrators from the script; confirm names/consent separately rather than inventing names. Model failure means an honest fallback, not a faked resolved take.

6. VERIFY AND HAND OFF
- Assert exactly five PPTX slides and five PDF pages, including hidden slides/auto-generated continuation pages. No appended references or title slide. Confirm matching order/content and 16:9 geometry.
- Render/reopen both actual exports, inspect every page at 1080p and on the recording laptop: no clipping/overlap, broken arrows, unreadable UI crop, substituted glyph/font, missing qualification or bad contrast. Compare PDF to PPTX. File existence or a successful generator call alone is not visual verification.
- Verify native text/architecture are editable, all five slides have notes, reading order/alt text are sensible and PDF text is selectable where supported. Review notes/metadata/screenshots for secrets, unsupported outcomes, real identities and private links. Use only licensed/approved assets; retain any required attribution/branding.
- Check every number and future/implemented label against the recorded revision. Include short source pointers on slides and detailed file/page/URL references in notes; no sixth bibliography slide. A public URL must genuinely exist and be approved; no fabricated repository/video QR code.
- Run relevant presentation/link checks and npm run check as AGENTS.md requires; record actual results/limits in existing CHANGES.md/docs/VERIFICATION.md and update only your task in the active plan. Actual five-slide assets still require presentation-owner/integrator review before R8 is closed.
- Leave files uncommitted/unpushed/unpublished unless separately authorized. Report delivered paths, creation/export route, exact counts, inspected renders, the recording handoff and remaining blockers. Never promise a hackathon win.
```

## For the presentation and recording teammates

1. The presentation teammate gives the block above to a repository-aware agent. First confirm the five slide claims, then approve only sanitized content for any cloud generator. Keep detailed technical content in notes, not tiny diagram labels.
2. If using Gamma: set five cards/slides, fixed 16:9 slide format, restrained text and the Proofline theme; paste the approved five-slot content, not the repository. Inspect Present Mode; export **all five** to PPTX, inspect/repair in PowerPoint if necessary, then produce a matching PDF from the finalized deck. Keep the free badge if applicable; no automatic upgrade.
3. The recording teammate receives actual PPTX/PDF plus notes, not only a Gamma link. Test on the same recording laptop, offline if possible. Keep app actions primary; follow the cue timings in the prompt and [the existing script](../video/script.md#timed-run--930-total). Use one backend/DB for role sessions; independent localhost copies do not share progress.
4. Put the final reviewed files at **ppt/dayone_proof_final.pptx** and **ppt/dayone_proof_final.pdf**. These are not ignored; they may be staged only after consent, secret/size and actual-content review. A name containing “final” does not establish acceptance. Actual deliverable status stays in [the active plan](../docs/decisions/2026-11-07-improvement-plan.md), not a new checklist document.

## Research sources

Use these sources to confirm capabilities; product claims must come from the repository, not generator marketing. Vendor plan/settings pages may change after the research date.

- **Authority:** local [challenge PDF](../AI_Innovation_Challenge_University_Brief%201.pdf), p. 1 duration/team, p. 2 Topic 3/stack flexibility, p. 3 deliverables/rubric.
- [Gamma exports, notes, editable tables and free-plan badge](https://help.gamma.app/en/articles/8022861-what-s-the-easiest-way-to-export-my-gamma).
- [Gamma fixed slide/page setup](https://help.gamma.app/en/articles/11029115-how-do-i-control-slide-sizes-and-adjust-page-setups) and [export differences](https://help.gamma.app/en/articles/15939201-why-doesn-t-my-exported-pdf-or-powerpoint-match-what-i-see-in-gamma).
- [Gamma pricing/creation limits](https://gamma.app/pricing); verify the actual workspace entitlement before use, not a third-party price comparison.
- [Gamma AI-training Data Controls](https://help.gamma.app/en/articles/12281928-does-gamma-use-my-content-to-train-its-ai-features) and [sharing/workspace permissions](https://help.gamma.app/en/articles/11047226-how-do-collaboration-and-sharing-settings-work-in-gamma).
- [Canva AI presentation drafts](https://www.canva.com/create/ai-presentations/) and [PowerPoint export](https://www.canva.com/create/powerpoint-alternative/). Treat free-use numbers as account/version-dependent; check Pro assets/export before committing to the route.
- [PptxGenJS editable slide objects](https://gitbrent.github.io/PptxGenJS/) and [speaker notes](https://gitbrent.github.io/PptxGenJS/docs/speaker-notes.html). This is a fallback capability reference, not a newly installed project dependency.
- [Microsoft readable presentation guidance](https://support.microsoft.com/en-us/powerpoint/tips-for-creating-and-delivering-an-effective-presentation) and [accessibility: contrast, alt text and reading order](https://support.microsoft.com/en-us/accessibility/powerpoint/make-your-powerpoint-presentations-accessible-to-people-with-disabilities). Our larger recording-oriented type targets are recommendations, not official challenge rules.

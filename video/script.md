# OnboardIQ demo — “Ready on paper. Ready in reality?”

**Target: 9 minutes 30 seconds; never exceed 10:00.** Eight real teammates, seven product roles and one host/harness narrator. This is a rehearsal script, **not a completed recording**. Replace M1–M8 with your names. Confirm organizer permission for eight members and the actual deadline; the official brief lists 3–5 with variable actual size.

## The story in simple words

Priya is about to join. Her profile says Hyderabad, but her offer says Bengaluru. Different teams have pieces of her onboarding. We first show the normal six-area plan, then follow one disagreement from evidence to clarification, approval and a checked result. The ending is deliberately honest: **a Bengaluru laptop is reserved; collection is still pending**. The remaining teams own their work. We are pitching better handoffs, not a robot that takes over HR.

One line to remember: **“AI helps us investigate. People approve. The system checks what actually changed.”**

## Recording tools — researched official sources, 7 November 2026

This is a focused practical comparison, not an exhaustive internet survey or a test of your account/devices. Plans, administrator settings and permission can change. No service was purchased, meeting created or recorder installed by this task.

| Option                                                        | What the team gets                                                                                          | Important limit                                                                                                                                                                                                                                | Recommendation                                                                                                                |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **Zoom Basic + desktop computer recording**                   | Eight participants, shared-screen video/audio, local file; recording is available on free and paid accounts | Most Basic-hosted meetings end after 40 minutes. Computer recording requires supported desktop app and host/admin permission; not mobile. Cloud recording is a separate entitlement. Layout is not independent separate gallery/screen tracks. | **Simplest first choice** if the host can record to computer. Rehearse once, then start a fresh meeting for the final take.   |
| **Google Meet + OBS Studio**                                  | Meet for the conversation; OBS captures the chosen app/window and meeting audio/microphone locally          | Consumer group meetings are generally1 hour/up to100 people. Native Meet recording depends on an eligible edition/admin/host permission; do not assume a free Gmail account has it. OBS needs setup/audio testing.                             | Good no-paid-recording alternative when Meet is familiar and OBS works on the host laptop.                                    |
| **Existing eligible college Google Workspace Meet recording** | Built-in recording of active speaker/presented content, saved to organizer Drive                            | Check actual college edition, administrator permission and Drive capacity first. Pinning a participant does not determine the recorded view.                                                                                                   | Use only if your account already has the feature and a test file plays correctly. Do not buy an upgrade merely for this demo. |

## One screen controller, one real state

**Recommended:** M8 controls one recording laptop running one backend and one private synthetic demo DB. All eight join Zoom/Meet and speak their assigned parts. M8 switches between already-authenticated browser profiles/windows for the seven roles while that role’s teammate narrates. Each profile is logged into its actual role; there is no demo role-impersonation feature. Never record the password entry.

This is better than seven screen-sharing handoffs. Eight independent localhost databases do **not** share Priya’s record. Do not upload/share SQLite files, expose a dev server publicly or silently pretend independent demos are synchronized. If every person must click personally, explicitly agree a secure common hosted setup or permitted remote control first; neither is a hidden prerequisite of this script.

Show all eight participants briefly at the beginning and end; keep the app large during work, with the active speaker/small gallery if the recorder allows. A native recorder may not show all eight faces throughout screen sharing—test the layout. Everyone can remain virtually present without covering the UI. Use real first names and roles, not claimed job titles or customers. Ask consent before recording faces/voices or publishing names.

### Cast

| Member | Part                                        | What they demonstrate                                                          |
| ------ | ------------------------------------------- | ------------------------------------------------------------------------------ |
| M1     | Employee / Priya                            | Why the handoff matters, own uploads/tasks and final employee view             |
| M2     | HR                                          | Profile-based plan, document review, clarification and exact location approval |
| M3     | IT                                          | Separate equipment approval and collection-pending read-back                   |
| M4     | Payroll                                     | Sanitized setup status, not banking/payment execution                          |
| M5     | Benefits                                    | Invitation/enrolment/decline workflow, not insurer integration                 |
| M6     | Training                                    | Assigned/completed training evidence                                           |
| M7     | Manager                                     | Buddy and first-week plan                                                      |
| M8     | Host + harness engineer + screen controller | Opening, transitions, safety/architecture/evidence, timing and closing         |

## Before the meeting — do these privately

1. Follow [root setup](../README.md#install-and-run). Use a **new practice directory/DB**, not deletion/reset of the working data. Set matching DATABASE_PATH for seed/app. Seed once; keep the fresh Priya account available. Use the same reviewed commit/schema/fixture revision as the recording.
2. Run npm run check. For stable recording use npm run build then npm start; run built-origin smoke. Do not run test suites while narrating; prepare real sanitized output with its date/commit for slide 4.
3. Privately configure **one real available model**, check licence/account/data-use/quota/spending limits and rehearse the exact story. Historical Groq results are not your new run. Allow quota to recover; do not perform a burst of extra AI questions before the take. No paid upgrade/key rotation/provider switch without explicit approval.
4. Create seven browser profiles/windows and sign in before recording. Prepare HR/employee/IT routes, plus payroll/benefits/training/manager screens pointing to **the same backend and DB**. Refresh after someone changes state. Do not prepare a fake successful result.
5. Prepare the actual five slides in [ppt/](../ppt/README.md): problem/value, workflow, architecture/harness, safety/evidence, future impact. No extra title/contact slides if the deliverable must be exactly five.
6. For the demo hire, use Priya Sharma, employee, engineer, office, initial Hyderabad, manager Manoj Verma, employee login Priya; pick a valid upcoming start date and the appropriate existing department/designation. The offer fixture says Bengaluru. Use fixtures/documents/offer_letter_priya.txt and government_id_priya.txt—never real identity/bank files.
7. Rehearse on a disposable practice DB first. Decide which actual task/evidence state you will show; do not say an equipment task is completed unless that screen really says so. The reliable point is a location mismatch and separate reservation/handover evidence.
8. Check all microphones, headphones, readable browser scale, notifications off, no private bookmarks/tabs. Host captures the app/meeting, not the editor, .env, network authorization headers or account dashboards. Avoid mirrors/infinite screen-share windows.
9. Make a 30-second sample: two remote people speak, host speaks, app switches, a role label is legible. Play the saved file back and verify **all three voices**, not just moving meters. With OBS, capture meeting audio+host mic once; disable duplicated Desktop Audio when also using application audio. Use headphones to avoid echo.
10. Aim for 1080p/30 fps if hardware supports it; readability/audio matter more than effects. Choose local recording, enough disk and a safe destination outside Git drafts. OBS Auto-Configuration Wizard can help. Record to a resilient format such as MKV when available, then use the recorder’s remux/export to H.264 MP4 for delivery. Test playback; do not assume a file is complete because recording stopped.

## Timed run — 9:30 total

Times include clicking and short natural waits. The words below are speaking prompts, not a demand to read every instruction aloud. Only make a statement if the visible build actually supports it.

| Time      | Speaker | Screen/action                                                              |
| --------- | ------- | -------------------------------------------------------------------------- |
| 0:00–0:35 | M8      | Brief gallery of eight, then slide 1/problem and live app                  |
| 0:35–1:00 | M1      | Employee problem/setup                                                     |
| 1:00–1:50 | M2      | HR creates Priya; six-category plan and owners                             |
| 1:50–2:25 | M1      | Own document uploads                                                       |
| 2:25–3:05 | M2      | Human review and actual advisory extraction/mismatch                       |
| 3:05–4:20 | M2      | Investigation -> saved human question -> answer -> exact location approval |
| 4:20–5:15 | M3      | IT exact reservation approval and fresh read-back                          |
| 5:15–5:45 | M4      | Payroll setup flag                                                         |
| 5:45–6:15 | M5      | Benefits record                                                            |
| 6:15–6:45 | M6      | Training completion                                                        |
| 6:45–7:15 | M7      | Buddy/first-week plan                                                      |
| 7:15–7:40 | M1      | Refresh own onboarding; show remaining work honestly                       |
| 7:40–8:35 | M8      | Slide 3/harness plus one rehearsed safe refusal/outage proof               |
| 8:35–9:10 | M8      | Slide 4/actual tests, model evidence and limitations                       |
| 9:10–9:30 | M8      | Slide 5/next steps and brief gallery close                                 |

Slide 2 is the six-area workflow shown beside/before the live plan; do not stop for a separate feature-list lecture. There is a 30-second submission margin after 9:30, not an excuse to exceed 10:00. Actual timing must be rehearsed.

### 0:00–0:35 — M8: start with the failure, not your framework

> “A new employee can have a finished checklist and still have an unfinished first day. A laptop can be reserved in the wrong city, while every team thinks someone else is handling it. We built OnboardIQ to connect the next step, the right person and the proof behind it. We are an eight-person team. Let’s follow one employee, Priya.”

Show the team briefly, slide 1, then app. Add a small visible verbal or slide note: **fictional company, synthetic documents, simulated external systems**. No claim of real customer deployment.

### 0:35–1:00 — M1: make the user problem personal

> “I’m playing Priya. My profile says Hyderabad, but my offer says Bengaluru. I need one clear place to see my joining tasks, upload my documents and know who is waiting for me. I should not have to chase seven separate conversations.”

This is a role-play opening, not fabricated customer testimony. M8 opens the actual Priya account only after HR links the hire.

### 1:00–1:50 — M2: prove normal onboarding exists

> “As HR, I create the hire with the worker type, job, location and start date. Approved rules create the document, equipment, payroll, benefits, training and manager tasks. Each has an owner and dependencies. We track task progress separately from checked evidence—finishing a task does not automatically prove the outcome.”

Create Priya using the prepared real form, then show the plan/owners and evidence labels. Click deliberately; do not fill every optional field on camera. This is the official Topic 3 workflow, not just a rescue chatbot.

### 1:50–2:25 — M1: upload the evidence

> “I upload the two fictional sample documents from our fixture folder. My offer says Bengaluru. Uploading is a submission, not approval. I can see my own work, not another employee’s private records.”

In Priya’s profile/window upload the offer as signed employment and the government-ID fixture in its correct category. Show the submitted/under-review status. Never show a real identity document.

### 2:25–3:05 — M2: AI assists; HR remains responsible

> “The extraction is advisory. It helps identify fields and the location disagreement, but it cannot verify the document for me. I inspect the source and make the human review decision. Now we have a concrete conflict to investigate—not permission for the model to guess a new location.”

Run the actual extraction on the configured model if rehearsed successfully. Show its recorded provider/model/label and mismatch, then actual human review. If the call rate-limits, say so and use the visible manual review path; do not read the success line.

### 3:05–4:20 — M2: the governed recovery

> “I open an investigation about the offer and profile disagreement. The agent reads only permitted sources and asks the responsible person when the location is uncertain. The question and waiting state are saved. I answer Bengaluru. That answer is not approval: I still review the exact location change and plan impact before approving it.”

Open the actual investigation, show a permitted read and the question in Notifications/investigation. Answer the actual question, wait for the proposed diff, inspect changed/preserved work and approve as HR. Do not approve blindly just to stay on time.

If this model chooses a different safe sequence, describe **what actually happened**, not the expected script. If the question/diff never arrives, use the failure branch below. A full process restart can be shown here **only if rehearsed and within time**; otherwise show dated restart-test evidence later and do not claim you restarted in this take.

### 4:20–5:15 — M3: finish with a precise outcome

> “HR’s location approval does not let HR approve my equipment action. As IT, I inspect the specific asset and location, then approve this reservation. The system checks current versions before writing and reads the result back. The receipt says the laptop is reserved and collection is pending. We have not proved delivery.”

Switch to real IT session, review actual asset/location/evidence, approve once, wait for the action result and refresh evidence. LAPTOP_22 is the expected fixture candidate, **not a guaranteed model choice**; speak the asset shown. A queue entry is not a successful action. Do not click a separate handover control just to make the ending green.

### 5:15–5:45 — M4: payroll stays accountable

> “Payroll is a separate responsibility. I record whether the payroll profile and setup checks are complete. This demo stores sanitized flags, not real bank or salary data. My update becomes a record other permitted screens can check.”

Use Priya’s actual payroll row if scoped/available; save one meaningful setup flag and refresh. If a prerequisite remains, show it and explain waiting rather than bypassing it.

### 5:45–6:15 — M5: benefits is not just a tick

> “I manage the benefits handoff. Invited, enrolled and declined are different states. I record the state we actually have, rather than treating an invitation as completed enrolment.”

Use the Benefits screen, select the actual applicable state such as Invited and save once. Do not claim real insurer enrolment.

### 6:15–6:45 — M6: show the training evidence

> “I can see required training and record a completed course. The plan shows that result separately from the other teams’ work. One completed course does not mean all onboarding is complete.”

Use the Training screen; complete the rehearsed assigned course if allowed. State this is a local synthetic record, not a live learning-system response.

### 6:45–7:15 — M7: include the human welcome

> “My part is the first week, not just paperwork. I assign a buddy and save a short first-week plan for my hire. The record makes that handoff visible without pretending the employee has already attended those meetings.”

Choose the actual hire/buddy and enter a short plan such as “Meet your buddy; review the approved onboarding checklist.” Save and show confirmation.

### 7:15–7:40 — M1: return to the person we started with

> “Back in my view, I can see what changed and what still needs someone’s action. The location is corrected; the laptop is reserved, not handed over. I know the next owner instead of assuming every green-looking task means I am ready.”

Refresh Priya’s real portal and point to the current states. If the location/reservation failed, describe that failure instead. Do not promise an overall “Onboarding complete” ending: intentionally pending handover/other work means it should not be complete. Skip an extra knowledge-answer call in the final take if quota/time is tight; this story already has real AI work.

### 7:40–8:35 — M8: explain the harness in ordinary language

> “The browser calls our FastAPI backend. Approved rules and SQLite hold the work and evidence. One worker runs a bounded investigation. Every model reply passes typed validation; it can request narrow reads or a proposal, not arbitrary SQL or writes. Human waits are persisted. Important changes require the correct reviewer, fresh versions and read-back. If the model fails, people can continue their normal work.”

Show slide 3 with the actual architecture, then **one rehearsed real proof**: an unauthorized route is denied, an outdated decision is rejected, or AI-off/manual work still functions. Choose the one you have actually prepared; do not invent a click path or claim a denied screen alone proves every backend control. If demonstrating AI-off, change config privately outside the captured area and let the visible app confirm it; no recording of.env or terminal secrets. This can be a clearly labelled separate short proof segment, not a disguised continuation of a successful live model call.

### 8:35–9:10 — M8: evidence, including the weak part

> “Our automated tests use scripted model replies to check controls, not model intelligence. Here is the actual test output for the recorded revision. Historical real-model evaluation covered one Groq model. Untuned retrieval was five out of eleven, and quota interruptions occurred. We still need independent model-quality scoring and broader device testing. Those are limitations, not hidden successes.”

Slide 4 uses **actual latest counts/date/commit**, not hard-coded numbers from an old script. Cite docs/EVALUATION.md for historical model results; distinguish any new authorized take. Do not claim that JSON validation proves every answer correct or that one investigation measures a success rate.

### 9:10–9:30 — M8: close on value, not a feature shopping list

> “OnboardIQ does not replace the teams. It makes their handoffs visible and checks the exact outcome. Our next priorities are stronger retrieval, independent evaluation and shared-deployment hardening—not more unchecked automation. The goal is simple: a completed task should lead to a trustworthy next step.”

Show slide 5 and briefly return to the team. Stop recording by 9:30. No invented time-saved percentage, customer endorsement or guaranteed compliance.

## Failure branches — rehearse these too

- **Model slow/429:** “The provider is quota-limited. The case is not magically resolved. Here is the manual review path.” If the core live model story cannot fit, stop and retake after quota recovers, or include a clearly labelled genuine recorded run. Never present stub/offline rules as live AI or an earlier model run as today’s inference.
- **Model proposes the wrong thing:** do not approve. Show the rejection/escalation and explain what a person must resolve. A safe refusal is better than a fabricated successful result.
- **State differs from rehearsal:** refresh the same DB/profile; describe observed facts. Use a new practice directory for another take, never destructive reset of working data.
- **Someone disconnects/audio missing:** stop and retake the affected scene; ensure all eight actually appear/speak in the final version. Do not synthesize a teammate’s voice/identity.
- **Editing:** only shorten dead air or join clearly labelled genuine scenes if organizer rules permit. Label “wait shortened” or “separate recorded proof” where relevant; never stitch different states/model modes into an apparently continuous verified transaction. Timing of an edited clip is not measured application latency.

## Final recording / upload checklist

- Actual file duration below 10:00; all eight names/parts present with consent, no hidden personal/credential material. Playback checks app text and every voice at normal speed.
- Exactly five actual slides, not placeholder Markdown alone; final PPTX/PDF agree with the recorded build and synthetic labels.
- Save a reviewed H.264 MP4 such as dayone_proof_demo.mp4. Keep unwanted drafts outside the source tree. Record actual date, submitted commit, model/mode and any edited waiting periods.
- GitHub ordinary Git blocks files over 100 MiB; browser upload limit25 MiB. Prefer a real approved YouTube/Drive/Release link for a large video, or deliberately configured Git LFS after reviewing account quotas. Do not overcompress until UI text is unreadable. [GitHub file-size guidance](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).
- Test the final link in a signed-out/private window, including audio and seeking. A Drive link still restricted to the owner is not an accessible submission. Do not publish/upload automatically without owner approval.
- Replace [VIDEO_LINK.md](VIDEO_LINK.md) with the actual playable link/path, duration/date/commit/provider and playback result; update the root README’s pending label. A script or nonexistent example video is not the required deliverable.
- Freeze new features three hours before the real deadline; only necessary fixes/checks/assets afterward. Resume publication needs each owner’s separate consent and organizer handling instructions.

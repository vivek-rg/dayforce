---
name: OnboardIQ
description: Open Handoffs — confident monochrome work surfaces that keep completion claims and evidence distinct.
colors:
  canvas: "#f7f7f7"
  surface: "#ffffff"
  surface-2: "#f1f1f1"
  ink: "#141414"
  ink-2: "#454545"
  ink-3: "#626262"
  line: "#dedede"
  line-2: "#b6b6b6"
  accent: "#171717"
  accent-hover: "#363636"
  accent-soft: "#e8e8e8"
  side: "#111111"
  side-ink: "#e8e8e8"
  side-muted: "#aaaaaa"
  side-hover: "#262626"
  story-muted: "#cccccc"
  story-rule: "#444444"
  example-ground: "#151515"
  example-muted: "#bbbbbb"
  ok: "#14693a"
  ok-bg: "#e8f3ed"
  warn: "#855400"
  warn-bg: "#faf2e1"
  bad: "#ad241c"
  bad-bg: "#fbecea"
  info: "#474e56"
  info-bg: "#eef0f2"
typography:
  display:
    fontFamily: '"Source Sans 3", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif'
    fontSize: "clamp(40px, 5vw, 68px)"
    fontWeight: 650
    lineHeight: 1.04
    letterSpacing: "-0.035em"
  guide-heading:
    fontFamily: '"Source Sans 3", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif'
    fontSize: "32px"
    fontWeight: 600
    lineHeight: 1.16
    letterSpacing: "-0.02em"
  headline:
    fontFamily: '"Source Sans 3", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif'
    fontSize: "32px"
    fontWeight: 650
    lineHeight: 1.25
    letterSpacing: "-0.01em"
  title:
    fontFamily: '"Source Sans 3", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif'
    fontSize: "18px"
    fontWeight: 650
    lineHeight: 1.35
  body:
    fontFamily: '"Source Sans 3", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif'
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: '"Source Sans 3", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif'
    fontSize: "13px"
    fontWeight: 600
    lineHeight: 1.5
  control:
    fontFamily: '"Source Sans 3", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif'
    fontSize: "14px"
    fontWeight: 600
    lineHeight: 1.25
rounded:
  proof: "3px"
  control: "4px"
  surface: "6px"
spacing:
  compact: "6px"
  control-gap: "8px"
  record-gap: "12px"
  panel: "16px"
  section: "24px"
  gutter: "32px"
  reading-section: "64px"
  reading-gutter: "80px"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.surface}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "7px 13px"
  button-primary-hover:
    backgroundColor: "{colors.accent-hover}"
    textColor: "{colors.surface}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "7px 13px"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "7px 10px"
  nav-current:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.side}"
    rounded: "{rounded.control}"
    padding: "7px 10px"
  work-panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.surface}"
    padding: "16px"
  proof-verified:
    backgroundColor: "{colors.ok-bg}"
    textColor: "{colors.ok}"
    rounded: "{rounded.proof}"
    padding: "5px 8px 6px"
  proof-unknown:
    backgroundColor: "{colors.warn-bg}"
    textColor: "{colors.warn}"
    rounded: "{rounded.proof}"
    padding: "5px 8px 6px"
  proof-blocked:
    backgroundColor: "{colors.bad-bg}"
    textColor: "{colors.bad}"
    rounded: "{rounded.proof}"
    padding: "5px 8px 6px"
---

# Design System: OnboardIQ

## Overview

**Creative North Star: "Open Handoffs"**

Confident and readable for every role: strong monochrome contrast and orderly records show the work, its owner and what independent evidence actually establishes. The signature pairs Claim and Proof without collapsing them into a single success signal. Familiar controls and aligned information carry the identity rather than decoration.

Near-black navigation and authentication story contrast with white working surfaces and neutral-grey supporting regions. Stronger Source Sans 3 headings and deliberate rules establish hierarchy without ornament. Public explanations share this language while using a larger reading scale. This document records the current implementation, not a future feature list or an independent shipping verdict. Test, browser and finish-review evidence is maintained separately by the integration owner.

**Key Characteristics:**

- Black navigation, white work surfaces and neutral interaction states.
- Separate, adjacent Claim and Proof cells.
- Thin rules and compact records instead of nested cards.
- Native controls, visible focus and explicit state text.
- The same visual language for all seven authorized roles.

Source authority: `src/styles.css`, `src/fonts.css`, `src/shared/ui.tsx`, `src/shared/logic.ts`, `src/shared/HandoffIllustration.tsx`, `src/features/auth/Login.tsx`, `src/features/portal/Portal.tsx` and `src/features/guide/Guide.tsx`, relative to this frontend root. The token values above are normative; the sidecar supplies renderable examples and extensions, not another primitive palette.

## Colors

### Primary

Near-black (`accent`) identifies primary actions, links, selected role explanations and focus on light surfaces. Neutral hover and selection shades provide feedback without another brand hue. Current sidebar navigation inverts to white with dark text; sidebar focus is white. Authentication form focus remains near-black on white; its static dark story contains no interactive controls.

**The Monochrome Brand Rule.** Black, white and neutral greys carry the identity; green, amber and red communicate actual semantic states, not decorative categories.

### Neutral

Neutral canvas surrounds white work surfaces; pale secondary surfaces distinguish table headings and quiet hover feedback. Near-black navigation carries light text and muted grey group labels. Ink, secondary ink and muted ink establish reading order; light and stronger rules define records and controls. The auth story locally inverts text and rules for its fixed explanation and illustrative equipment example; the public example uses a dark ground with light copy.

### Semantic states

- Green (`ok` / `ok-bg`): verified evidence and affirmative outcomes.
- Amber (`warn` / `warn-bg`): waiting, unknown or missing proof; never a substitute for a confirmed mismatch.
- Red (`bad` / `bad-bg`): blocked checks, errors and contradictions.
- Grey (`info` / `info-bg`): informational state; muted ink also marks neutral/no-check states.

Text and boundary style supplement color. Evidence is VERIFIED, BLOCKED, UNKNOWN or NOT_APPLICABLE; the UI also distinguishes Not checked and No check without inventing API results.

## Typography

Source Sans 3 is the shared heading/body/control family, bundled in `src/fonts.css` as an embedded Latin variable WOFF2 (28,872 font bytes), normal style, weight range 200–900, with `font-display: swap`. The SIL OFL notice is `OFL-Source-Sans-3.txt`. Font loading needs no external request. The fallback stack is in the frontmatter; monospace is reserved for identifiers, code and source facts, not display headings.

The frontmatter records page headline, section title, body, field label and control roles. Smaller subheadings use 14px/650 and 13px/600; supporting copy commonly uses 12–13.5px. Tabular numerals align counts. Page descriptions stop at 72ch. Portal's “Your progress” is a normal section h2; no next-action eyebrow precedes its task heading.

Sign-in has a local responsive headline (`clamp(36px, 3.8vw, 56px)`, 600, line-height 1.14) and a 30px/600 form title. At 960px and below, its story headline becomes 30px. These are authentication-surface treatments, not the dashboard heading scale.

Guide headlines use the frontmatter display role, reduced to 43px at 640px. Guide h2 is 32px/600, reduced to 28px; journey headings and role purposes are 21px, introduction text is 20px (18px on narrow screens), body lists are 16px and boundary headings 17px. Public brand is 26px; example conclusion is 25px. Numbered journey markers are 24px, exception counts 40px. Compact source sizes also include 10.5px, 11px, 11.5px, 12px, 12.5px, 13px, 13.5px, 14px and 15px. These are source-derived treatments, not a requirement to introduce every step on a new screen.

## Layout

The desktop shell uses a 232px navigation column and flexible workspace below a 22px demo strip. Its white account bar is at least 60px tall. Content uses 28px top, 32px side and 56px bottom padding, with a 24px section gap. Section grids use two or three equal flexible columns; forms generally use two columns and 12px gaps.

Task rows align description, a 272px Claim/Proof region, owner/due metadata and existing actions. At 1240px they become two columns. At 1100px, three-column grids reduce and portal/profile top regions stack. At 960px, the shell becomes one column, navigation becomes a 264px off-canvas drawer, two-column working grids stack, and content gutters become 16px. Sign-in stacks its fixed story above the form at the same breakpoint and hides the nonessential illustrative Claim / Proof example at 960px and below to prioritize the form.

At 640px, task/form/proposal/upload grids stack, Claim/Proof expands to available width, task actions align left and content gaps become 20px. Inputs become 16px text and at least 40px tall; standard buttons are at least 40px, while small buttons, tabs, toggles, notification and user controls are at least 44px. Navigation rows are at least 42px. These are observed sizes, not a claim that every control has the same target dimensions.

Data tables retain their columns in a horizontal scroll region (default minimum table width 640px). A measured overflow check adds “Scroll horizontally to see all columns and actions.” only when needed, connects it with `aria-describedby` and updates via ResizeObserver. Regions remain keyboard-focusable and named; tables retain captions and column headers. The sticky first column becomes static at 640px so it does not cover narrow-screen actions.

Public guides use a 1184px reading container with 80px vertical spacing; public header/footer stop at 1280px. Desktop public gutters are 48px, reduced to 24px at 960px, where vertical reading padding becomes 48px. Introductory, journey and FAQ grids stack at 960px; the proof section stacks at 1100px and its Claim/Proof pair at 640px. The role explorer uses a 240px index, reduced to 180px by 960px and replaced by a labelled native select by 640px. Its desktop role controls are at least 52px tall and the mobile select is 48px. Embedded guides retain the app shell, reduce top spacing to 48px and use 32px column gaps.

The decorative handoff scene sits beside the auth brand (156px wide, 92px at 960px and below, 76px at 640px and below); the following headline has 48px top margin, reduced to 20px at 960px. The How it works example caption pairs text with 112px art, reduced to 84px at 640px. The Role guide introduction is a text/art flex row with `clamp(160px, 20vw, 260px)` art; at 640px it becomes a column with end-aligned 124px art. Embedded Role guide art remains 150px even on mobile because its more-specific rule wins. All scenes retain the intrinsic 300:210 ratio with automatic height.

## Elevation & Depth

The system is flat at rest: white surfaces, tonal changes and thin rules establish hierarchy without card shadows. Independent records may have a boundary; details inside a work surface flatten into separators with transparent backgrounds and square corners. Observed facts, code and citations also resolve to transparent, borderless treatments after the final stylesheet overrides.

**The Flat Worksurface Rule.** Reserve shadows for the floating account menu; separate ordinary work with tone and rules.

The account popover alone uses `0 8px 24px rgba(21, 24, 28, 0.14)`. The mobile drawer has a translucent neutral scrim, not glass or backdrop blur. Control color/border feedback lasts 140ms ease-out; drawer movement lasts 160ms ease-out. Under `prefers-reduced-motion: no-preference`, the anchored account menu arrives over 160ms with `cubic-bezier(0.16, 1, 0.3, 1)`, opacity 0.7 to 1 and `translateY(-4px)` to none. New rule, menu and press motion is scoped to no-preference; global reduced-motion styles disable transitions and animations with `!important`, preserving static content and immediate states.

## Shapes

Controls have modest 4px corners; standalone work surfaces use 6px and Claim/Proof cells use 3px. Rules are generally 1px. Blocked proof has a stronger 1.5px red boundary; unknown/not-checked proof is dashed; no-check/not-applicable proof uses a dotted neutral boundary. Circular status dots accompany written labels rather than replacing them. Compact progress tracks use 1–2px corners, not pill silhouettes.

## Components

### Buttons and fields

Primary buttons use near-black with white text; secondary buttons use white, ink and a stronger neutral outline. Both share compact padding and 14px/600 type. Hover is tonal; secondary active state becomes ink/white, while primary active stays neutral dark. Disabled buttons lower opacity and retain a not-allowed cursor. Small and icon variants preserve the same language. Global keyboard focus is a 2px accent outline with 2px offset; the sidebar uses a white outline. Authentication form controls retain standard near-black focus on white; the static story needs no local focus override.

Under no-preference only, shared buttons, authentication submit and role-picker buttons use 140ms ease-out background/border/text-color feedback and a 120ms ease-out one-pixel downward press. Disabled shared/submit buttons do not move. Reduced motion keeps immediate tone feedback without the press transform.

Fields have explicit native labels, white backgrounds, stronger neutral borders and a 4px radius. Standard inputs use 13.5px type, 38px minimum height and 7px/10px padding; hover strengthens the border. Invalid fields use a red border plus written error. Authentication inputs are a separate 48px-high variant with inline SVG and an accessible password-visibility button. Do not replace labels with placeholders.

### Navigation and tabs

Sidebar links sit on near-black, hover with a lighter charcoal tint and invert to white/dark with `aria-current="page"` for the current location. Tabs use a thin dark bottom rule and `aria-selected`, not filled pills. Existing arrow-key movement and roving tab focus remain part of the tab pattern. Preserve drawer controls and existing routes; examples do not create new destinations.

### Authentication explanation

One fixed headline introduces the work, owner and evidence; there is no headline selector or decorative feature list. A flat, ruled equipment example places “Equipment task completed” beside “Reservation recorded. Handover unknown.” under separate Claim and Proof labels. “Reserved ≠ handed over.” and “Illustrative demo. No live employee record.” keep the outcome and synthetic status explicit. This noninteractive example is hidden at 960px and below; sign-in, reset, account creation and guide links remain in the white form region.

Under no-preference only, a neutral 1px top-rule pseudo-element draws left to right across the example over 560ms with `cubic-bezier(0.16, 1, 0.3, 1)`, scaling from 0.12 to 1. It runs once with no delay or fill; text and ordinary borders are always present. This illustrates the Claim / Proof connection, not live verification or progress. Reduced motion retains the static example; the existing 960px hiding rule is unchanged.

### Product guides

Public navigation provides How it works, Role guide and Sign in. Embedded pages retain the workspace and Help links. The role index uses native pressed-state buttons on desktop and a labelled native select on mobile; selecting a role changes explanatory content only. Native disclosure elements expand the FAQs. Synthetic equipment examples state that reserved is not handed over, with no live employee data. Dark example panels use light text and grey rules; broader reading sections use whitespace and rules, not nested cards.

### Decorative handoff illustration

Original assistant/laptop/document line art accompanies the auth brand, How it works caption and Role guide introduction; it is not a live assistant, progress indicator or outcome. The inline SVG is noninteractive (`aria-hidden="true"`, `focusable="false"`, pointer events off), with no text, IDs, remote assets or dependency. Local scene variables reuse incumbent monochrome values and invert on dark auth/example grounds, without introducing a brand color. The complete scene is visible by default.

Only under no-preference, two SVG groups animate once over 1800ms: the paper uses `cubic-bezier(0.16, 1, 0.3, 1)`, moving from `translate(38px, -10px) rotate(12deg)` through `translate(-4px, 3px) rotate(-3deg)` at 65% to rest; the helper uses ease-out, rising/nodding at 25% and 55% before returning to rest. Neither animation has a delay, fill or loop. Global reduced-motion rules disable animation and transition with `!important`, leaving the complete static scene. Existing Claim / Proof rule, menu and control feedback remain separate and unchanged.

### Status and feedback

Badges are text plus a small status dot, not filled capsules; the muted variant has an outlined dot. Notices combine a full boundary, optional semantic tint and explicit text. Bad notices are alerts; other tones are status regions. Loading uses static skeleton rows with an accessible Loading status, empty states use a dashed boundary, denied/error states state the problem, and a refresh failure leaves a written “Showing the last loaded data” warning. Preserve existing retry/reload actions and pending labels.

### Work surfaces and tables

Forms and independent records use white, a thin light boundary, 6px corners and compact padding. Nested details flatten instead of creating another raised card. Tables use pale headings, uppercase column labels, record separators, quiet row hover and tabular/right-aligned numeric columns. Keep the conditional overflow cue and keyboard-focusable region described in Layout; a table preview is only a snapshot of its overflowing state.

### Claim / Proof — signature

Two equal cells remain adjacent across a 14px seam. Keys are uppercase 11px/700; values are 12px/600. The generic pair is at most 272px wide until the mobile layout expands it. Color, line style and plain-language flags express the relationship:

- Completed claim + VERIFIED: green proof cell, solid green seam, “Claim proven”.
- Completed claim + UNKNOWN or Not checked: amber dashed proof/seam, “Claim without proof”.
- Completed claim + BLOCKED: red proof and dashed seam, “Evidence contradicts the claim”.
- Completed claim + no independent check: dotted neutral proof boundary, “Claim only, no independent check”.
- VERIFIED while the task remains open: “Proof exists, task still open”; do not draw the proven-claim seam.
- Cancelled claims strike through their claim value. No applicability or no-check state is promoted to verification.

**The Separate Proof Rule.** A completed task is a claim; only its independently checked outcome can supply proof.

The companion ledger uses aligned Claimed and Proven rows on the same total, with real counts and an explicit gap/no-check note. Do not merge them into a new readiness score. Model output stays in the existing Advisory wrapper with model identity and the explicit “Offline rules, not AI” label when applicable.

## Do's and Don'ts

### Do:

- **Do** keep Claim and Proof separate and adjacent, with their written relationship.
- **Do** use monochrome for the brand and semantic color only for a real state.
- **Do** retain native labels, keyboard focus, pending copy and existing retry/reload controls.
- **Do** flatten details inside a working surface and let rules align records.
- **Do** preserve every role's existing authorized actions and exact outcome wording.

### Don't:

- **Don't** equate reservation, approval, task completion or a model statement with delivery or verified evidence.
- **Don't** add gradients, glass, decorative status pills, colored side-border cards or nested cards.
- **Don't** add decorative eyebrows, marketing greetings, invented metrics or unsupported controls to working screens.
- **Don't** use color or a dot as the only state label.
- **Don't** treat these source-derived documents as final screenshot approval or a completed shipping verdict.

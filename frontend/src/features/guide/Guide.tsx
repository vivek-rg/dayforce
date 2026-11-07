import { useState } from "react";
import type { Role } from "../../shared/api-types";
import { HandoffIllustration } from "../../shared/HandoffIllustration";
import { Icon } from "../../shared/icons";
import { Field } from "../../shared/ui";
import { ThemeToggle } from "../../shared/theme";
import { GUIDE_FAQS, ROLE_GUIDES, ROLE_ORDER, WORKFLOW } from "./guide-content";

type GuideName = "how-it-works" | "role-guide";

function GuideLinks({ current }: { current?: GuideName }) {
  return (
    <nav className="guide-links" aria-label="Product guide">
      <a
        href="#/how-it-works"
        aria-current={current === "how-it-works" ? "page" : undefined}
      >
        How it works
      </a>
      <a
        href="#/role-guide"
        aria-current={current === "role-guide" ? "page" : undefined}
      >
        Role guide
      </a>
    </nav>
  );
}

function HowItWorks() {
  return (
    <>
      <header className="guide-intro">
        <div>
          <h1>
            Good onboarding.
            <br />
            No loose ends.
          </h1>
          <p>
            One plan across people and teams. Every task has an owner. Every
            completion claim has its own evidence.
          </p>
          <a className="btn btn-primary" href="#/role-guide">
            Find your part in the process
          </a>
        </div>
        <figure className="handoff-example">
          <figcaption>
            <span>A laptop, from request to collection</span>
            <HandoffIllustration />
          </figcaption>
          <dl>
            <div>
              <dt>Request</dt>
              <dd>A device is requested for an employee.</dd>
            </div>
            <div>
              <dt>Review</dt>
              <dd>IT reviews the exact reservation.</dd>
            </div>
            <div>
              <dt>Outcome</dt>
              <dd>Reserved. Collection still pending.</dd>
            </div>
          </dl>
          <p>Reserved ≠ handed over.</p>
          <small>Illustrative demo. No live employee record.</small>
        </figure>
      </header>
      <section className="guide-journey" aria-labelledby="journey-title">
        <div className="guide-section-title">
          <h2 id="journey-title">
            From assigned work
            <br />
            to a checked outcome.
          </h2>
          <p>Five connected steps. Each one has a different responsibility.</p>
        </div>
        <ol className="journey-list">
          {WORKFLOW.map((step, index) => (
            <li key={step.title}>
              <span className="journey-number num" aria-hidden="true">
                {index + 1}
              </span>
              <div>
                <h3>{step.title}</h3>
                <p>{step.detail}</p>
                <span className="journey-owner">{step.owner}</span>
              </div>
            </li>
          ))}
        </ol>
      </section>
      <section className="guide-proof" aria-labelledby="proof-title">
        <div>
          <h2 id="proof-title">
            “Done” is a claim.
            <br />
            Proof is another thing.
          </h2>
          <p>
            Someone can finish their task while a record is missing, a review is
            waiting or a source disagrees. OnboardIQ keeps those facts separate.
          </p>
        </div>
        <dl className="guide-proof-pair">
          <div>
            <dt>Claim</dt>
            <dd>
              <strong>Equipment task marked complete</strong>
              <p>What the person recorded.</p>
            </dd>
          </div>
          <div>
            <dt>Proof</dt>
            <dd>
              <strong>No handover record</strong>
              <p>Collection is unknown—not verified.</p>
            </dd>
          </div>
        </dl>
      </section>
      <section className="guide-faq" aria-labelledby="faq-title">
        <h2 id="faq-title">A few things worth knowing.</h2>
        <div>
          {GUIDE_FAQS.map((item) => (
            <details key={item.question}>
              <summary>{item.question}</summary>
              <p>{item.answer}</p>
            </details>
          ))}
        </div>
      </section>
      <div className="guide-close">
        <h2>
          Understand the handoff.
          <br />
          Then find your own.
        </h2>
        <a className="btn btn-primary" href="#/role-guide">
          Explore the seven roles
        </a>
      </div>
    </>
  );
}

function RoleGuide() {
  const [selected, setSelected] = useState<Role>("HR");
  const role = ROLE_GUIDES[selected];
  return (
    <>
      <header className="guide-role-intro">
        <div>
          <h1>
            Different roles.
            <br />
            One connected start.
          </h1>
          <p>
            Choose a role to see its work, its boundaries and what it hands on.
            This is a guide—not a change to your account.
          </p>
        </div>
        <HandoffIllustration />
      </header>
      <div className="role-explorer">
        <div className="role-picker">
          <nav aria-label="Explore roles">
            {ROLE_ORDER.map((id) => (
              <button
                key={id}
                type="button"
                aria-pressed={selected === id}
                onClick={() => setSelected(id)}
              >
                <Icon name={ROLE_GUIDES[id].icon} />
                <span>{ROLE_GUIDES[id].name}</span>
                <svg
                  className="role-picker-mark"
                  width="16"
                  height="16"
                  viewBox="0 0 16 16"
                  fill="none"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path d={selected === id ? "M3 8h10" : "M3 8h10M8 3v10"} />
                </svg>
              </button>
            ))}
          </nav>
          <div className="role-picker-select">
            <Field label="Explore a role">
              <select
                className="input"
                value={selected}
                onChange={(event) => {
                  const id = ROLE_ORDER.find(
                    (item) => item === event.target.value,
                  );
                  if (id) setSelected(id);
                }}
              >
                {ROLE_ORDER.map((id) => (
                  <option value={id} key={id}>
                    {ROLE_GUIDES[id].name}
                  </option>
                ))}
              </select>
            </Field>
          </div>
        </div>
        <section className="role-detail" aria-labelledby="role-title">
          <div className="role-detail-head">
            <Icon name={role.icon} />
            <h2 id="role-title">{role.name}</h2>
          </div>
          <p className="role-purpose">{role.purpose}</p>
          <h3>Your work</h3>
          <ul className="role-actions">
            {role.actions.map((action) => (
              <li key={action}>{action}</li>
            ))}
          </ul>
          <div className="role-boundary">
            <h3>Where the responsibility stops</h3>
            <p>{role.boundary}</p>
          </div>
          <div className="role-handoff">
            <h3>What you hand on</h3>
            <p>{role.handoff}</p>
          </div>
        </section>
      </div>
      <div className="guide-assurance">
        <Icon name="inbox" />
        <p>
          Everyone sees only their authorized work. The guide never grants
          access, changes a role or approves an action.
        </p>
      </div>
      <div className="guide-close">
        <h2>
          The workflow behind
          <br />
          every role.
        </h2>
        <a className="btn btn-primary" href="#/how-it-works">
          See how it works
        </a>
      </div>
    </>
  );
}

export function GuidePage({
  page,
  embedded = false,
}: {
  page: GuideName;
  embedded?: boolean;
}) {
  const content = (
    <div className="guide-content">
      {page === "how-it-works" ? <HowItWorks /> : <RoleGuide />}
    </div>
  );
  if (embedded)
    return (
      <div className="guide-embedded">
        <GuideLinks current={page} />
        {content}
      </div>
    );
  return (
    <div className="public-guide">
      <a
        className="skip-link"
        href={"#/" + page}
        onClick={(event) => {
          event.preventDefault();
          document.getElementById("guide-main")?.focus();
        }}
      >
        Skip to content
      </a>
      <header className="public-header">
        <a className="public-brand" href="#/how-it-works">
          OnboardIQ<span aria-hidden="true">.</span>
        </a>
        <GuideLinks current={page} />
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <ThemeToggle />
          <a className="btn btn-primary" href="#/">
            Sign in
          </a>
        </div>
      </header>
      <main id="guide-main" tabIndex={-1}>
        {content}
      </main>
      <footer className="public-footer">
        <span>OnboardIQ — clear work, checked outcomes.</span>
        <span>Demonstration system. Fictional company and policies.</span>
        <a href="#/">Open your workspace</a>
      </footer>
    </div>
  );
}

import { type FormEvent, type ReactNode, useEffect, useState } from "react";
import { useAction } from "../../shared/hooks";
import { useSession } from "../../shared/session-context";
import { ActionError, Notice } from "../../shared/ui";
import { LoginArt } from "./LoginArt";

const MIN_PASSWORD = 12;
const SLIDE_MS = 8000;

const DEMO_USERS: [string, string][] = [
  ["hema@northstar.example", "HR"],
  ["imran@northstar.example", "IT"],
  ["padma@northstar.example", "Payroll"],
  ["ben@northstar.example", "Benefits"],
  ["tara@northstar.example", "Training"],
  ["manoj@northstar.example", "Manager"],
  ["priya@northstar.example", "New employee"],
  ["arjun@northstar.example", "New employee"],
];

const SLIDES = [
  {
    lines: ["Simplify", "Employee Onboarding"],
    pill: "with AI",
    lede: "A smart, end-to-end onboarding platform that automates workflows, checks documents, and helps new hires get productive faster.",
  },
  {
    lines: ["Every Task", "Claimed, Then"],
    pill: "Proven",
    lede: "A completed task is a claim. Independent checks show what really happened, so a reserved laptop is never reported as delivered.",
  },
  {
    lines: ["AI Assists,", "People"],
    pill: "Decide",
    lede: "AI reads approved sources, cites them and proposes next steps. HR and IT approve anything that matters.",
  },
];

const stroke = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
} as const;

const FEATURES: [ReactNode, string, string][] = [
  [
    <path key="i" d="M13 3 5 14h6l-1 7 8-11h-6l1-7Z" />,
    "Automated Workflows",
    "From offer to day one",
  ],
  [
    <>
      <path d="M12 3 5 6v5c0 5 3 8 7 10 4-2 7-5 7-10V6l-7-3Z" />
      <path d="m9 12 2 2 4-4" />
    </>,
    "Document Verification",
    "AI-assisted, people approve",
  ],
  [
    <>
      <path d="M21 12a8 8 0 0 1-8 8H5l-2 2V12a8 8 0 0 1 8-8h2a8 8 0 0 1 8 8Z" />
      <path d="M8 12h.01M12 12h.01M16 12h.01" />
    </>,
    "AI HR Assistant",
    "Cited answers, anytime",
  ],
  [
    <>
      <path d="M6 20v-5M12 20V10M18 20V4" strokeWidth="3.5" />
    </>,
    "Progress Tracking",
    "Real-time onboarding status",
  ],
];

function Sparkle() {
  return (
    <svg width="42" height="42" viewBox="0 0 42 42" aria-hidden="true">
      <path
        d="M16 10l3.5 11 11 3.5-11 3.5L16 39l-3.5-11-11-3.5 11-3.5z"
        fill="#f9d9f5"
      />
      <path d="M31 3l2 7 7 2-7 2-2 7-2-7-7-2 7-2z" fill="#ffc6ea" />
    </svg>
  );
}

function Icon({ children }: { children: ReactNode }) {
  return (
    <svg
      width="22"
      height="22"
      viewBox="0 0 24 24"
      aria-hidden="true"
      {...stroke}
    >
      {children}
    </svg>
  );
}

function GoogleLogo() {
  return (
    <svg width="24" height="24" viewBox="0 0 48 48" aria-hidden="true">
      <path
        fill="#EA4335"
        d="M24 9.5c3.5 0 6.7 1.2 9.2 3.6l6.9-6.9C35.9 2.4 30.5 0 24 0 14.6 0 6.5 5.4 2.6 13.2l8 6.2C12.5 13.6 17.8 9.5 24 9.5z"
      />
      <path
        fill="#4285F4"
        d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.7c-.6 3-2.2 5.5-4.7 7.2l7.7 6c4.5-4.2 7.1-10.3 7.1-17.7z"
      />
      <path
        fill="#FBBC05"
        d="M10.6 28.6A14.5 14.5 0 0 1 9.8 24c0-1.6.3-3.2.8-4.6l-8-6.2A24 24 0 0 0 0 24c0 3.9.9 7.5 2.6 10.8l8-6.2z"
      />
      <path
        fill="#34A853"
        d="M24 48c6.5 0 11.9-2.1 15.9-5.8l-7.7-6c-2.2 1.5-5 2.3-8.2 2.3-6.2 0-11.5-4.2-13.4-9.9l-8 6.2C6.5 42.6 14.6 48 24 48z"
      />
    </svg>
  );
}

function MicrosoftLogo() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true">
      <path fill="#F25022" d="M1 1h10.5v10.5H1z" />
      <path fill="#7FBA00" d="M12.5 1H23v10.5H12.5z" />
      <path fill="#00A4EF" d="M1 12.5h10.5V23H1z" />
      <path fill="#FFB900" d="M12.5 12.5H23V23H12.5z" />
    </svg>
  );
}

const MESSAGES = {
  forgot:
    "Passwords can't be reset from this demo. Ask your OnboardIQ administrator for the demo password.",
  google:
    "Google sign-in isn't connected in this demo. Use your email and password.",
  microsoft:
    "Microsoft sign-in isn't connected in this demo. Use your email and password.",
  create:
    "Accounts are created by HR during onboarding, so there is no self sign-up. Open Demo accounts below to try one.",
};

export function LoginPage() {
  const { login, expired } = useSession();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [tooShort, setTooShort] = useState(false);
  const [missingEmail, setMissingEmail] = useState(false);
  const [message, setMessage] = useState<keyof typeof MESSAGES | null>(null);
  const [slide, setSlide] = useState(0);
  const action = useAction();
  const current = SLIDES[slide];

  useEffect(() => {
    if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) return;
    const timer = window.setTimeout(
      () => setSlide((value) => (value + 1) % SLIDES.length),
      SLIDE_MS,
    );
    return () => window.clearTimeout(timer);
  }, [slide]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setMessage(null);
    if (!email.trim()) {
      setMissingEmail(true);
      return;
    }
    setMissingEmail(false);
    if (password.length < MIN_PASSWORD) {
      setTooShort(true);
      return;
    }
    setTooShort(false);
    await action.run(() => login(email.trim(), password));
  }

  return (
    <main className="auth">
      <section className="auth-story" aria-label="About OnboardIQ">
        <svg
          className="auth-waves"
          viewBox="0 0 1000 940"
          preserveAspectRatio="none"
          aria-hidden="true"
        >
          <path
            d="M700 0C640 150 560 230 660 330c120 120 220-160 340-230V0Z"
            fill="#fff"
            opacity="0.05"
          />
          <path
            d="M0 860c220-40 400-110 560-250 150-130 290-230 440-260v590H0Z"
            fill="#fff"
            opacity="0.05"
          />
          <path
            d="M0 930c300-10 560-70 1000-300v310H0Z"
            fill="#8b5cf6"
            opacity="0.35"
          />
        </svg>
        <div className="auth-brand">
          <svg
            className="auth-brand-mark"
            width="40"
            height="40"
            viewBox="0 0 40 40"
            aria-hidden="true"
          >
            <rect width="40" height="40" rx="10" fill="#8450f0" />
            <circle
              cx="20"
              cy="20"
              r="9"
              fill="none"
              stroke="#fff"
              strokeWidth="4"
            />
            <circle cx="21" cy="20" r="3.5" fill="#1b1650" />
          </svg>
          <span className="auth-brand-name">OnboardIQ</span>
          <span className="auth-brand-rule" />
          <span className="auth-brand-tag">Employee Onboarding Platform</span>
        </div>
        <h1 className="auth-headline">
          {current.lines.map((line) => (
            <span key={line}>{line}</span>
          ))}
          <span className="auth-pill">
            {current.pill} <Sparkle />
          </span>
        </h1>
        <p className="auth-lede">{current.lede}</p>
        <ul className="auth-features">
          {FEATURES.map(([icon, title, detail]) => (
            <li key={title} className="auth-feature">
              <span className="auth-feature-icon">
                <svg
                  width="28"
                  height="28"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                  {...stroke}
                >
                  {icon}
                </svg>
              </span>
              <span>
                <strong>{title}</strong>
                <small>{detail}</small>
              </span>
            </li>
          ))}
        </ul>
        <div className="auth-dots">
          {SLIDES.map((item, index) => (
            <button
              key={item.pill}
              type="button"
              className="auth-dot"
              aria-label={`Show message ${index + 1} of ${SLIDES.length}`}
              aria-pressed={slide === index}
              onClick={() => setSlide(index)}
            />
          ))}
        </div>
        <LoginArt />
      </section>
      <section className="auth-panel" aria-labelledby="login-title">
        <div className="auth-card">
          <h2 id="login-title">Welcome Back 👋</h2>
          <p className="auth-subtitle">Sign in to your OnboardIQ account</p>
          <form
            className="auth-form"
            onSubmit={(event) => void submit(event)}
            noValidate
          >
            {expired && (
              <Notice tone="warn" title="Your session ended">
                Sign in again to continue.
              </Notice>
            )}
            <div>
              <label className="auth-label" htmlFor="login-email">
                Email Address
              </label>
              <div className="auth-input">
                <Icon>
                  <rect x="3" y="5" width="18" height="14" rx="2" />
                  <path d="m3 7 9 6 9-6" />
                </Icon>
                <input
                  id="login-email"
                  value={email}
                  placeholder="Enter your email"
                  onChange={(event) => setEmail(event.target.value)}
                  autoComplete="username"
                  inputMode="email"
                  spellCheck={false}
                  autoCapitalize="none"
                  required
                />
              </div>
              {missingEmail && (
                <p className="auth-field-error" role="alert">
                  Enter your email address.
                </p>
              )}
            </div>
            <div>
              <label className="auth-label" htmlFor="login-password">
                Password
              </label>
              <div className="auth-input">
                <Icon>
                  <rect x="5" y="11" width="14" height="10" rx="2" />
                  <path d="M8 11V7a4 4 0 0 1 8 0v4" />
                  <path d="M12 15v2" />
                </Icon>
                <input
                  id="login-password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  placeholder="Enter your password"
                  onChange={(event) => setPassword(event.target.value)}
                  autoComplete="current-password"
                  required
                />
                <button
                  type="button"
                  className="auth-eye"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  aria-pressed={showPassword}
                  onClick={() => setShowPassword((value) => !value)}
                >
                  <Icon>
                    <path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7-10-7-10-7Z" />
                    <circle cx="12" cy="12" r="3" />
                    {!showPassword && <path d="M4 4l16 16" />}
                  </Icon>
                </button>
              </div>
              {tooShort && (
                <p className="auth-field-error" role="alert">
                  Password must be at least {MIN_PASSWORD} characters.
                </p>
              )}
            </div>
            <button
              type="button"
              className="auth-link auth-forgot"
              onClick={() => setMessage("forgot")}
            >
              Forgot password?
            </button>
            <ActionError error={action.error} />
            <button
              type="submit"
              className="auth-submit"
              disabled={action.pending}
            >
              {action.pending ? "Signing in" : "Sign In"}
            </button>
          </form>
          <div className="auth-form">
            <p className="auth-or">or continue with</p>
            <div className="auth-sso-group">
              <button
                type="button"
                className="auth-sso"
                onClick={() => setMessage("google")}
              >
                <GoogleLogo /> Continue with Google
              </button>
              <button
                type="button"
                className="auth-sso"
                onClick={() => setMessage("microsoft")}
              >
                <MicrosoftLogo /> Continue with Microsoft
              </button>
            </div>
          </div>
          {message && (
            <div style={{ marginTop: 14 }}>
              <Notice tone="info">{MESSAGES[message]}</Notice>
            </div>
          )}
          <p className="auth-new">
            New to OnboardIQ?{" "}
            <button
              type="button"
              className="auth-link"
              onClick={() => setMessage("create")}
            >
              Create an account
            </button>
          </p>
          <details className="auth-demo">
            <summary>Demo accounts</summary>
            <ul>
              {DEMO_USERS.map(([address, role]) => (
                <li key={address}>
                  <button
                    type="button"
                    className="auth-demo-user"
                    onClick={() => setEmail(address)}
                  >
                    {role}
                    <small>{address}</small>
                  </button>
                </li>
              ))}
            </ul>
          </details>
          <p className="auth-note muted small">
            Demo environment. All data is synthetic.
          </p>
        </div>
      </section>
    </main>
  );
}

import { type FormEvent, type ReactNode, useEffect, useState } from "react";
import { api } from "../../shared/api";
import { useAction } from "../../shared/hooks";
import { useSession } from "../../shared/session-context";
import { ActionError, Notice } from "../../shared/ui";
import { LoginArt } from "./LoginArt";

declare const __DEMO_PASSWORD__: string;

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

type Mode = "signin" | "forgot" | "signup";

function EmailField({
  value,
  onChange,
}: {
  value: string;
  onChange: (value: string) => void;
}) {
  return (
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
          value={value}
          placeholder="Enter your email"
          onChange={(event) => onChange(event.target.value)}
          autoComplete="username"
          inputMode="email"
          spellCheck={false}
          autoCapitalize="none"
          required
        />
      </div>
    </div>
  );
}

function PasswordField({
  value,
  onChange,
  autoComplete,
  placeholder = "Enter your password",
}: {
  value: string;
  onChange: (value: string) => void;
  autoComplete: string;
  placeholder?: string;
}) {
  const [visible, setVisible] = useState(false);
  return (
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
          type={visible ? "text" : "password"}
          value={value}
          placeholder={placeholder}
          onChange={(event) => onChange(event.target.value)}
          autoComplete={autoComplete}
          required
        />
        <button
          type="button"
          className="auth-eye"
          aria-label={visible ? "Hide password" : "Show password"}
          aria-pressed={visible}
          onClick={() => setVisible((current) => !current)}
        >
          <Icon>
            <path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7-10-7-10-7Z" />
            <circle cx="12" cy="12" r="3" />
            {!visible && <path d="M4 4l16 16" />}
          </Icon>
        </button>
      </div>
    </div>
  );
}

function SignInForm({ onMode }: { onMode: (mode: Mode) => void }) {
  const { login, expired } = useSession();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [problem, setProblem] = useState<string | null>(null);
  const action = useAction();

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!email.trim()) return setProblem("Enter your email address.");
    if (password.length < MIN_PASSWORD) {
      return setProblem(
        `Password must be at least ${MIN_PASSWORD} characters.`,
      );
    }
    setProblem(null);
    await action.run(() => login(email.trim(), password));
  }

  return (
    <>
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
        <EmailField value={email} onChange={setEmail} />
        <PasswordField
          value={password}
          onChange={setPassword}
          autoComplete="current-password"
        />
        <button
          type="button"
          className="auth-link auth-forgot"
          onClick={() => onMode("forgot")}
        >
          Forgot password?
        </button>
        {problem && (
          <p className="auth-field-error" role="alert">
            {problem}
          </p>
        )}
        <ActionError error={action.error} />
        <button type="submit" className="auth-submit" disabled={action.pending}>
          {action.pending ? "Signing in" : "Sign In"}
        </button>
      </form>
      <p className="auth-new">
        New to OnboardIQ?{" "}
        <button
          type="button"
          className="auth-link"
          onClick={() => onMode("signup")}
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
                onClick={() => {
                  setEmail(address);
                  if (__DEMO_PASSWORD__) setPassword(__DEMO_PASSWORD__);
                }}
              >
                {role}
                <small>{address}</small>
              </button>
            </li>
          ))}
        </ul>
      </details>
    </>
  );
}

function ForgotForm({ onMode }: { onMode: (mode: Mode) => void }) {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [problem, setProblem] = useState<string | null>(null);
  const action = useAction();

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!email.trim()) return setProblem("Enter your email address.");
    setProblem(null);
    const result = await action.run(() =>
      api.requestPasswordReset(email.trim()),
    );
    if (result.ok) setSent(true);
  }

  return (
    <>
      <h2 id="login-title">Reset your password</h2>
      <p className="auth-subtitle">HR will give you a temporary password.</p>
      {sent ? (
        <div className="auth-form">
          <Notice tone="info" title="Request sent">
            If that account exists, HR has been told. They will give you a
            temporary password to sign in with.
          </Notice>
        </div>
      ) : (
        <form
          className="auth-form"
          onSubmit={(event) => void submit(event)}
          noValidate
        >
          <EmailField value={email} onChange={setEmail} />
          {problem && (
            <p className="auth-field-error" role="alert">
              {problem}
            </p>
          )}
          <ActionError error={action.error} />
          <button
            type="submit"
            className="auth-submit"
            disabled={action.pending}
          >
            {action.pending ? "Sending" : "Request Reset"}
          </button>
        </form>
      )}
      <p className="auth-new">
        <button
          type="button"
          className="auth-link"
          onClick={() => onMode("signin")}
        >
          Back to sign in
        </button>
      </p>
    </>
  );
}

function SignUpForm({ onMode }: { onMode: (mode: Mode) => void }) {
  const { signUp } = useSession();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [problem, setProblem] = useState<string | null>(null);
  const action = useAction();

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!name.trim()) return setProblem("Enter your full name.");
    if (!email.trim()) return setProblem("Enter your email address.");
    if (password.length < MIN_PASSWORD) {
      return setProblem(
        `Password must be at least ${MIN_PASSWORD} characters.`,
      );
    }
    setProblem(null);
    await action.run(() => signUp(name.trim(), email.trim(), password));
  }

  return (
    <>
      <h2 id="login-title">Create your account</h2>
      <p className="auth-subtitle">
        For new employees. HR then links you to your onboarding plan.
      </p>
      <form
        className="auth-form"
        onSubmit={(event) => void submit(event)}
        noValidate
      >
        <div>
          <label className="auth-label" htmlFor="signup-name">
            Full Name
          </label>
          <div className="auth-input">
            <Icon>
              <circle cx="12" cy="8" r="4" />
              <path d="M4 21c1-4 4-6 8-6s7 2 8 6" />
            </Icon>
            <input
              id="signup-name"
              value={name}
              placeholder="Enter your full name"
              maxLength={200}
              onChange={(event) => setName(event.target.value)}
              autoComplete="name"
              required
            />
          </div>
        </div>
        <EmailField value={email} onChange={setEmail} />
        <PasswordField
          value={password}
          onChange={setPassword}
          autoComplete="new-password"
          placeholder="At least 12 characters"
        />
        {problem && (
          <p className="auth-field-error" role="alert">
            {problem}
          </p>
        )}
        <ActionError error={action.error} />
        <button type="submit" className="auth-submit" disabled={action.pending}>
          {action.pending ? "Creating" : "Create Account"}
        </button>
      </form>
      <p className="auth-new">
        Already have an account?{" "}
        <button
          type="button"
          className="auth-link"
          onClick={() => onMode("signin")}
        >
          Sign in
        </button>
      </p>
    </>
  );
}

export function LoginPage() {
  const [mode, setMode] = useState<Mode>("signin");
  const [slide, setSlide] = useState(0);
  const current = SLIDES[slide];

  useEffect(() => {
    if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) return;
    const timer = window.setTimeout(
      () => setSlide((value) => (value + 1) % SLIDES.length),
      SLIDE_MS,
    );
    return () => window.clearTimeout(timer);
  }, [slide]);

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
          {mode === "signin" && <SignInForm onMode={setMode} />}
          {mode === "forgot" && <ForgotForm onMode={setMode} />}
          {mode === "signup" && <SignUpForm onMode={setMode} />}
          <p className="auth-note muted small">
            Demo environment. All data is synthetic.
          </p>
        </div>
      </section>
    </main>
  );
}

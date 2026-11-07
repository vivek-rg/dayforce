import { type FormEvent, type ReactNode, useState } from "react";
import { HandoffIllustration } from "../../shared/HandoffIllustration";
import { api } from "../../shared/api";
import { useAction } from "../../shared/hooks";
import { useSession } from "../../shared/session-context";
import { ActionError, Notice } from "../../shared/ui";
import { ThemeToggle } from "../../shared/theme";

const MIN_PASSWORD = 12;
const DEMO_PASSWORD = "DemoPassword123!";

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

const stroke = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
} as const;

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
      <h2 id="login-title">Sign in to OnboardIQ</h2>
      <p className="auth-subtitle">
        Continue with your work email and password.
      </p>
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
        <p className="muted small">
          Choose an email, then enter the demo password shared by your team.
        </p>
        <ul>
          {DEMO_USERS.map(([address, role]) => (
            <li key={address}>
              <button
                type="button"
                className="auth-demo-user"
                onClick={() => {
                  setEmail(address);
                  setPassword(DEMO_PASSWORD);
                  setProblem(null);
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

  return (
    <main className="auth">
      <section className="auth-story" aria-label="About OnboardIQ">
        <div className="auth-opening">
          <div className="auth-brand">
            <svg
              className="auth-brand-mark"
              width="32"
              height="32"
              viewBox="0 0 32 32"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              aria-hidden="true"
            >
              <rect x="3" y="5" width="10" height="22" rx="2" />
              <rect x="19" y="5" width="10" height="22" rx="2" />
              <path d="M13 16h6m3-1 2 2 3-4" />
            </svg>
            <span className="auth-brand-name">OnboardIQ</span>
          </div>
          <HandoffIllustration />
        </div>
        <h1 className="auth-headline">
          <span>The next step.</span>
          <span>The right person.</span>
          <span>The proof behind it.</span>
        </h1>
        <p className="auth-lede">
          One place for your onboarding work. See what needs doing, who owns it,
          and what the evidence actually shows.
        </p>
        <figure className="auth-proof">
          <figcaption>A completion claim. A separate check.</figcaption>
          <dl>
            <div>
              <dt>Claim</dt>
              <dd>Equipment task completed</dd>
            </div>
            <div>
              <dt>Proof</dt>
              <dd>
                Reservation recorded.
                <br />
                Handover unknown.
              </dd>
            </div>
          </dl>
          <p>Reserved ≠ handed over.</p>
          <small>Illustrative demo. No live employee record.</small>
        </figure>
      </section>
      <section className="auth-panel" aria-labelledby="login-title">
        <div className="auth-card">
          {mode === "signin" && <SignInForm onMode={setMode} />}
          {mode === "forgot" && <ForgotForm onMode={setMode} />}
          {mode === "signup" && <SignUpForm onMode={setMode} />}
          <nav className="auth-guide-links" aria-label="Learn about OnboardIQ">
            <a href="#/how-it-works">How it works</a>
            <a href="#/role-guide">Find your role</a>
            <ThemeToggle className="theme-toggle-link" />
          </nav>
          <p className="auth-note muted small">
            Demo environment. All data is synthetic.
          </p>
        </div>
      </section>
    </main>
  );
}

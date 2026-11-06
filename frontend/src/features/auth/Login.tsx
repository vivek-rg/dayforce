import { type FormEvent, useState } from "react";
import { useAction } from "../../shared/hooks";
import { useSession } from "../../shared/session-context";
import { ActionError, ClaimProof, Field, Notice } from "../../shared/ui";

const DEMO_USERS: [string, string][] = [
  ["U_HR", "HR"],
  ["U_IT", "IT"],
  ["U_PAYROLL", "Payroll"],
  ["U_BENEFITS", "Benefits"],
  ["U_TRAINING", "Training"],
  ["U_MANAGER", "Manager"],
  ["U_MANAGER2", "Manager"],
  ["U_PRIYA", "Employee"],
  ["U_ARJUN", "Employee"],
  ["U_LEELA", "Employee"],
  ["U_RAVI", "Employee"],
];

const MIN_PASSWORD = 12;

export function LoginPage() {
  const { login, expired } = useSession();
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [tooShort, setTooShort] = useState(false);
  const action = useAction();

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (password.length < MIN_PASSWORD) {
      setTooShort(true);
      return;
    }
    setTooShort(false);
    await action.run(() => login(userId.trim(), password));
  }

  return (
    <main className="login">
      <section className="login-story" aria-label="What OnboardIQ does">
        <p className="brand brand-ink">OnboardIQ</p>
        <h1>
          A completed task is a claim.
          <br />
          Evidence is proof.
        </h1>
        <p className="login-lede">
          Onboarding work is tracked twice: what someone said was done, and what
          independent checks can show. A reservation is never reported as a
          delivery.
        </p>
        <div className="login-example">
          <p className="login-example-title">Hand over laptop</p>
          <ClaimProof
            task={{
              work_state: "COMPLETED",
              display_status: "COMPLETED",
              evidence_result: "UNKNOWN",
              check_type: "device_handover_recorded",
            }}
          />
          <p className="login-example-title">Identity document</p>
          <ClaimProof
            task={{
              work_state: "COMPLETED",
              display_status: "COMPLETED",
              evidence_result: "VERIFIED",
              check_type: "identity_document_verified",
            }}
          />
        </div>
      </section>
      <section className="login-form-wrap" aria-labelledby="login-title">
        <form
          className="login-form"
          onSubmit={(event) => void submit(event)}
          noValidate
        >
          <h2 id="login-title">Sign in</h2>
          {expired && (
            <Notice tone="warn" title="Your session ended">
              Sign in again to continue.
            </Notice>
          )}
          <Field label="User ID">
            <input
              className="input mono"
              value={userId}
              onChange={(event) => setUserId(event.target.value)}
              autoComplete="username"
              spellCheck={false}
              autoCapitalize="none"
              required
            />
          </Field>
          <Field
            label="Password"
            hint={`At least ${MIN_PASSWORD} characters. Use the private demo password.`}
            error={
              tooShort
                ? `Password must be at least ${MIN_PASSWORD} characters.`
                : null
            }
          >
            <input
              className="input"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
              minLength={MIN_PASSWORD}
              required
            />
          </Field>
          <ActionError error={action.error} />
          <button
            type="submit"
            className="btn btn-primary btn-block"
            disabled={action.pending || !userId.trim() || !password}
          >
            {action.pending ? "Signing in" : "Sign in"}
          </button>
          <fieldset className="demo-users">
            <legend>Demo logins. Click to fill the user ID.</legend>
            <ul>
              {DEMO_USERS.map(([id, role]) => (
                <li key={id}>
                  <button
                    type="button"
                    className="demo-user"
                    aria-pressed={userId === id}
                    onClick={() => setUserId(id)}
                  >
                    <span className="mono">{id}</span>
                    <span className="muted">{role}</span>
                  </button>
                </li>
              ))}
            </ul>
          </fieldset>
        </form>
      </section>
    </main>
  );
}

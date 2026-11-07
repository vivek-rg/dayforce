import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import {
  SessionContext,
  type SessionValue,
} from "../../shared/session-context";
import { LoginPage } from "./Login";

function renderLogin(expired = false) {
  const session: SessionValue = {
    user: null,
    expired,
    restoring: false,
    login: vi.fn(),
    signUp: vi.fn(),
    logout: vi.fn(),
  };
  return renderToStaticMarkup(
    createElement(
      SessionContext.Provider,
      { value: session },
      createElement(LoginPage),
    ),
  );
}

describe("purposeful sign-in", () => {
  it("uses one fixed message without a headline selector", () => {
    const html = renderLogin();
    expect(html).toContain("The proof behind it.");
    expect(html).toContain('class="auth-opening"');
    expect(html.match(/class="handoff-illustration"/g)).toHaveLength(1);
    expect(html).not.toMatch(
      /auth-dots?|Show message|About OnboardIQ messages/,
    );
    expect(html).toContain("Illustrative demo. No live employee record.");
    expect(html).toContain("Handover unknown.");
  });

  it("keeps the labelled sign-in form, private demo password and public guides", () => {
    const html = renderLogin();
    expect(html).toContain('for="login-email"');
    expect(html).toMatch(/autocomplete="current-password"/i);
    expect(html).toContain("fill in its email and the demo password");
    expect(html).not.toContain("DemoPassword123!");
    expect(html).toContain('href="#/how-it-works"');
    expect(html).toContain('href="#/role-guide"');
    expect(html).toContain("Forgot password?");
    expect(html).toContain("Create an account");
  });

  it("retains the expired-session recovery message", () => {
    expect(renderLogin(true)).toContain("Your session ended");
    expect(renderLogin(false)).not.toContain("Your session ended");
  });
});

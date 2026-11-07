/** Decorative only: no task status or permission is represented by this drawing. */
export function HandoffIllustration() {
  return (
    <svg
      className="handoff-illustration"
      viewBox="0 0 300 210"
      width="300"
      height="210"
      aria-hidden="true"
      focusable="false"
      fill="none"
      stroke="var(--scene-ink)"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <ellipse
        cx="151"
        cy="186"
        rx="130"
        ry="10"
        fill="var(--scene-muted)"
        stroke="none"
        opacity="0.25"
      />
      <path d="m43 82 162-20 9 103-163 19Z" fill="var(--scene-muted)" />
      <path d="m55 91 140-17 7 81-140 17Z" fill="var(--scene-paper)" />
      <path d="m47 174 170-20 38 25-183 25-44-15Z" fill="var(--scene-paper)" />
      <path
        d="m76 181 126-15 20 12-127 17Z"
        fill="var(--scene-soft)"
        stroke="none"
      />
      <path
        d="m120 190 40-5 10 5-40 5Z"
        fill="var(--scene-muted)"
        stroke="none"
      />
      <circle cx="83" cy="112" r="8" fill="var(--scene-soft)" />
      <path
        d="m101 107 66-8m-65 19 47-6m-65 27 83-10m-82 21 63-8"
        stroke="var(--scene-muted)"
        strokeWidth="3"
      />
      <path d="M210 111q23 14 41-3" stroke="var(--scene-muted)" />
      <g className="handoff-helper">
        <rect
          x="216"
          y="50"
          width="10"
          height="25"
          rx="5"
          fill="var(--scene-muted)"
        />
        <rect
          x="278"
          y="50"
          width="10"
          height="25"
          rx="5"
          fill="var(--scene-muted)"
        />
        <path d="M240 94v11m23-11v11" />
        <rect
          x="224"
          y="29"
          width="56"
          height="64"
          rx="22"
          fill="var(--scene-paper)"
        />
        <rect
          x="232"
          y="48"
          width="40"
          height="26"
          rx="10"
          fill="var(--scene-accent)"
          stroke="none"
        />
        <path
          d="M240 60q4-6 8 0m9 0q4-6 8 0m-16 7h7"
          stroke="var(--scene-paper)"
        />
        <path d="M231 108q21-13 42 0" fill="var(--scene-paper)" />
      </g>
      <g className="handoff-paper">
        <path d="M142 23h29l12 12v44h-41Z" fill="var(--scene-paper)" />
        <path d="M171 23v12h12" fill="var(--scene-accent)" />
        <path d="M151 46h23m-23 10h18m-18 10h12" stroke="var(--scene-muted)" />
      </g>
    </svg>
  );
}

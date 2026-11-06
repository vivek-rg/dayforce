/** The sign-in illustration: a laptop showing a checklist, with an assistant robot beside it. */
const ROWS: [string, boolean][] = [
  ["Complete Your Profile", true],
  ["Upload Documents", true],
  ["Finish Compliance Training", false],
  ["Set Up Your Workspace", false],
];

export function LoginArt() {
  return (
    <div className="auth-art" aria-hidden="true">
      <svg viewBox="0 0 470 560" role="presentation">
        <defs>
          <linearGradient id="art-lid" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#8b7fe0" />
            <stop offset="1" stopColor="#5a45b8" />
          </linearGradient>
          <linearGradient id="art-base" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#f1effc" />
            <stop offset="1" stopColor="#bdb4ea" />
          </linearGradient>
          <linearGradient id="art-robot" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#ffffff" />
            <stop offset="1" stopColor="#d9d3f7" />
          </linearGradient>
          <linearGradient id="art-mug" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stopColor="#ffffff" />
            <stop offset="1" stopColor="#cfc8f2" />
          </linearGradient>
          <linearGradient id="art-leaf" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#58c2a6" />
            <stop offset="1" stopColor="#23705f" />
          </linearGradient>
          <filter id="art-shadow" x="-20%" y="-20%" width="140%" height="150%">
            <feDropShadow
              dx="0"
              dy="14"
              stdDeviation="14"
              floodColor="#120a3a"
              floodOpacity="0.45"
            />
          </filter>
        </defs>

        {/* Sparkles */}
        <path
          d="M386 2 l6 19 19 6 -19 6 -6 19 -6 -19 -19 -6 19 -6z"
          fill="#d9c8ff"
        />
        <path
          d="M412 42 l4 13 13 4 -13 4 -4 13 -4 -13 -13 -4 13 -4z"
          fill="#c79dff"
        />

        {/* Robot */}
        <g filter="url(#art-shadow)">
          <rect x="247" y="74" width="16" height="50" rx="8" fill="#8f7be6" />
          <rect x="352" y="74" width="16" height="50" rx="8" fill="#8f7be6" />
          <ellipse cx="307" cy="145" rx="30" ry="14" fill="#7a68d8" />
          <rect
            x="254"
            y="34"
            width="108"
            height="104"
            rx="46"
            fill="url(#art-robot)"
          />
          <rect x="266" y="62" width="84" height="48" rx="20" fill="#16123a" />
          <path
            d="M281 90 q9 -14 18 0"
            stroke="#c9b6ff"
            strokeWidth="5"
            fill="none"
            strokeLinecap="round"
          />
          <path
            d="M316 90 q9 -14 18 0"
            stroke="#c9b6ff"
            strokeWidth="5"
            fill="none"
            strokeLinecap="round"
          />
          <path
            d="M299 98 q9 8 18 0"
            stroke="#c9b6ff"
            strokeWidth="4"
            fill="none"
            strokeLinecap="round"
          />
        </g>
        <ellipse
          cx="307"
          cy="164"
          rx="34"
          ry="16"
          fill="#6b58cf"
          opacity="0.6"
        />

        {/* Laptop lid */}
        <g filter="url(#art-shadow)">
          <path
            d="M116 216 L448 170 Q462 168 461 182 L440 462 L92 490 Z"
            fill="url(#art-lid)"
          />
          <path d="M128 226 L442 183 L424 452 L106 478 Z" fill="#f5f3fe" />
          <path d="M128 226 L208 215 L190 471 L106 478 Z" fill="#2a2263" />
          <circle cx="146" cy="244" r="8" fill="#8f7be6" />
          <text
            x="156"
            y="248"
            fill="#fff"
            fontSize="9.5"
            fontWeight="700"
            transform="rotate(-6 156 248)"
          >
            OnboardIQ
          </text>
          {[276, 306, 336, 366, 396].map((y, index) => (
            <rect
              key={y}
              x={138 - index * 2}
              y={y - index}
              width="52"
              height="9"
              rx="4"
              fill={index === 0 ? "#6d5bd0" : "#4a3f96"}
            />
          ))}
          <path d="M214 214 L442 183 L440 212 L212 240 Z" fill="#ffffff" />
          <circle cx="400" cy="205" r="5" fill="#c9c3ea" />
          <rect
            x="356"
            y="196"
            width="34"
            height="11"
            rx="5"
            fill="#f2b8d6"
            transform="rotate(-6 356 196)"
          />
          <text
            x="238"
            y="276"
            fill="#16123a"
            fontSize="19"
            fontWeight="800"
            transform="rotate(-5 238 276)"
          >
            Welcome Aboard! 🎉
          </text>
          <path d="M222 296 L420 276 L406 442 L202 460 Z" fill="#ffffff" />
          {ROWS.map(([label, done], index) => {
            const y = 322 + index * 37;
            const x = 240 - index * 3;
            return (
              <g key={label} transform={`rotate(-4 ${x} ${y})`}>
                <rect
                  x={x - 8}
                  y={y - 11}
                  width="15"
                  height="15"
                  rx="3"
                  fill="#a999ec"
                />
                <path
                  d={`M${x - 4} ${y - 4} l3 4 6 -7`}
                  stroke="#fff"
                  strokeWidth="2"
                  fill="none"
                />
                <text x={x + 15} y={y} fill="#2b2654" fontSize="10.5">
                  {label}
                </text>
                {done ? (
                  <>
                    <circle cx={x + 166} cy={y - 4} r="9" fill="#21a95c" />
                    <path
                      d={`M${x + 161} ${y - 4} l4 4 6 -8`}
                      stroke="#fff"
                      strokeWidth="2.2"
                      fill="none"
                    />
                  </>
                ) : (
                  <circle
                    cx={x + 166}
                    cy={y - 4}
                    r="8"
                    fill="none"
                    stroke="#c4bfda"
                    strokeWidth="2"
                  />
                )}
              </g>
            );
          })}
        </g>

        {/* Laptop base */}
        <g filter="url(#art-shadow)">
          <path
            d="M92 490 L440 462 L466 498 Q468 508 456 510 L44 540 Q26 540 34 526 Z"
            fill="url(#art-base)"
          />
          <path
            d="M104 494 L424 470 L440 492 L82 520 Z"
            fill="#a79ee0"
            opacity="0.55"
          />
          <path d="M214 516 L306 509 L312 523 L216 531 Z" fill="#d5cff4" />
        </g>

        {/* Plant */}
        <g>
          <path
            d="M72 470 C40 420 30 370 58 330 C76 380 84 420 76 470Z"
            fill="url(#art-leaf)"
          />
          <path
            d="M72 470 C96 420 118 396 142 384 C138 424 112 462 80 474Z"
            fill="url(#art-leaf)"
          />
          <path
            d="M72 472 C46 450 18 436 2 436 C12 462 40 480 72 480Z"
            fill="#2f8a73"
          />
          <path
            d="M36 468 H114 L106 536 Q104 546 94 546 H56 Q46 546 44 536Z"
            fill="url(#art-mug)"
          />
          <ellipse cx="75" cy="468" rx="39" ry="8" fill="#ece9fb" />
        </g>

        {/* Mug */}
        <g>
          <path
            d="M430 500 q34 0 32 28 q-2 26 -38 26"
            stroke="#d9d3f7"
            strokeWidth="9"
            fill="none"
          />
          <path
            d="M352 490 H436 L428 548 Q426 558 414 558 H374 Q362 558 360 548Z"
            fill="url(#art-mug)"
          />
          <ellipse cx="394" cy="490" rx="42" ry="9" fill="#efedfb" />
          <ellipse cx="394" cy="491" rx="35" ry="6" fill="#3a2410" />
        </g>
      </svg>
    </div>
  );
}

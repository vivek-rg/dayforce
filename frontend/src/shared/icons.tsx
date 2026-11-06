import type { NavIcon } from "./routes";

const PATHS: Record<NavIcon, string> = {
  dashboard: "M3 3h6v8H3zM11 3h6v4h-6zM11 9h6v8h-6zM3 13h6v4H3z",
  people:
    "M7.5 9a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM2 17c0-3 2.5-5 5.5-5s5.500 2 5.500 5M13 3.300a3 3 0 0 1 0 5.400M15 12.500c1.800.6 3 2.300 3 4.500",
  tasks:
    "M3 5l1.500 1.500L7 4M3 10.500 4.500 12 7 9.500M3 16l1.500 1.500L7 15M10 5.500h7M10 11h7M10 16.500h7",
  document: "M5 2h7l4 4v12H5zM12 2v4h4M8 10h5M8 13.500h5",
  device: "M4 4h12v9H4zM2 16h16M8 13v3M12 13v3",
  inbox: "M3 11l2.500-7h9L17 11v5H3zM3 11h4.500l1 2h3l1-2H17",
  payroll: "M3 5h14v10H3zM3 9h14M6 12.500h3",
  benefits: "M10 17s-7-4-7-9a4 4 0 0 1 7-2.500A4 4 0 0 1 17 8c0 5-7 9-7 9z",
  training: "M2 8l8-4 8 4-8 4zM5.500 10v4c1.500 1.500 7.500 1.500 9 0v-4",
  team: "M10 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM4 18v-2a6 6 0 0 1 12 0v2M3 9.500a2 2 0 0 1 1.500-3.500M17 9.500A2 2 0 0 0 15.500 6",
  home: "M3 9l7-6 7 6v8H3zM8 17v-5h4v5",
  assistant: "M3 4h14v10H9l-4 3v-3H3zM7 8h6M7 11h4",
  insights: "M3 17V3M3 17h14M7 13V9M11 13V6M15 13v-3",
  book: "M4 3h9a3 3 0 0 1 3 3v11H7a3 3 0 0 1-3-3zM4 14a3 3 0 0 1 3-3h9",
  bell: "M5 14V9a5 5 0 0 1 10 0v5l1.500 2h-13zM8.500 18.500h3",
  audit: "M3 3h14v14H3zM6.500 7H14M6.500 10H14M6.500 13H11",
  settings:
    "M10 12.500a2.500 2.500 0 1 0 0-5 2.500 2.500 0 0 0 0 5zM10 2v2.500M10 15.500V18M2 10h2.500M15.500 10H18M4.300 4.300 6 6M14 14l1.700 1.700M4.300 15.700 6 14M14 6l1.700-1.700",
};

export function Icon({ name }: { name: NavIcon }) {
  return (
    <svg
      className="icon"
      viewBox="0 0 20 20"
      width="16"
      height="16"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d={PATHS[name]} />
    </svg>
  );
}

export function MenuIcon() {
  return (
    <svg
      className="icon"
      viewBox="0 0 20 20"
      width="18"
      height="18"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      aria-hidden="true"
    >
      <path d="M3 5.500h14M3 10h14M3 14.500h14" />
    </svg>
  );
}

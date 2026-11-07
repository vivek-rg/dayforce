import type { Role } from "../../shared/api-types";
import type { NavIcon } from "../../shared/routes";

export const ROLE_ORDER: Role[] = [
  "HR",
  "IT",
  "PAYROLL",
  "BENEFITS",
  "TRAINING",
  "MANAGER",
  "EMPLOYEE",
];

export const ROLE_GUIDES: Record<
  Role,
  {
    name: string;
    icon: NavIcon;
    purpose: string;
    actions: string[];
    boundary: string;
    handoff: string;
  }
> = {
  HR: {
    name: "HR",
    icon: "people",
    purpose:
      "Set the plan in motion. Keep the people, documents and decisions connected.",
    actions: [
      "Create an employee profile and generate the applicable onboarding plan.",
      "Assign and follow up on work, review submitted documents and request corrections.",
      "Answer clarification questions and review proposed work-location changes.",
      "Maintain approved knowledge, inspect scoped activity and run escalation checks.",
    ],
    boundary:
      "HR does not approve IT equipment reservations or record department-owned payroll, benefits, training or handover outcomes.",
    handoff:
      "The approved profile and plan give every responsible team its next piece of work.",
  },
  IT: {
    name: "IT",
    icon: "device",
    purpose:
      "Prepare equipment and access. Record exactly what has happened, not what is planned.",
    actions: [
      "Inspect assets and access requests within your scope.",
      "Request a device and review equipment-reservation proposals.",
      "Record simulated provisioning and, when appropriate, confirm a device handover.",
    ],
    boundary:
      "A request is not a reservation. A reservation is not a handover. Access provisioning here is a local simulation, not a live company-system integration.",
    handoff:
      "Fresh source records let independent checks distinguish reserved equipment from equipment actually handed over.",
  },
  PAYROLL: {
    name: "Payroll",
    icon: "payroll",
    purpose:
      "Make payroll setup visible without putting financial details into this workspace.",
    actions: [
      "Review the employees and payroll records assigned to your scope.",
      "Record bank-form and tax-form submission status.",
      "Record profile creation, then confirm setup when its prerequisites are met.",
    ],
    boundary:
      "Only submission and setup status is stored here—not bank-account numbers, tax identifiers or actual payroll payments.",
    handoff:
      "Recorded setup status becomes evidence for the payroll check; a completed task alone does not establish it.",
  },
  BENEFITS: {
    name: "Benefits",
    icon: "benefits",
    purpose: "Keep invitation and enrolment states clear for each employee.",
    actions: [
      "Review benefits records for employees in your scope.",
      "Record invitation, enrolment or declined states using the existing controls.",
      "Follow your assigned work and any questions addressed to you.",
    ],
    boundary:
      "Recording an enrolment state is not an integration with an insurer. Employees retain their own decline-benefits control.",
    handoff:
      "The recorded enrolment or decline supplies the exact outcome checked by the plan.",
  },
  TRAINING: {
    name: "Training",
    icon: "training",
    purpose: "Follow the required learning and record completion honestly.",
    actions: [
      "See assigned training records for employees in your scope.",
      "Mark an assigned course completed when the completion is established.",
      "Track your owned tasks and answer your addressed questions.",
    ],
    boundary:
      "A course-completion record is not a test of competence or certification, and this demo does not connect to a live learning platform.",
    handoff:
      "The completion record supports the training check; the task claim stays a separate fact.",
  },
  MANAGER: {
    name: "Manager",
    icon: "team",
    purpose:
      "Make the first week concrete, and keep your part of the plan moving.",
    actions: [
      "Review your assigned hires, their start dates and permitted plan details.",
      "Choose a buddy and record a first-week plan.",
      "Start or complete your owned tasks and respond to questions addressed to you.",
    ],
    boundary:
      "Team access is scoped. A manager cannot review HR documents, approve another role's actions or turn task completion into independent proof.",
    handoff:
      "Your recorded buddy and first-week plan provide evidence for the manager-plan check.",
  },
  EMPLOYEE: {
    name: "Employee",
    icon: "home",
    purpose:
      "Know what to do next, what you have submitted and what is waiting on someone else.",
    actions: [
      "Use your onboarding page to find your next action and checklist.",
      "Upload required documents, see review feedback and replace files when requested.",
      "Start and complete your owned tasks, answer your questions and, if needed, decline benefits.",
      "Ask the knowledge assistant about approved guidance; source search remains available when AI is off.",
    ],
    boundary:
      "You see your own authorized onboarding—not other employees' records. Uploading is not approval, and marking complete does not verify a document or equipment handover.",
    handoff:
      "Your submissions and answers go to the responsible reviewer; the page keeps waiting work and actual proof distinct.",
  },
};

export const WORKFLOW = [
  {
    title: "Assign the right work",
    owner: "HR + approved rules",
    detail:
      "An approved worker and location profile determines the applicable plan, owners, dates and dependencies.",
  },
  {
    title: "Do your part",
    owner: "The responsible person",
    detail:
      "People submit documents, record department work and complete their owned tasks. Completion records a claim.",
  },
  {
    title: "Check the evidence",
    owner: "Independent application checks",
    detail:
      "The system reads permitted source records. Missing or unavailable evidence stays unknown; a real mismatch is blocked.",
  },
  {
    title: "Review the exact change",
    owner: "The authorized reviewer",
    detail:
      "When recovery needs a location change or device reservation, the correct HR or IT reviewer sees the proposed change before it can run.",
  },
  {
    title: "Read back the outcome",
    owner: "Trusted application code",
    detail:
      "Current permissions and input versions are checked again. The recorded result says exactly what changed and what is still pending.",
  },
];

export const GUIDE_FAQS = [
  {
    question: "Does a completed task mean everything is verified?",
    answer:
      "No. Completion is a person's claim. The Claim / Proof pair shows that claim beside the independently checked outcome. Unknown, blocked and not-applicable are different states.",
  },
  {
    question: "What does the AI do?",
    answer:
      "When enabled, it can help with approved-source answers, advisory document extraction, investigation steps and insight summaries. It does not own permissions or approvals. The responsible person still reviews a proposed action.",
  },
  {
    question: "Can people work when AI is off?",
    answer:
      "Yes. Manual tasks, document review, department records and human approvals continue. The interface states when AI is unavailable or when labelled offline rules are being used.",
  },
  {
    question: "Are equipment and access connected to real company systems?",
    answer:
      "No. These are fictional, local demonstration records. A reservation means set aside; only a handover record supports collection. Simulated provisioning does not create a real account.",
  },
  {
    question: "Can this guide change what my account can do?",
    answer:
      "No. The guide is public, static product information. Choosing a role here changes the explanation only. Real workspace access is checked against the signed-in user's current role and employee scope.",
  },
];

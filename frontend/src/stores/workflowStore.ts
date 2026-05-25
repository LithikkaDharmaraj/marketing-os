import { create } from "zustand";
import type { WorkflowStep } from "@/types/workflow";

const STEP_ORDER: WorkflowStep[] = [
  "intake", "scraping", "cleaning", "extracting",
  "positioning", "icp_generating", "embedding", "completed",
];

interface WorkflowStore {
  runId: string | null;
  currentStep: WorkflowStep;
  percent: number;
  stepLabel: string;
  message: string;
  error: string | null;
  isComplete: boolean;
  isFailed: boolean;
  setRunId: (id: string) => void;
  updateProgress: (step: WorkflowStep, percent: number, label: string, msg: string, err?: string) => void;
  reset: () => void;
}

export const useWorkflowStore = create<WorkflowStore>((set) => ({
  runId: null,
  currentStep: "intake",
  percent: 0,
  stepLabel: "Starting...",
  message: "",
  error: null,
  isComplete: false,
  isFailed: false,

  setRunId: (id) => set({ runId: id }),
  updateProgress: (step, percent, label, msg, err) =>
    set({
      currentStep: step,
      percent,
      stepLabel: label,
      message: msg,
      error: err || null,
      isComplete: step === "completed",
      isFailed: step === "failed",
    }),
  reset: () =>
    set({
      runId: null,
      currentStep: "intake",
      percent: 0,
      stepLabel: "Starting...",
      message: "",
      error: null,
      isComplete: false,
      isFailed: false,
    }),
}));

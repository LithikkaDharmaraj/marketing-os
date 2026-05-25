import { create } from "zustand";
import type { IntakeFormData } from "@/types/intake";

const DEFAULT_TENANT_ID = "00000000-0000-0000-0000-000000000001";

interface IntakeStore {
  currentStep: number;
  totalSteps: number;
  formData: Partial<IntakeFormData>;
  isSubmitting: boolean;
  submittedCompanyId: string | null;
  submittedRunId: string | null;
  setStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  updateFormData: (data: Partial<IntakeFormData>) => void;
  setSubmitting: (v: boolean) => void;
  setSubmitResult: (companyId: string, runId: string) => void;
  reset: () => void;
}

export const useIntakeStore = create<IntakeStore>((set) => ({
  currentStep: 1,
  totalSteps: 5,
  formData: {
    tenant_id: DEFAULT_TENANT_ID,
    contacts: [],
    competitors: [],
  },
  isSubmitting: false,
  submittedCompanyId: null,
  submittedRunId: null,

  setStep: (step) => set({ currentStep: step }),
  nextStep: () => set((s) => ({ currentStep: Math.min(s.currentStep + 1, s.totalSteps) })),
  prevStep: () => set((s) => ({ currentStep: Math.max(s.currentStep - 1, 1) })),
  updateFormData: (data) => set((s) => ({ formData: { ...s.formData, ...data } })),
  setSubmitting: (v) => set({ isSubmitting: v }),
  setSubmitResult: (companyId, runId) =>
    set({ submittedCompanyId: companyId, submittedRunId: runId, isSubmitting: false }),
  reset: () =>
    set({
      currentStep: 1,
      formData: { tenant_id: DEFAULT_TENANT_ID, contacts: [], competitors: [] },
      isSubmitting: false,
      submittedCompanyId: null,
      submittedRunId: null,
    }),
}));

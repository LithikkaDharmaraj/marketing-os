"use client";

import { useMutation } from "@tanstack/react-query";
import { submitIntake } from "@/lib/api";
import { useIntakeStore } from "@/stores/intakeStore";
import { useWorkflowStore } from "@/stores/workflowStore";
import { useRouter } from "next/navigation";
import type { IntakeFormData, IntakeResponse } from "@/types/intake";

export function useSubmitIntake() {
  const { setSubmitting, setSubmitResult } = useIntakeStore();
  const { setRunId } = useWorkflowStore();
  const router = useRouter();

  return useMutation<IntakeResponse, Error, IntakeFormData>({
    mutationFn: (data) => submitIntake(data),
    onMutate: () => setSubmitting(true),
    onSuccess: (data) => {
      setSubmitResult(data.company_id, data.workflow_run_id);
      setRunId(data.workflow_run_id);
      router.push(`/intelligence/${data.company_id}?run=${data.workflow_run_id}`);
    },
    onError: () => setSubmitting(false),
  });
}

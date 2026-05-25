"use client";

import { useEffect, useRef } from "react";
import type { WorkflowProgress } from "@/types/workflow";
import { useWorkflowStore } from "@/stores/workflowStore";

const SSE_BASE = process.env.NEXT_PUBLIC_API_URL || "/api";
const MAX_ERRORS = 5;

export function useSSE(workflowRunId: string | null) {
  const eventSourceRef = useRef<EventSource | null>(null);
  const errorCountRef = useRef(0);
  const updateProgress = useWorkflowStore((s) => s.updateProgress);
  const { isComplete, isFailed } = useWorkflowStore();

  useEffect(() => {
    if (!workflowRunId || isComplete || isFailed) return;

    errorCountRef.current = 0;

    const url = `${SSE_BASE}/v1/events/${workflowRunId}`;
    const es = new EventSource(url);
    eventSourceRef.current = es;

    es.onmessage = (event) => {
      errorCountRef.current = 0;
      try {
        const data: WorkflowProgress = JSON.parse(event.data);
        if (data.type === "progress" || data.type === "connected") {
          updateProgress(
            data.step,
            data.percent,
            data.step_label,
            data.message,
            data.error ?? undefined
          );
          if (data.step === "completed" || data.step === "failed") {
            es.close();
          }
        }
      } catch {
        // ignore parse errors
      }
    };

    es.onerror = () => {
      errorCountRef.current += 1;
      // SSE connections naturally retry — only treat as permanent failure after
      // several consecutive errors with no successful message in between.
      if (errorCountRef.current >= MAX_ERRORS) {
        updateProgress("failed", 0, "Connection error", "Lost connection to server");
        es.close();
      }
    };

    return () => {
      es.close();
    };
  }, [workflowRunId, isComplete, isFailed, updateProgress]);

  return eventSourceRef;
}

"use client";

import { useWorkflowStore } from "@/stores/workflowStore";
import { useSSE } from "@/hooks/useSSE";
import { CheckCircle, Circle, Loader2, XCircle } from "lucide-react";

const STEPS = [
  { key: "scraping", label: "Web Scraping" },
  { key: "extracting", label: "AI Extraction" },
  { key: "positioning", label: "Positioning" },
  { key: "icp_generating", label: "ICP Generation" },
  { key: "embedding", label: "Vector Memory" },
  { key: "completed", label: "Complete" },
];

interface Props {
  runId: string;
}

export function WorkflowProgress({ runId }: Props) {
  useSSE(runId);
  const { currentStep, percent, stepLabel, message, isComplete, isFailed, error } =
    useWorkflowStore();

  return (
    <div className="card p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">Processing your business data</h3>
        <span className="text-sm text-gray-500">{percent}%</span>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-100 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${
            isFailed ? "bg-red-500" : isComplete ? "bg-green-500" : "bg-brand-500"
          }`}
          style={{ width: `${percent}%` }}
        />
      </div>

      {/* Current step */}
      <div className="flex items-center gap-3">
        {isFailed ? (
          <XCircle className="w-5 h-5 text-red-500 shrink-0" />
        ) : isComplete ? (
          <CheckCircle className="w-5 h-5 text-green-500 shrink-0" />
        ) : (
          <Loader2 className="w-5 h-5 text-brand-500 animate-spin shrink-0" />
        )}
        <div>
          <p className="text-sm font-medium text-gray-900">{stepLabel}</p>
          {message && <p className="text-xs text-gray-500">{message}</p>}
          {error && <p className="text-xs text-red-500">{error}</p>}
        </div>
      </div>

      {/* Steps timeline */}
      <div className="flex items-center gap-1">
        {STEPS.map((step, idx) => {
          const stepIdx = STEPS.findIndex((s) => s.key === currentStep);
          const isDone = idx < stepIdx || isComplete;
          const isActive = step.key === currentStep && !isComplete;
          return (
            <div key={step.key} className="flex items-center flex-1">
              <div className="flex flex-col items-center gap-1 flex-1">
                <div
                  className={`w-3 h-3 rounded-full transition-colors ${
                    isDone
                      ? "bg-green-500"
                      : isActive
                      ? "bg-brand-500 ring-2 ring-brand-200"
                      : "bg-gray-200"
                  }`}
                />
                <span className="text-[10px] text-gray-500 text-center leading-tight">
                  {step.label}
                </span>
              </div>
              {idx < STEPS.length - 1 && (
                <div
                  className={`h-0.5 flex-1 mb-4 transition-colors ${
                    isDone ? "bg-green-400" : "bg-gray-200"
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

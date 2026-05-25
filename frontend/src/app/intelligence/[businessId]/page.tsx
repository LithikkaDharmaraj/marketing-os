"use client";

import { useEffect } from "react";
import { useParams, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Navbar } from "@/components/shared/Navbar";
import { WorkflowProgress } from "@/components/shared/WorkflowProgress";
import { IntelligenceDashboard } from "@/components/intelligence/IntelligenceDashboard";
import { useBusinessProfile } from "@/hooks/useBusinessProfile";
import { useWorkflowStore } from "@/stores/workflowStore";
import { getWorkflowStatus } from "@/lib/api";
import { Loader2, XCircle } from "lucide-react";

export default function IntelligencePage() {
  const { businessId } = useParams<{ businessId: string }>();
  const searchParams = useSearchParams();
  const runId = searchParams.get("run");
  const { isComplete, isFailed, updateProgress } = useWorkflowStore();

  const { data, isLoading, error } = useBusinessProfile(businessId);

  // Resolve SSE race condition: if the workflow already completed before EventSource
  // subscribed, we'd never receive the "completed" event. Check DB status on mount.
  useEffect(() => {
    if (!runId || isComplete || isFailed) return;
    getWorkflowStatus(runId)
      .then((wf) => {
        if (wf.status === "completed") {
          updateProgress("completed", 100, "Complete", "Marketing blueprint ready");
        } else if (wf.status === "failed") {
          updateProgress("failed", 0, "Failed", "Processing failed");
        }
      })
      .catch(() => {});
    // Only run once on mount — intentionally omitting isComplete/isFailed/updateProgress
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [runId]);

  // Safety net: if React Query returns a business_profile, the workflow must be done.
  // Note: this may fire after effect 1 already set isFailed (e.g., embedding step failed
  // but intelligence succeeded). The Zustand isComplete flag is set here so WorkflowProgress
  // and the "View Positioning" button show correctly.
  useEffect(() => {
    if (data?.business_profile) {
      updateProgress("completed", 100, "Complete", "Marketing blueprint ready");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data?.business_profile]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Business Intelligence</h1>
            <p className="text-sm text-gray-500 mt-1">AI-extracted business profile and market intelligence</p>
          </div>
          {(isComplete || !!data?.business_profile) && (
            <Link
              href={`/positioning/${businessId}`}
              className="btn-primary"
            >
              View Positioning →
            </Link>
          )}
        </div>

        {runId && !isComplete && !data?.business_profile && (
          <div className="mb-6">
            <WorkflowProgress runId={runId} />
          </div>
        )}

        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
          </div>
        ) : error ? (
          <div className="card p-6 text-center">
            <XCircle className="w-8 h-8 text-red-400 mx-auto mb-3" />
            <p className="font-medium text-gray-800">Failed to load intelligence data</p>
            <p className="text-sm text-gray-500 mt-1">{(error as Error).message}</p>
            <button onClick={() => window.location.reload()} className="mt-4 btn-primary text-sm">
              Retry
            </button>
          </div>
        ) : data?.business_profile ? (
          <IntelligenceDashboard
            profile={data.business_profile}
            companyName={data.company_name}
            aiDiscoveredCompetitors={data.ai_discovered_competitors || []}
            userSuggestedCompetitors={data.user_suggested_competitors || []}
            competitorProfiles={data.competitor_profiles || []}
          />
        ) : data?.status === "completed" || data?.status === "failed" || isFailed ? (
          // Workflow finished but business_profile is null — extraction failed or hit rate limit.
          // Also covers the case where company.intelligence_status wasn't updated on failure.
          <div className="card p-8 text-center">
            <XCircle className="w-8 h-8 text-red-400 mx-auto mb-3" />
            <p className="font-semibold text-gray-800">Intelligence extraction incomplete</p>
            <p className="text-sm text-gray-500 mt-2">
              {data?.status === "failed" || isFailed
                ? "The workflow failed during processing. Please try submitting again."
                : "Processing completed but AI extraction produced no output. This is usually caused by API rate limits — please wait a moment and retry."}
            </p>
            <button onClick={() => window.location.reload()} className="mt-4 btn-primary text-sm">
              Refresh
            </button>
          </div>
        ) : (
          <div className="card p-8 text-center">
            <Loader2 className="w-8 h-8 text-brand-400 animate-spin mx-auto mb-3" />
            <p className="text-gray-500">Analyzing your business data...</p>
            <p className="text-xs text-gray-400 mt-1">This usually takes 2–5 minutes</p>
          </div>
        )}
      </div>
    </div>
  );
}

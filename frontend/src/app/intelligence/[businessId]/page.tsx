"use client";

import { useEffect } from "react";
import { useParams, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Navbar } from "@/components/shared/Navbar";
import { WorkflowProgress } from "@/components/shared/WorkflowProgress";
import { IntelligenceDashboard } from "@/components/intelligence/IntelligenceDashboard";
import { useBusinessProfile } from "@/hooks/useBusinessProfile";
import { useWorkflowStore } from "@/stores/workflowStore";
import { Loader2, XCircle } from "lucide-react";

export default function IntelligencePage() {
  const { businessId } = useParams<{ businessId: string }>();
  const searchParams = useSearchParams();
  const runId = searchParams.get("run");
  const { isComplete, isFailed, updateProgress } = useWorkflowStore();

  const { data, isLoading, error } = useBusinessProfile(businessId);

  // Safety net: if business_profile loaded, mark workflow complete in store.
  useEffect(() => {
    if (data?.business_profile) {
      updateProgress("completed", 100, "Complete", "Marketing blueprint ready");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data?.business_profile]);

  // Derive stuck state directly from the API response — works even without a ?run= param
  // and across page refreshes / direct navigation.
  const workflowRunStatus = (data as any)?.workflow_run_status as string | undefined;
  const isStuck =
    !data?.business_profile &&
    !isLoading &&
    !error &&
    (
      data?.status === "failed" ||
      data?.status === "completed" ||
      workflowRunStatus === "failed" ||
      workflowRunStatus === "completed" ||
      isFailed
    );

  const stuckReason =
    workflowRunStatus === "failed" || data?.status === "failed" || isFailed
      ? "The workflow failed during processing."
      : "Processing completed but AI extraction produced no output — likely caused by API rate limits.";

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
            <Link href={`/positioning/${businessId}`} className="btn-primary">
              View Positioning →
            </Link>
          )}
        </div>

        {runId && !isComplete && !data?.business_profile && !isStuck && (
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
          />
        ) : isStuck ? (
          <div className="card p-8 text-center">
            <XCircle className="w-8 h-8 text-red-400 mx-auto mb-3" />
            <p className="font-semibold text-gray-800">Intelligence extraction incomplete</p>
            <p className="text-sm text-gray-500 mt-2">{stuckReason}</p>
            <p className="text-sm text-gray-400 mt-1">
              Please submit the intake form again to re-run the full pipeline.
            </p>
            <Link href="/intake" className="mt-4 btn-primary text-sm inline-block">
              Re-submit Intake
            </Link>
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

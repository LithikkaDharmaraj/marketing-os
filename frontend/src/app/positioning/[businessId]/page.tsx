"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { Navbar } from "@/components/shared/Navbar";
import { PositioningBoard } from "@/components/positioning/PositioningBoard";
import { usePositioning } from "@/hooks/usePositioning";
import { Loader2 } from "lucide-react";

export default function PositioningPage() {
  const { businessId } = useParams<{ businessId: string }>();
  const { data, isLoading, error } = usePositioning(businessId);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Positioning Strategy</h1>
            <p className="text-sm text-gray-500 mt-1">AI-generated positioning, messaging angles, and emotional triggers</p>
          </div>
          <Link href={`/icp/${businessId}`} className="btn-primary">
            View ICPs →
          </Link>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
          </div>
        ) : error || !data ? (
          <div className="card p-6 text-center text-gray-500">
            Positioning not yet generated. Check back after processing completes.
          </div>
        ) : (
          <PositioningBoard
            profile={data}
            companyId={businessId}
            isApproved={data.is_approved}
          />
        )}
      </div>
    </div>
  );
}

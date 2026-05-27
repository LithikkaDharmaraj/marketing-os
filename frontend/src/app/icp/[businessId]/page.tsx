"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { Navbar } from "@/components/shared/Navbar";
import { ICPView } from "@/components/icp/ICPView";
import { useICPs } from "@/hooks/useICP";
import { Loader2 } from "lucide-react";

export default function ICPPage() {
  const { businessId } = useParams<{ businessId: string }>();
  const { data, isLoading, error } = useICPs(businessId);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Ideal Customer Profiles</h1>
            <p className="text-sm text-gray-500 mt-1">AI-generated buyer personas with firmographic and psychographic detail</p>
          </div>
          <div className="flex gap-3">
            <Link href={`/targets/${businessId}`} className="btn-primary">
              View Targets →
            </Link>
            <Link href={`/blueprint/${businessId}`} className="btn-secondary">
              Blueprint
            </Link>
          </div>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
          </div>
        ) : error || !data?.length ? (
          <div className="card p-6 text-center text-gray-500">
            ICP profiles not yet generated. Processing may still be in progress.
          </div>
        ) : (
          <ICPView profiles={data} />
        )}
      </div>
    </div>
  );
}

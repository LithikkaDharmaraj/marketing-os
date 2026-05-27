"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { Loader2, RefreshCw } from "lucide-react";
import { Navbar } from "@/components/shared/Navbar";
import { TargetCompaniesView } from "@/components/targets/TargetCompaniesView";
import { useTargetCompanies, useTargetContacts } from "@/hooks/useTargets";

export default function TargetsPage() {
  const { businessId } = useParams<{ businessId: string }>();
  const { data: companies, isLoading: loadingCompanies } = useTargetCompanies(businessId);
  const { data: contacts, isLoading: loadingContacts } = useTargetContacts(businessId);

  const isLoading = loadingCompanies || loadingContacts;
  const empty = !isLoading && (!companies?.length);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">GTM Target Intelligence</h1>
            <p className="text-sm text-gray-500 mt-1">
              AI-discovered prospect companies and recommended contacts for outreach
            </p>
          </div>
          <Link href={`/blueprint/${businessId}`} className="btn-primary">
            View Blueprint →
          </Link>
        </div>

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-24 gap-3">
            <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
            <p className="text-sm text-gray-500">Loading target intelligence...</p>
          </div>
        ) : empty ? (
          <div className="card p-8 text-center space-y-3">
            <RefreshCw className="w-8 h-8 text-gray-300 mx-auto" />
            <p className="text-gray-500">Target discovery is still processing or not yet started.</p>
            <p className="text-sm text-gray-400">
              Run the full analysis pipeline to generate target companies and contacts.
            </p>
            <Link href={`/icp/${businessId}`} className="btn-secondary inline-block mt-2">
              ← Back to ICPs
            </Link>
          </div>
        ) : (
          <TargetCompaniesView
            companies={companies ?? []}
            contacts={contacts ?? []}
          />
        )}
      </div>
    </div>
  );
}

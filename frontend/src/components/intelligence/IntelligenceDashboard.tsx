"use client";

import type { BusinessProfile, ProductIntelligence, CompetitorSummary } from "@/types/intelligence";
import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

interface Props {
  profile: BusinessProfile;
  companyName: string;
  // Legacy competitor props — kept for API compat but no longer rendered prominently
  aiDiscoveredCompetitors?: unknown[];
  userSuggestedCompetitors?: unknown[];
  competitorProfiles?: CompetitorSummary[];
}

export function IntelligenceDashboard({ profile, companyName }: Props) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card p-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{companyName}</h2>
            <p className="text-gray-500 mt-1">{profile.industry}{profile.sub_industry ? ` · ${profile.sub_industry}` : ""}</p>
          </div>
          <span className="inline-flex items-center gap-1.5 bg-green-50 text-green-700 text-sm font-medium px-3 py-1 rounded-full">
            <span className="w-2 h-2 bg-green-500 rounded-full" />
            {Math.round(profile.confidence_score * 100)}% confidence
          </span>
        </div>
        <p className="mt-4 text-gray-700 text-lg font-medium italic">"{profile.value_proposition}"</p>
      </div>

      {/* Product Intelligence — primary GTM driver */}
      {profile.product_intelligence?.product_name && (
        <ProductIntelligenceCard product={profile.product_intelligence} />
      )}

      {/* Business Profile Grid */}
      <div className="grid grid-cols-3 gap-4">
        <InfoCard label="Business Model" value={profile.business_model} />
        <InfoCard label="Company Stage" value={profile.company_stage} />
        <InfoCard label="Market Position" value={profile.market_position} />
        <InfoCard label="Pricing Model" value={profile.pricing_model} />
        <InfoCard label="Company Size" value={profile.company_size_range} />
        <InfoCard label="Funding Stage" value={profile.funding_stage} />
      </div>

      {/* Target Segments */}
      {profile.target_segments?.length > 0 && (
        <div className="card p-6">
          <h3 className="font-semibold text-gray-900 mb-3">Target Segments</h3>
          <div className="flex flex-wrap gap-2">
            {profile.target_segments.map((s) => (
              <span key={s} className="bg-blue-50 text-blue-700 text-sm px-3 py-1 rounded-full">{s}</span>
            ))}
          </div>
        </div>
      )}

      {/* Key Differentiators */}
      {profile.key_differentiators?.length > 0 && (
        <div className="card p-6">
          <h3 className="font-semibold text-gray-900 mb-3">Key Differentiators</h3>
          <ul className="space-y-2">
            {profile.key_differentiators.map((d, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="text-brand-500 mt-0.5">✦</span> {d}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Growth Signals */}
      {profile.growth_signals?.length > 0 && (
        <div className="card p-6">
          <h3 className="font-semibold text-gray-900 mb-3">Growth Signals</h3>
          <div className="flex flex-wrap gap-2">
            {profile.growth_signals.map((s) => (
              <span key={s} className="bg-amber-50 text-amber-700 text-sm px-3 py-1 rounded-full">{s}</span>
            ))}
          </div>
        </div>
      )}

      {/* Competitors — lightweight, collapsed by default */}
      {profile.competitive_landscape?.length > 0 && (
        <CompetitorsCollapsed competitors={profile.competitive_landscape} />
      )}
    </div>
  );
}

function CompetitorsCollapsed({ competitors }: { competitors: CompetitorSummary[] }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="card p-5">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between text-left"
      >
        <div>
          <p className="font-semibold text-gray-700 text-sm">Known Competitors</p>
          <p className="text-xs text-gray-400 mt-0.5">{competitors.length} identified</p>
        </div>
        {open ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
      </button>
      {open && (
        <div className="mt-4 flex flex-wrap gap-2">
          {competitors.map((c, i) => (
            <span key={i} className="text-sm bg-gray-100 text-gray-700 px-3 py-1.5 rounded-lg">
              {c.name}
              {c.positioning && <span className="text-gray-400 text-xs ml-1.5">· {c.positioning.slice(0, 40)}</span>}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

function ProductIntelligenceCard({ product }: { product: ProductIntelligence }) {
  return (
    <div className="card p-6 border-l-4 border-brand-500">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900">Product Intelligence</h3>
        <span className="text-xs font-medium bg-brand-50 text-brand-700 px-2.5 py-1 rounded-full">GTM Core Driver</span>
      </div>

      <div className="space-y-4">
        <div>
          <p className="text-sm font-semibold text-gray-900">{product.product_name}</p>
          {product.product_description && (
            <p className="text-sm text-gray-600 mt-1">{product.product_description}</p>
          )}
        </div>

        {product.main_problem_solved && (
          <div className="bg-orange-50 border border-orange-100 rounded-lg p-3">
            <p className="text-xs font-medium text-orange-700 uppercase tracking-wide mb-1">Problem Solved</p>
            <p className="text-sm text-orange-900">{product.main_problem_solved}</p>
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          {product.main_features?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Main Features</p>
              <ul className="space-y-1">
                {product.main_features.slice(0, 6).map((f, i) => (
                  <li key={i} className="flex items-start gap-1.5 text-xs text-gray-700">
                    <span className="text-brand-500 mt-0.5 shrink-0">✦</span> {f}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {product.use_cases?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Use Cases</p>
              <ul className="space-y-1">
                {product.use_cases.slice(0, 5).map((u, i) => (
                  <li key={i} className="flex items-start gap-1.5 text-xs text-gray-700">
                    <span className="text-indigo-400 mt-0.5 shrink-0">→</span> {u}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="flex flex-wrap gap-3 pt-1 border-t border-gray-100">
          {product.target_industry && (
            <div>
              <p className="text-xs text-gray-400">Target Industry</p>
              <p className="text-sm font-medium text-gray-800">{product.target_industry}</p>
            </div>
          )}
          {product.target_company_size && (
            <div>
              <p className="text-xs text-gray-400">Ideal Company Size</p>
              <p className="text-sm font-medium text-gray-800">{product.target_company_size}</p>
            </div>
          )}
          {product.deployment_model && (
            <div>
              <p className="text-xs text-gray-400">Deployment</p>
              <p className="text-sm font-medium text-gray-800">{product.deployment_model}</p>
            </div>
          )}
        </div>

        {product.pricing_signals?.length > 0 && (
          <div>
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Pricing Signals</p>
            <div className="flex flex-wrap gap-1.5">
              {product.pricing_signals.map((s, i) => (
                <span key={i} className="text-xs bg-green-50 text-green-700 border border-green-100 px-2 py-0.5 rounded-full">{s}</span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  if (!value) return null;
  return (
    <div className="card p-4">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className="font-semibold text-gray-900 text-sm">{value}</p>
    </div>
  );
}

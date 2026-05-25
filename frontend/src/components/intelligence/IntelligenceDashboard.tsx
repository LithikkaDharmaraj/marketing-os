"use client";

import type { BusinessProfile, DiscoveredCompetitor, CompetitorSummary } from "@/types/intelligence";

interface Props {
  profile: BusinessProfile;
  companyName: string;
  aiDiscoveredCompetitors?: DiscoveredCompetitor[];
  userSuggestedCompetitors?: DiscoveredCompetitor[];
  /** Legacy prop — mapped to aiDiscoveredCompetitors when new props are absent */
  competitorProfiles?: CompetitorSummary[];
}

export function IntelligenceDashboard({
  profile,
  companyName,
  aiDiscoveredCompetitors,
  userSuggestedCompetitors,
  competitorProfiles = [],
}: Props) {
  // Resolve props: new keys take priority over legacy competitor_profiles
  const aiCompetitors: DiscoveredCompetitor[] =
    aiDiscoveredCompetitors ??
    (competitorProfiles as unknown as DiscoveredCompetitor[]);
  const userCompetitors: DiscoveredCompetitor[] = userSuggestedCompetitors ?? [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card p-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{companyName}</h2>
            <p className="text-gray-500 mt-1">{profile.industry} · {profile.sub_industry}</p>
          </div>
          <div className="text-right">
            <span className="inline-flex items-center gap-1.5 bg-green-50 text-green-700 text-sm font-medium px-3 py-1 rounded-full">
              <span className="w-2 h-2 bg-green-500 rounded-full" />
              {Math.round(profile.confidence_score * 100)}% confidence
            </span>
          </div>
        </div>
        <p className="mt-4 text-gray-700 text-lg font-medium italic">
          "{profile.value_proposition}"
        </p>
      </div>

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
      <div className="card p-6">
        <h3 className="font-semibold text-gray-900 mb-3">Target Segments</h3>
        <div className="flex flex-wrap gap-2">
          {profile.target_segments.map((s) => (
            <span key={s} className="bg-blue-50 text-blue-700 text-sm px-3 py-1 rounded-full">{s}</span>
          ))}
        </div>
      </div>

      {/* Key Differentiators */}
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

      {/* Growth Signals */}
      {profile.growth_signals.length > 0 && (
        <div className="card p-6">
          <h3 className="font-semibold text-gray-900 mb-3">Growth Signals</h3>
          <div className="flex flex-wrap gap-2">
            {profile.growth_signals.map((s) => (
              <span key={s} className="bg-amber-50 text-amber-700 text-sm px-3 py-1 rounded-full">{s}</span>
            ))}
          </div>
        </div>
      )}

      {/* ── AI-Discovered Competitors ─────────────────────────────────────── */}
      {aiCompetitors.length > 0 && (
        <div className="card p-6">
          <div className="flex items-center justify-between mb-1">
            <h3 className="font-semibold text-gray-900">AI-Discovered Competitors</h3>
            <span className="inline-flex items-center gap-1 text-xs font-medium bg-violet-50 text-violet-700 px-2.5 py-1 rounded-full">
              <span className="w-1.5 h-1.5 rounded-full bg-violet-500" />
              AI Intelligence Engine
            </span>
          </div>
          <p className="text-xs text-gray-400 mb-5">
            Autonomously discovered by AI analysis — not based on user input
          </p>

          {/* Direct competitors */}
          {(() => {
            const direct = aiCompetitors.filter((c) => c.competitor_type === "direct" || !c.competitor_type);
            const indirect = aiCompetitors.filter((c) => c.competitor_type === "indirect");
            const emerging = aiCompetitors.filter((c) => c.competitor_type === "emerging");
            return (
              <div className="space-y-6">
                {direct.length > 0 && (
                  <CompetitorGroup title="Direct Competitors" competitors={direct} />
                )}
                {indirect.length > 0 && (
                  <CompetitorGroup title="Indirect Competitors" competitors={indirect} />
                )}
                {emerging.length > 0 && (
                  <CompetitorGroup title="Emerging Competitors" competitors={emerging} />
                )}
              </div>
            );
          })()}
        </div>
      )}

      {/* ── User-Suggested Competitors ────────────────────────────────────── */}
      {userCompetitors.length > 0 && (
        <div className="card p-6">
          <div className="flex items-center justify-between mb-1">
            <h3 className="font-semibold text-gray-900">User-Suggested Competitors</h3>
            <span className="inline-flex items-center gap-1 text-xs font-medium bg-gray-100 text-gray-600 px-2.5 py-1 rounded-full">
              <span className="w-1.5 h-1.5 rounded-full bg-gray-400" />
              Manually provided
            </span>
          </div>
          <p className="text-xs text-gray-400 mb-5">
            Competitors entered during intake — enriched with scraped website intelligence
          </p>
          <div className="space-y-4">
            {userCompetitors.map((c, i) => (
              <DiscoveredCompetitorCard key={i} competitor={c} />
            ))}
          </div>
        </div>
      )}

      {/* Fallback: no new data, fall back to lightweight competitive_landscape */}
      {aiCompetitors.length === 0 && userCompetitors.length === 0 && profile.competitive_landscape.length > 0 && (
        <div className="card p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Competitive Landscape</h3>
          <div className="space-y-3">
            {profile.competitive_landscape.map((c, i) => (
              <LegacyCompetitorRow key={i} competitor={c} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Sub-components ────────────────────────────────────────────────────────

function InfoCard({ label, value }: { label: string; value: string }) {
  if (!value) return null;
  return (
    <div className="card p-4">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className="font-semibold text-gray-900 text-sm">{value}</p>
    </div>
  );
}

function CompetitorGroup({
  title,
  competitors,
}: {
  title: string;
  competitors: DiscoveredCompetitor[];
}) {
  return (
    <div>
      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">{title}</p>
      <div className="space-y-4">
        {competitors.map((c, i) => (
          <DiscoveredCompetitorCard key={i} competitor={c} />
        ))}
      </div>
    </div>
  );
}

const LEVEL_STYLES: Record<string, { badge: string; dot: string }> = {
  "Highly Competitive":     { badge: "bg-red-100 text-red-700",    dot: "bg-red-500" },
  "Moderately Competitive": { badge: "bg-amber-100 text-amber-700", dot: "bg-amber-500" },
  "Less Competitive":       { badge: "bg-green-100 text-green-700", dot: "bg-green-500" },
};

const SOURCE_LABEL: Record<string, string> = {
  ai_reasoning:      "AI Reasoning",
  google_search:     "Search Analysis",
  vector_similarity: "Semantic Match",
  user_provided:     "User Provided",
};

function DiscoveredCompetitorCard({ competitor: c }: { competitor: DiscoveredCompetitor }) {
  const level = c.competitiveness_level || "";
  const style = LEVEL_STYLES[level] ?? { badge: "bg-gray-100 text-gray-600", dot: "bg-gray-400" };
  const sourceLabel = SOURCE_LABEL[c.discovery_source] || c.discovery_source;
  const domain = c.website?.replace(/^https?:\/\/(www\.)?/, "") || "";
  const hasScores = c.confidence_score > 0 || c.similarity_score > 0;

  return (
    <div className="border border-gray-200 rounded-xl p-5 space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-gray-100 rounded-lg flex items-center justify-center text-sm font-bold text-gray-700 shrink-0">
            {c.name.charAt(0).toUpperCase()}
          </div>
          <div>
            <p className="font-semibold text-gray-900">{c.name}</p>
            {domain && <p className="text-xs text-gray-400">{domain}</p>}
          </div>
        </div>
        <div className="flex flex-col items-end gap-1.5 shrink-0">
          {level && (
            <span className={`inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full ${style.badge}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${style.dot}`} />
              {level}
            </span>
          )}
          <span className="text-xs text-gray-400">{sourceLabel}</span>
        </div>
      </div>

      {/* Category + type badges */}
      <div className="flex flex-wrap gap-2">
        {c.category && (
          <span className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full">{c.category}</span>
        )}
        {c.competitor_type && c.competitor_type !== "direct" && (
          <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full capitalize">{c.competitor_type}</span>
        )}
        {c.market_segment && (
          <span className="text-xs bg-purple-50 text-purple-700 px-2 py-0.5 rounded-full">{c.market_segment}</span>
        )}
      </div>

      {/* Positioning */}
      {c.positioning && (
        <p className="text-sm text-gray-600 italic">"{c.positioning}"</p>
      )}

      {/* Messaging style */}
      {c.messaging_style && (
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Messaging Style</p>
          <p className="text-sm text-gray-700">{c.messaging_style}</p>
        </div>
      )}

      {/* Target audience */}
      {c.target_audience?.length > 0 && (
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Target Audience</p>
          <div className="flex flex-wrap gap-1.5">
            {c.target_audience.map((a, i) => (
              <span key={i} className="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full">{a}</span>
            ))}
          </div>
        </div>
      )}

      {/* Core features */}
      {c.core_features?.length > 0 && (
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Core Features</p>
          <div className="flex flex-wrap gap-1.5">
            {c.core_features.slice(0, 5).map((f, i) => (
              <span key={i} className="text-xs border border-gray-200 text-gray-700 px-2 py-0.5 rounded-full">{f}</span>
            ))}
          </div>
        </div>
      )}

      {/* Pricing */}
      {c.pricing_model && (
        <div className="flex items-center gap-2 text-sm">
          <span className="text-gray-500 text-xs font-medium uppercase tracking-wide">Pricing:</span>
          <span className="text-gray-700">{c.pricing_model}</span>
          {c.estimated_company_size && (
            <>
              <span className="text-gray-300">·</span>
              <span className="text-gray-700">{c.estimated_company_size}</span>
            </>
          )}
        </div>
      )}

      {/* Strengths vs Differentiation side-by-side */}
      {((c.strengths?.length ?? 0) > 0 || (c.differentiation_opportunities?.length ?? 0) > 0) && (
        <div className="grid grid-cols-2 gap-4 pt-1">
          {(c.strengths?.length ?? 0) > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Their Strengths</p>
              <ul className="space-y-1">
                {c.strengths!.slice(0, 3).map((s, i) => (
                  <li key={i} className="flex items-start gap-1.5 text-xs text-gray-700">
                    <span className="text-red-400 mt-0.5 shrink-0">•</span> {s}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {(c.differentiation_opportunities?.length ?? 0) > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Your Opportunities</p>
              <ul className="space-y-1">
                {c.differentiation_opportunities!.slice(0, 3).map((o, i) => (
                  <li key={i} className="flex items-start gap-1.5 text-xs text-gray-700">
                    <span className="text-green-500 mt-0.5 shrink-0">→</span> {o}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Weaknesses */}
      {(c.weaknesses?.length ?? 0) > 0 && (
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Their Weaknesses vs You</p>
          <ul className="space-y-1">
            {c.weaknesses!.slice(0, 3).map((w, i) => (
              <li key={i} className="flex items-start gap-1.5 text-xs text-gray-700">
                <span className="text-amber-400 mt-0.5 shrink-0">△</span> {w}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Scores */}
      {hasScores && (
        <div className="flex gap-4 pt-1 border-t border-gray-100">
          {c.confidence_score > 0 && (
            <div>
              <p className="text-xs text-gray-400">Confidence</p>
              <p className="text-sm font-semibold text-gray-700">{Math.round(c.confidence_score * 100)}%</p>
            </div>
          )}
          {c.similarity_score > 0 && (
            <div>
              <p className="text-xs text-gray-400">Similarity</p>
              <p className="text-sm font-semibold text-gray-700">{Math.round(c.similarity_score * 100)}%</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function LegacyCompetitorRow({ competitor }: { competitor: CompetitorSummary }) {
  return (
    <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
      <div className="w-8 h-8 bg-gray-200 rounded-lg flex items-center justify-center text-xs font-bold text-gray-600 shrink-0">
        {competitor.name.charAt(0)}
      </div>
      <div>
        <p className="font-medium text-gray-900 text-sm">{competitor.name}</p>
        <p className="text-xs text-gray-500 mt-0.5">{competitor.positioning}</p>
        {competitor.key_differentiator && (
          <p className="text-xs text-gray-400 mt-1 italic">vs you: {competitor.key_differentiator}</p>
        )}
      </div>
    </div>
  );
}

"use client";

import type { PositioningProfile } from "@/types/positioning";
import { useApprovePositioning } from "@/hooks/usePositioning";
import { CheckCircle } from "lucide-react";

interface Props {
  profile: PositioningProfile;
  companyId: string;
  isApproved?: boolean;
}

export function PositioningBoard({ profile, companyId, isApproved }: Props) {
  const approveMutation = useApprovePositioning(companyId);

  return (
    <div className="space-y-6">
      {/* Core Positioning */}
      <div className="card p-6 border-l-4 border-brand-500">
        <p className="text-xs font-semibold text-brand-600 uppercase tracking-wide mb-2">
          Core Positioning Statement
        </p>
        <p className="text-xl font-semibold text-gray-900">
          {profile.core_positioning.statement}
        </p>
        <div className="flex gap-3 mt-3">
          <span className="bg-brand-50 text-brand-700 text-xs px-3 py-1 rounded-full">
            {profile.core_positioning.category}
          </span>
          {profile.core_positioning.market_frame && (
            <span className="bg-gray-100 text-gray-600 text-xs px-3 py-1 rounded-full">
              {profile.core_positioning.market_frame}
            </span>
          )}
        </div>
      </div>

      {/* Segment Positioning */}
      {profile.segment_positioning.length > 0 && (
        <div className="card p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Segment Positioning</h3>
          <div className="grid grid-cols-2 gap-4">
            {profile.segment_positioning.map((seg, i) => (
              <div key={i} className="bg-gradient-to-br from-gray-50 to-white border border-gray-200 rounded-xl p-4">
                <p className="text-xs text-gray-500 font-medium uppercase tracking-wide mb-2">{seg.segment}</p>
                <p className="font-bold text-gray-900 text-lg">{seg.headline}</p>
                <p className="text-gray-500 text-sm mt-1 italic">"{seg.tagline}"</p>
                {seg.proof_point && (
                  <p className="text-xs text-green-600 mt-2 font-medium">✓ {seg.proof_point}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Messaging Angles */}
      {profile.messaging_angles.length > 0 && (
        <div className="card p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Messaging Angles</h3>
          <div className="space-y-3">
            {profile.messaging_angles.map((angle, i) => (
              <div key={i} className="flex gap-4 p-4 bg-gray-50 rounded-xl">
                <div className="w-16 shrink-0">
                  <span className="text-xs font-bold text-brand-600 uppercase">{angle.angle_name}</span>
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{angle.message}</p>
                  {angle.emotional_hook && (
                    <p className="text-xs text-amber-600 mt-1">⚡ {angle.emotional_hook}</p>
                  )}
                  {angle.use_case && (
                    <p className="text-xs text-gray-500 mt-1">Use case: {angle.use_case}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Emotional Triggers */}
      {profile.emotional_triggers.length > 0 && (
        <div className="card p-6">
          <h3 className="font-semibold text-gray-900 mb-3">Emotional Triggers</h3>
          <div className="grid grid-cols-3 gap-3">
            {profile.emotional_triggers.map((t, i) => (
              <div key={i} className="bg-red-50 border border-red-100 rounded-lg p-3">
                <p className="text-xs font-bold text-red-600 uppercase">{t.trigger}</p>
                <p className="text-xs text-gray-600 mt-1">{t.audience}</p>
                <p className="text-xs text-gray-800 mt-2 italic">"{t.message}"</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Competitive Moats */}
      {profile.competitive_moats.length > 0 && (
        <div className="card p-6">
          <h3 className="font-semibold text-gray-900 mb-3">Competitive Moats</h3>
          <div className="flex flex-wrap gap-2">
            {profile.competitive_moats.map((m, i) => (
              <span key={i} className="bg-purple-50 text-purple-700 text-sm px-3 py-1 rounded-full">{m}</span>
            ))}
          </div>
        </div>
      )}

      {/* Approve */}
      {!isApproved && (
        <div className="flex justify-end">
          <button
            className="btn-primary flex items-center gap-2"
            onClick={() => approveMutation.mutate()}
            disabled={approveMutation.isPending}
          >
            <CheckCircle className="w-4 h-4" />
            Approve Positioning
          </button>
        </div>
      )}

      {isApproved && (
        <div className="flex items-center gap-2 text-green-600 text-sm justify-end">
          <CheckCircle className="w-4 h-4" />
          Positioning Approved
        </div>
      )}
    </div>
  );
}

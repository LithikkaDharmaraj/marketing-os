"use client";

import type { ICPProfile } from "@/types/icp";
import { useState } from "react";

interface Props {
  profiles: ICPProfile[];
}

export function ICPView({ profiles }: Props) {
  const [activeIdx, setActiveIdx] = useState(0);
  const active = profiles[activeIdx];

  if (!active) return null;

  return (
    <div className="space-y-6">
      {/* Tabs */}
      <div className="flex gap-2 flex-wrap">
        {profiles.map((p, i) => (
          <button
            key={i}
            onClick={() => setActiveIdx(i)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              i === activeIdx
                ? "bg-brand-500 text-white"
                : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
            }`}
          >
            {p.profile_name}
          </button>
        ))}
      </div>

      {/* Active ICP */}
      <div className="grid grid-cols-3 gap-6">
        {/* Left: Firmographics */}
        <div className="col-span-1 space-y-4">
          <div className="card p-4">
            <h3 className="font-semibold text-gray-900 text-sm mb-3">Firmographics</h3>
            <FirmoRow label="Industries" items={active.firmographics.industries} color="blue" />
            <FirmoRow label="Company Size" items={active.firmographics.company_sizes} color="green" />
            <FirmoRow label="Revenue" items={active.firmographics.revenue_ranges} color="purple" />
            <FirmoRow label="Geography" items={active.firmographics.geographies} color="amber" />
            <FirmoRow label="Funding" items={active.firmographics.funding_stages} color="gray" />
          </div>

          <div className="card p-4">
            <h3 className="font-semibold text-gray-900 text-sm mb-3">Job Titles</h3>
            <div className="flex flex-wrap gap-1.5">
              {active.job_titles.map((t, i) => (
                <span key={i} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">{t}</span>
              ))}
            </div>
          </div>
        </div>

        {/* Center: Psychographics + Pain Points */}
        <div className="col-span-2 space-y-4">
          <div className="card p-5">
            <h3 className="font-semibold text-gray-900 mb-3">Psychographics</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs font-semibold text-green-600 uppercase mb-2">Goals</p>
                <ul className="space-y-1">
                  {active.psychographics.goals.map((g, i) => (
                    <li key={i} className="text-sm text-gray-700 flex gap-1.5"><span className="text-green-500">✓</span>{g}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="text-xs font-semibold text-red-600 uppercase mb-2">Fears</p>
                <ul className="space-y-1">
                  {active.psychographics.fears.map((f, i) => (
                    <li key={i} className="text-sm text-gray-700 flex gap-1.5"><span className="text-red-500">!</span>{f}</li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-gray-100">
              <span className="text-xs text-gray-500">Decision style: </span>
              <span className="text-sm font-medium text-gray-700">{active.psychographics.decision_style}</span>
            </div>
          </div>

          {/* Pain Points */}
          <div className="card p-5">
            <h3 className="font-semibold text-gray-900 mb-3">Pain Points</h3>
            <div className="space-y-3">
              {active.pain_points.map((p, i) => (
                <div key={i} className="flex gap-3">
                  <span className={`text-xs font-bold px-2 py-0.5 rounded shrink-0 h-fit mt-0.5 ${
                    p.severity === "high" ? "bg-red-100 text-red-700" :
                    p.severity === "medium" ? "bg-amber-100 text-amber-700" :
                    "bg-gray-100 text-gray-600"
                  }`}>
                    {p.severity}
                  </span>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{p.pain}</p>
                    {p.current_solution && (
                      <p className="text-xs text-gray-500 mt-0.5">Currently: {p.current_solution}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Buying Triggers */}
          <div className="card p-5">
            <h3 className="font-semibold text-gray-900 mb-3">Buying Triggers</h3>
            <div className="flex flex-wrap gap-2">
              {active.buying_triggers.map((t, i) => (
                <span key={i} className="bg-green-50 text-green-700 text-sm px-3 py-1 rounded-full">{t}</span>
              ))}
            </div>
          </div>

          {/* Sample Messaging */}
          {active.sample_messaging && (
            <div className="card p-5 border-l-4 border-brand-400">
              <p className="text-xs font-semibold text-brand-600 uppercase mb-2">Sample Outreach Message</p>
              <p className="text-sm text-gray-700 italic">"{active.sample_messaging}"</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function FirmoRow({ label, items, color }: { label: string; items: string[]; color: string }) {
  if (!items?.length) return null;
  const colorMap: Record<string, string> = {
    blue: "bg-blue-50 text-blue-700",
    green: "bg-green-50 text-green-700",
    purple: "bg-purple-50 text-purple-700",
    amber: "bg-amber-50 text-amber-700",
    gray: "bg-gray-100 text-gray-600",
  };
  return (
    <div className="mb-3">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <div className="flex flex-wrap gap-1">
        {items.map((item, i) => (
          <span key={i} className={`text-xs px-2 py-0.5 rounded ${colorMap[color]}`}>{item}</span>
        ))}
      </div>
    </div>
  );
}

"use client";

import { useState } from "react";
import { useIntakeStore } from "@/stores/intakeStore";
import { Plus, X } from "lucide-react";

interface Props {
  onNext: () => void;
  onBack: () => void;
}

export function CompetitorStep({ onNext, onBack }: Props) {
  const { formData, updateFormData } = useIntakeStore();
  const [input, setInput] = useState("");

  const add = () => {
    const raw = input.trim();
    if (!raw) return;
    updateFormData({ competitors: [...(formData.competitors || []), raw] });
    setInput("");
  };

  const remove = (idx: number) => {
    const comps = [...(formData.competitors || [])];
    comps.splice(idx, 1);
    updateFormData({ competitors: comps });
  };

  const hasMax = (formData.competitors || []).length >= 5;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Competitors</h2>
        <p className="text-sm text-gray-500 mt-1">
          Add competitor names or website URLs. Completely optional — AI auto-discovers competitors from your web presence.
        </p>
      </div>

      <div className="space-y-3">
        {!hasMax && (
          <div className="flex gap-2">
            <input
              className="input-field"
              placeholder="competitor.com or Competitor Name"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && add()}
            />
            <button className="btn-secondary shrink-0" onClick={add}>
              <Plus className="w-4 h-4" />
            </button>
          </div>
        )}

        {(formData.competitors || []).map((item, i) => (
          <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100">
            <span className="text-sm text-gray-700 truncate">{item}</span>
            <button onClick={() => remove(i)} className="text-gray-400 hover:text-red-500 ml-2 shrink-0">
              <X className="w-4 h-4" />
            </button>
          </div>
        ))}

        {(formData.competitors || []).length === 0 && (
          <div className="text-center py-8 text-gray-400 text-sm border-2 border-dashed border-gray-200 rounded-xl">
            <p className="font-medium">No competitors added</p>
            <p className="text-xs mt-1">AI will discover them automatically from Google, LinkedIn & Crunchbase</p>
          </div>
        )}
      </div>

      <div className="flex justify-between">
        <button className="btn-secondary" onClick={onBack}>← Back</button>
        <div className="flex gap-3">
          <button className="btn-secondary text-gray-500" onClick={onNext}>
            Skip for now
          </button>
          <button className="btn-primary" onClick={onNext}>
            Next: Contacts →
          </button>
        </div>
      </div>
    </div>
  );
}

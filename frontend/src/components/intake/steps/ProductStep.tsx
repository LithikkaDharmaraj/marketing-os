"use client";

import { useIntakeStore } from "@/stores/intakeStore";

const PRODUCT_TYPES = [
  "SaaS Platform", "Mobile App", "API / Developer Tool",
  "Services", "Physical Product", "Marketplace", "Other"
];

interface Props {
  onNext: () => void;
  onBack: () => void;
}

export function ProductStep({ onNext, onBack }: Props) {
  const { formData, updateFormData } = useIntakeStore();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Product Details</h2>
        <p className="text-sm text-gray-500 mt-1">
          Optional hints — AI will extract the full product story from your website.
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="label">Product Type <span className="text-gray-400 font-normal">(optional)</span></label>
          <select
            className="input-field"
            value={formData.product_type || ""}
            onChange={(e) => updateFormData({ product_type: e.target.value })}
          >
            <option value="">Select type (AI will infer if skipped)</option>
            {PRODUCT_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>

        <div>
          <label className="label">Pricing Range <span className="text-gray-400 font-normal">(optional)</span></label>
          <input
            className="input-field"
            placeholder="e.g. $500–$5,000/month, Freemium, Custom"
            value={formData.pricing_range || ""}
            onChange={(e) => updateFormData({ pricing_range: e.target.value })}
          />
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 text-sm text-blue-700">
        <p className="font-medium mb-1">What AI extracts from your website:</p>
        <ul className="list-disc list-inside space-y-0.5 text-blue-600">
          <li>Core product features and differentiators</li>
          <li>Pricing signals and packaging</li>
          <li>Problems solved and use cases</li>
          <li>Target audience and segments</li>
        </ul>
      </div>

      <div className="flex justify-between">
        <button className="btn-secondary" onClick={onBack}>← Back</button>
        <button className="btn-primary" onClick={onNext}>Next: Competitors →</button>
      </div>
    </div>
  );
}

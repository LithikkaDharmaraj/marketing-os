"use client";

import { useIntakeStore } from "@/stores/intakeStore";

const INDUSTRIES = [
  "FinTech", "HealthTech", "EdTech", "SaaS", "E-Commerce", "Manufacturing",
  "Logistics", "Real Estate", "HR Tech", "Legal Tech", "Marketing Tech",
  "CleanTech", "AgriTech", "Other"
];

interface Props {
  onNext: () => void;
}

export function CompanyInfoStep({ onNext }: Props) {
  const { formData, updateFormData } = useIntakeStore();

  const isValid =
    formData.company_name?.trim() &&
    formData.website_url?.trim() &&
    formData.industry &&
    formData.geography?.trim();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Company Information</h2>
        <p className="text-sm text-gray-500 mt-1">
          Enter your website — our AI will crawl and extract everything else automatically.
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="label">Company Name *</label>
          <input
            className="input-field"
            placeholder="e.g. Lendkraft"
            value={formData.company_name || ""}
            onChange={(e) => updateFormData({ company_name: e.target.value })}
          />
        </div>

        <div>
          <label className="label">Website URL *</label>
          <input
            className="input-field"
            placeholder="https://yourcompany.com"
            value={formData.website_url || ""}
            onChange={(e) => updateFormData({ website_url: e.target.value })}
          />
          <p className="text-xs text-gray-400 mt-1">
            This is the primary source — AI will extract your product, positioning, and audience from here.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">Industry *</label>
            <select
              className="input-field"
              value={formData.industry || ""}
              onChange={(e) => updateFormData({ industry: e.target.value })}
            >
              <option value="">Select industry</option>
              {INDUSTRIES.map((i) => <option key={i} value={i}>{i}</option>)}
            </select>
          </div>

          <div>
            <label className="label">Geography / HQ *</label>
            <input
              className="input-field"
              placeholder="e.g. India, USA, Global"
              value={formData.geography || ""}
              onChange={(e) => updateFormData({ geography: e.target.value })}
            />
          </div>
        </div>

        <div>
          <label className="label">LinkedIn URL <span className="text-gray-400 font-normal">(optional)</span></label>
          <input
            className="input-field"
            placeholder="https://linkedin.com/company/..."
            value={formData.linkedin_url || ""}
            onChange={(e) => updateFormData({ linkedin_url: e.target.value })}
          />
        </div>

        <div>
          <label className="label">Additional Notes <span className="text-gray-400 font-normal">(optional)</span></label>
          <textarea
            className="input-field min-h-[72px] resize-none"
            placeholder="Anything specific you want the AI to focus on or know about your business..."
            value={formData.additional_notes || ""}
            onChange={(e) => updateFormData({ additional_notes: e.target.value })}
          />
        </div>
      </div>

      <div className="flex justify-end">
        <button
          className="btn-primary"
          onClick={onNext}
          disabled={!isValid}
        >
          Next: Product →
        </button>
      </div>
    </div>
  );
}

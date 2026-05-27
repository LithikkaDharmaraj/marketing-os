"use client";

import { useIntakeStore } from "@/stores/intakeStore";

const INDUSTRIES = [
  "Banking", "Healthcare", "SaaS", "Retail", "Logistics",
  "FinTech", "EdTech", "Legal Tech", "HR Tech", "Real Estate",
  "Manufacturing", "E-Commerce", "CleanTech", "Other",
];

const COMPANY_SIZES = ["Startup", "SMB", "Mid-Market", "Enterprise"];

const DEPARTMENTS = [
  "Sales", "Marketing", "HR", "Compliance",
  "Operations", "Finance", "Engineering", "Legal",
];

const PRICING_OPTIONS = ["Low", "Mid", "Enterprise"];

interface Props {
  onNext: () => void;
  onBack: () => void;
}

function MultiSelect({
  options,
  selected,
  onChange,
}: {
  options: string[];
  selected: string[];
  onChange: (val: string[]) => void;
}) {
  const toggle = (item: string) => {
    onChange(selected.includes(item) ? selected.filter((x) => x !== item) : [...selected, item]);
  };

  return (
    <div className="flex flex-wrap gap-2">
      {options.map((opt) => (
        <button
          key={opt}
          type="button"
          onClick={() => toggle(opt)}
          className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors ${
            selected.includes(opt)
              ? "bg-brand-600 text-white border-brand-600"
              : "bg-white text-gray-600 border-gray-200 hover:border-brand-300"
          }`}
        >
          {opt}
        </button>
      ))}
    </div>
  );
}

export function ProductStep({ onNext, onBack }: Props) {
  const { formData, updateFormData } = useIntakeStore();

  const isValid =
    formData.product_description?.trim() &&
    formData.main_problem_solved?.trim();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Product Details</h2>
        <p className="text-sm text-gray-500 mt-1">Key context for the AI analysis pipeline.</p>
      </div>

      <div className="space-y-5">
        <div>
          <label className="label">Product Description *</label>
          <input
            className="input-field"
            placeholder="AI-powered compliance automation platform for banks."
            value={formData.product_description || ""}
            onChange={(e) => updateFormData({ product_description: e.target.value })}
          />
        </div>

        <div>
          <label className="label">Main Problem Solved *</label>
          <input
            className="input-field"
            placeholder="Manual compliance workflows"
            value={formData.main_problem_solved || ""}
            onChange={(e) => updateFormData({ main_problem_solved: e.target.value })}
          />
        </div>

        <div>
          <label className="label">
            Target Industry <span className="text-gray-400 font-normal">(optional)</span>
          </label>
          <MultiSelect
            options={INDUSTRIES}
            selected={formData.target_industry || []}
            onChange={(val) => updateFormData({ target_industry: val })}
          />
        </div>

        <div>
          <label className="label">
            Target Company Size <span className="text-gray-400 font-normal">(optional)</span>
          </label>
          <div className="flex flex-wrap gap-2">
            {COMPANY_SIZES.map((size) => (
              <button
                key={size}
                type="button"
                onClick={() =>
                  updateFormData({
                    target_company_size:
                      formData.target_company_size === size ? "" : size,
                  })
                }
                className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors ${
                  formData.target_company_size === size
                    ? "bg-brand-600 text-white border-brand-600"
                    : "bg-white text-gray-600 border-gray-200 hover:border-brand-300"
                }`}
              >
                {size}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="label">
            Main Users / Departments <span className="text-gray-400 font-normal">(optional)</span>
          </label>
          <MultiSelect
            options={DEPARTMENTS}
            selected={formData.target_departments || []}
            onChange={(val) => updateFormData({ target_departments: val })}
          />
        </div>

        <div>
          <label className="label">
            Pricing Range <span className="text-gray-400 font-normal">(optional)</span>
          </label>
          <div className="flex gap-2">
            {PRICING_OPTIONS.map((opt) => (
              <button
                key={opt}
                type="button"
                onClick={() =>
                  updateFormData({
                    pricing_range: formData.pricing_range === opt ? "" : opt,
                  })
                }
                className={`px-4 py-1.5 rounded-lg text-sm font-medium border transition-colors ${
                  formData.pricing_range === opt
                    ? "bg-brand-600 text-white border-brand-600"
                    : "bg-white text-gray-600 border-gray-200 hover:border-brand-300"
                }`}
              >
                {opt}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="flex justify-between">
        <button className="btn-secondary" onClick={onBack}>← Back</button>
        <button className="btn-primary" onClick={onNext} disabled={!isValid}>
          Next: Competitors →
        </button>
      </div>
    </div>
  );
}

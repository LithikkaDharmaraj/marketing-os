"use client";

import { useIntakeStore } from "@/stores/intakeStore";
import { useSubmitIntake } from "@/hooks/useIntake";
import { Loader2, Zap, Search, Brain, Target } from "lucide-react";
import type { IntakeFormData } from "@/types/intake";

interface Props {
  onBack: () => void;
}

export function ReviewStep({ onBack }: Props) {
  const { formData, isSubmitting } = useIntakeStore();
  const submitMutation = useSubmitIntake();

  const handleSubmit = () => {
    submitMutation.mutate(formData as IntakeFormData);
  };

  const isPending = isSubmitting || submitMutation.isPending;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Ready to Analyze</h2>
        <p className="text-sm text-gray-500 mt-1">
          Confirm your details and launch the AI analysis.
        </p>
      </div>

      {/* Summary */}
      <div className="space-y-3">
        <div className="card p-4 space-y-2">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Company</p>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Name</span>
            <span className="font-medium text-gray-900">{formData.company_name}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Website</span>
            <span className="font-medium text-brand-600 truncate max-w-[60%]">{formData.website_url}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Industry</span>
            <span className="font-medium text-gray-900">{formData.industry}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Geography</span>
            <span className="font-medium text-gray-900">{formData.geography}</span>
          </div>
          {formData.product_type && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Product Type</span>
              <span className="font-medium text-gray-900">{formData.product_type}</span>
            </div>
          )}
          {(formData.competitors || []).length > 0 && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Competitors</span>
              <span className="font-medium text-gray-900">{formData.competitors!.length} added</span>
            </div>
          )}
        </div>
      </div>

      {/* What happens next */}
      <div className="bg-gradient-to-br from-brand-50 to-blue-50 border border-brand-100 rounded-xl p-5 space-y-3">
        <p className="text-sm font-semibold text-gray-800">AI analysis pipeline:</p>
        <div className="space-y-2">
          {[
            { icon: Search, text: "Crawl website, LinkedIn & Crunchbase" },
            { icon: Brain, text: "Extract business intelligence with Llama AI" },
            { icon: Zap, text: "Generate positioning strategy & messaging" },
            { icon: Target, text: "Create 2–4 Ideal Customer Profiles" },
          ].map(({ icon: Icon, text }) => (
            <div key={text} className="flex items-center gap-3 text-sm text-gray-700">
              <div className="w-7 h-7 rounded-full bg-white border border-brand-100 flex items-center justify-center shrink-0">
                <Icon className="w-3.5 h-3.5 text-brand-500" />
              </div>
              {text}
            </div>
          ))}
        </div>
        <p className="text-xs text-gray-500 pt-1">Average processing time: 3–5 minutes</p>
      </div>

      {submitMutation.isError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
          {submitMutation.error?.message || "Failed to submit. Please try again."}
        </div>
      )}

      <div className="flex justify-between">
        <button className="btn-secondary" onClick={onBack} disabled={isPending}>
          ← Back
        </button>
        <button
          className="btn-primary flex items-center gap-2 px-6"
          onClick={handleSubmit}
          disabled={isPending}
        >
          {isPending ? (
            <><Loader2 className="w-4 h-4 animate-spin" /> Launching...</>
          ) : (
            <><Zap className="w-4 h-4" /> Launch AI Analysis</>
          )}
        </button>
      </div>
    </div>
  );
}

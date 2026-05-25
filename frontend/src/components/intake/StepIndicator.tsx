"use client";

const STEPS = [
  { number: 1, label: "Company" },
  { number: 2, label: "Product" },
  { number: 3, label: "Competitors" },
  { number: 4, label: "Contacts" },
  { number: 5, label: "Review" },
];

interface Props {
  currentStep: number;
}

export function StepIndicator({ currentStep }: Props) {
  return (
    <div className="flex items-center">
      {STEPS.map((step, idx) => (
        <div key={step.number} className="flex items-center flex-1">
          <div className="flex flex-col items-center gap-1">
            <div
              className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-semibold transition-all ${
                step.number < currentStep
                  ? "bg-green-500 text-white"
                  : step.number === currentStep
                  ? "bg-brand-500 text-white ring-4 ring-brand-100"
                  : "bg-gray-100 text-gray-400"
              }`}
            >
              {step.number < currentStep ? "✓" : step.number}
            </div>
            <span
              className={`text-[11px] font-medium ${
                step.number === currentStep ? "text-brand-600" : "text-gray-400"
              }`}
            >
              {step.label}
            </span>
          </div>
          {idx < STEPS.length - 1 && (
            <div
              className={`h-0.5 flex-1 mb-5 mx-1 transition-colors ${
                step.number < currentStep ? "bg-green-400" : "bg-gray-200"
              }`}
            />
          )}
        </div>
      ))}
    </div>
  );
}

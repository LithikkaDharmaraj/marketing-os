"use client";

import { useIntakeStore } from "@/stores/intakeStore";
import { StepIndicator } from "./StepIndicator";
import { CompanyInfoStep } from "./steps/CompanyInfoStep";
import { ProductStep } from "./steps/ProductStep";
import { CompetitorStep } from "./steps/CompetitorStep";
import { ContactStep } from "./steps/ContactStep";
import { ReviewStep } from "./steps/ReviewStep";

export function IntakeForm() {
  const { currentStep, nextStep, prevStep } = useIntakeStore();

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <StepIndicator currentStep={currentStep} />

      <div className="card p-8">
        {currentStep === 1 && <CompanyInfoStep onNext={nextStep} />}
        {currentStep === 2 && <ProductStep onNext={nextStep} onBack={prevStep} />}
        {currentStep === 3 && <CompetitorStep onNext={nextStep} onBack={prevStep} />}
        {currentStep === 4 && <ContactStep onNext={nextStep} onBack={prevStep} />}
        {currentStep === 5 && <ReviewStep onBack={prevStep} />}
      </div>
    </div>
  );
}

import { Navbar } from "@/components/shared/Navbar";
import { IntakeForm } from "@/components/intake/IntakeForm";

export default function IntakePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 py-10">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold text-gray-900">Business Intake</h1>
          <p className="text-gray-500 mt-2">
            Provide your business details — our AI will build your complete marketing blueprint.
          </p>
        </div>
        <IntakeForm />
      </div>
    </div>
  );
}

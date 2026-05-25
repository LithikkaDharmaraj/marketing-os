"use client";

import { useIntakeStore } from "@/stores/intakeStore";
import type { ContactInput } from "@/types/intake";

interface Props {
  onNext: () => void;
  onBack: () => void;
}

const SLOTS = [
  { label: "Primary Contact", is_primary: true, is_founder: false },
  { label: "Second Contact (optional)", is_primary: false, is_founder: false },
];

export function ContactStep({ onNext, onBack }: Props) {
  const { formData, updateFormData } = useIntakeStore();

  const updateContact = (index: number, field: keyof ContactInput, value: string | boolean) => {
    const contacts: ContactInput[] = [...(formData.contacts || [])];
    while (contacts.length <= index) {
      contacts.push({ contact_type: "general", is_founder: false, is_primary: false });
    }
    contacts[index] = { ...contacts[index], [field]: value };
    updateFormData({ contacts });
  };

  const get = (i: number): ContactInput =>
    formData.contacts?.[i] || { contact_type: "general", is_founder: false, is_primary: false };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Key Contacts</h2>
        <p className="text-sm text-gray-500 mt-1">
          Just a name and email — used for personalized outreach context. All optional.
        </p>
      </div>

      {SLOTS.map((slot, idx) => {
        const c = get(idx);
        return (
          <div key={slot.label} className="card p-4 space-y-3">
            <h3 className="font-medium text-gray-700 text-sm">{slot.label}</h3>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">Full Name</label>
                <input
                  className="input-field"
                  placeholder="Jane Doe"
                  value={c.full_name || ""}
                  onChange={(e) => updateContact(idx, "full_name", e.target.value)}
                />
              </div>
              <div>
                <label className="label">Email</label>
                <input
                  className="input-field"
                  type="email"
                  placeholder="jane@company.com"
                  value={c.email || ""}
                  onChange={(e) => updateContact(idx, "email", e.target.value)}
                />
              </div>
            </div>
          </div>
        );
      })}

      <div className="flex justify-between">
        <button className="btn-secondary" onClick={onBack}>← Back</button>
        <button className="btn-primary" onClick={onNext}>Review & Submit →</button>
      </div>
    </div>
  );
}

"use client";

import { Building2, Users, Linkedin, Mail, Star, ChevronDown, ChevronUp, Target, Zap } from "lucide-react";
import { useState } from "react";

interface TargetContact {
  id: string;
  full_name: string;
  designation: string;
  department: string;
  seniority: string;
  linkedin_url: string;
  email: string;
  why_target: string;
  outreach_angle: string;
  priority: string;
  company_name: string;
  data_source?: string;
}

interface TargetCompany {
  id: string;
  name: string;
  domain: string;
  linkedin_url: string;
  industry: string;
  company_size: string;
  headquarters: string;
  why_they_match: string;
  icp_profile_name: string;
  pain_points_matched: string[];
  priority: string;
}

const priorityColor: Record<string, string> = {
  high: "bg-red-100 text-red-700 border-red-200",
  medium: "bg-yellow-100 text-yellow-700 border-yellow-200",
  low: "bg-gray-100 text-gray-600 border-gray-200",
};

const seniorityBadge: Record<string, string> = {
  "C-Suite": "bg-purple-100 text-purple-700",
  VP: "bg-blue-100 text-blue-700",
  Director: "bg-indigo-100 text-indigo-700",
  Manager: "bg-teal-100 text-teal-700",
  "Senior IC": "bg-green-100 text-green-700",
};

const dataSourceBadge: Record<string, { label: string; cls: string }> = {
  linkedin_scraped: { label: "LinkedIn Scraped", cls: "bg-green-100 text-green-700 border-green-200" },
  google_snippet: { label: "Google / LinkedIn", cls: "bg-blue-50 text-blue-600 border-blue-200" },
  inferred: { label: "AI Inferred", cls: "bg-gray-100 text-gray-500 border-gray-200" },
};

function ContactCard({ contact }: { contact: TargetContact }) {
  return (
    <div className="border border-gray-100 rounded-lg p-4 bg-white space-y-2">
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="font-semibold text-gray-900">{contact.full_name || "—"}</p>
          <p className="text-sm text-gray-600">{contact.designation}</p>
          <p className="text-xs text-gray-400">{contact.department}</p>
        </div>
        <div className="flex flex-col items-end gap-1">
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium border ${priorityColor[contact.priority] ?? priorityColor.medium}`}>
            {contact.priority}
          </span>
          {contact.seniority && (
            <span className={`text-xs px-2 py-0.5 rounded-full ${seniorityBadge[contact.seniority] ?? "bg-gray-100 text-gray-600"}`}>
              {contact.seniority}
            </span>
          )}
        </div>
      </div>

      <div className="flex flex-wrap gap-3 text-xs items-center">
        {contact.linkedin_url && (
          <a href={contact.linkedin_url} target="_blank" rel="noreferrer"
            className="flex items-center gap-1 text-blue-600 hover:underline">
            <Linkedin className="w-3 h-3" /> LinkedIn
          </a>
        )}
        {contact.email && (
          <span className="flex items-center gap-1 text-gray-500">
            <Mail className="w-3 h-3" /> {contact.email}
          </span>
        )}
        {contact.data_source && (() => {
          const badge = dataSourceBadge[contact.data_source] ?? { label: contact.data_source, cls: "bg-gray-100 text-gray-500 border-gray-200" };
          return (
            <span className={`px-2 py-0.5 rounded-full border text-xs font-medium ${badge.cls}`}>
              {badge.label}
            </span>
          );
        })()}
      </div>

      {contact.why_target && (
        <p className="text-xs text-gray-600 border-l-2 border-brand-300 pl-2">{contact.why_target}</p>
      )}

      {contact.outreach_angle && (
        <div className="flex items-start gap-1.5 bg-brand-50 rounded p-2">
          <Zap className="w-3 h-3 text-brand-500 mt-0.5 shrink-0" />
          <p className="text-xs text-brand-700 italic">{contact.outreach_angle}</p>
        </div>
      )}
    </div>
  );
}

function CompanyCard({
  company,
  contacts,
}: {
  company: TargetCompany;
  contacts: TargetContact[];
}) {
  const [open, setOpen] = useState(false);
  const companyContacts = contacts.filter((c) => c.company_name === company.name);

  return (
    <div className="card overflow-hidden">
      <div className="p-5">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-lg bg-brand-100 flex items-center justify-center shrink-0">
              <Building2 className="w-5 h-5 text-brand-600" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-gray-900">{company.name}</h3>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium border ${priorityColor[company.priority] ?? priorityColor.medium}`}>
                  {company.priority} priority
                </span>
              </div>
              <p className="text-sm text-gray-500">{company.industry} · {company.company_size}</p>
              {company.headquarters && (
                <p className="text-xs text-gray-400">{company.headquarters}</p>
              )}
            </div>
          </div>

          <div className="flex gap-2 shrink-0">
            {company.linkedin_url && (
              <a href={company.linkedin_url} target="_blank" rel="noreferrer"
                className="p-1.5 rounded hover:bg-gray-100 text-gray-400 hover:text-blue-600 transition-colors">
                <Linkedin className="w-4 h-4" />
              </a>
            )}
            {company.domain && (
              <a href={`https://${company.domain}`} target="_blank" rel="noreferrer"
                className="text-xs text-brand-600 hover:underline flex items-center gap-1 px-2">
                {company.domain}
              </a>
            )}
          </div>
        </div>

        {company.why_they_match && (
          <p className="mt-3 text-sm text-gray-700 border-l-2 border-brand-400 pl-3">
            {company.why_they_match}
          </p>
        )}

        {company.pain_points_matched?.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {company.pain_points_matched.map((p, i) => (
              <span key={i} className="text-xs bg-orange-50 text-orange-700 border border-orange-100 px-2 py-0.5 rounded-full">
                {p}
              </span>
            ))}
          </div>
        )}

        {company.icp_profile_name && (
          <p className="mt-2 text-xs text-gray-400 flex items-center gap-1">
            <Target className="w-3 h-3" /> Matches ICP: {company.icp_profile_name}
          </p>
        )}

        <button
          onClick={() => setOpen(!open)}
          className="mt-4 flex items-center gap-1.5 text-sm text-brand-600 font-medium hover:text-brand-700"
        >
          <Users className="w-4 h-4" />
          {companyContacts.length} recommended contact{companyContacts.length !== 1 ? "s" : ""}
          {open ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {open && companyContacts.length > 0 && (
        <div className="border-t border-gray-100 bg-gray-50 p-4 space-y-3">
          {companyContacts.map((c) => (
            <ContactCard key={c.id} contact={c} />
          ))}
        </div>
      )}
    </div>
  );
}

export function TargetCompaniesView({
  companies,
  contacts,
}: {
  companies: TargetCompany[];
  contacts: TargetContact[];
}) {
  const highPriority = companies.filter((c) => c.priority === "high");
  const rest = companies.filter((c) => c.priority !== "high");

  const totalContacts = contacts.length;
  const withLinkedIn = contacts.filter((c) => c.linkedin_url).length;
  const scraped = contacts.filter((c) => c.data_source && c.data_source !== "inferred").length;

  return (
    <div className="space-y-6">
      {/* Summary bar */}
      <div className="grid grid-cols-4 gap-4">
        <div className="card p-4 text-center">
          <p className="text-2xl font-bold text-brand-600">{companies.length}</p>
          <p className="text-sm text-gray-500 mt-1">Target Companies</p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-2xl font-bold text-brand-600">{totalContacts}</p>
          <p className="text-sm text-gray-500 mt-1">Recommended Contacts</p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-2xl font-bold text-brand-600">{withLinkedIn}</p>
          <p className="text-sm text-gray-500 mt-1">With LinkedIn Profile</p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-2xl font-bold text-green-600">{scraped}</p>
          <p className="text-sm text-gray-500 mt-1">Scraped from Web</p>
        </div>
      </div>

      {highPriority.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3 flex items-center gap-2">
            <Star className="w-4 h-4 text-red-500" /> High Priority
          </h2>
          <div className="space-y-4">
            {highPriority.map((c) => (
              <CompanyCard key={c.id} company={c} contacts={contacts} />
            ))}
          </div>
        </div>
      )}

      {rest.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Other Prospects
          </h2>
          <div className="space-y-4">
            {rest.map((c) => (
              <CompanyCard key={c.id} company={c} contacts={contacts} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

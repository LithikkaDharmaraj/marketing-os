export const queryKeys = {
  intake: {
    status: (companyId: string) => ["intake", "status", companyId] as const,
  },
  intelligence: {
    profile: (companyId: string) => ["intelligence", companyId] as const,
  },
  positioning: {
    profile: (companyId: string) => ["positioning", companyId] as const,
  },
  icp: {
    profiles: (companyId: string) => ["icp", companyId] as const,
    profile: (companyId: string, icpId: string) => ["icp", companyId, icpId] as const,
  },
  targets: {
    companies: (companyId: string) => ["targets", "companies", companyId] as const,
    contacts: (companyId: string) => ["targets", "contacts", companyId] as const,
  },
  campaign: {
    context: (companyId: string) => ["campaign", companyId] as const,
  },
  workflow: {
    status: (runId: string) => ["workflow", runId] as const,
  },
};

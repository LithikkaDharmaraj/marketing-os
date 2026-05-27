"use client";

import { useQuery } from "@tanstack/react-query";
import { getTargetCompanies, getTargetContacts } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";

export function useTargetCompanies(companyId: string) {
  return useQuery({
    queryKey: queryKeys.targets.companies(companyId),
    queryFn: () => getTargetCompanies(companyId),
    enabled: !!companyId,
  });
}

export function useTargetContacts(companyId: string) {
  return useQuery({
    queryKey: queryKeys.targets.contacts(companyId),
    queryFn: () => getTargetContacts(companyId),
    enabled: !!companyId,
  });
}

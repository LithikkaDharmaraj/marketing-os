"use client";

import { useQuery } from "@tanstack/react-query";
import { getIntelligence } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";

export function useBusinessProfile(companyId: string) {
  return useQuery({
    queryKey: queryKeys.intelligence.profile(companyId),
    queryFn: () => getIntelligence(companyId),
    enabled: !!companyId,
    // React Query v5: refetchInterval receives the Query object, not the response data.
    // Access response data via query.state.data to check the workflow status from the API.
    refetchInterval: (query) => {
      const status = (query as any)?.state?.data?.status as string | undefined;
      return status === "completed" || status === "failed" ? false : 5000;
    },
  });
}

"use client";

import { useQuery } from "@tanstack/react-query";
import { getICPs } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";

export function useICPs(companyId: string) {
  return useQuery({
    queryKey: queryKeys.icp.profiles(companyId),
    queryFn: () => getICPs(companyId),
    enabled: !!companyId,
  });
}

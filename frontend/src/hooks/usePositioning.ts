"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getPositioning, approvePositioning } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";

export function usePositioning(companyId: string) {
  return useQuery({
    queryKey: queryKeys.positioning.profile(companyId),
    queryFn: () => getPositioning(companyId),
    enabled: !!companyId,
    retry: 3,
  });
}

export function useApprovePositioning(companyId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => approvePositioning(companyId),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.positioning.profile(companyId) }),
  });
}

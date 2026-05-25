import { create } from "zustand";
import type { BusinessProfile } from "@/types/intelligence";
import type { PositioningProfile } from "@/types/positioning";
import type { ICPProfile } from "@/types/icp";

interface BusinessStore {
  businessProfile: BusinessProfile | null;
  positioningProfile: PositioningProfile | null;
  icpProfiles: ICPProfile[];
  setBusinessProfile: (profile: BusinessProfile) => void;
  setPositioningProfile: (profile: PositioningProfile) => void;
  setICPProfiles: (profiles: ICPProfile[]) => void;
  clearAll: () => void;
}

export const useBusinessStore = create<BusinessStore>((set) => ({
  businessProfile: null,
  positioningProfile: null,
  icpProfiles: [],
  setBusinessProfile: (profile) => set({ businessProfile: profile }),
  setPositioningProfile: (profile) => set({ positioningProfile: profile }),
  setICPProfiles: (profiles) => set({ icpProfiles: profiles }),
  clearAll: () =>
    set({ businessProfile: null, positioningProfile: null, icpProfiles: [] }),
}));

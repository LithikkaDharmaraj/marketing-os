"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { Navbar } from "@/components/shared/Navbar";
import { useBusinessProfile } from "@/hooks/useBusinessProfile";
import { usePositioning } from "@/hooks/usePositioning";
import { useICPs } from "@/hooks/useICP";
import { Loader2, Target, Users, Zap, BookOpen } from "lucide-react";

export default function BlueprintPage() {
  const { businessId } = useParams<{ businessId: string }>();
  const { data: intelligence } = useBusinessProfile(businessId);
  const { data: positioning } = usePositioning(businessId);
  const { data: icps } = useICPs(businessId);

  const isReady = intelligence?.business_profile && positioning && icps?.length;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Marketing Blueprint</h1>
          <p className="text-gray-500 mt-1">Complete AI-generated marketing foundation for {intelligence?.company_name || "your company"}</p>
        </div>

        {!isReady ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <Loader2 className="w-8 h-8 text-brand-500 animate-spin mx-auto mb-3" />
              <p className="text-gray-500">Building your marketing blueprint...</p>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Summary tiles */}
            <div className="grid grid-cols-4 gap-4">
              <BlueprintTile
                icon={<BookOpen className="w-5 h-5" />}
                label="Business Profile"
                description={intelligence.business_profile?.value_proposition}
                href={`/intelligence/${businessId}`}
                color="brand"
              />
              <BlueprintTile
                icon={<Target className="w-5 h-5" />}
                label="Positioning"
                description={positioning?.core_positioning?.statement}
                href={`/positioning/${businessId}`}
                color="purple"
              />
              <BlueprintTile
                icon={<Users className="w-5 h-5" />}
                label={`${icps.length} ICP Profiles`}
                description={icps.map((icp: any) => icp.profile_name).join(", ")}
                href={`/icp/${businessId}`}
                color="green"
              />
              <BlueprintTile
                icon={<Zap className="w-5 h-5" />}
                label="Campaign Ready"
                description="Ready to generate campaigns"
                href="#"
                color="amber"
                disabled
              />
            </div>

            {/* Key messages */}
            {positioning?.messaging_angles?.length > 0 && (
              <div className="card p-6">
                <h2 className="font-semibold text-gray-900 mb-4">Top Messaging Angles</h2>
                <div className="grid grid-cols-2 gap-3">
                  {positioning.messaging_angles.slice(0, 4).map((angle: any, i: number) => (
                    <div key={i} className="bg-gradient-to-br from-brand-50 to-white border border-brand-100 rounded-xl p-4">
                      <p className="text-xs font-bold text-brand-600 uppercase mb-1">{angle.angle_name}</p>
                      <p className="text-sm text-gray-800 font-medium">{angle.message}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ICP quick view */}
            <div className="card p-6">
              <h2 className="font-semibold text-gray-900 mb-4">Target Personas</h2>
              <div className="grid grid-cols-2 gap-4">
                {icps.slice(0, 4).map((icp: any, i: number) => (
                  <div key={i} className="border border-gray-200 rounded-xl p-4">
                    <h3 className="font-medium text-gray-900 text-sm">{icp.profile_name}</h3>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {(icp.job_titles || []).slice(0, 3).map((t: string, j: number) => (
                        <span key={j} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{t}</span>
                      ))}
                    </div>
                    {icp.sample_messaging && (
                      <p className="text-xs text-gray-500 mt-2 italic line-clamp-2">"{icp.sample_messaging}"</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function BlueprintTile({
  icon, label, description, href, color, disabled,
}: {
  icon: React.ReactNode;
  label: string;
  description?: string;
  href: string;
  color: string;
  disabled?: boolean;
}) {
  const colorMap: Record<string, string> = {
    brand: "from-brand-500 to-brand-600",
    purple: "from-purple-500 to-purple-600",
    green: "from-green-500 to-green-600",
    amber: "from-amber-400 to-amber-500",
  };

  const content = (
    <div className={`card p-5 bg-gradient-to-br ${colorMap[color]} text-white ${disabled ? "opacity-60" : "hover:shadow-md transition-shadow"}`}>
      <div className="flex items-center gap-2 mb-2">
        {icon}
        <span className="font-semibold text-sm">{label}</span>
      </div>
      {description && (
        <p className="text-xs text-white/80 line-clamp-2">{description}</p>
      )}
    </div>
  );

  if (disabled) return content;
  return <Link href={href}>{content}</Link>;
}

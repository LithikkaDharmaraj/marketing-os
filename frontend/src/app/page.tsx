import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-brand-900 via-brand-700 to-brand-500 text-white p-8">
      <div className="max-w-3xl text-center space-y-6">
        <div className="inline-flex items-center gap-2 bg-white/10 px-4 py-2 rounded-full text-sm font-medium">
          <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          AI-Native Marketing Platform
        </div>

        <h1 className="text-5xl font-bold tracking-tight">
          Marketing OS
        </h1>
        <p className="text-xl text-brand-100 max-w-2xl">
          Transform your business into a fully-automated marketing machine.
          Intelligent positioning, ICP generation, and campaign execution — powered by AI.
        </p>

        <div className="flex gap-4 justify-center pt-4">
          <Link
            href="/intake"
            className="bg-white text-brand-700 hover:bg-brand-50 font-semibold px-8 py-3 rounded-xl transition-colors shadow-lg"
          >
            Get Started →
          </Link>
          <Link
            href="/blueprint/demo"
            className="bg-white/10 hover:bg-white/20 font-medium px-8 py-3 rounded-xl transition-colors"
          >
            View Demo
          </Link>
        </div>

        <div className="grid grid-cols-4 gap-6 pt-12 text-center">
          {[
            { label: "Business Intelligence", icon: "🧠" },
            { label: "Positioning Engine", icon: "🎯" },
            { label: "ICP Generation", icon: "👥" },
            { label: "Campaign Context", icon: "🚀" },
          ].map((f) => (
            <div key={f.label} className="bg-white/10 rounded-xl p-4 space-y-2">
              <div className="text-3xl">{f.icon}</div>
              <div className="text-sm font-medium">{f.label}</div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}

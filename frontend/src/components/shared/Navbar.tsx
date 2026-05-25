import Link from "next/link";

export function Navbar() {
  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <Link href="/" className="font-bold text-xl text-brand-700">
        Marketing OS
      </Link>
      <div className="flex items-center gap-6 text-sm text-gray-600">
        <Link href="/intake" className="hover:text-brand-600">New Business</Link>
        <Link href="/" className="hover:text-brand-600">Dashboard</Link>
      </div>
    </nav>
  );
}

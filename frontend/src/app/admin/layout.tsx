// ~/idol_voting/frontend/src/app/admin/layout.tsx
'use client';

import Link from 'next/link';
// HIGHLIGHT: Import useRouter for redirection
import { usePathname, useRouter } from 'next/navigation';
import { LogOut } from 'lucide-react';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  // HIGHLIGHT: Initialize the router
  const router = useRouter();

  const navItems = [
    { href: '/admin/dashboard', label: 'Dashboard' },
    { href: '/admin/contestants', label: 'Contestants' },
    { href: '/admin/voting-lines', label: 'Voting Lines' },
  ];

  // HIGHLIGHT: Logout handler function
  const handleLogout = () => {
    // Remove the admin's token from local storage
    localStorage.removeItem('adminAccessToken');
    // Redirect to the admin login page
    router.push('/admin/login');
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <nav className="bg-gray-800">
        <div className="container mx-auto px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <span className="font-bold text-xl">Idol Admin</span>
            </div>
            <div className="flex items-center space-x-4">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    pathname === item.href
                      ? 'bg-gray-900 text-white'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
              {/* HIGHLIGHT: Logout Button */}
              <button
                onClick={handleLogout}
                className="p-2 rounded-md text-gray-300 hover:bg-red-700 hover:text-white"
                title="Logout"
              >
                <LogOut size={20} />
              </button>
            </div>
          </div>
        </div>
      </nav>
      <main className="container mx-auto p-8">{children}</main>
    </div>
  );
}

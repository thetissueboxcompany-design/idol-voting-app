// ~/idol_voting/frontend/src/app/admin/dashboard/page.tsx
'use client';

import Link from 'next/link';

export default function AdminDashboardPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Welcome, Admin!</h1>
      <p className="mb-8">Select a section from the navigation bar to get started.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Link href="/admin/contestants" className="block p-6 bg-gray-800 hover:bg-gray-700 rounded-lg">
            <h2 className="text-2xl font-semibold">Manage Contestants</h2>
            <p className="mt-2">Add, edit, or remove contestants from the show.</p>
        </Link>
        <Link href="/admin/voting-lines" className="block p-6 bg-gray-800 hover:bg-gray-700 rounded-lg">
            <h2 className="text-2xl font-semibold">Manage Voting Lines</h2>
            <p className="mt-2">Create and control the voting periods.</p>
        </Link>
      </div>
    </div>
  );
}

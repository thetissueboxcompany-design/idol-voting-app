// ~/idol_voting/frontend/src/app/admin/dashboard/page.tsx
'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
// HIGHLIGHT: Import the new form component
import ContestantForm from '@/components/admin/ContestantForm';

interface Contestant {
  id: number;
  name: string;
  age: number;
  gender: string;
  details: string | null;
  image_url: string | null;
}

export default function AdminDashboardPage() {
  const [contestants, setContestants] = useState<Contestant[]>([]);
  const [error, setError] = useState('');

  const fetchContestants = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL + '/api/contestants';
      const response = await axios.get(apiUrl);
      setContestants(response.data);
    } catch (err) {
      setError('Failed to fetch contestants.');
      console.error(err);
    }
  };

  useEffect(() => {
    fetchContestants();
  }, []);

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">Admin Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-1">
          <h2 className="text-2xl font-semibold mb-4">Add New Contestant</h2>
          {/* HIGHLIGHT: Add the ContestantForm component here */}
          {/* It calls fetchContestants when a new one is created */}
          <ContestantForm onContestantCreated={fetchContestants} />
        </div>

        <div className="md:col-span-2">
          <h2 className="text-2xl font-semibold mb-4">Current Contestants</h2>
          <div className="space-y-4">
            {contestants.map((c) => (
              <div key={c.id} className="p-4 bg-gray-800 rounded-lg">
                <h3 className="text-xl font-bold">{c.name}</h3>
                <p>{c.age}, {c.gender}</p>
              </div>
            ))}
             {contestants.length === 0 && <p>No contestants found.</p>}
          </div>
          {error && <p className="mt-4 text-red-500">{error}</p>}
        </div>
      </div>
    </div>
  );
}

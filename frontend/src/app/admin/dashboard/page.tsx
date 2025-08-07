// ~/idol_voting/frontend/src/app/admin/dashboard/page.tsx
'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts';

// Define types for our data
interface VotingLine {
  id: number;
  name: string;
}
interface Stat {
  contestant_name: string;
  total_votes: number;
}
interface DashboardStats {
  voting_line_name: string;
  stats: Stat[];
}

export default function AdminDashboardPage() {
  const [votingLines, setVotingLines] = useState<VotingLine[]>([]);
  const [selectedLineId, setSelectedLineId] = useState<string>('');
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState('');

  // Fetch all available voting lines for the dropdown
  useEffect(() => {
    const fetchVotingLines = async () => {
      try {
        const token = localStorage.getItem('adminAccessToken');
        const apiUrl = process.env.NEXT_PUBLIC_API_URL + '/api/admin/voting-lines';
        const response = await axios.get(apiUrl, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setVotingLines(response.data);
        // Select the first line by default if it exists
        if (response.data.length > 0) {
          setSelectedLineId(response.data[0].id.toString());
        }
      } catch (err) {
        setError('Failed to fetch voting lines.');
      }
    };
    fetchVotingLines();
  }, []);

  // Fetch stats when a voting line is selected
  useEffect(() => {
    if (!selectedLineId) return;

    const fetchStats = async () => {
      setStats(null); // Clear previous stats
      setError('');
      try {
        const token = localStorage.getItem('adminAccessToken');
        const apiUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/admin/dashboard-stats/${selectedLineId}`;
        const response = await axios.get(apiUrl, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setStats(response.data);
      } catch (err) {
        setError('Failed to fetch stats for this voting line.');
        console.error(err);
      }
    };
    fetchStats();
  }, [selectedLineId]);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Voting Dashboard</h1>
        <div>
          <label htmlFor="voting-line-select" className="mr-2">Select Voting Line:</label>
          <select
            id="voting-line-select"
            value={selectedLineId}
            onChange={(e) => setSelectedLineId(e.target.value)}
            className="bg-gray-800 border border-gray-600 rounded-md px-3 py-2"
          >
            {votingLines.map((line) => (
              <option key={line.id} value={line.id}>
                {line.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && <p className="text-red-500">{error}</p>}
      
      {stats ? (
        <div className="bg-gray-800 p-6 rounded-lg">
          <h2 className="text-2xl font-semibold mb-4 text-center">{stats.voting_line_name} - Live Results</h2>
          <div style={{ width: '100%', height: 400 }}>
            <ResponsiveContainer>
              <BarChart data={stats.stats} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#4A5568" />
                <XAxis dataKey="contestant_name" stroke="#E2E8F0" />
                <YAxis stroke="#E2E8F0" />
                <Tooltip contentStyle={{ backgroundColor: '#2D3748', border: 'none' }} />
                <Legend />
                <Bar dataKey="total_votes" fill="#ED64A6" name="Total Votes" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      ) : (
        <p>{selectedLineId ? 'Loading stats...' : 'Please select a voting line.'}</p>
      )}
    </div>
  );
}

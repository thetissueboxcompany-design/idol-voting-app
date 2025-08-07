// ~/idol_voting/frontend/src/app/history/page.tsx
'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { LogOut, ArrowLeft } from 'lucide-react';

interface VoteHistory {
  voting_line_name: string;
  voting_line_dates: string;
  contestant_name: string;
  vote_count: number;
  voted_at: string;
}

export default function HistoryPage() {
  const [history, setHistory] = useState<VoteHistory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    router.push('/');
  };

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const token = localStorage.getItem('accessToken');
        if (!token) {
          router.push('/');
          return;
        }
        const apiUrl = process.env.NEXT_PUBLIC_API_URL + '/api/vote/history';
        const response = await axios.get(apiUrl, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setHistory(response.data.history);
      } catch (err) {
        if (axios.isAxiosError(err) && err.response?.status === 401) {
          handleLogout();
        } else {
          setError('Could not fetch vote history.');
        }
      } finally {
        setIsLoading(false);
      }
    };
    fetchHistory();
  }, [router]);

  return (
    <div className="container mx-auto p-4 md:p-8">
      <header className="flex justify-between items-center mb-8">
        <Link href="/voting" className="flex items-center space-x-2 text-gray-400 hover:text-white">
          <ArrowLeft size={20} />
          <span>Back to Voting</span>
        </Link>
        <h1 className="text-4xl font-bold">My Vote History</h1>
        <button
          onClick={handleLogout}
          className="flex items-center space-x-2 px-4 py-2 rounded-md text-gray-300 bg-gray-800 hover:bg-red-700 hover:text-white"
          title="Logout"
        >
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </header>

      {isLoading && <p>Loading history...</p>}
      {error && <p className="text-red-400 text-center">{error}</p>}
      
      {!isLoading && history.length === 0 && (
        <p className="text-center text-gray-400">You have not cast any votes yet.</p>
      )}

      {!isLoading && history.length > 0 && (
        <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
          <table className="min-w-full">
            <thead className="bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Voting Period</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Contestant</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Votes Cast</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Date of Vote</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {history.map((vote, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium">{vote.voting_line_name}</div>
                    <div className="text-sm text-gray-400">{vote.voting_line_dates}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">{vote.contestant_name}</td>
                  <td className="px-6 py-4 whitespace-nowrap font-bold text-pink-400">{vote.vote_count}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                    {new Date(vote.voted_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

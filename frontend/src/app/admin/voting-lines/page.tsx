// ~/idol_voting/frontend/src/app/admin/voting-lines/page.tsx
'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

// HIGHLIGHT: Updated Contestant and VotingLine interfaces
interface Contestant {
    id: number;
    name: string;
}

interface VotingLine {
  id: number;
  name: string;
  start_time: string;
  end_time: string;
  max_votes_per_user: number;
  is_active: boolean;
  contestants: Contestant[]; // Now includes the list of contestants
}

export default function VotingLinesPage() {
  const [lines, setLines] = useState<VotingLine[]>([]);
  const [name, setName] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [maxVotes, setMaxVotes] = useState('50');
  const [error, setError] = useState('');
  
  const [contestants, setContestants] = useState<Contestant[]>([]);
  const [selectedContestants, setSelectedContestants] = useState<Set<number>>(new Set());

  const fetchLines = async () => {
    try {
      const token = localStorage.getItem('adminAccessToken');
      const apiUrl = process.env.NEXT_PUBLIC_API_URL + '/api/admin/voting-lines';
      const response = await axios.get(apiUrl, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setLines(response.data);
    } catch (err) {
      setError('Failed to fetch voting lines.');
    }
  };
  
  const fetchContestants = async () => {
      try {
          const apiUrl = process.env.NEXT_PUBLIC_API_URL + '/api/contestants';
          const response = await axios.get(apiUrl);
          setContestants(response.data);
      } catch (err) {
          setError('Failed to fetch contestants.');
      }
  };

  useEffect(() => {
    fetchLines();
    fetchContestants();
  }, []);

  const handleContestantSelect = (contestantId: number) => {
      setSelectedContestants(prev => {
          const newSet = new Set(prev);
          if (newSet.has(contestantId)) {
              newSet.delete(contestantId);
          } else {
              newSet.add(contestantId);
          }
          return newSet;
      });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const token = localStorage.getItem('adminAccessToken');
      const apiUrl = process.env.NEXT_PUBLIC_API_URL + '/api/admin/voting-lines';
      await axios.post(
        apiUrl,
        {
          name,
          start_time: new Date(startTime).toISOString(),
          end_time: new Date(endTime).toISOString(),
          max_votes_per_user: parseInt(maxVotes, 10),
          contestant_ids: Array.from(selectedContestants)
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchLines();
      setName('');
      setStartTime('');
      setEndTime('');
      setMaxVotes('50');
      setSelectedContestants(new Set());
    } catch (err) {
      setError('Failed to create voting line.');
    }
  };

  const handleToggleActive = async (line: VotingLine) => {
    try {
        const token = localStorage.getItem('adminAccessToken');
        const action = line.is_active ? 'deactivate' : 'activate';
        const apiUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/admin/voting-lines/${line.id}/${action}`;
        await axios.patch(apiUrl, {}, {
            headers: { Authorization: `Bearer ${token}` }
        });
        fetchLines();
    } catch (err) {
        setError(`Failed to ${line.is_active ? 'deactivate' : 'activate'} line.`);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Manage Voting Lines</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-1">
          <h2 className="text-2xl font-semibold mb-4">Create New Line</h2>
          <form onSubmit={handleSubmit} className="p-4 bg-gray-800 rounded-lg space-y-4">
            <div>
                <label htmlFor="name" className="block text-sm font-medium">Line Name</label>
                <input type="text" id="name" value={name} onChange={e => setName(e.target.value)} required className="mt-1 block w-full px-3 py-2 text-black rounded-md"/>
            </div>
            <div>
                <label htmlFor="start_time" className="block text-sm font-medium">Start Time</label>
                <input type="datetime-local" id="start_time" value={startTime} onChange={e => setStartTime(e.target.value)} required className="mt-1 block w-full px-3 py-2 text-black rounded-md"/>
            </div>
            <div>
                <label htmlFor="end_time" className="block text-sm font-medium">End Time</label>
                <input type="datetime-local" id="end_time" value={endTime} onChange={e => setEndTime(e.target.value)} required className="mt-1 block w-full px-3 py-2 text-black rounded-md"/>
            </div>
            <div>
                <label htmlFor="max_votes" className="block text-sm font-medium">Max Votes Per User</label>
                <input type="number" id="max_votes" value={maxVotes} onChange={e => setMaxVotes(e.target.value)} required className="mt-1 block w-full px-3 py-2 text-black rounded-md"/>
            </div>
            <div>
                <label className="block text-sm font-medium">Select Contestants</label>
                <div className="mt-2 p-2 bg-gray-900 rounded-md max-h-40 overflow-y-auto">
                    {contestants.map(c => (
                        <div key={c.id} className="flex items-center">
                            <input
                                id={`contestant-${c.id}`}
                                type="checkbox"
                                checked={selectedContestants.has(c.id)}
                                onChange={() => handleContestantSelect(c.id)}
                                className="h-4 w-4 rounded"
                            />
                            <label htmlFor={`contestant-${c.id}`} className="ml-2">{c.name}</label>
                        </div>
                    ))}
                </div>
            </div>
            <button type="submit" className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 rounded-md font-bold">Create Line</button>
            {error && <p className="text-red-500 text-sm">{error}</p>}
          </form>
        </div>
        <div className="md:col-span-2">
          <h2 className="text-2xl font-semibold mb-4">Existing Voting Lines</h2>
          <div className="space-y-4">
            {lines.map(line => (
                // HIGHLIGHT: Updated the card to show more details
                <div key={line.id} className={`p-4 rounded-lg ${line.is_active ? 'bg-green-900 border-2 border-green-400' : 'bg-gray-800'}`}>
                    <div className="flex justify-between items-start">
                        <div>
                            <h3 className="text-xl font-bold">{line.name}</h3>
                            <p className="text-sm text-gray-300">Votes per user: {line.max_votes_per_user}</p>
                            <div className="text-xs text-gray-400 mt-2">
                                <p>Starts: {new Date(line.start_time).toLocaleString()}</p>
                                <p>Ends: {new Date(line.end_time).toLocaleString()}</p>
                            </div>
                        </div>
                        <button onClick={() => handleToggleActive(line)} className={`px-4 py-2 rounded-md font-bold text-sm ${line.is_active ? 'bg-yellow-500 hover:bg-yellow-600' : 'bg-green-500 hover:bg-green-600'}`}>
                            {line.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                    </div>
                    <div className="mt-4 pt-2 border-t border-gray-700">
                        <h4 className="text-sm font-semibold">Eligible Contestants:</h4>
                        <p className="text-xs text-gray-300">
                            {line.contestants.map(c => c.name).join(', ') || 'None'}
                        </p>
                    </div>
                </div>
            ))}
            {lines.length === 0 && <p>No voting lines found.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

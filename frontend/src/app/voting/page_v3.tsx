// ~/idol_voting/frontend/src/app/voting/page.tsx
'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import { Heart, LogOut } from 'lucide-react';
import { useRouter } from 'next/navigation';

// Define types for our data
interface Contestant {
  id: number;
  name: string;
  details: string | null;
  image_url: string | null;
}
interface VotingLine {
  id: number;
  name: string;
  max_votes_per_user: number;
}
type Votes = { [key: number]: number };

export default function VotingPage() {
  const [contestants, setContestants] = useState<Contestant[]>([]);
  const [votingLine, setVotingLine] = useState<VotingLine | null>(null);
  const [votes, setVotes] = useState<Votes>({});
  const [votesCast, setVotesCast] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  const totalVotesUsed = Object.values(votes).reduce((sum, count) => sum + count, 0);
  const votesRemaining = votingLine ? votingLine.max_votes_per_user - votesCast - totalVotesUsed : 0;

  useEffect(() => {
    const fetchVotingState = async () => {
      try {
        const token = localStorage.getItem('accessToken');
        if (!token) {
          router.push('/');
          return;
        }
        const apiUrl = process.env.NEXT_PUBLIC_API_URL + '/api/vote/state';
        const response = await axios.get(apiUrl, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setContestants(response.data.contestants);
        setVotingLine(response.data.voting_line);
        setVotesCast(response.data.user_total_votes);
      } catch (err) {
        // HIGHLIGHT: Improved error handling
        if (axios.isAxiosError(err) && err.response?.status === 401) {
          // If token is invalid or expired, log the user out
          handleLogout();
        } else {
          // For other errors (like 404), show the voting closed message
          setError('Voting is currently closed. Please check back later.');
        }
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchVotingState();
  }, [router]);

  const handleVote = (contestantId: number) => {
    if (votesRemaining > 0) {
      setVotes((prevVotes) => ({
        ...prevVotes,
        [contestantId]: (prevVotes[contestantId] || 0) + 1,
      }));
    }
  };
  
  const handleSubmitVotes = async () => {
    setError('');
    try {
        const token = localStorage.getItem('accessToken');
        const apiUrl = process.env.NEXT_PUBLIC_API_URL + '/api/vote/submit';
        await axios.post(apiUrl, { votes }, {
            headers: { Authorization: `Bearer ${token}` }
        });
        setVotes({});
        setVotesCast(prev => prev + totalVotesUsed);
        alert("Votes submitted successfully!");
    } catch (err) {
        if (axios.isAxiosError(err) && err.response?.status === 401) {
            handleLogout();
        } else {
            setError('Failed to submit votes. Please try again.');
        }
        console.error(err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    router.push('/');
  };

  if (isLoading) {
    return <main className="text-center">Loading Voting Booth...</main>;
  }

  if (error) {
    return <main className="text-center text-red-400">{error}</main>;
  }

  return (
    <div className="container mx-auto p-4 md:p-8">
      <header className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-bold">{votingLine?.name}</h1>
          <p className="text-xl text-gray-400">You have <span className="font-bold text-pink-400">{votesRemaining}</span> votes remaining.</p>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center space-x-2 px-4 py-2 rounded-md text-gray-300 bg-gray-800 hover:bg-red-700 hover:text-white"
          title="Logout"
        >
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {contestants.map((c) => (
          <div key={c.id} className="bg-gray-800 rounded-lg shadow-lg overflow-hidden flex flex-col">
            <div className="h-48 bg-gray-700 flex items-center justify-center">
                <span className="text-gray-500">Image</span>
            </div>
            <div className="p-6 flex-grow flex flex-col">
              <h2 className="text-2xl font-bold mb-2">{c.name}</h2>
              <p className="text-gray-400 mb-4 flex-grow">{c.details}</p>
              <div className="flex items-center justify-between mt-4">
                <button
                  onClick={() => handleVote(c.id)}
                  disabled={votesRemaining <= 0}
                  className="flex items-center justify-center w-16 h-16 bg-pink-600 rounded-full text-white hover:bg-pink-700 disabled:bg-gray-600 transition-colors"
                >
                  <Heart size={32} />
                </button>
                <span className="text-5xl font-bold text-pink-400">
                  {votes[c.id] || 0}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {totalVotesUsed > 0 && (
        <div className="mt-12 text-center">
            <button onClick={handleSubmitVotes} className="px-12 py-4 bg-green-600 text-white font-bold text-xl rounded-lg hover:bg-green-700">
                Submit My {totalVotesUsed} Votes
            </button>
        </div>
      )}
    </div>
  );
}

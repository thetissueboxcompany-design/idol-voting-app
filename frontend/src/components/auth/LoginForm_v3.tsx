// ~/idol_voting/frontend/src/components/auth/LoginForm.tsx
'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';

export default function LoginForm() {
  const [identifier, setIdentifier] = useState(''); // Can be mobile or email
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [view, setView] = useState('enter-identifier');

  // New state to manage login method and loading
  const [loginMethod, setLoginMethod] = useState<'mobile' | 'email' | 'loading'>('loading');
  
  const router = useRouter();

  // useEffect to detect user's country on component mount
  useEffect(() => {
    const fetchCountry = async () => {
      try {
        // This is a free geolocation API
        const response = await axios.get('http://ip-api.com/json');
        if (response.data.countryCode === 'IN') {
          setLoginMethod('mobile');
        } else {
          setLoginMethod('email');
        }
      } catch (error) {
        console.error('Could not fetch location, defaulting to email.', error);
        setLoginMethod('email'); // Default to email if API fails
      }
    };
    fetchCountry();
  }, []);

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');

    // Basic validation
    if (loginMethod === 'mobile' && !/^\d{10}$/.test(identifier)) {
        setError('Please enter a valid 10-digit mobile number.');
        return;
    }
    if (loginMethod === 'email' && !/\S+@\S+\.\S+/.test(identifier)) {
        setError('Please enter a valid email address.');
        return;
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL + '/api/auth/send-otp';
      const payload = loginMethod === 'mobile' 
        ? { mobile_number: identifier } 
        : { email: identifier };
        
      await axios.post(apiUrl, payload);
      setMessage('OTP sent successfully! Please check your terminal/email.');
      setView('enter-otp');
    } catch (err) {
      setError('Failed to send OTP. Please try again.');
      console.error(err);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL + '/api/auth/verify-otp';
      const payload = loginMethod === 'mobile'
        ? { mobile_number: identifier, otp_code: otp }
        : { email: identifier, otp_code: otp };

      const response = await axios.post(apiUrl, payload);
      localStorage.setItem('accessToken', response.data.access_token);
      setMessage('Login Successful! Redirecting...');
      router.push('/voting');
    } catch (err) {
      setError('Invalid or expired OTP. Please try again.');
      console.error(err);
    }
  };

  // Loading state while detecting location
  if (loginMethod === 'loading') {
      return <div className="text-center">Detecting your location...</div>;
  }

  // Render the identifier entry form
  if (view === 'enter-identifier') {
    return (
      <div className="w-full max-w-md p-8 space-y-6 bg-gray-800 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-center">Login to Vote</h2>
        <form onSubmit={handleSendOtp} className="space-y-4">
          <div>
            <label htmlFor="identifier" className="block mb-2 text-sm font-medium">
              {loginMethod === 'mobile' ? 'Mobile Number' : 'Email Address'}
            </label>
            <input
              type={loginMethod === 'mobile' ? 'tel' : 'email'}
              id="identifier"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              className="w-full px-3 py-2 text-black bg-gray-200 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-pink-500"
              placeholder={loginMethod === 'mobile' ? 'Enter 10-digit number' : 'Enter your email'}
            />
          </div>
          <button
            type="submit"
            className="w-full px-4 py-2 font-bold text-white bg-pink-600 rounded-md hover:bg-pink-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-pink-500"
          >
            Send OTP
          </button>
        </form>
        {error && <p className="text-sm text-center text-red-500">{error}</p>}
        {message && <p className="text-sm text-center text-green-500">{message}</p>}
      </div>
    );
  }

  // Render the OTP entry form
  return (
    <div className="w-full max-w-md p-8 space-y-6 bg-gray-800 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-center">Verify OTP</h2>
      <p className="text-sm text-center text-gray-400">
        An OTP was sent to {identifier}
      </p>
      <form onSubmit={handleVerifyOtp} className="space-y-4">
        <div>
          <label htmlFor="otp" className="block mb-2 text-sm font-medium">
            Enter 6-Digit OTP
          </label>
          <input
            type="text"
            id="otp"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            className="w-full px-3 py-2 text-black bg-gray-200 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-pink-500"
            placeholder="______"
          />
        </div>
        <button
          type="submit"
          className="w-full px-4 py-2 font-bold text-white bg-pink-600 rounded-md hover:bg-pink-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-pink-500"
        >
          Verify & Login
        </button>
      </form>
      {error && <p className="text-sm text-center text-red-500">{error}</p>}
      {message && <p className="text-sm text-center text-green-500">{message}</p>}
    </div>
  );
}

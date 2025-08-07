// ~/idol_voting/frontend/src/components/auth/LoginForm.tsx
'use client';

import { useState } from 'react';
import axios from 'axios';

// This component manages the two-step login process
export default function LoginForm() {
  const [mobileNumber, setMobileNumber] = useState('');
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  // HIGHLIGHT: This state controls which view is shown: 'enter-mobile' or 'enter-otp'
  const [view, setView] = useState('enter-mobile');

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');

    if (!/^\d{10}$/.test(mobileNumber)) {
      setError('Please enter a valid 10-digit mobile number.');
      return;
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL + '/api/auth/send-otp';
      await axios.post(apiUrl, { mobile_number: mobileNumber });
      setMessage('OTP sent successfully! Please check your backend terminal.');
      setView('enter-otp'); // Switch to the OTP entry view
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
      const response = await axios.post(apiUrl, {
        mobile_number: mobileNumber,
        otp_code: otp,
      });

      // In a real app, we would save this token and redirect the user
      console.log('Login successful! Token:', response.data.access_token);
      setMessage('Login Successful! Redirecting...');
      // We will handle redirection in the next phase
    } catch (err) {
      setError('Invalid or expired OTP. Please try again.');
      console.error(err);
    }
  };

  // Render the mobile number entry form
  if (view === 'enter-mobile') {
    return (
      <div className="w-full max-w-md p-8 space-y-6 bg-gray-800 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-center">Login to Vote</h2>
        <form onSubmit={handleSendOtp} className="space-y-4">
          <div>
            <label htmlFor="mobile" className="block mb-2 text-sm font-medium">
              Mobile Number
            </label>
            <input
              type="tel"
              id="mobile"
              value={mobileNumber}
              onChange={(e) => setMobileNumber(e.target.value)}
              className="w-full px-3 py-2 text-black bg-gray-200 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-pink-500"
              placeholder="Enter 10-digit number"
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
        An OTP was sent to {mobileNumber}
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

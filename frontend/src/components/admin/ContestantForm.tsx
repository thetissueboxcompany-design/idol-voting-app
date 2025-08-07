// ~/idol_voting/frontend/src/components/admin/ContestantForm.tsx
'use client';

import { useState } from 'react';
import axios from 'axios';

interface ContestantFormProps {
  onContestantCreated: () => void;
}

export default function ContestantForm({ onContestantCreated }: ContestantFormProps) {
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  // HIGHLIGHT: Default gender to "Male"
  const [gender, setGender] = useState('Male');
  const [details, setDetails] = useState('');
  const [image, setImage] = useState<File | null>(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    const formData = new FormData();
    formData.append('name', name);
    formData.append('age', age);
    formData.append('gender', gender);
    formData.append('details', details);
    if (image) {
      formData.append('image', image);
    }

    try {
      const token = localStorage.getItem('adminAccessToken');
      if (!token) {
        setError('Admin not authenticated.');
        return;
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL + '/api/admin/contestants';
      await axios.post(apiUrl, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`,
        },
      });

      setSuccess('Contestant created successfully!');
      setName('');
      setAge('');
      setGender('Male'); // Reset to default
      setDetails('');
      setImage(null);
      onContestantCreated();
    } catch (err) {
      setError('Failed to create contestant.');
      console.error(err);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 bg-gray-800 rounded-lg space-y-4">
      <div>
        <label htmlFor="name" className="block text-sm font-medium">Name</label>
        <input type="text" id="name" value={name} onChange={(e) => setName(e.target.value)} required className="mt-1 block w-full px-3 py-2 text-black rounded-md"/>
      </div>
      <div>
        <label htmlFor="age" className="block text-sm font-medium">Age</label>
        <input type="number" id="age" value={age} onChange={(e) => setAge(e.target.value)} required className="mt-1 block w-full px-3 py-2 text-black rounded-md"/>
      </div>
      {/* HIGHLIGHT: Replaced text input with a select dropdown for Gender */}
      <div>
        <label htmlFor="gender" className="block text-sm font-medium">Gender</label>
        <select
          id="gender"
          value={gender}
          onChange={(e) => setGender(e.target.value)}
          required
          className="mt-1 block w-full px-3 py-2 text-black rounded-md"
        >
          <option value="Male">Male</option>
          <option value="Female">Female</option>
          <option value="Others">Others</option>
        </select>
      </div>
       <div>
        <label htmlFor="details" className="block text-sm font-medium">Details</label>
        <textarea id="details" value={details} onChange={(e) => setDetails(e.target.value)} className="mt-1 block w-full px-3 py-2 text-black rounded-md"/>
      </div>
      <div>
        <label htmlFor="image" className="block text-sm font-medium">Image</label>
        <input type="file" id="image" onChange={(e) => setImage(e.target.files ? e.target.files[0] : null)} className="mt-1 block w-full text-sm"/>
      </div>
      <button type="submit" className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 rounded-md font-bold">
        Add Contestant
      </button>
      {error && <p className="text-red-500 text-sm">{error}</p>}
      {success && <p className="text-green-500 text-sm">{success}</p>}
    </form>
  );
}

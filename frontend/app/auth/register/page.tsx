'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
// For Better Auth v0.1.0-beta.13, signUp is accessed differently
// We'll use a direct fetch to the backend authentication endpoint
import { RegisterForm } from '../../../components/auth/RegisterForm';

export default function RegisterPage() {
  const router = useRouter();
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleRegister = async (email: string, password: string, name: string) => {
    setIsLoading(true);
    setError('');

    try {
      // Call the proxy registration endpoint which sets cookies correctly
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, username: name }),
      });

      // Attempt to parse the response as JSON
      let data;
      try {
        data = await response.json();
      } catch (parseErr: unknown) {
        console.error('JSON parsing error:', parseErr);
        setError('Server error: Received unexpected response format from server');
        return;
      }

      if (!response.ok) {
        setError(data.detail?.error || data.error || 'Registration failed');
      } else {
        // Successful registration - store the token and redirect to dashboard
        if (typeof window !== 'undefined' && data.access_token) {
          localStorage.setItem('auth-token', data.access_token);
        }
        router.push('/dashboard');
        router.refresh();
      }
    } catch (err: any) {
      console.error('Registration error:', err);
      // Handle network errors, CORS issues, server unavailability, or timeout
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        setError('Network error: Unable to connect to the server. Please check your connection.');
      } else if (err.name === 'AbortError') {
        setError('Request timeout: The server took too long to respond. Please try again.');
      } else if (err.message && (err.message.includes('HTML instead of JSON') || err.message.includes('response format'))) {
        setError('Server configuration error: Please try again later or contact support.');
      } else if (err.message && (err.message.includes('JSON') || err.message.includes('HTML'))) {
        setError('Server configuration error: Please try again later or contact support.');
      } else {
        setError(err.message || 'An unexpected error occurred');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
        </div>

        <RegisterForm onSubmit={handleRegister} isLoading={isLoading} error={error} />

        <div className="text-center mt-4">
          <p className="text-sm text-gray-600">
            Already have an account?{' '}
            <Link href="/auth/login" className="font-medium text-blue-600 hover:text-blue-500">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
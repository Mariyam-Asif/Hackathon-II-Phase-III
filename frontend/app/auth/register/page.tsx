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
      // Get the backend API URL from environment variables
      const apiUrl = process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:8000';
      const registerUrl = `${apiUrl}/auth/register`;

      // Direct API call to the backend registration endpoint with timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

      const response = await fetch(registerUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, username: name }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      // Attempt to parse the response as JSON
      let data;
      try {
        // Check if response is HTML by looking at the content type
        const contentType = response.headers.get('content-type');

        // If the response is HTML, try to get a text response instead of JSON
        if (contentType && contentType.includes('text/html')) {
          const textResponse = await response.text();
          console.error('HTML response received:', textResponse.substring(0, 200));
          throw new Error('Server configuration error: Received HTML instead of JSON from API endpoint');
        }

        data = await response.json();

        // Additional check: if the response looks like HTML, it might have been parsed as a string
        if (typeof data === 'string' && (data.startsWith('<!DOCTYPE') || data.startsWith('<html>'))) {
          console.error('HTML string received:', data.substring(0, 200));
          throw new Error('Server configuration error: Received HTML instead of JSON from API endpoint');
        }
      } catch (parseErr) {
        // If JSON parsing fails, provide a meaningful error
        console.error('JSON parsing error:', parseErr);
        // Check if it's the specific error we're expecting
        if (parseErr.message && parseErr.message.includes('HTML instead of JSON')) {
          setError('Server configuration error: Please try again later or contact support.');
        } else {
          setError('Server error: Received unexpected response format from server');
        }
        return;
      }

      if (!response.ok) {
        setError(data.detail?.error || data.error || 'Registration failed');
      } else {
        // Successful registration - store the token and redirect to dashboard
        if (typeof window !== 'undefined' && data.access_token) {
          localStorage.setItem('better-auth-session', data.access_token);
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
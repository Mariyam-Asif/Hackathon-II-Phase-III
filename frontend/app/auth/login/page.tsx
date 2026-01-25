'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
// For Better Auth v0.1.0-beta.13, signIn is accessed differently
// We'll use a direct fetch to the backend authentication endpoint
import { LoginForm } from '../../../components/auth/LoginForm';

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Get the return URL from query params
  const returnUrl = searchParams.get('return') || '/dashboard';

  const handleLogin = async (email: string, password: string) => {
    setIsLoading(true);
    setError('');

    try {
      // Get the backend API URL from environment variables
      const apiUrl = process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:8000';
      const loginUrl = `${apiUrl}/auth/login`;

      // Direct API call to the backend authentication endpoint with timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

      const response = await fetch(loginUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
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
        // Check if it's a user not registered error
        if (data.code === 'USER_NOT_REGISTERED' || data.detail?.code === 'USER_NOT_REGISTERED') {
          setError(data.detail?.error || data.error || 'No account found with this email. Please register first.');
        } else {
          setError(data.detail?.error || data.error || 'Login failed');
        }
      } else {
        // Successful login - store the token and redirect to return URL or dashboard
        if (typeof window !== 'undefined' && data.access_token) {
          localStorage.setItem('better-auth-session', data.access_token);
        }
        router.push(returnUrl);
        router.refresh();
      }
    } catch (err: any) {
      console.error('Login error:', err);
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
            Sign in to your account
          </h2>
        </div>

        <LoginForm onSubmit={handleLogin} isLoading={isLoading} error={error} />

        <div className="text-center mt-4">
          <p className="text-sm text-gray-600">
            Don't have an account?{' '}
            <Link href="/auth/register" className="font-medium text-blue-600 hover:text-blue-500">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
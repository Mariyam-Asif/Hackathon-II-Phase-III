'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Suspense } from 'react';
// For Better Auth v0.1.0-beta.13, signIn is accessed differently
// We'll use a direct fetch to the backend authentication endpoint
import { LoginForm } from '../../../components/auth/LoginForm';

// Wrap the actual component to handle the useSearchParams hook
function LoginPageContent() {
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
      // Use the internal API route to handle login.
      // This route will proxy the request to the backend and set a secure HttpOnly cookie.
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const data = await response.json();
        // Check for specific error codes or messages from the backend
        if (data.code === 'USER_NOT_REGISTERED' || data.detail?.code === 'USER_NOT_REGISTERED') {
          setError(data.detail?.error || data.error || 'No account found with this email. Please register first.');
        } else {
          setError(data.detail?.error || data.error || 'Login failed');
        }
      } else {
        // Successful login, the server has set the cookie.
        // Now we can redirect to the dashboard.
        router.push(returnUrl);
      }
    } catch (err: any) {
      console.error('Login error:', err);
      setError('An unexpected error occurred during login. Please try again.');
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

export default function LoginPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LoginPageContent />
    </Suspense>
  );
}
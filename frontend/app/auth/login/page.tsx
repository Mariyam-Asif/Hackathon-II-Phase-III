'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Suspense } from 'react';
import { useAuth } from '../../auth-provider';
import { LoginForm } from '../../../components/auth/LoginForm';
import { useRouter, useSearchParams } from 'next/navigation';

// Wrap the actual component to handle the useSearchParams hook
function LoginPageContent() {
  const { login } = useAuth();
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
      await login(email, password);
      window.location.href = returnUrl;
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
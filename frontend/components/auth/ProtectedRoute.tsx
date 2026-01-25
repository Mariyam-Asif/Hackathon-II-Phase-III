'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function ProtectedRoute({ children, fallback }: ProtectedRouteProps) {
  const [session, setSession] = useState<any>(null);
  const [isPending, setIsPending] = useState(true);

  useEffect(() => {
    // For Better Auth integration, we can validate the token using the validate-token endpoint
    const checkAuth = async () => {
      try {
        // Try to validate token from localStorage or cookies
        const token = typeof window !== 'undefined' ? localStorage.getItem('better-auth-session') : null;

        if (!token) {
          setSession(null);
          setIsPending(false);
          return;
        }

        // Get the backend API URL from environment variables
        const apiUrl = process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:8000';
        const validateUrl = `${apiUrl}/auth/validate-token`;

        // Validate the token with the backend
        const response = await fetch(validateUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ token }),
        });

        if (response.ok) {
          const data = await response.json();
          if (data.valid) {
            setSession({ user: { id: data.user_id } }); // Simplified session object
          } else {
            setSession(null);
          }
        } else {
          setSession(null);
        }
      } catch (error) {
        console.error('Error checking auth status:', error);
        setSession(null);
      } finally {
        setIsPending(false);
      }
    };

    checkAuth();
  }, []);
  const router = useRouter();
  const pathname = usePathname();

  // If no fallback is provided, show a simple spinner while checking auth status
  if (isPending) {
    return fallback || (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  // If user is not authenticated, redirect to login
  if (!session) {
    // Store the attempted route for redirect after login
    const returnUrl = encodeURIComponent(pathname);
    router.replace(`/auth/login?return=${returnUrl}`);
    return null;
  }

  // If authenticated, render the protected content
  return <>{children}</>;
}
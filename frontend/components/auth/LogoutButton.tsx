'use client';

import { useState } from 'react';
// For Better Auth v0.1.0-beta.13, signOut is accessed differently
// We'll use a direct fetch to the backend authentication endpoint
import { useRouter } from 'next/navigation';

interface LogoutButtonProps {
  onLogout?: () => void;
}

export function LogoutButton({ onLogout }: LogoutButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleLogout = async () => {
    setIsLoading(true);

    try {
      // Get the backend API URL from environment variables
      const apiUrl = process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:8000';
      const logoutUrl = `${apiUrl}/auth/logout`;

      // Direct API call to the backend logout endpoint
      const response = await fetch(logoutUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        // Optionally call the onLogout callback
        if (onLogout) {
          onLogout();
        }

        // Refresh the page to update the UI
        router.refresh();
        // Navigate to login page
        router.push('/auth/login');
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={handleLogout}
      disabled={isLoading}
      className="ml-4 px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
    >
      {isLoading ? 'Logging out...' : 'Logout'}
    </button>
  );
}
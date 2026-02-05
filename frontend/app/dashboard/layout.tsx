import Link from 'next/link';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { LogoutButton } from '../../components/auth/LogoutButton';

// Helper function to parse the JWT payload.
const parseJwt = (token: string) => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Failed to parse JWT:', error);
    return null;
  }
};

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // This is now a Server Component, so we can securely access cookies.
  const cookieStore = await cookies();
  const token = cookieStore.get('better-auth.session_token')?.value;

  if (!token) {
    // This should not happen if middleware is set up correctly,
    // but as a safeguard, redirect to login if no token is found.
    redirect('/auth/login');
  }

  const userData = parseJwt(token);
  const userIdentifier = userData?.email || 'User';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <span className="text-xl font-bold text-gray-900">Todo App</span>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <Link
                  href="/dashboard"
                  className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                >
                  Dashboard
                </Link>
                <Link
                  href={userData?.sub ? `/dashboard/tasks?userId=${userData.sub}` : '/dashboard/tasks'}
                  className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                >
                  Tasks
                </Link>
              </div>
            </div>
            <div className="flex items-center">
              <div className="ml-3 relative">
                <div className="text-sm text-gray-700">
                  Welcome, {userIdentifier}
                </div>
              </div>
              <div className="ml-4">
                <LogoutButton />
              </div>
            </div>
          </div>
        </div>
      </nav>

      <main>
        {children}
      </main>
    </div>
  );
}
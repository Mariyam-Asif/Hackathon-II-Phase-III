import Link from 'next/link';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

// Helper function to parse the JWT payload.
// Note: This does not validate the token's signature.
// It's safe to use here because this page is protected by middleware
// which should have already validated the token before allowing access.
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

export default function DashboardPage() {
  // This is now a Server Component, so we can securely access cookies on the server.
  const cookieStore = await cookies();
  const token = cookieStore.get('better-auth.session_token')?.value;

  if (!token) {
    // This should not happen if the middleware is set up correctly,
    // but as a safeguard, we redirect to login if no token is found.
    redirect('/auth/login');
  }

  const userData = parseJwt(token);
  // Use email as the identifier, fall back to the user ID ('sub'), or a generic 'User'.
  const userIdentifier = userData?.email || userData?.sub || 'User';
  const userId = userData?.sub; // 'sub' is the standard JWT claim for the subject (user ID).

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <div className="bg-white shadow rounded-lg p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-1">
            Dashboard
          </h1>
          <p className="text-md text-gray-600 mb-6">
            Welcome, <span className="font-semibold">{userIdentifier}</span>!
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h2 className="text-lg font-semibold text-blue-800">Manage Tasks</h2>
              <p className="text-blue-600 mt-2">View and manage your tasks.</p>
              <Link
                href={userId ? `/dashboard/tasks?userId=${userId}` : '/dashboard/tasks'}
                className="mt-3 inline-block bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Go to Tasks
              </Link>
            </div>

            <div className="bg-green-50 p-4 rounded-lg">
              <h2 className="text-lg font-semibold text-green-800">Account Settings</h2>
              <p className="text-green-600 mt-2">Update your account information.</p>
              <button
                className="mt-3 inline-block bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 cursor-not-allowed"
                disabled
              >
                Coming Soon
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
'use client';

import { useEffect } from 'react';
import Link from 'next/link';

export default function DashboardPage() {

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <div className="bg-white shadow rounded-lg p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Dashboard</h1>


          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h2 className="text-lg font-semibold text-blue-800">Manage Tasks</h2>
              <p className="text-blue-600 mt-2">View and manage your tasks</p>
              <Link
                href="/dashboard/tasks"
                className="mt-3 inline-block bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Go to Tasks
              </Link>
            </div>

            <div className="bg-green-50 p-4 rounded-lg">
              <h2 className="text-lg font-semibold text-green-800">Account Settings</h2>
              <p className="text-green-600 mt-2">Update your account information</p>
              <button
                className="mt-3 inline-block bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
                disabled
              >
                Account Settings
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
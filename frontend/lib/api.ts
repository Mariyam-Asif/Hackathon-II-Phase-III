
'use client';

import { authService } from './auth';

// A wrapper around fetch that adds the Authorization header to requests
export const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  const token = authService.getToken();

  const headers = {
    ...options.headers,
    'Content-Type': 'application/json',
  };

  if (token) {
    // @ts-ignore
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const errorMessage = 
      errorData.detail?.error || 
      (typeof errorData.detail === 'string' ? errorData.detail : null) || 
      errorData.error || 
      'API request failed';
    throw new Error(errorMessage);
  }

  return response.json();
};

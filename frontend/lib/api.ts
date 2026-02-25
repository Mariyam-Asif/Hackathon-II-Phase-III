
import { getToken } from './token-utils';

// A wrapper around fetch that adds the Authorization header to requests
export const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  const token = getToken();

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
    
    // Create an error object with status
    const error: any = new Error(errorMessage);
    error.status = response.status;
    throw error;
  }

  return response.json();
};

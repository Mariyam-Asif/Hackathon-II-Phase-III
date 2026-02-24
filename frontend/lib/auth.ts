import { fetchWithAuth } from './api';
import { getToken, setToken, removeToken, isAuthenticated } from './token-utils';

// Authentication service for Better Auth integration
// Handles login, registration, token management, and user session

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
  username: string;
}

interface AuthResponse {
  user_id: string;
  email: string;
  username: string;
  access_token: string;
  token_type?: string;
}

class AuthService {
  private baseUrl: string;

  constructor() {
    // In the browser, we want to hit our Next.js API routes which proxy to the backend
    // On the server (e.g., in a route handler), we want to hit the backend directly
    if (typeof window !== 'undefined') {
      this.baseUrl = '/api';
    } else {
      this.baseUrl = process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:8000';
    }
  }

  // Login user and store token
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const data: AuthResponse = await fetchWithAuth(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      body: JSON.stringify({
        email: credentials.email,
        password: credentials.password,
      }),
    });

    // Store the token in localStorage for use with API calls
    if (data.access_token) {
      setToken(data.access_token);
    }

    return data;
  }

  // Register new user
  async register(userData: RegisterData): Promise<AuthResponse> {
    const data: AuthResponse = await fetchWithAuth(`${this.baseUrl}/auth/register`, {
      method: 'POST',
      body: JSON.stringify({
        email: userData.email,
        password: userData.password,
        username: userData.username,
      }),
    });

    // Store the token in localStorage for use with API calls
    if (data.access_token) {
      setToken(data.access_token);
    }

    return data;
  }

  // Logout user by clearing stored token
  async logout(): Promise<void> {
    // Clear the stored token
    removeToken();

    // Call the backend logout endpoint (stateless, just for consistency)
    try {
      await fetchWithAuth(`${this.baseUrl}/auth/logout`, {
        method: 'POST',
      });
    } catch (error) {
      // Ignore logout errors as logout is client-side anyway
      console.warn('Logout request failed:', error);
    }
  }

  // Validate current token
  async validateToken(token?: string): Promise<boolean> {
    const authToken = token || getToken();

    if (!authToken) {
      return false;
    }

    try {
      const data = await fetchWithAuth(`${this.baseUrl}/auth/validate-token`, {
        method: 'POST',
        body: JSON.stringify({ token: authToken }),
      });
      return data.valid === true;
    } catch (error) {
      console.error('Token validation error:', error);
      return false;
    }
  }

  // Get current user token
  getToken(): string | null {
    return getToken();
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return isAuthenticated();
  }
}

// Export singleton instance
export const authService = new AuthService();

// Export types
export type { LoginCredentials, RegisterData, AuthResponse };

// Export for direct use in components
export default AuthService;
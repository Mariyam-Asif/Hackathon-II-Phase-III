'use client';

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
    this.baseUrl = process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:8000';
  }

  // Login user and store token
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: credentials.email,
        password: credentials.password,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail?.error || errorData.error || 'Login failed');
    }

    const data: AuthResponse = await response.json();

    // Store the token in localStorage for use with API calls
    if (typeof window !== 'undefined' && data.access_token) {
      localStorage.setItem('auth-token', data.access_token);
    }

    return data;
  }

  // Register new user
  async register(userData: RegisterData): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: userData.email,
        password: userData.password,
        username: userData.username,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail?.error || errorData.error || 'Registration failed');
    }

    const data: AuthResponse = await response.json();

    // Store the token in localStorage for use with API calls
    if (typeof window !== 'undefined' && data.access_token) {
      localStorage.setItem('auth-token', data.access_token);
    }

    return data;
  }

  // Logout user by clearing stored token
  async logout(): Promise<void> {
    // Clear the stored token
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth-token');
    }

    // Call the backend logout endpoint (stateless, just for consistency)
    try {
      await fetch(`${this.baseUrl}/auth/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
    } catch (error) {
      // Ignore logout errors as logout is client-side anyway
      console.warn('Logout request failed:', error);
    }
  }

  // Validate current token
  async validateToken(token?: string): Promise<boolean> {
    const authToken = token || (typeof window !== 'undefined' ? localStorage.getItem('auth-token') : null);

    if (!authToken) {
      return false;
    }

    try {
      const response = await fetch(`${this.baseUrl}/auth/validate-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token: authToken }),
      });

      if (!response.ok) {
        return false;
      }

      const data = await response.json();
      return data.valid === true;
    } catch (error) {
      console.error('Token validation error:', error);
      return false;
    }
  }

  // Get current user token
  getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth-token');
    }
    return null;
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return this.getToken() !== null;
  }
}

// Export singleton instance
export const authService = new AuthService();

// Export types
export type { LoginCredentials, RegisterData, AuthResponse };

// Export for direct use in components
export default AuthService;
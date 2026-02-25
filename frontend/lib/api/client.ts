// Base API client with JWT token injection
class ApiClient {
  private baseUrl: string;

  constructor() {
    // In the browser, we use the relative /api prefix to hit our Next.js proxy
    if (typeof window !== 'undefined') {
      this.baseUrl = '/api';
    } else {
      this.baseUrl = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') + '/api';
    }
  }

  // Generic request method with JWT token injection
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    // Get the token from localStorage (where Better Auth would store it)
    const token = typeof window !== 'undefined'
      ? localStorage.getItem('auth-token')
      : null;

    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    };

    // Adjust the base URL for local development
    // When running locally, the backend runs on port 8000
    const fullUrl = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}${endpoint}`;

    console.log(`API Request: ${options.method || 'GET'} ${fullUrl}`);

    const response = await fetch(fullUrl, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.detail || errorData.error || `API request failed: ${response.status}`;
      console.error(`API Error (${response.status}):`, errorMessage);
      throw new Error(errorMessage);
    }

    // Handle 204 No Content responses (common for DELETE requests)
    if (response.status === 204) {
      return undefined as unknown as T; // Return undefined for 204 responses
    }

    return response.json();
  }

  // GET request
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  // POST request
  async post<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // PUT request
  async put<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // PATCH request
  async patch<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  // DELETE request
  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export the class for potential extension
export default ApiClient;